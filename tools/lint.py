"""Text lint over every script entry: translated, fits its box, control codes match, font/encodable, glossary.
Prints errors + a one-line summary; exit 1 on any error. Warnings are counted, not listed (use --warn to list)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import batches as B  # noqa: E402


def main():
    gl = B.glossary()
    errs = warns = n = 0
    show = '--warn' in sys.argv
    for b in B.batches():
        kind, path, data = B.entries(b)
        for e in data:
            n += 1
            en = (e.get('name', '') + '\n\n' + e.get('en', '')) if kind == 'prof' else e.get('en', '')
            if not e.get('en'):
                print(f"{e['id']}: untranslated")
                errs += 1
                continue
            er, wa = B.check_entry(kind, e, en, gl)
            for x in er:
                print(f"{e['id']}: {x}")
            if show:
                for x in wa:
                    print(f"warn {e['id']}: {x}")
            errs += len(er)
            warns += len(wa)
    print(f'lint: {n} entries, {errs} error(s), {warns} warning(s)')
    return 1 if errs else 0


if __name__ == '__main__':
    sys.exit(main())
