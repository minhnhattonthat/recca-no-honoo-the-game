# Engine / RAM (used by tools/debug/warp.lua)

- Scene system: task struct 0x03000020, current scene function at 0x0300002C (prev 0x03000050).
  `set_scene(fn)` = 0x0800D974. Known scenes: title 0x0802D20D, main menu 0x0802DACD, story char select 0x080332A9,
  story script 0x0803141D, VS COM 0x08037B35, link VS 0x08039ACD, secret (??????) 0x0803BDD1, database 0x0803FE71,
  option 0x08042389.
- Main menu: result index 0x03000BA0 (0 story, 1 battle, 2 secret, 3 database, 4 option), battle sub 0x03000BA1;
  read at 0x0802E0A4 (jump table 0x0802E0C0) — warp.lua overrides it there.
- Script interpreter: PC 0x03000BA8, file base 0x03000BA4, string table 0x03000BAC, label table 0x03000BB0. Story
  scene loads file index `[[0x0843B390]+0x218+6]` at 0x080313B8 (table 0x08468354). Instruction length =
  (op & 0xF)·2 + 2; dispatcher stores the new PC at 0x08031234. `jump`: PC = base + label - 4.
- Command names/handlers table 0x08468890 (12-byte rows: name, opcode, handler).
