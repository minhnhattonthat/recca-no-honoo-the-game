# Graphics-text survey (all handled in tools/gfx.py, applied by build.py)

| Screen | Element | Source | Status |
|---|---|---|---|
| Intro crawl (after Konami logo) | 16 text lines | ASP0 128x16 sprites, table 0x0846829C[1..16] (first has a palette) | English, in place |
| Staff roll (CREY.AC `staff_roll`, warp `story:21:0 PC=3526`) | 8 credit pages | ABG0 pages (30-wide u16 map), table 0x08468E68 (+0x468E88 = page 0); VRAM slots 0x0040/0x2040, 254 tiles max | English, relocated |
| End card | 完 | ABG0 0x778E0C via literal 0x34C98 (uses h-flip map bit) | "THE END", relocated |
| Database list | 25 character names | ASP0 96x16 at 0x72ED64 + 0x30C*k (table 0x469B64) | English, in place |
| Database buttons | プロフィール / ワザリスト / リザルト / もどる | ASP0 64x16 0x733CC8 / 0x733ED4 / 0x7340E0 / 0x7342EC | English, in place |
| Name plates (portraits, select screens) | CREY, FŪKO, KOKŪ, KŪKAI, KAGEROU, SAICHOU | ASP0 64x16 0x7351EC.. (tables 0x4686C8..) | respelled to glossary (KUREI, FUKO, KOKU, KUKAI, KAGERO, SAICHO) |
| Chapter cards (story `title` cmd 0x2E02 [episode, title], over flames before each episode; QA: emu.py `--script tools/debug/warp.lua --var "SCENE='story:7:0'" --var PC=176`) | 第N話 (9) + 「title」 (28) | ABG0 8bpp (u8 width/2, u16 height*2, (w//8)x(h//8) u16 map), tables 0x4687B4 / 0x4687D8; text = sys.json save-panel entries (tables 0x468DA8 / 0x468DCC, same order) | English, relocated (gfx.py `chapter_cards`) |
| Episode-clear STATUS screen buttons (story `terminal` cmd 0x2E12; QA: `SCENE='story:6:0'` `PC=466`, 3200 frames) | 進む / 終わる | ASP0 64x16 0x769890 / 0x769A9C (code 0x33B1C / 0x33B54) | "Continue" / "Quit", in place |
| Title screen | 烈火の炎 logo | BG | kept: series logo; it already carries the English title "Flame of Recca" and "THE GAME" |
| End card | 烈火の炎 logo | ABG0 | kept (same logo) |
| Menus (STORY/BATTLE/DATA BASE/OPTION, CONFIGURATION, FIELD SELECT, VS, READY/GO, results) | | | already English in the original |
