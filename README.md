# Recca no Honoo: The Game (Flame of Recca) English translation

Unofficial English fan translation of **Recca no Honoo - The Game** (Game Boy Advance, Konami, 2001): the source text
and tools that build the patch.

**No game data is included.** Download the BPS patch from the [latest release](../../releases/latest) and apply it to
your own dump, `Recca no Honoo - The Game (Japan).gba` (8,388,608 bytes, CRC32 B29BEE34). The release README lists the
hashes, patching steps and known issues. The patched ROM is larger than the original; that is expected.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## Translation status

| Part | Status |
|---|---|
| Story mode: every character's story, the training chapter, Kurei's story, endings | Translated |
| Menus, help bars, save panel, option dialogs, sound test names | Translated |
| Database profiles, name list and buttons | Translated |
| Opening text crawl, chapter title cards, episode-clear buttons, name plates | Translated |
| Title screen | Title logo kept in Japanese (series logo; it already carries the English title) |
| Staff roll and "THE END" card | Translated (staff names romanised from kanji; some readings may differ) |
| Link-cable (two GBA) screens | Not checked in play |

Names follow the official English (Viz) *Flame of Recca* spellings, given name first, no honorifics.

Known issues: the save-panel label for super special moves is shortened to "Super Specials" (6-character slot); full
list in the release README.

## Building from source
You need your own ROM under `rom/` (gitignored). See `CLAUDE.md` for the commands (`python -X utf8 build.py build`,
`tools/check.py`, `build.py release`) and `docs/re/` for the engine research.

- `script/`: story (`ac/`), menus (`sys.json`) and database profiles (Japanese + English)
- `tools/`: insertion, VWF font, graphics, lint, debug warp and release tools
- `tbl/`: text tables and the English font
- `glossary.md`: naming rulings

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

Translation, tools and patch were produced with AI assistance (Claude, Anthropic) under the direction of the project
owner. Flame of Recca is (c) Nobuyuki Anzai / Shogakukan; the game is (c) Konami. This project is not affiliated with
them. Do not share patched ROMs.
