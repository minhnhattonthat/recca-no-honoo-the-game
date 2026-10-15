"""The English build: builds its own ROM, fits every line, touches only allowed ranges, valid pointers."""
import struct
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tools'))
import build  # noqa: E402
import textlib as T  # noqa: E402

SKILL = Path(r'H:\translation\batch\.claude\skills\translate-retro-game')


@pytest.fixture(scope='module')
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp('b') / 'recca_en.gba'
    b = build.Builder()
    assert b.run(out) == 0, b.errors[:5]
    return b, out


def test_no_fit_errors_and_all_english(built):
    b, _ = built
    assert not b.errors
    assert b.stats['jp'] == 0
    assert len(b.alloc.codes) < 120 * 192


def test_romdiff_allowed_ranges(built):
    b, out = built
    rng = [f'{lo:X}-{hi - 1:X}' for lo, hi in b.ranges]
    r = subprocess.run([sys.executable, '-X', 'utf8', str(SKILL / 'scripts' / 'romdiff.py'), str(T.ORIG), str(out)] + rng,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-2000:]


def test_ac_files_parse_and_strings_end(built):
    _, out = built
    d = out.read_bytes()
    for i in range(T.AC_COUNT):
        f = T.ac_parse(d, i)               # asserts the %ASS header and contiguous string layout
        orig = T.ac_parse(T.rom(), i)
        assert f['head'][12:] == orig['head'][12:] and len(f['strings']) == len(orig['strings'])


def test_hook_and_font_table(built):
    _, out = built
    d = out.read_bytes()
    assert d[0xC6CC:0xC6CE] == bytes.fromhex('1847')
    hook = (struct.unpack_from('<I', d, 0xC6D4)[0] & ~1) - T.ROMBASE
    assert hook >= T.FREE_START and len(d) <= 0x1000000
