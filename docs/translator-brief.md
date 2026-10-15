# Translator brief - Recca no Honoo: The Game (Flame of Recca, GBA, Konami 2001)

You translate part of the Japanese script of a Flame of Recca fighting game's story mode into English for a fan
patch. Shonen ninja action: Recca Hanabishi and his Hokage friends storm Koran Mori's fortress city SODOM to rescue
Yanagi; Kurei and the Uruha/Ura Uruha assassins get in the way. Lots of trash talk before fights.
Work only on the batch named in your dispatch. Do all translation yourself; do not dispatch subagents.
Repo root: H:\translation\batch\projects\recca-no-honoo-the-game (run commands from there).

## Read first
1. `docs/style-reference.md` - character voices and approved example pairs. Match this voice.
2. `work/tl/terms_<batch>.txt` - binding glossary rows for this batch (full table + rulings in `glossary.md`).

## Input: `work/tl/<batch>.tsv`
`id<TAB>speaker<TAB>form<TAB>limit<TAB>Japanese`
- Story batches (ac..): `speaker` is only the PORTRAIT shown in the box (`portrait:Recca`), which is often NOT the
  speaker in two-person scenes - decide the speaker from content and the neighbouring lines. `no-portrait` = a shout
  from everyone, narration or a system line. ` / ` separates the lines of one box: translate the box as one utterance,
  do NOT copy the line breaks (the build wraps English automatically).
- Menu batches (sys..): `speaker` describes where the text appears. Keep these short and clear.
- Profile batch (prof): `name // paragraph text` of a character's database entry. Output: the English name line,
  then `\n\n`, then the profile paragraphs (separate paragraphs with `\n\n`). The build wraps lines itself.
- `limit`: lines x cells. A cell is 14 px; the font is proportional (about 2.5 letters per cell). Dialogue boxes are
  3 lines x 13 cells (182 px per line).

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (not a shell heredoc)
`id<TAB>English`, every input id exactly once, same order. Plain ASCII: straight quotes, `...`, `--`; no tabs inside
the English, no Japanese, no `\uXXXX`. Exceptions that MUST stay as given (they are drawn by the game):
- control codes `%W1 %w5 %T7 %/ %K %B %P6 %S %P7` - copy every one, in the same order/position (start, middle or end)
  as in the Japanese. `%n` is a line break: do not use it (the build wraps), except `%n` in ac22.
- fullwidth button text in skill lines: `Ｒ＋→＋Ｂ` etc. (keep fullwidth, keep inside the %B%P6 ... %S%P7 codes).
- `σ１２３４５６７８９０１` (party-member names, printed as "Domon, Fuko, Mikagami," WITH a trailing comma: write
  English that reads on from a comma) and `Σ` (one digit, a count) - copy exactly.
- `０／３`-style tails marked LABEL ONLY: keep the fullwidth tail exactly, translate the label before it.

## Fit
Check any line with `python -X utf8 tools/fit.py "English text" --cells 13 --lines 3` (it prints the wrapped lines).
Dialogue gets 3 lines x 13 cells, roughly 90-100 characters. Menus get the cells shown in `limit`.

## Validate
Run `python -X utf8 tools/batches.py check <batch>` and fix every reported error until it prints OK. Warnings about
glossary terms: fix if the name/term really should be there; pronouns or a natural omission are fine.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add details the Japanese doesn't
  state; don't summarise or skip. Adapt wordplay so the joke still lands (no translator notes).
- Names and terms exactly as in the glossary (given name first; no honorifics: -chan/-kun/-san dropped; -sama ->
  "Lord"/"Lady" only for a servant addressing a master). Never abbreviate a name or term. If a line can't fit without
  losing meaning, keep the meaning and report it as `LONG: id`.
- Punctuation: 「」 -> "...", 『』 -> "...", ・・・/… -> ..., ！！ -> !!, ！？ -> !?, ～ -> drop or stretch the word.
- 姫 (Recca about Yanagi) -> "Princess". ＣＤ -> "CD". 第一話 -> "Episode 1" style only if it fits, else "Part 1".
- Skill-learned lines: `烈火は%n「焔群」（%B%P6Ｒ＋→＋Ｂ%S%P7）が%n使えるようになった！` ->
  `Recca can now use "Homura" (%B%P6Ｒ＋→＋Ｂ%S%P7)!` (move names: glossary, else Hepburn of the kanji reading, or the
  English meaning for plain words like 竜巻 -> "Tornado"; report your choice as NEW TERM).
- No suffix glued to a placeholder (no "Σth"); no "a/an" right before σ or Σ.
- Swearing at the level of a shonen anime ("damn", "bastard" ok).

## Consistency
Never edit `glossary.md` or any file other than your own output file. For a recurring name or term not in the
glossary, pick a form, use it consistently, and report it.

## Report (reply with only this)
Files written and entry count; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`, `LONG: id - note`.
