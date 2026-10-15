"""Core text library: ROM layout, .AC script files, system strings, English VWF cell encoder.

Engine facts: docs/re/text.md. Every glyph the game draws is one 2-byte code = one 16x16 cell, placed at a fixed
pitch (14 px in dialogue). English is set with a proportional font at build time: glyphs are laid out on a
continuous x axis, never straddling a cell edge (spaces may), and each cell's content becomes one generated glyph
(code lead 0x88-0xFF, trail 0x40-0xFF) in a new font table that a small hook indexes directly.
"""
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ORIG = ROOT / 'rom' / 'Recca no Honoo - The Game (Japan).gba'
ROMBASE = 0x08000000

AC_TABLE = 0x468354
AC_COUNT = 23
AC_NAMES = ['INIT', 'INTRO1', 'INTRO2', 'INTRO3', 'CLOSE1', 'CLOSE2', 'RECCA1', 'RECCA2', 'RECCA3', 'DOMON1',
            'DOMON2', 'DOMON3', 'FUKO1', 'FUKO2', 'FUKO3', 'TOKIYA1', 'TOKIYA2', 'TOKIYA3', 'KAORU1', 'KAORU2',
            'KAORU3', 'CREY', 'VIEW-CHR']
SYS_LO, SYS_HI = 0x4B460, 0x4F8E4          # system string block
SLOT_RANGES = [(0, 0x50000), (0x467000, 0x46C000)]   # where real pointers to system strings live
SYS_DATA = [(0x4C236, 0x4C254), (0x4F82C, 0x4F89C)]  # non-text tables inside the block

FONT_JP = 0x7403BC
CELL = 14                                   # default cell pitch (px)
FREE_START = 0x800000                       # new data is appended past the original 8 MiB

CTRL_RE = re.compile(r'%[TWwP].|%[A-Za-z/]')


def rom():
    return ORIG.read_bytes()


def u16(d, o):
    return struct.unpack_from('<H', d, o)[0]


def u32(d, o):
    return struct.unpack_from('<I', d, o)[0]


# ---------- Shift-JIS with control codes ----------

def decode(b):
    """Bytes -> text. `%x` codes and `\\n` pass through as ASCII; bad pairs become [XXXX]."""
    out, i = [], 0
    while i < len(b):
        c = b[i]
        if c < 0x80:
            out.append(chr(c))
            i += 1
            continue
        pair = b[i:i + 2]
        try:
            out.append(pair.decode('cp932'))
        except UnicodeDecodeError:
            out.append('[%02X%02X]' % (pair[0], pair[1]))
        i += 2
    return ''.join(out)


def encode_jp(s):
    out, i = bytearray(), 0
    while i < len(s):
        m = re.match(r'\[([0-9A-F]{4})\]', s[i:])
        if m:
            out += bytes.fromhex(m.group(1))
            i += 6
            continue
        out += s[i].encode('cp932')
        i += 1
    return bytes(out)


def cstr(d, o):
    return d[o:d.index(b'\0', o)]


# ---------- .AC script files ----------

def ac_parse(d, idx):
    base = u32(d, AC_TABLE + 4 * idx) - ROMBASE
    assert d[base:base + 4] == b'%ASS'
    nl, ol, ns, os_ = struct.unpack_from('<4H', d, base + 4)
    offs = struct.unpack_from('<%dH' % ns, d, base + os_) if ns else ()
    strings = [cstr(d, base + o) for o in offs]
    end = base + os_ + 2 * ns
    if offs:
        end = base + offs[-1] + len(strings[-1]) + 1
    # strings follow the string table in order, contiguous
    pos = base + os_ + 2 * ns
    for o, s in zip(offs, strings):
        assert base + o == pos, (idx, hex(base + o), hex(pos))
        pos += len(s) + 1
    return {'base': base, 'head': d[base:base + os_], 'nlabels': nl, 'strings': strings, 'end': end}


