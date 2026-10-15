"""Identity build + roundtrip: unpack the original text and repack it with no edits -> byte-identical ROM."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import textlib as T  # noqa: E402


def test_ac_identity():
    d = T.rom()
    out = bytearray(d)
    for i in range(T.AC_COUNT):
        f = T.ac_parse(d, i)
        blob = T.ac_build(f['head'], [T.encode_jp(T.decode(s)) for s in f['strings']])
        out[f['base']:f['base'] + len(blob)] = blob
    assert bytes(out) == d


def test_sys_roundtrip_and_coverage():
    d = T.rom()
    strs, refs = T.sys_strings(d)
    for o, s in strs:
        assert T.encode_jp(T.decode(s)) == s, hex(o)
    assert len(strs) == 723          # every Japanese string in the block (minus 2 data tables), pointer at its start
    # coverage: no Japanese string in the block lacks a pointer (sys_strings drops those silently)
    found = {o for o, s in strs}
    o = T.SYS_LO
    while o < T.SYS_HI:
        if d[o] == 0 or any(a <= o < b for a, b in T.SYS_DATA):
            o += 1
            continue
        e = d.index(b'\0', o)
        if any(0x81 <= c <= 0x9F for c in d[o:e]) and o not in found:
            raise AssertionError('unreferenced Japanese at %X' % o)
        o = e


def test_script_json_matches_rom():
    d = T.rom()
    for i in range(T.AC_COUNT):
        f = T.ac_parse(d, i)
        if not f['strings']:
            continue
        data = json.loads((ROOT / 'script' / 'ac' / ('%02d_%s.json' % (i, T.AC_NAMES[i]))).read_text(encoding='utf-8'))
        assert [T.encode_jp(e['jp']) for e in data] == f['strings']
    for e in json.loads((ROOT / 'script' / 'sys.json').read_text(encoding='utf-8')):
        o = int(e['id'][4:], 16)
        assert T.encode_jp(e['jp']) == T.cstr(d, o)
