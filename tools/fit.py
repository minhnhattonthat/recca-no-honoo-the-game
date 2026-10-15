"""Dry-run fitter: python -X utf8 tools/fit.py "English text" [--cells 13] [--lines 3]
Prints the wrapped lines with their width in cells (1 cell = 14 px) the way the build will set them."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import textlib as T  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument('text')
    p.add_argument('--cells', type=int, default=13)
    p.add_argument('--lines', type=int, default=3)
    a = p.parse_args()
    f = T.Font()
    lines = T.wrap(a.text, f, a.cells)
    for ln in lines:
        print(f'{T.line_cells(ln, f):2d}/{a.cells} cells  {T.px_width(ln, f):3d}px  {ln}')
    ok = len(lines) <= a.lines and all(T.line_cells(ln, f) <= a.cells for ln in lines)
    print('FITS' if ok else f'DOES NOT FIT ({len(lines)} lines, max {a.lines})')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
