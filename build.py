"""Build entry point.
  python -X utf8 build.py build    -> build/recca_en.gba     (English where `en` is filled, Japanese elsewhere)
  python -X utf8 build.py marker   -> build/recca_marker.gba (every line replaced by its short id + filler)
  python -X utf8 build.py release  -> release/recca-no-honoo-the-game_en.zip (see tools/release.py)
Layout of the output: original 8 MiB untouched except pointer slots, the AC table, the glyph hook; everything new is
appended from 0x800000 (allowed ranges in build/ranges.txt for romdiff)."""
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools'))
import textlib as T  # noqa: E402

DIALOGUE = {'max': 13, 'lines': 3}          # story box: 13 cells x 14 px, 3 lines
PROFILE_CELLS = 10
HOOK_SITE = 0xC6CC                          # `ldrh r0,[r3]` -> `bx r3`
HOOK_LIT = 0xC6D4                           # font-pointer literal -> hook | 1
MEMBERS = 0x43B374                         # 5 pointers to party-member names
MEMBER_SEP = 0xC91A                         # `beq` that skips the separator before the first name
FILLER ='The quick brown fox jumps over the lazy dog while five wizards box quickly'


class Fit(Exception):
    pass


def hook_code(addr, font_addr):
    from keystone import Ks, KS_ARCH_ARM, KS_MODE_THUMB
    src = f"""
        lsrs r0, r1, #8
        cmp r0, #0x88
        bcc orig
        subs r0, #0x88
        movs r2, #192
        muls r0, r2, r0
        lsls r2, r1, #24
        lsrs r2, r2, #24
        subs r2, #0x40
        adds r0, r0, r2
        movs r2, #24
        muls r0, r2, r0
        ldr r3, =0x{font_addr | T.ROMBASE:08X}
        adds r3, r3, r0
        b done
    orig:
        ldr r3, =0x{T.FONT_JP | T.ROMBASE:08X}
    done:
        ldrh r0, [r3]
        ldr r2, =0x0000FFFF
        ldr r4, =0x0800C6E1
        bx r4
        .align 2
    """
    ks = Ks(KS_ARCH_ARM, KS_MODE_THUMB)
    enc, _ = ks.asm(src, addr | T.ROMBASE)
    return bytes(enc)


