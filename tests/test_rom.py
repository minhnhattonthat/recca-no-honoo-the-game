import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ORIG = ROOT / 'rom' / 'Recca no Honoo - The Game (Japan).gba'
SHA1 = '35fe535e24ddde1428d359a95bf114b0968911e9'


def test_original_rom_hash():
    assert hashlib.sha1(ORIG.read_bytes()).hexdigest() == SHA1
