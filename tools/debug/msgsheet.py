"""Contact sheet of the dialogue box from msgshot.lua shots: python -X utf8 tools/debug/msgsheet.py DIR [OUT.png]"""
import glob
import sys

from PIL import Image

d = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else d + '/msgs.png'
fs = sorted(glob.glob(d + '/msg_*.png'))
W = Image.new('RGB', (480 * 2, max(1, (len(fs) + 1) // 2) * 112))
for i, f in enumerate(fs):
    W.paste(Image.open(f).crop((0, 104, 240, 160)).resize((480, 112), Image.NEAREST), ((i % 2) * 480, (i // 2) * 112))
W.save(out)
print(out, len(fs))
