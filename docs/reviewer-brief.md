# Translation reviewer brief - Recca no Honoo: The Game (Flame of Recca, GBA)

You review part of a JP->English fan translation. Read-only: no edits, no git, no subagents.
Mechanical validity (ids, control codes, encodable characters, width) is already enforced by the check tool - judge
translation quality. Return the report as your final message (do not write files).

## Inputs (paths in your dispatch; repo root H:\translation\batch\projects\recca-no-honoo-the-game)
- Pairs file: `>> id | JP` then the English on the next line, in story order. Read ALL of it, in passes if large.
- `glossary.md` (rulings at the top), `docs/style-reference.md`, `docs/translator-brief.md` (notes section = binding
  decisions).
- Note: the portrait tag in story files is not the speaker; speakers are inferred from content.

## Judge
- Accuracy: mistranslation, omission, addition, wrong speaker or addressee, reversed meaning. Quote the JP and say what
  it means.
- Consistency: glossary names/terms exactly; nicknames per the brief notes; voice matches the style reference.
- Things players catch: jokes/wordplay losing punch; abbreviated names or terms; awkward stock phrases ("... GET!").
- Naturalness: would a fan-translation reader stumble?

## Report
### Issues
#### Critical (meaning reversed, wrong speaker making the scene wrong, broken placeholder grammar)
#### Important (clear mistranslation, glossary inconsistency, abbreviation)
#### Minor (style)
Each: `id - JP gist - problem - suggested EN` (suggested EN must keep every control code and placeholder).
### Assessment
Approved | Needs fixes - one sentence why.
