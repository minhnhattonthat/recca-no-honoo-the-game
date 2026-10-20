# Recca no Honoo - The Game (GBA) English translation

Skill: translate-retro-game (H:\translation\batch\.claude\skills\translate-retro-game\SKILL.md). Read it before ROM, text or QA work. `$SKILL` below = that dir.

## Commands (run from repo root)
- Build:    `python -X utf8 build.py build` -> build/recca_en.gba (`build.py marker` -> build/recca_marker.gba; `build.py build ID=text ..` -> build/recca_qa.gba with test overrides)
- Check:    `python -X utf8 tools/check.py` (tests incl. a full build + romdiff, then tools/lint.py; the pre-commit hook runs this)
- Smoke:    `python -X utf8 H:/translation/batch/.claude/skills/translate-retro-game/scripts/emu.py build/recca_en.gba --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 tools/debug/warp.py SCENE [--rom build/recca_en.gba] [--sheet]` (scenes: tools/debug/scenes.json, or raw `title|menu|mode:N[:SUB]|story:FILE[:LABEL]`; `warp.py all` regenerates every scene + work/states/). Staff roll: emu.py ... `--script tools/debug/warp.lua --var "SCENE='story:21:0'" --var PC=3526 --frames 6500`. Message shots: add `--script tools/debug/msgshot.lua`, then `tools/debug/msgsheet.py DIR`.
- Text:     `tools/batches.py split|check|merge|fix`, `tools/fit.py "text" --cells 13 --lines 3`, `tools/pairs.py` (review input)
- Release:  `python -X utf8 build.py release` (gate + BPS + verify + zip in release/; never publish without the user)

## Paths
- Original ROM: `rom/Recca no Honoo - The Game (Japan).gba` (gitignored; SHA-1 35fe535e24ddde1428d359a95bf114b0968911e9). Emulator: `tools/mesen/` (MesenCE 2.2.1, github.com/nesdev-org/MesenCE/releases/download/2.2.1/Mesen_2.2.1_Windows.zip, + Firmware/gba_bios.bin via fetch_emu.py gba-bios; gitignored; settings in `tools/emu-config/`).
- Text: `script/ac/*.json` (story), `script/sys.json` (menus; ctx/max/layout from tools/sysctx.py), `script/profiles.json`. Font: `tbl/font_en.txt`. Graphics: `tools/gfx.py`. Glossary + rulings: `glossary.md`. Briefs: `docs/`. RE notes: `docs/re/README.md`.

## Rulings (pre-approved by the user)
- Edit source files only with the file-edit tool. Full names, no abbreviations (engine work first). Honorifics dropped; given name first. Romanization: Viz/official English > Hepburn, no macrons. Credits in English. Graphics text in scope (title kanji logo kept: carries the English title).
- Never push/publish/upload. Release = local `release/recca-no-honoo-the-game_en.zip` (patch + README).
- Engine gotchas: English = build-time VWF cells (private 2-byte codes, leads 0x85-87/A0-DF/F0-FF, font hook at 0x0800C6CC); widgets pad to the JP cell count; relocated strings must stay 4-byte aligned (ldm copies); save-panel digit labels are fixed 6 cells; option dialogs fill a 6-cell grid.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update the Status section.

## Status
- Done: all phases 0-9; v1.0 released locally (release/recca-no-honoo-the-game_en.zip). Next: optional Minor polish from reviews (docs/ notes), hardware/link-cable test. Open bugs: none known.
