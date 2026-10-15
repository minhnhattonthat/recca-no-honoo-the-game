# RE notes index — Recca no Honoo - The Game (GBA, ARHJ, Konami 2001)

ROM: 8 MiB, `RECCATHEGAMEARHJA4`. CRC32 B29BEE34, MD5 ac593798dfb4a39c4502ba3ea9092680, SHA-1 35fe535e24ddde1428d359a95bf114b0968911e9.
Prior work: none found (romhacking.net/cdromance/web searches, Oct 2026). No earlier English patch.

- `text.md` — encoding, renderer, typewriter, control codes, font, story scripts (.AC), system strings, pointers.
- `engine.md` — scene system, script interpreter, RAM addresses used by the debug tool.
- `graphics.md` — graphics-text survey.

## Free space
- 0x798B10-0x7FFFFF (~423 KB) is 0xFF fill after the last AC file. ROM can grow to 16 MiB (no save-type issue expected: the game uses SRAM/flash? see engine.md).

## Text ranges
- Story scripts: 23 `.AC` files at 0x77A1C8-0x798B0A, pointer table 0x468354 (23 × u32).
- System strings: 0x4B460-0x4F8E4 (730 Japanese strings, every one reached by a pointer at its start; slots in code literal pools < 0x50000 and tables 0x467000-0x46C000).
- English debug names 0x4B000-0x4B460 and 0x4F8E8+ (TENDOU-ZIGOKU...) are debug-only: kept.
- Font: 1072 glyphs at 0x7403BC (24-byte entries: u16 SJIS code + 11 rows × 16 px 1bpp), sorted, 0xFFFF end.
