"""One-command check: tests + text lint. The pre-commit hook runs this; exit code gates the commit."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    r = subprocess.run([sys.executable, '-X', 'utf8', '-m', 'pytest', '-q', '-p', 'no:cacheprovider', str(ROOT / 'tests')],
                       cwd=ROOT)
    if r.returncode:
        return r.returncode
    lint = ROOT / 'tools' / 'lint.py'
    if lint.exists():
        r = subprocess.run([sys.executable, '-X', 'utf8', str(lint)], cwd=ROOT)
    return r.returncode


if __name__ == '__main__':
    sys.exit(main())
