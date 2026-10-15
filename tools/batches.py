"""Translation batches.
  python -X utf8 tools/batches.py split            -> work/tl/<batch>.tsv + work/tl/terms_<batch>.txt (all batches)
  python -X utf8 tools/batches.py check <batch>    -> validates work/tl/<batch>.out.tsv; prints OK or the bad ids
  python -X utf8 tools/batches.py merge <batch>    -> check, then write the English into script/*.json
  python -X utf8 tools/batches.py list             -> batch names with entry counts and status
Batches: ac01..ac22 (one story file each), sys1..sys3 (menus and system text), prof (database profiles)."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import textlib as T  # noqa: E402
import acdis  # noqa: E402

ROOT = T.ROOT
TL = ROOT / 'work' / 'tl'
DLG_CELLS, DLG_LINES, PROF_CELLS = 13, 3, 10
FACES = {0: 'Recca', 1: 'Domon', 2: 'Fuko', 3: 'Mikagami', 4: 'Koganei', 5: 'Kurei', 6: 'Renge?', 7: 'Hiruko?',
         8: 'Kadotsu', 9: 'Koran Mori', 10: 'Kashamaru', 11: 'Mokuren', 13: '?', 14: 'Yanagi', 15: 'Kagero',
         16: 'Aoi', 17: 'Raiha?', 18: 'Koku (old man)', 19: 'Kukai?', 20: 'Saicho?', 21: 'Kirito?', 23: '?',
         24: '?'}
JP_RE = re.compile(r'[぀-ヿ一-鿿]')
FONT = None


def font():
    global FONT
    if FONT is None:
        FONT = T.Font()
    return FONT


def batches():
    out = {}
    for p in sorted((ROOT / 'script' / 'ac').glob('*.json')):
        out['ac' + p.name[:2]] = ('ac', p, None)
    n = len(json.loads((ROOT / 'script' / 'sys.json').read_text(encoding='utf-8')))
    per = (n + 2) // 3
    for k in range(3):
        out['sys%d' % (k + 1)] = ('sys', ROOT / 'script' / 'sys.json', (k * per, min(n, (k + 1) * per)))
    out['prof'] = ('prof', ROOT / 'script' / 'profiles.json', None)
    return out


def entries(batch):
    kind, path, rng = batches()[batch]
    data = json.loads(path.read_text(encoding='utf-8'))
    if rng:
        data = data[rng[0]:rng[1]]
    return kind, path, data


def limit(kind, e):
    if kind == 'ac':
        return DLG_CELLS, DLG_LINES
    if kind == 'prof':
        return PROF_CELLS, 99
    return e.get('max', max(e['cells'])), e.get('lines', len(e['cells']))


def split():
    TL.mkdir(parents=True, exist_ok=True)
    gl = glossary()
    d = T.rom()
    for b, (kind, path, rng) in batches().items():
        kind, path, data = entries(b)
        rows, text = [], ''
        sp = acdis.speakers(d, int(b[2:])) if kind == 'ac' else {}
        for k, e in enumerate(data):
            if kind == 'prof':
                jp = e['name_jp'] + ' // ' + ' '.join(e['jp'])
                rows.append(f"{e['id']}\t-\tprofile\tname line + paragraphs (blank line = '\\n\\n'), {PROF_CELLS} cells/line\t{jp}")
                text += jp
                continue
            mc, ml = limit(kind, e)
            if kind == 'ac':
                f = sp.get(int(e['id'].split('_')[1]))
                speaker = 'portrait:' + FACES.get(f, '?') if f is not None else 'no-portrait'
                form = 'dlg'
            else:
                speaker, form = e.get('ctx', '-'), 'menu'
            jp = e['jp'].replace('%n', ' / ').replace('\n', ' / ')
            rows.append(f"{e['id']}\t{speaker}\t{form}\t{ml} line(s) x {mc} cells ({mc * 14}px)\t{jp}")
            text += e['jp']
        (TL / f'{b}.tsv').write_text('\n'.join(rows) + '\n', encoding='utf-8', newline='\n')
        terms = [r for r in gl if any(j in text for j in r[0])]
        (TL / f'terms_{b}.txt').write_text(''.join(f"{' / '.join(r[0])} = {' / '.join(r[1])}"
                                                    f"{'  (avoid: ' + r[2] + ')' if r[2] else ''}\n" for r in terms),
                                           encoding='utf-8', newline='\n')
    print('split', len(batches()), 'batches into', TL)


def glossary():
    rows = []
    for line in (ROOT / 'glossary.md').read_text(encoding='utf-8').splitlines():
        if line.startswith('| ') and not line.startswith('| JP') and not line.startswith('|---'):
            c = [x.strip() for x in line.strip('|').split('|')]
            if len(c) >= 2:
                rows.append(([j.strip() for j in c[0].split('/')], [x.strip() for x in c[1].split('/')],
                             c[3] if len(c) > 3 else ''))
    return rows


def read_out(batch):
    p = TL / f'{batch}.out.tsv'
    if not p.exists():
        return None
    out = {}
    for line in p.read_text(encoding='utf-8-sig').splitlines():
        if not line.strip():
            continue
        if '\t' not in line:
            out.setdefault('__bad__', []).append(line[:40])
            continue
        i, en = line.split('\t', 1)
        out[i.strip()] = en.replace('\\n', '\n').strip()
    return out


def ctrl(s):
    return sorted(c for c in T.CTRL_RE.findall(s) if c != '%n')


def check_entry(kind, e, en, gl):
    errs, warns = [], []
    if not en:
        return ['empty'], warns
    if JP_RE.search(en):
        errs.append('Japanese left in English')
    if '\t' in en or '\\u' in en:
        errs.append('tab or \\u escape')
    fnt = font()
    for t in T.tokens(en):
        if t[0] == 't' and not fnt.has(t[1]):
            errs.append(f'character {t[1]!r} not in the font')
        if t[0] == 'w':
            try:
                t[1].encode('cp932')
            except UnicodeEncodeError:
                errs.append(f'unencodable {t[1]!r}')
    jp = e['jp'] if kind != 'prof' else ''
    if kind != 'prof' and ctrl(jp) != ctrl(en):
        errs.append(f'control codes {ctrl(jp)} != {ctrl(en)}')
    if re.search(r'%[A-Za-z]\d?(st|nd|rd|th)\b', en):
        errs.append('ordinal suffix after a variable')
    if errs:
        return errs, warns
    mc, ml = limit(kind, e)
    try:
        if e.get('layout') == 'digits':
            tail = e['jp'][-3:]
            if not en.endswith(tail):
                errs.append(f'must end with {tail} exactly')
            elif T.line_cells(en[:-3].rstrip(), fnt) > 6:
                errs.append('label before the digits wider than 6 cells')
        elif kind == 'prof':
            name, _, body = en.partition('\n\n')
            if T.line_cells(name, fnt) > mc:
                errs.append(f'name line wider than {mc} cells')
            n = 1
            for para in body.split('\n\n'):
                n += len(T.wrap(para.replace('\n', ' '), fnt, mc)) + 1
            if n > 40:
                errs.append(f'profile too long ({n} lines, max 40)')
        else:
            lines = T.wrap(en, fnt, mc)
            wide = [T.line_cells(x, fnt) for x in lines]
            if len(lines) > ml or max(wide) > mc:
                errs.append(f'does not fit: {len(lines)} lines (max {ml}), widest {max(wide)} cells (max {mc}) -> '
                            + ' | '.join(lines))
            elif len(lines) > 1 and len(lines[-1]) < 5 and len(en) > 30:
                warns.append(f'stub last line {lines[-1]!r}')
    except Exception as ex:  # noqa: BLE001
        errs.append(f'fit error {ex}')
    src = e['jp'] if kind != 'prof' else e['name_jp'] + ''.join(e['jp'])
    for jps, ens, avoid in gl:
        for a in [x.strip() for x in avoid.split(',') if x.strip()]:
            if re.search(r'\b' + re.escape(a) + r'\b', en):
                errs.append(f'avoided spelling {a!r}')
        if any(len(j) >= 2 and j in src for j in jps) and not any(x.lower() in en.lower() for x in ens):
            warns.append(f'glossary: {"/".join(jps)} -> {" / ".join(ens)} not found')
    return errs, warns


def check(batch, quiet=False):
    kind, path, data = entries(batch)
    out = read_out(batch)
    if out is None:
        print(f'{batch}: no output file work/tl/{batch}.out.tsv')
        return False
    gl = glossary()
    ids = [e['id'] for e in data]
    bad = 0
    for x in out.get('__bad__', []):
        print('  line without a tab:', x)
        bad += 1
    missing = [i for i in ids if i not in out]
    extra = [i for i in out if i not in ids and i != '__bad__']
    if missing:
        print('  missing ids:', ', '.join(missing[:20]), '...' if len(missing) > 20 else '')
        bad += len(missing)
    if extra:
        print('  unknown ids:', ', '.join(extra[:20]))
        bad += len(extra)
    nwarn = 0
    for e in data:
        if e['id'] not in out:
            continue
        errs, warns = check_entry(kind, e, out[e['id']], gl)
        for x in errs:
            print(f"  {e['id']}: {x}")
        bad += len(errs)
        if not quiet:
            for w in warns:
                print(f"  warn {e['id']}: {w}")
        nwarn += len(warns)
    print(f'{batch}: ' + ('OK' if not bad else f'{bad} error(s)') + (f', {nwarn} warning(s)' if nwarn else ''))
    return bad == 0


def merge(batch):
    if not check(batch, quiet=True):
        return False
    kind, path, _ = entries(batch)
    out = read_out(batch)
    data = json.loads(path.read_text(encoding='utf-8'))
    for e in data:
        if e['id'] in out:
            en = out[e['id']]
            if kind == 'prof':
                name, _, body = en.partition('\n\n')
                e['name'], e['en'] = name.strip(), body.strip()
            else:
                e['en'] = en
            e['status'] = 'tl'
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
    print('merged', batch)
    return True


def fix(path):
    """Apply a review-fix TSV (id<TAB>English, any batch; prof = name\\n\\nbody) after checking every line."""
    fixes = {}
    for line in Path(path).read_text(encoding='utf-8-sig').splitlines():
        if line.strip():
            i, en = line.split('\t', 1)
            fixes[i.strip()] = en.replace('\\n', '\n').strip()
    gl, bad, done = glossary(), 0, set()
    for b in batches():
        kind, p, _ = entries(b)
        data = json.loads(p.read_text(encoding='utf-8'))
        changed = False
        for e in data:
            if e['id'] not in fixes or e['id'] in done:
                continue
            errs, _ = check_entry(kind, e, fixes[e['id']], gl)
            if errs:
                print(f"  {e['id']}: {errs}")
                bad += 1
                continue
            if kind == 'prof':
                name, _, body = fixes[e['id']].partition('\n\n')
                e['name'], e['en'] = name.strip(), body.strip()
            else:
                e['en'] = fixes[e['id']]
            e['status'] = 'reviewed'
            done.add(e['id'])
            changed = True
        if changed:
            p.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
    missing = set(fixes) - done
    print(f'fixed {len(done)}, rejected {bad}, unknown {sorted(missing - set())[:10] if missing else 0}')
    return bad == 0


def main():
    a = sys.argv[1:]
    if a and a[0] == 'fix':
        return 0 if fix(a[1]) else 1
    if not a or a[0] == 'list':
        for b in batches():
            kind, path, data = entries(b)
            done = sum(1 for e in data if e.get('en'))
            print(f'{b}: {len(data)} entries, {done} translated')
        return 0
    if a[0] == 'split':
        split()
        return 0
    if a[0] == 'check':
        return 0 if check(a[1]) else 1
    if a[0] == 'merge':
        return 0 if merge(a[1]) else 1
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main())
