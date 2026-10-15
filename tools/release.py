"""Release gate + package: check (tests+lint) -> build -> smoke -> leftover Japanese -> short warp tour -> BPS
(re-applied and verified) -> README -> release/recca-no-honoo-the-game_en.zip (patch + README only).
python -X utf8 tools/release.py [--no-tour]. Never publishes anything."""
import hashlib
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = Path(r'H:\translation\batch\.claude\skills\translate-retro-game')
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tools'))
import textlib as T  # noqa: E402

VERSION = '1.0'
REL = ROOT / 'release'
PATCH = f'Recca_no_Honoo_The_Game_EN_v{VERSION}.bps'
PY = [sys.executable, '-X', 'utf8']


def run(cmd, what):
    print('==', what)
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode:
        sys.exit(f'release stopped: {what} failed ({r.returncode})')


def hashes(b):
    return {'crc32': '%08X' % zlib.crc32(b), 'md5': hashlib.md5(b).hexdigest(), 'sha1': hashlib.sha1(b).hexdigest()}


def main():
    run(PY + [str(ROOT / 'tools' / 'check.py')], 'tests + lint')
    run(PY + [str(ROOT / 'build.py'), 'build'], 'build')
    built = ROOT / 'build' / 'recca_en.gba'
    run(PY + [str(SKILL / 'scripts' / 'emu.py'), str(built), '--out', str(ROOT / 'work' / 'qa' / 'rel_smoke'),
              '--route', str(ROOT / 'tools' / 'routes' / 'boot.txt'), '--smoke'], 'smoke')
    run(PY + [str(SKILL / 'scripts' / 'jp_left.py'), str(built), '--sjis', '--slots', str(ROOT / 'build' / 'slots.txt'),
              '--dbcs'],
        'leftover Japanese (pointer-reached text)')
    if '--no-tour' not in sys.argv:
        for scene in ('story:1', 'mode:3', 'mode:4'):
            run(PY + [str(ROOT / 'tools' / 'debug' / 'warp.py'), scene, '--rom', str(built), '--frames', '2200',
                      '--out', str(ROOT / 'work' / 'qa' / ('rel_' + scene.replace(':', '_'))), '--mash', '120'],
                f'tour {scene}')
    REL.mkdir(exist_ok=True)
    patch = REL / PATCH
    run(PY + [str(SKILL / 'scripts' / 'bps.py'), 'make', str(T.ORIG), str(built), str(patch)], 'BPS make + verify')
    check = ROOT / 'work' / 'rel_applied.gba'
    run(PY + [str(SKILL / 'scripts' / 'bps.py'), 'apply', str(T.ORIG), str(patch), str(check)], 'BPS apply')
    if check.read_bytes() != built.read_bytes():
        sys.exit('release stopped: patched ROM differs from the build')
    o, p = hashes(T.ORIG.read_bytes()), hashes(built.read_bytes())
    readme = (ROOT / 'docs' / 'README_release.txt').read_text(encoding='utf-8').format(
        version=VERSION, patch=PATCH, o_crc=o['crc32'], o_md5=o['md5'], o_sha1=o['sha1'], p_crc=p['crc32'],
        p_md5=p['md5'], p_sha1=p['sha1'], o_size=T.ORIG.stat().st_size, p_size=built.stat().st_size)
    (REL / 'README.txt').write_text(readme, encoding='utf-8', newline='\r\n')
    z = REL / 'recca-no-honoo-the-game_en.zip'
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(patch, PATCH)
        zf.write(REL / 'README.txt', 'README.txt')
    ph = hashes(patch.read_bytes())
    print(f'release: {z}\n  patch {PATCH} crc32 {ph["crc32"]} sha1 {ph["sha1"]}\n  patched ROM crc32 {p["crc32"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
