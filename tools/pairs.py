"""Reviewer input: python -X utf8 tools/pairs.py OUT.txt BATCH [BATCH..]  (every entry of those batches, story order)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import batches as B  # noqa: E402


def main():
    out, names = sys.argv[1], sys.argv[2:]
    lines = []
    for b in names:
        kind, path, data = B.entries(b)
        lines.append(f'### batch {b}')
        for e in data:
            jp = (e['name_jp'] + ' // ' + ' '.join(e['jp'])) if kind == 'prof' else e['jp'].replace('%n', ' / ')
            en = (e.get('name', '') + ' // ' + e.get('en', '')) if kind == 'prof' else e.get('en', '')
            lines.append(f">> {e['id']} | {jp}\n   {en}")
    Path(out).write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    print(out, len(lines))


if __name__ == '__main__':
    main()
