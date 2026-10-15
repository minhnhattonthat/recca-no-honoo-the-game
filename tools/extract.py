"""Dump the original ROM's text to script/*.json. Never overwrites existing files (use --force to regenerate the
`jp` fields while keeping every `en`/`status`/`notes` already written)."""
import json
import struct
import sys

sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
import textlib as T  # noqa: E402

OUT = T.ROOT / 'script'
PROF_TABLE = 0x469A54        # (u32 ptr into the line-pointer array, u32 line count) per character
PROF_N = 25
PROF_LINES = (0x469380, 0x469CC0)


def write(path, data, force):
    if path.exists():
        if not force:
            print('exists, skipped:', path.name)
            return
        old = {e['id']: e for e in json.loads(path.read_text(encoding='utf-8'))}
        for e in data:
            o = old.get(e['id'])
            if o:
                for k in ('en', 'status', 'notes'):
                    if k in o:
                        e[k] = o[k]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
    print('wrote', path.name, len(data))


def profiles(d):
    out = []
    for i in range(PROF_N):
        p, n = struct.unpack_from('<II', d, PROF_TABLE + 8 * i)
        first = p - T.ROMBASE
        slots = [first + 4 * k for k in range(n)]
        lines = [T.decode(T.cstr(d, T.u32(d, s) - T.ROMBASE)).rstrip('　') for s in slots]
        out.append({'id': 'prof_%02d' % i, 'table': PROF_TABLE + 8 * i, 'name_jp': lines[0], 'jp': lines[1:],
                    'name': '', 'en': '', 'status': ''})
    return out


def main(force=False):
    d = T.rom()
    OUT.mkdir(exist_ok=True)
    (OUT / 'ac').mkdir(exist_ok=True)
    for i in range(T.AC_COUNT):
        f = T.ac_parse(d, i)
        if not f['strings']:
            continue
        data = [{'id': 'ac%02d_%03d' % (i, k), 'jp': T.decode(s), 'en': '', 'status': ''}
                for k, s in enumerate(f['strings'])]
        write(OUT / 'ac' / ('%02d_%s.json' % (i, T.AC_NAMES[i])), data, force)
    strs, refs = T.sys_strings(d)
    data = []
    for o, s in strs:
        slots = [x for x in refs[o] if not PROF_LINES[0] <= x < PROF_LINES[1]]
        if not slots:
            continue
        jp = T.decode(s)
        if not jp.strip('　'):   # all-blank clear strings (box/line wipes): data, kept as is
            continue
        data.append({'id': 'sys_%05X' % o, 'slots': ['%06X' % x for x in slots], 'jp': jp,
                     'cells': cells_jp(s), 'en': '', 'status': ''})
    write(OUT / 'sys.json', data, force)
    write(OUT / 'profiles.json', profiles(d), force)


def cells_jp(b):
    """Cell count per line of an original string (2-byte codes; `%n` / `\\n` split lines)."""
    lines, n, i = [], 0, 0
    while i < len(b):
        c = b[i]
        if c == 0x25:
            if b[i + 1:i + 2] == b'n':
                lines.append(n)
                n = 0
            i += 3 if chr(b[i + 1]) in 'TWwP' else 2
        elif c == 0x0A:
            lines.append(n)
            n = 0
            i += 1
        elif c >= 0x80:
            n += 1
            i += 2
        else:
            i += 1
    lines.append(n)
    return lines


if __name__ == '__main__':
    main('--force' in sys.argv)
