# Recca no Honoo - The Game (GBA) English translation

Skill: translate-retro-game (H:\translation\batch\.claude\skills\translate-retro-game\SKILL.md). Read it before ROM, text or QA work. `$SKILL` below = that dir.

## Commands (run from repo root)
- Build:    `python -X utf8 build.py build` -> build/recca_en.gba (`build.py marker` -> build/recca_marker.gba)
- Check:    `python -X utf8 tools/check.py` (tests + lint; the pre-commit hook runs this)
- Smoke:    `python -X utf8 H:/translation/batch/.claude/skills/translate-retro-game/scripts/emu.py build/recca_en.gba --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 tools/debug/warp.py SCENE [--rom build/recca_en.gba]` (scene list: `tools/debug/scenes.json`; never ask the user to play to a scene)
- Release:  `python -X utf8 build.py release` (patch + verify; never publish without the user)

## Paths
- Original ROM: `rom/Recca no Honoo - The Game (Japan).gba` (gitignored; SHA-1 35fe535e24ddde1428d359a95bf114b0968911e9). Emulator: `tools/mesen/` (MesenCE 2.2.1, github.com/nesdev-org/MesenCE/releases/download/2.2.1/Mesen_2.2.1_Windows.zip, + Firmware/gba_bios.bin via fetch_emu.py gba-bios; gitignored; settings in `tools/emu-config/`). States: `work/states/`.
- Text: `script/` (JSON). Glossary + rulings: `glossary.md`. RE notes: `docs/re/README.md`.

## Rulings (pre-approved by the user)
- Edit source files only with the file-edit tool. Full names, no abbreviations (engine work first). Honorifics dropped; given name first. Romanization: Viz/official English (Flame of Recca) > Hepburn. Credits in English. Graphics text in scope.
- Never push/publish/upload. Release = local `release/recca-no-honoo-the-game_en.zip` (patch + README).

## Status
- Done: Step 0. Next: phase 1 recon. Open bugs: none.
