# Text system

## Encoding
Shift-JIS, double-byte only. ASCII bytes are NOT drawn: the renderer treats any non-`%`, non-`\n` byte as the lead of a
2-byte code, the typewriter skips bytes < 0x80. Every glyph = one 2-byte code = one 16×16 4bpp cell (0x80 bytes,
tile order TL TR BL BR).

## Renderer `0x0800C798 render(dst r0, str r1)` (48 callers: all menus, database, dialogue)
- Walks the string; per glyph calls `0x0800C6B4 glyph(dst, code, color)` and dst += 0x80. Returns the cell count.
- `glyph` linear-searches the font list at 0x087403BC (literal at 0x0800C6D4) for the code; not found → colour 0xF garbage.
  Glyph bitmap: 11 rows × 2 bytes, MSB = leftmost pixel. Each set pixel also writes a 1-px shadow to its right
  (colour = high nibble of the colour byte; normal 1, `%B` = same colour = bold, `%N` = none).
- Codes (jump table 0x0800C7DC, letter - 0x42): `%B` bold/shadow=colour, `%S` shadow 1 (normal), `%N` no shadow,
  `%P<d>` colour = d+0xD8 (`6` → 0xE highlight, `7` → 0xF normal), `%T<d> %W<d> %w<d>` 1-byte arg skipped, others
  (`%n %K %/`) skipped. `\n` (0x0A) skipped.
- Special codes: 0x83B0 = number (`'０' + [0x03003D0C]`), 0x83D0 = party member names (table 0x0843B374, mask
  0x03003D24, member cells padded to 12).

## Dialogue typewriter `0x0802F690` (reads the string again from ROM, task struct r7)
- Byte ≥ 0x80 → show next cell sprite: x += 14 px (`+0x22`), tile += 4, count++; auto-wrap after N cells
  (table 0x0846886C by box type: 16, 13, 13, 11) via `0x08048A68` (mod). `%n` → column 0 (new line).
- `%W<d>` wait 60·d, `%w<d>` wait 6·d, `%T<d>` speed (table 0x08468874), `%K` flag, `%/` wait 60.
- Dialogue box: 13 cells × 14 px = 182 px, 3 lines.

## Story scripts (.AC, compiled bytecode, read in place from ROM)
File: `%ASS` (header op 0x4125, 12 bytes) + u16 n_labels, u16 label_table_off, u16 n_strings, u16 string_table_off;
bytecode; label table (u16 offsets from file start); string table (u16 offsets from file start); NUL-terminated
strings; pad to 4. Strings are referenced by index only, so a rebuilt file with new string data + table works.
Pointer table 0x08468354 (23 files): INIT, INTRO1-3, CLOSE1-2, RECCA1-3, DOMON1-3, FUKO1-3, TOKIYA1-3, KAORU1-3, CREY,
VIEW-CHR (names at 0x4B57C reversed). 1813 strings, ≤ 13 chars/line, ≤ 3 lines; skill-learned lines use
`%B%P6...%S%P7` highlight.

## System strings 0x4B460-0x4F8E4
730 Japanese strings; each reached by ≥ 1 pointer at its start (code literal pools < 0x50000, tables 0x467000-0x46C000:
menu descriptions 0x468318, profile lines 0x469340 (453, fixed 24-byte slots, 10 cells per line, stored bottom-up),
sound-test names 0x469CFC (269), stages 0x468D90, misc). Many are padded with `　` to a fixed cell count to clear old
cells: keep the same cell count in English.

## English plan (engine spike, phase 5)
Build-time "cell groups": the insert tool wraps English into runs of letters whose VWF width fits one cell
(≤ 14 px incl. 1-px spacing/shadow), renders each unique run into a glyph in the game's own font format, and encodes
it as a 2-byte code (lead 0x88-0xFF). A 10-instruction hook in `glyph` indexes the new font table directly instead of
the linear search. Renderer, typewriter, menus and cell counts keep working unchanged.
