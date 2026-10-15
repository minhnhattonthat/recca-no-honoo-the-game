"""Context labels + measured/assumed widget limits for script/sys.json (by string address). Re-run after extract.
python -X utf8 tools/sysctx.py   (writes `ctx` and, where set here, `max` into script/sys.json)"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# (lo, hi, context, max cells or None = JP cell count)
CTX = [
    (0x4B460, 0x4B560, 'help bar at the bottom of a menu (15 cells)', None),
    (0x4B560, 0x4B57C, 'link-cable error message', None),
    (0x4BB04, 0x4BB58, 'help bar, story mode start', None),
    (0x4BB58, 0x4BB7C, 'story mode: chapter to start from (list item)', 9),
    (0x4BB7C, 0x4BBFC, 'story save-info panel (label : value)', None),
    (0x4BBFC, 0x4BC44, 'story save-info panel: character full name', 9),
    (0x4BC44, 0x4BC8C, 'story save-info panel: episode number', None),
    (0x4BC8C, 0x4BDF8, 'story save-info panel: episode title', 9),
    (0x4BDF8, 0x4BE5C, 'story save-info panel (label : value)', None),
    (0x4BE5C, 0x4BF3C, 'battle-mode help bar / prompt', None),
    (0x4BF3C, 0x4C00C, 'link-cable battle setup message (Kagero speaking)', None),
    (0x4C00C, 0x4C254, 'Koku rates your training-mode performance (3-line box)', 13),
    (0x4C254, 0x4C2F4, 'database help bar', None),
    (0x4E434, 0x4E590, 'option menu help bar / dialog', None),
    (0x4E590, 0x4F24C, 'sound test: voice clip name (Name: description)', 14),
    (0x4F24C, 0x4F600, 'sound test: sound effect name', 14),
    (0x4F600, 0x4F82C, 'sound test: music track name', 14),
    (0x4F89C, 0x4F8E4, 'save error message', None),
]


# copied to RAM as 19 bytes and digits patched at bytes 13 and 17: 6-cell label + JP '０／３' tail, fixed
DIGITS = {0x4BBB4, 0x4BBC8, 0x4BE04, 0x4BE18}


def main():
    p = ROOT / 'script' / 'sys.json'
    data = json.loads(p.read_text(encoding='utf-8'))
    for e in data:
        o = int(e['id'][4:], 16)
        for lo, hi, ctx, mx in CTX:
            if lo <= o < hi:
                e['ctx'] = ctx
                if mx:
                    e['max'] = mx
                break
        else:
            e['ctx'] = 'misc'
        if o in DIGITS:
            e['layout'] = 'digits'
            e['ctx'] += '; LABEL ONLY: keep the trailing ０／３ (or ０／１) exactly, the label before it max 6 cells'
    p.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
    print('ctx set on', len(data))


if __name__ == '__main__':
    sys.exit(main())