class Builder:
    def __init__(self, marker=False, qa=None):
        self.qa = qa or {}                       # {id: English} test overrides (build.py build --qa ID=text)
        self.d = T.rom()
        self.out = bytearray(self.d) + b'\xff' * 0  # grows by append()
        self.marker = marker
        self.font = T.Font()
        self.alloc = T.CodeAlloc()
        self.ranges = []
        self.errors = []
        self.slots = []                          # (slot offset, target offset) for jp_left --slots
        self.stats = {'en': 0, 'jp': 0}

    def append(self, blob, align=4):
        if len(self.out) < T.FREE_START:
            self.out += b'\xff' * (T.FREE_START - len(self.out))
        while len(self.out) % align:
            self.out.append(0xFF)
        at = len(self.out)
        self.out += blob
        assert len(self.out) <= 0x1000000, 'ROM over 16 MiB'
        return at

    def patch32(self, off, value):
        struct.pack_into('<I', self.out, off, value)
        self.ranges.append((off, off + 4))

    # ---- encoding ----
    def enc_lines(self, lines, pads=None):
        out = []
        for k, line in enumerate(lines):
            items, n = T.layout_line(T.tokens(line), self.font)
            if pads and k < len(pads) and pads[k] and n < pads[k]:
                items += [('w', '　')] * (pads[k] - n)
            out.append(T.encode_items(items, self.alloc))
        return b'%n'.join(out)

    def fit(self, text, max_cells, max_lines, where):
        lines = T.wrap(text, self.font, max_cells)
        bad = [ln for ln in lines if T.line_cells(ln, self.font) > max_cells]
        if bad or len(lines) > max_lines:
            raise Fit(f'{where}: {len(lines)} lines (max {max_lines}), widest '
                      f'{max(T.line_cells(ln, self.font) for ln in lines)} cells (max {max_cells}): {text!r}')
        return lines

    def marker_text(self, tag, jp, max_cells, max_lines):
        ctrl = ''.join(c for c in T.CTRL_RE.findall(jp) if c != '%n')
        words = FILLER.split()
        best = tag
        for n in range(len(words) + 1):
            cand = ' '.join([tag] + words[:n])
            try:
                self.fit(cand, max_cells, max_lines, tag)
                best = cand
            except Fit:
                break
        # keep the control codes (waits, colour, %K) so timing/flags behave as in the original
        return best + ctrl

    # ---- story scripts ----
    def build_ac(self):
        for i in range(T.AC_COUNT):
            f = T.ac_parse(self.d, i)
            if not f['strings']:
                continue
            path = ROOT / 'script' / 'ac' / ('%02d_%s.json' % (i, T.AC_NAMES[i]))
            entries = json.loads(path.read_text(encoding='utf-8'))
            strings = []
            for k, e in enumerate(entries):
                tag = 'A%d.%d' % (i, k)
                if e['id'] in self.qa:
                    e = dict(e, en=self.qa[e['id']])
                try:
                    if self.marker:
                        txt = self.marker_text(tag, e['jp'], DIALOGUE['max'], DIALOGUE['lines'])
                    elif e.get('en'):
                        txt = e['en']
                    else:
                        strings.append(T.encode_jp(e['jp']))
                        self.stats['jp'] += 1
                        continue
                    lines = self.fit(txt, DIALOGUE['max'], DIALOGUE['lines'], e['id'])
                    strings.append(self.enc_lines(lines))
                    self.stats['en'] += 1
                except Fit as ex:
                    self.errors.append(str(ex))
                    strings.append(T.encode_jp(e['jp']))
            blob = T.ac_build(f['head'], strings)
            at = self.append(blob)
            self.patch32(T.AC_TABLE + 4 * i, at | T.ROMBASE)
            st = T.u16(blob, 10)
            for k in range(len(strings)):   # slot = string-table entry, target = the string
                self.slots.append(('%X' % (at + st + 2 * k), '%X' % (at + T.u16(blob, st + 2 * k))))

    # ---- system strings ----
    def build_sys(self):
        entries = json.loads((ROOT / 'script' / 'sys.json').read_text(encoding='utf-8'))
        for n, e in enumerate(entries):
            cells = e['cells']
            pads = cells   # widgets show a fixed number of cells: pad to the JP count so no stale cell stays
            max_cells = e.get('max', max(cells))
            max_lines = e.get('lines', len(cells))
            sep = b'\n' if '\n' in e['jp'] else b'%n'
            try:
                if self.marker and e.get('layout') == 'digits':
                    txt = self.marker_text('S%d' % n, '', 6, 1) + e['jp'][-3:]
                elif self.marker:
                    txt = self.marker_text('S%d' % n, e['jp'], max_cells, max_lines)
                elif e.get('en'):
                    txt = e['en']
                else:
                    self.stats['jp'] += 1
                    continue
                if e.get('layout') == 'digits':   # 6-cell label + the JP digit tail the code patches in RAM
                    tail = e['jp'][-3:]
                    label = txt[:-3].rstrip() if txt.endswith(tail) else txt
                    self.fit(label, 6, 1, e['id'])
                    blob = self.enc_lines([label], [6]) + T.encode_jp(tail)
                    assert len(blob) == 18, e['id']
                    at = self.append(blob + b'\0', align=1)
                    for s in e['slots']:
                        self.patch32(int(s, 16), at | T.ROMBASE)
                    self.stats['en'] += 1
                    continue
                lines = self.fit(txt, max_cells, max_lines, e['id'])
                lines += [''] * (len(cells) - len(lines))
                blob =self.enc_lines(lines, pads).replace(b'%n', sep) if sep == b'\n' else self.enc_lines(lines, pads)
                self.stats['en'] += 1
            except Fit as ex:
                self.errors.append(str(ex))
                continue
            at = self.append(blob + b'\0', align=1)
            for s in e['slots']:
                self.patch32(int(s, 16), at | T.ROMBASE)
                self.slots.append((s, '%X' % at))

    # ---- database profiles ----
    def build_profiles(self):
        entries = json.loads((ROOT / 'script' / 'profiles.json').read_text(encoding='utf-8'))
        pad = [PROFILE_CELLS]
        for n, e in enumerate(entries):
            try:
                if self.marker:
                    name = 'P%d name' % n
                    body = self.marker_text('P%d' % n, '', PROFILE_CELLS, 99)
                elif e.get('en'):
                    name, body = e['name'], e['en']
                else:
                    self.stats['jp'] += 1
                    continue
                lines = [name]
                for para in body.split('\n\n'):
                    if len(lines) > 1:
                        lines.append('')
                    lines += self.fit(para.replace('\n', ' '), PROFILE_CELLS, 99, e['id'])
                self.stats['en'] += 1
            except Fit as ex:
                self.errors.append(str(ex))
                continue
            ptrs = bytearray()
            for ln in lines:
                at = self.append(self.enc_lines([ln], pad) + b'\0', align=1)
                ptrs += struct.pack('<I', at | T.ROMBASE)
            arr = self.append(bytes(ptrs))
            self.patch32(e['table'], arr | T.ROMBASE)
            self.patch32(e['table'] + 4, len(lines))

    # ---- party-member names (story placeholder σ...: renderer 0x0800C8F0, 12 cells, names table 0x0843B374) ----
    def build_members(self):
        names = ['Recca,', 'Domon,', 'Fuko,', 'Mikagami,', 'Koganei,']   # trailing comma: the separator is cut
        for k, n in enumerate(names):
            at = self.append(self.enc_lines([n]) + b'\0', align=1)
            self.patch32(MEMBERS + 4 * k, at | T.ROMBASE)
        self.out[MEMBER_SEP:MEMBER_SEP + 2] = bytes.fromhex('09E0')   # beq -> b: no '・' cell between names
        self.ranges.append((MEMBER_SEP, MEMBER_SEP + 2))

    # ---- glyphs + hook ----
    def finish(self):
        table = self.alloc.table()
        font_at = self.append(table + b'\xff\xff')
        hook_at = self.append(b'\0' * 64)
        code = hook_code(hook_at, font_at)
        assert len(code) <= 64
        self.out[hook_at:hook_at + len(code)] = code
        self.out[HOOK_SITE:HOOK_SITE + 2] = bytes.fromhex('1847')   # bx r3
        self.ranges.append((HOOK_SITE, HOOK_SITE + 2))
        self.patch32(HOOK_LIT, (hook_at | T.ROMBASE) | 1)
        self.ranges.append((T.FREE_START, len(self.out)))
        while len(self.out) % 0x10:
            self.out.append(0xFF)

    def run(self, out_path):
        self.build_ac()
        self.build_sys()
        self.build_profiles()
        self.build_members()
        self.finish()
        out_path.parent.mkdir(exist_ok=True)
        out_path.write_bytes(self.out)
        rng = '\n'.join('%X-%X' % (a, b - 1) for a, b in sorted(self.ranges))
        (out_path.parent / 'ranges.txt').write_text(rng + '\n', encoding='utf-8', newline='\n')
        (out_path.parent / 'slots.txt').write_text(''.join(f'{s} {t}\n' for s, t in self.slots),
                                                     encoding='utf-8', newline='\n')
        print(f'{out_path.name}: {len(self.out):#x} bytes, glyphs {len(self.alloc.codes)}, '
              f'en {self.stats["en"]} jp {self.stats["jp"]}, fit errors {len(self.errors)}')
        for e in self.errors[:40]:
            print('  FIT', e)
        return 0 if not self.errors else 1


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'build'
    if cmd == 'build':
        qa = dict(a.split('=', 1) for a in sys.argv[2:] if '=' in a)
        out = ROOT / 'build' / ('recca_qa.gba' if qa else 'recca_en.gba')
        return Builder(qa=qa).run(out)
    if cmd == 'marker':
        return Builder(marker=True).run(ROOT / 'build' / 'recca_marker.gba')
    if cmd == 'release':
        import subprocess
        return subprocess.call([sys.executable, '-X', 'utf8', str(ROOT / 'tools' / 'release.py')] + sys.argv[2:])
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main())