def ac_build(head, strings):
    """head = everything before the string table (header, bytecode, label table)."""
    ns = len(strings)
    os_ = len(head)
    h = bytearray(head)
    struct.pack_into('<H', h, 8, ns)
    struct.pack_into('<H', h, 10, os_)
    table, body, pos = bytearray(), bytearray(), os_ + 2 * ns
    for s in strings:
        table += struct.pack('<H', pos)
        body += s + b'\0'
        pos += len(s) + 1
    assert pos < 0x10000, 'AC file too big for u16 offsets'
    return bytes(h + table + body)


# ---------- system strings ----------

def sys_slots(d):
    """{string offset: [pointer slot offsets]} for every aligned pointer into the system block."""
    refs = {}
    for lo, hi in SLOT_RANGES:
        for o in range(lo, hi, 4):
            v = u32(d, o) - ROMBASE
            if SYS_LO <= v < SYS_HI:
                refs.setdefault(v, []).append(o)
    return refs


def sys_strings(d):
    """[(offset, bytes)] for every NUL-terminated string in the block that contains Japanese and has a pointer."""
    refs = sys_slots(d)
    out, o = [], SYS_LO
    while o < SYS_HI:
        if d[o] == 0 or any(a <= o < b for a, b in SYS_DATA):
            o += 1
            continue
        e = d.index(b'\0', o)
        s = d[o:e]
        if re.search(rb'[\x81-\x9f\xe0-\xef][\x40-\xfc]', s) and o in refs:
            out.append((o, s))
        o = e
    return out, refs


# ---------- English font + cell encoder ----------

class Font:
    def __init__(self, path=ROOT / 'tbl' / 'font_en.txt'):
        self.glyphs = {}   # char -> (top, rows[list of str], adv)
        cur = None
        for line in Path(path).read_text(encoding='utf-8').splitlines():
            if line.startswith('#') and not cur:
                continue
            if line.startswith('== '):
                parts = line[3:].split()
                ch = parts[0]
                ch = chr(int(ch[2:], 16)) if ch.startswith('U+') else ch
                top = int(parts[1])
                adv = None
                for p in parts[2:]:
                    if p.startswith('adv='):
                        adv = int(p[4:])
                cur = [ch, top, [], adv]
                self.glyphs[ch] = cur
            elif line.strip() == '':
                cur = None
            elif cur is not None:
                cur[2].append(line)
        for ch, g in list(self.glyphs.items()):
            w = max(len(r) for r in g[2])
            assert g[1] + len(g[2]) <= 11, ch
            self.glyphs[ch] = (g[1], g[2], g[3] if g[3] is not None else w + 1)

    def adv(self, ch):
        return self.glyphs[ch][2]

    def has(self, ch):
        return ch in self.glyphs


SUBST = {'‘': "'", '’': "'", '“': '"', '”': '"', '–': '-', '　': ' '}


def tokens(s):
    """Text -> list of ('c', ctrl) | ('n',) newline | ('t', char) | ('w', fullwidth char)."""
    out, i = [], 0
    while i < len(s):
        m = CTRL_RE.match(s, i)
        if m:
            code = m.group(0)
            out.append(('n',) if code == '%n' else ('c', code))
            i = m.end()
            continue
        ch = SUBST.get(s[i], s[i])
        if ch == '\n':
            out.append(('n',))
        elif ord(ch) < 0x80 or ch in '—…':
            out.append(('t', ch))
        else:
            out.append(('w', ch))
        i += 1
    return out


def layout_line(toks, font, pitch=CELL):
    """One line of tokens -> list of cells; each cell = ('g', ((char, x), ...)) | ('w', fullwidth) and controls
    ('c', code) placed between cells. Returns (items, ncells)."""
    items, cur, cs, x = [], [], 0, 0

    def close():  # finish the current cell (blank if it only holds space) and move to the next
        nonlocal cur, cs, x
        items.append(('g', tuple(cur)) if cur else ('w', '　'))
        cur = []
        cs += pitch
        x = max(x, cs)

    for t in toks:
        if t[0] == 'c':
            if cur:  # a control code (colour, wait) closes the current cell
                close()
                x = cs
            items.append(t)
        elif t[0] == 'w':
            if cur or x > cs:
                close()
                x = cs
            items.append(('w', t[1]))
            cs += pitch
            x = cs
        else:
            ch = t[1]
            a = font.adv(ch)
            if ch == ' ':
                x += a
                while x >= cs + pitch:   # whitespace may cross cell edges
                    close()
                continue
            if x + a > cs + pitch:
                close()
                x = cs
            cur.append((ch, x - cs))
            x += a
    if cur:
        items.append(('g', tuple(cur)))
    ncells = sum(1 for it in items if it[0] in 'gw')
    return items, ncells


