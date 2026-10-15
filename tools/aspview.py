"""Render ASP0 sprite resources (16 px tall, 1D 32x16 sprites, 4bpp) in a ROM range to a labelled sheet.
python -X utf8 tools/aspview.py ROM LO HI OUT.png"""
import re
import sys

from PIL import Image, ImageDraw

d = open(sys.argv[1], 'rb').read()
lo, hi = int(sys.argv[2], 16), int(sys.argv[3], 16)
items = []
for m in re.finditer(rb'ASP0', d[lo:hi]):
    a = lo + m.start()
    size = d[a + 10] | d[a + 11] << 8
    flag = d[a + 8]
    if size == 0 or size % 256:
        continue
    w = size * 2 // 16
    data = a + 12 + (32 if flag & 0x10 else 0)
    items.append((a, w, data))
pal = [(0, 0, 40)] + [(40 + i * 14, 40 + i * 14, 40 + i * 14) for i in range(1, 16)]
W = Image.new('RGB', (2 * 260, 18 * ((len(items) + 1) // 2)))
dr = ImageDraw.Draw(W)
for k, (a, w, data) in enumerate(items):
    ox, oy = (k % 2) * 260, (k // 2) * 18
    dr.text((ox, oy + 3), '%X' % a, fill=(255, 200, 0))
    for t in range(w // 8 * 2):
        spr, tt = t // 8, t % 8
        tx, ty = spr * 4 + tt % 4, tt // 4
        for r in range(8):
            for c in range(8):
                b = d[data + t * 32 + r * 4 + c // 2]
                v = (b >> 4) if c & 1 else b & 15
                if ox + 50 + tx * 8 + c < W.width:
                    W.putpixel((ox + 50 + tx * 8 + c, oy + ty * 8 + r), pal[v])
W.save(sys.argv[4])
print(len(items), 'resources')
