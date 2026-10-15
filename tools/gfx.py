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


def text_bitmap(text, w, h, fill=FILL, outline=OUTLINE, font=None, top=3, snap=1):
    """Centred text with a 1-px outline -> h rows of w palette indices. snap: align the start x (fewer tiles)."""
    font = font or T.Font()
    rows, ink = T.strip(text, font) if text else ([0] * 11, 0)
    x0 = max(1, (w - ink) // 2 // snap * snap + (1 if snap > 1 else 0))
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


# Staff roll: ABG0 pages (u8 width/2, u16 height, u8 flags (0x08 = 32-byte palette follows), u32 tile bytes, tiles,
# then a 30-wide map of u16 tile indices). Page pointers at 0x08468E68.. (8 pages, page 0 again at 0x468E88).
# Lines: (top y, text, heading?) placed where the Japanese lines were; heading = underlined.
CREDITS_TABLE = 0x468E68
CREDITS = [
    [(161, 'Flame of Recca THE GAME', 0), (177, 'Staff', 0), (225, '- Production -', 0)],
    [(1, 'Producer', 1), (17, 'Shun Kimoto', 0), (49, 'Director', 1), (65, 'Masahiro Hinami', 0),
     (97, 'Technical Advisor', 1), (113, 'Satoshi Mikami', 0), (145, 'Sound', 1), (161, 'Akira Nakata', 0),
     (177, 'Junichiro Kaneda', 0), (193, 'Toshiyuki Miyamoto', 0), (225, 'Voice Director', 1),
     (241, 'Sumiko Shindo (KME)', 0)],
    [(33, 'Recording Studio', 1), (49, 'Little Bach Aoyama', 0), (65, 'Engineer: Sho Hashimoto', 0),
     (129, '- Development -', 0), (161, 'Producer', 1), (177, 'Hidetaka Takayama', 0), (209, 'Director', 1),
     (225, 'Hiroyuki Nasu', 0)],
    [(1, 'Assist', 1), (17, 'Kozo Miyagawa', 0), (33, 'Tomoharu Mori', 0), (81, '- Program -', 0),
     (113, 'System', 1), (129, 'Kenji Abe', 0), (161, 'Battle', 1), (177, 'Masami Miyazo', 0), (209, 'Sub', 1),
     (225, 'Takashi Nishimura', 0)],
    [(17, '- Graphics -', 0), (49, 'Adventure & Demo', 1), (65, 'Arata Yasuda', 0),
     (97, 'Characters & Effects', 1), (113, 'Keiichiro Morita', 0), (129, 'Daisuke Furusawa', 0),
     (145, 'Nobuyuki Eguchi', 0), (161, 'Daiki Fujiwara', 0), (193, 'System & Boss Characters', 1),
     (209, 'Katsuo Saito', 0), (241, 'Stages', 1)],
    [(1, 'Katsuo Saito', 0), (17, 'Emiko Shindo', 0), (33, 'Junko Sawada', 0), (81, '- Voice Cast -', 0),
     (113, 'Katsuhiro Ota', 0), (129, 'Misato Fukuen', 0), (145, 'Akira Negishi', 0), (161, 'Masakazu Ohara', 0),
     (177, 'Hiroyuki Yoshino', 0), (193, 'Takumi Tanimoto', 0)],
    [(25, '- Original Work -', 0), (41, 'Nobuyuki Anzai', 0), (129, '- Special Thanks -', 0),
     (145, 'Shogakukan', 1), (161, 'Shinichiro Tsuzuki', 0), (177, 'Atsushi Nomura', 0),
     (193, 'Tsutomu Nakakado', 0), (209, 'Shogakukan Production', 1), (225, 'Hirohisa Mino', 0),
     (241, 'Sho Masuda', 0)],
    [(81, '(C) Nobuyuki Anzai / Shogakukan', 0), (97, '(C) 2001 KONAMI', 0)],
]


def credits_page(lines, w, h, font):
    px = [[0] * w for _ in range(h)]
    for y, text, head in lines:
        bm = text_bitmap(text, w, 14, fill=5, outline=4, font=font, top=1)
        for r in range(14):
            if 0 <= y + r < h:
                for x in range(w):
                    if bm[r][x]:
                        px[y + r][x] = bm[r][x]
        if head:
            xs = [x for x in range(w) if any(bm[r][x] for r in range(14))]
            for k, c in enumerate((4, 5, 4)):
                yy = y + 11 + k
                if yy < h:
                    for x in range(xs[0] - 1, xs[-1] + 2):
                        px[yy][x] = c
    return px


def tiles_map(px, hflip=False):
    """Pixel rows -> (tile bytes, u16 map) with tile 0 blank and duplicate tiles merged (hflip: also mirrored
    tiles, map bit 10 - only where the original data uses it)."""
    h, w = len(px), len(px[0])
    tiles, index, mp = [bytes(32)], {bytes(32): 0}, []
    for ty in range(h // 8):
        for tx in range(w // 8):
            t = bytes(px[ty * 8 + r][tx * 8 + c] | px[ty * 8 + r][tx * 8 + c + 1] << 4
                      for r in range(8) for c in range(0, 8, 2))
            if hflip and t not in index:
                m = bytes(px[ty * 8 + r][tx * 8 + 7 - c] | px[ty * 8 + r][tx * 8 + 6 - c] << 4
                          for r in range(8) for c in range(0, 8, 2))
                if m in index:
                    mp.append(index[m] | 0x400)
                    continue
            if t not in index:
                index[t] = len(tiles)
                tiles.append(t)
            mp.append(index[t])
    return b''.join(tiles), mp


def credits(out, append):
    font = T.Font()
    for k, lines in enumerate(CREDITS):
        p = T.u32(out, CREDITS_TABLE + 4 * k) - T.ROMBASE
        assert out[p:p + 4] == b'ABG0'
        w, h, fl, n = out[p + 4] * 2, T.u16(out, p + 5), out[p + 7], T.u32(out, p + 8)
        pal = out[p + 12:p + 44] if fl & 8 else b''
        rows = h // 16                         # map rows: 32 for h=512, 22 for h=352 (matches the ROM data)
        tiles, mp = tiles_map(credits_page(lines, w, rows * 8, font))
        # pages load into alternating VRAM slots 0x0040-0x1FFF / 0x2040-0x3FFF (art from 0x4000): 254 tiles each
        assert len(tiles) <= 254 * 32, f'credits page {k}: {len(tiles) // 32} tiles > 254'
        blob = bytes(out[p:p + 8]) + struct.pack('<I', len(tiles)) + pal + tiles + struct.pack(f'<{len(mp)}H', *mp)
        at = append(blob)
        struct.pack_into('<I', out, CREDITS_TABLE + 4 * k, at | T.ROMBASE)
        yield CREDITS_TABLE + 4 * k, CREDITS_TABLE + 4 * k + 4
        if k == 0:
            struct.pack_into('<I', out, CREDITS_TABLE + 0x20, at | T.ROMBASE)
            yield CREDITS_TABLE + 0x20, CREDITS_TABLE + 0x24


END_CARD_LIT = 0x34C98   # code literal -> ABG0 end card (logo + 完); 完 (rows 96-143) becomes "THE END"


def decode_abg(out, p, rows):
    fl, n = out[p + 7], T.u32(out, p + 8)
    t = p + 12 + (32 if fl & 8 else 0)
    m = t + n
    px = [[0] * 240 for _ in range(rows * 8)]
    for ty in range(rows):
        for tx in range(30):
            e = T.u16(out, m + 2 * (ty * 30 + tx))
            idx, hf, vf = e & 0x3FF, e >> 10 & 1, e >> 11 & 1
            for r in range(8):
                for c in range(8):
                    b = out[t + idx * 32 + r * 4 + c // 2]
                    px[ty * 8 + (7 - r if vf else r)][tx * 8 + (7 - c if hf else c)] = (b >> 4) if c & 1 else b & 15
    return px


def end_card(out, append):
    p = T.u32(out, END_CARD_LIT) - T.ROMBASE
    assert out[p:p + 4] == b'ABG0'
    h, fl, n = T.u16(out, p + 5), out[p + 7], T.u32(out, p + 8)
    rows = h // 16
    px = decode_abg(out, p, rows)
    for y in range(96, 144):
        px[y] = [0] * 240
    rows_bm, ink = T.strip('THE END', T.Font())
    x0 = (240 - ink * 2) // 2
    for r, v in enumerate(rows_bm):
        for x in range(ink):
            if v >> x & 1:
                for dy in range(2):
                    for dx in range(2):
                        px[104 + r * 2 + dy][x0 + x * 2 + dx] = 15
    tiles, mp = tiles_map(px, hflip=True)
    assert len(tiles) <= n, f'end card {len(tiles) // 32} tiles > original {n // 32}'
    pal = out[p + 12:p + 44] if fl & 8 else b''
    at = append(bytes(out[p:p + 8]) + struct.pack('<I', len(tiles)) + pal + tiles + struct.pack(f'<{len(mp)}H', *mp))
    struct.pack_into('<I', out, END_CARD_LIT, at | T.ROMBASE)
    yield END_CARD_LIT, END_CARD_LIT + 4


# ASP0 sprite labels (16 px tall, 1D 32x16 sprites): (resource offset, English, x or None = centred, top row,
# text box rows lo..hi to clear to the background colour, columns lo..hi)
DB_NAMES = ['Recca Hanabishi', 'Domon Ishijima', 'Fuko Kirisawa', 'Tokiya Mikagami', 'Kaoru Koganei', 'Kurei',
            'Renge', 'Hiruko', 'Kadotsu', 'Koran Mori', 'Kashamaru', 'Mokuren', 'Shiguma', 'Saicho',
            'Yanagi Sakoshita', 'Kagero', 'Aoi', 'Raiha', 'Koku', 'Kukai', 'Joker', 'Kirito', 'Mikoto',
            'Tsukishiro', 'Gashakura']
LABELS = ([(0x72ED64 + 0x30C * k, n, 4, 2, (2, 13), (2, 86)) for k, n in enumerate(DB_NAMES)] +
          [(0x733CC8, 'Profile', None, 1, (2, 9), (2, 60)), (0x733ED4, 'Move List', None, 1, (2, 9), (2, 60)),
           (0x7340E0, 'Results', None, 1, (2, 9), (2, 60)), (0x7342EC, 'Back', None, 1, (2, 9), (2, 60))])


def asp_pixels(out, a):
    size = T.u16(out, a + 10)
    data = a + 12 + (32 if out[a + 8] & 0x10 else 0)
    w = size * 2 // 16
    px = [[0] * w for _ in range(16)]
    for y in range(16):
        for x in range(w):
            t = (x // 32) * 8 + (y // 8) * 4 + (x % 32) // 8
            b = out[data + t * 32 + (y % 8) * 4 + (x % 8) // 2]
            px[y][x] = (b >> 4) if x & 1 else b & 15
    return px, data, size


def labels(out):
    font = T.Font()
    for a, text, x, top, (r0, r1), (c0, c1) in LABELS:
        assert out[a:a + 4] == b'ASP0', hex(a)
        px, data, size = asp_pixels(out, a)
        bg = max(set(px[(r0 + r1) // 2][c0:c1]), key=px[(r0 + r1) // 2][c0:c1].count)
        for y in range(r0, r1 + 1):
            for xx in range(c0, c1 + 1):
                px[y][xx] = bg
        rows, ink = T.strip(text, font)
        x0 = x if x is not None else c0 + (c1 - c0 + 1 - ink) // 2
        assert x0 + ink <= c1, (text, ink)
        for r, v in enumerate(rows):
            for dx in range(ink):
                if v >> dx & 1:
                    for oy in (-1, 0, 1):
                        for ox in (-1, 0, 1):
                            Y, X = top + r + oy, x0 + dx + ox
                            if r0 - 1 <= Y <= r1 + 1 and px[Y][X] != 15:
                                px[Y][X] = 1
        for r, v in enumerate(rows):
            for dx in range(ink):
                if v >> dx & 1:
                    px[top + r][x0 + dx] = 15
        blob = sprite_tiles(px)
        assert len(blob) == size
        out[data:data + size] = blob
        yield data, data + size


# Name plates (64x16 ASP0, 4x5 caps font, fill F, outline 1, bg D): respell the game's plates to the glossary.
PLATE_FONT = {
    'A': ['.##.', '#..#', '#..#', '####', '#..#'], 'C': ['.##.', '#..#', '#...', '#..#', '.##.'],
    'E': ['####', '#...', '###.', '#...', '####'], 'F': ['####', '#...', '###.', '#...', '#...'],
    'G': ['.##.', '#...', '#.##', '#..#', '.##.'], 'H': ['#..#', '#..#', '####', '#..#', '#..#'],
    'I': ['###', '.#.', '.#.', '.#.', '###'], 'K': ['#..#', '#.#.', '##..', '#.#.', '#..#'],
    'O': ['.##.', '#..#', '#..#', '#..#', '.##.'], 'R': ['###.', '#..#', '###.', '#.#.', '#..#'],
    'S': ['.###', '#...', '.##.', '...#', '###.'], 'U': ['#..#', '#..#', '#..#', '#..#', '.##.'],
}
PLATES = [(0x735C28, 'KUREI'), (0x735604, 'FUKO'), (0x7376C4, 'KOKU'), (0x7378D0, 'KUKAI'),
          (0x7370A0, 'KAGERO'), (0x736C88, 'SAICHO')]


def plates(out):
    for a, text in PLATES:
        assert out[a:a + 4] == b'ASP0', hex(a)
        px, data, size = asp_pixels(out, a)
        for y in range(3, 10):
            for x in range(3, 61):
                px[y][x] = 0xD
        w = sum(len(PLATE_FONT[c][0]) + 1 for c in text) - 1
        x = (64 - w) // 2
        for c in text:
            g = PLATE_FONT[c]
            for r, row in enumerate(g):
                for dx, p in enumerate(row):
                    if p == '#':
                        for oy in (-1, 0, 1):
                            for ox in (-1, 0, 1):
                                if px[4 + r + oy][x + dx + ox] == 0xD:
                                    px[4 + r + oy][x + dx + ox] = 1
            for r, row in enumerate(g):
                for dx, p in enumerate(row):
                    if p == '#':
                        px[4 + r][x + dx] = 0xF
            x += len(g[0]) + 1
        out[data:data + size] = sprite_tiles(px)
        yield data, data + size


CONTINUE_BTN = 0x73D97C   # ASP0 32x32 8bpp "続きから" (story character select, table 0x468D08)


def continue_button(out):
    a = CONTINUE_BTN
    assert out[a:a + 4] == b'ASP0'
    data = a + 12
    px = [[out[data + ((y // 8) * 4 + x // 8) * 64 + (y % 8) * 8 + x % 8] for x in range(32)] for y in range(32)]
    for y in range(3, 29):
        for x in range(3, 29):
            px[y][x] = 0x1B
    font = T.Font()
    for text, top in (('Load', 4), ('Game', 16)):
        rows, ink = T.strip(text, font)
        x0 = 3 + (26 - ink) // 2
        for r, v in enumerate(rows):
            for dx in range(ink):
                if v >> dx & 1:
                    for oy in (-1, 0, 1):
                        for ox in (-1, 0, 1):
                            if px[top + r + oy][x0 + dx + ox] == 0x1B:
                                px[top + r + oy][x0 + dx + ox] = 0x01
        for r, v in enumerate(rows):
            for dx in range(ink):
                if v >> dx & 1:
                    px[top + r][x0 + dx] = 0x5F
    for y in range(32):
        for x in range(32):
            out[data + ((y // 8) * 4 + x // 8) * 64 + (y % 8) * 8 + x % 8] = px[y][x]
    yield data, data + 1024


def patch(out, append):
    """Apply every graphics redraw to the bytearray `out` (append(blob) -> offset for new data); returns the
    original-ROM (lo, hi) ranges written."""
    return (list(intro(out)) + list(credits(out, append)) + list(end_card(out, append)) + list(labels(out)) + list(plates(out))
            + list(continue_button(out)))


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