def line_cells(text, font, pitch=CELL):
    return layout_line(tokens(text), font, pitch)[1]


def render_glyph(font, key):
    """key = ((char, x), ...) -> 22 bytes (11 rows x 16 px, MSB left)."""
    rows = [0] * 11
    for ch, x in key:
        top, art, _ = font.glyphs[ch]
        for r, line in enumerate(art):
            for c, p in enumerate(line):
                if p == '#':
                    assert x + c < 16
                    rows[top + r] |= 0x8000 >> (x + c)
    return b''.join(struct.pack('>H', v) for v in rows)


class CodeAlloc:
    """Allocates 2-byte codes for generated cell glyphs."""
    LEAD0, TRAIL0, PER = 0x88, 0x40, 192

    def __init__(self):
        self.codes = {}

    def code(self, key):
        c = self.codes.get(key)
        if c is None:
            i = len(self.codes)
            lead = self.LEAD0 + i // self.PER
            assert lead <= 0xFF, 'out of glyph codes'
            c = (lead << 8) | (self.TRAIL0 + i % self.PER)
            self.codes[key] = c
        return c

    def table(self, font):
        out = bytearray()
        for key, c in self.codes.items():   # insertion order = index order
            out += struct.pack('<H', c) + render_glyph(font, key)
        return bytes(out)


def encode_items(items, alloc):
    out = bytearray()
    for it in items:
        if it[0] == 'g':
            out += struct.pack('>H', alloc.code(it[1]))
        elif it[0] == 'w':
            out += it[1].encode('cp932')
        elif it[0] == 'c':
            out += it[1].encode('ascii')
        elif it[0] == 'n':
            out += b'%n'
    return bytes(out)


def wrap(text, font, max_cells, pitch=CELL):
    """Split text (no explicit breaks inside paragraphs) into lines of <= max_cells cells, balanced.
    Explicit %n / newline breaks are kept. Returns list of line strings."""
    lines = []
    for para in re.split(r'%n|\n', text):
        words = para.split(' ')
        # greedy count of lines needed
        cur, need = '', []
        for w in words:
            cand = (cur + ' ' + w) if cur else w
            if line_cells(cand, font, pitch) <= max_cells or not cur:
                cur = cand
            else:
                need.append(cur)
                cur = w
        need.append(cur)
        n = len(need)
        if n <= 1:
            lines += need
            continue
        lines += balance(words, n, font, max_cells, pitch) or need
    return lines


def balance(words, n, font, max_cells, pitch):
    """Best split of words into n lines: minimise the widest line (in px), all lines within max_cells."""
    import functools

    def width(i, j):
        s = ' '.join(words[i:j])
        items, nc = layout_line(tokens(s), font, pitch)
        return nc, px_width(s, font)

    @functools.lru_cache(None)
    def best(i, k):
        if k == 1:
            nc, w = width(i, len(words))
            return (w, (len(words),)) if nc <= max_cells else None
        res = None
        for j in range(i + 1, len(words) - k + 2):
            nc, w = width(i, j)
            if nc > max_cells:
                break
            r = best(j, k - 1)
            if r:
                cand = (max(w, r[0]), (j,) + r[1])
                if res is None or cand[0] < res[0]:
                    res = cand
        return res

    r = best(0, n)
    if not r:
        return None
    out, i = [], 0
    for j in r[1]:
        out.append(' '.join(words[i:j]))
        i = j
    return out


def px_width(s, font):
    w = 0
    for t in tokens(s):
        if t[0] == 't':
            w += font.adv(t[1])
        elif t[0] == 'w':
            w += CELL
    return w
