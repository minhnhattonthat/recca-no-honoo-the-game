"""Graphics text: redraw tile-drawn Japanese with English (docs/re/graphics.md). Called by build.py: patch(out).
python -X utf8 tools/gfx.py preview   -> work/gfx_*.png previews of every redraw."""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import textlib as T  # noqa: E402

# Intro crawl: 16 ASP0 sprite resources (128x16, 4bpp, 1D 32x16 sprites), table 0x0846829C[1..16].
# Resource: 'ASP0' + 8 header bytes (+ 32-byte palette when byte 8 has bit 0x10) + 1024 bytes of tiles.
INTRO_TABLE = 0x46829C
INTRO = [
    "Koran Mori seized",
    "Tendo Jigoku, the most",
    "fearsome madogu of",
    "the Hokage ninja clan.",
    "To merge with Princess",
    "Yanagi Sakoshita and",
    "her healing power, and",
    "become complete,",
    "he carried her away.",
    "",
    "To rescue Yanagi and",
    "crush Mori's ambitions,",
    "Recca and his friends",
    "had to reach SODOM,",
    "the fortress city,",
    "without a moment to lose...",
]
FILL, OUTLINE = 4, 2


def text_bitmap(text, w, h, fill=FILL, outline=OUTLINE, font=None, top=3):
    """Centred text with a 1-px outline -> h rows of w palette indices."""
    font = font or T.Font()
    rows, ink = T.strip(text, font) if text else ([0] * 11, 0)
    x0 = max(0, (w - ink) // 2)
    px = [[0] * w for _ in range(h)]
    for r, v in enumerate(rows):
        for x in range(ink):
            if v >> x & 1:
                X, Y = x0 + x, top + r
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if 0 <= X + dx < w and 0 <= Y + dy < h and px[Y + dy][X + dx] == 0:
                            px[Y + dy][X + dx] = outline
    for r, v in enumerate(rows):
        for x in range(ink):
            if v >> x & 1:
                px[top + r][x0 + x] = fill
    assert ink <= w, (text, ink)
    return px


def sprite_tiles(px, sw=32, sh=16):
    """Pixel rows -> 4bpp tiles in 1D order, sprite by sprite (sprites sw x sh, left to right)."""
    w = len(px[0])
    out = bytearray()
    for sx in range(0, w, sw):
        for ty in range(sh // 8):
            for tx in range(sw // 8):
                for r in range(8):
                    for c in range(0, 8, 2):
                        a = px[ty * 8 + r][sx + tx * 8 + c]
                        b = px[ty * 8 + r][sx + tx * 8 + c + 1]
                        out.append(a | b << 4)
    return bytes(out)


def intro(out):
    font = T.Font()
    for k, line in enumerate(INTRO):
        p = T.u32(out, INTRO_TABLE + 4 * (k + 1)) - T.ROMBASE
        assert out[p:p + 4] == b'ASP0'
        data = p + 12 + (32 if out[p + 8] & 0x10 else 0)
        tiles = sprite_tiles(text_bitmap(line, 128, 16, font=font))
        assert len(tiles) == 1024
        out[data:data + 1024] = tiles
        yield data, data + 1024


def patch(out):
    """Apply every graphics redraw to the bytearray `out`; returns written (lo, hi) ranges."""
    return list(intro(out))


def preview():
    from PIL import Image
    pal = [(0, 0, 0), (255, 255, 255), (112, 32, 32), (240, 232, 232), (255, 248, 248)] + [(128, 128, 128)] * 11
    font = T.Font()
    im = Image.new('RGB', (128, 16 * len(INTRO)))
    for k, line in enumerate(INTRO):
        for y, row in enumerate(text_bitmap(line, 128, 16, font=font)):
            for x, c in enumerate(row):
                im.putpixel((x, k * 16 + y), pal[c])
    im.resize((512, 64 * len(INTRO)), Image.NEAREST).save(T.ROOT / 'work' / 'gfx_intro.png')


if __name__ == '__main__':
    preview()
