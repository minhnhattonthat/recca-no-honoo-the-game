-- Cold-boot warp for Recca no Honoo - The Game (GBA). Appended after the emu.py driver (uses L.*).
-- Globals (via --var): SCENE = "title" | "menu" | "mode:N[:SUB]" | "story:FILE[:LABEL]"
--   mode N: main-menu result 0 story, 1 battle (SUB 0 = vs COM, 1 = link), 2 secret (??????), 3 database, 4 option
--   story FILE: AC script index 0-22 (pointer table 0x08468354); LABEL: index into that file's label table
-- AFTER = route string run once the scene is reached ("30 -;6 a;60 -"), GOD = 1 keeps story battles short (unused yet).
-- Logs "ARRIVED <frame>" when the target is reached; screenshots/frames come from emu.py flags.
local M = emu.memType.gbaMemory
local SCENE_FN = 0x0300002C
local FN_TITLE, FN_MENU, FN_CHARSEL, FN_STORY = 0x0802D20D, 0x0802DACD, 0x080332A9, 0x0803141D
local AC_TABLE = 0x08468354

local kind, a1, a2 = (SCENE or "title"):match("^(%a+):?(%d*):?(%d*)$")
assert(kind, "bad SCENE " .. tostring(SCENE))
a1, a2 = tonumber(a1), tonumber(a2)
local arrived = false
local function arrive()
  if arrived then return end
  arrived = true
  L.log("ARRIVED " .. L.frame)
  if AFTER then for step in AFTER:gmatch("[^;]+") do
    local n, spec = step:match("^%s*(%d+)%s+(%S+)%s*$")
    L.press(spec, tonumber(n))
  end end
end

-- main-menu result override (read at 0x0802E0A4 right before the mode jump table)
if kind == "mode" or kind == "story" then
  L.on_exec(0x0802E0A4, 0x0802E0A4, function()
    emu.write(0x03000BA0, kind == "story" and 0 or a1, M)
    emu.write(0x03000BA1, a2 or 0, M)
  end)
end

-- story: replace the first script the story scene loads (pc 0x080313C6 stores it, 0x0802E4A0 inits)
if kind == "story" then
  L.on_exec(0x080313CC, 0x080313CC, function()
    if arrived then return end
    local base = emu.read32(AC_TABLE + 4 * a1, M)
    emu.write32(0x03000BA8, base, M)
    if not a2 then arrive() end
  end)
  -- label: let the file set up its scene (fade, BG, faces) until its first message types, then jump the
  -- interpreter PC (0x03000BA8, just advanced by the dispatcher at 0x08031234) to the label
  if a2 then
    local typed = false
    L.on_exec(0x0802F690, 0x0802F690, function() typed = true end)
    L.on_exec(0x08031236, 0x08031236, function()
      if arrived or not typed then return end
      local base = emu.read32(0x03000BA4, M)
      local loff = emu.read16(base + 6, M)
      emu.write32(0x03000BA8, base + emu.read16(base + loff + 2 * a2, M), M)
      arrive()
    end)
  end
end

-- input: press through title / menu / character select until the target is reached
local hold = 0
emu.addEventCallback(L.safe(function()
  if arrived then return end
  local fn = emu.read32(SCENE_FN, M)
  local key
  if fn == FN_TITLE then key = "start"
  elseif fn == FN_MENU then
    if kind == "menu" then arrive() return end
    if kind == "title" then return end
    key = "a"
  elseif fn == FN_CHARSEL or kind == "mode" then
    if kind == "mode" and fn ~= FN_MENU then arrive() return end
    key = "a"
  else
    if kind == "title" and fn == FN_TITLE then arrive() end
    key = (L.frame % 120 < 6) and "start" or nil -- skip logos/intro
  end
  if kind == "title" and fn == FN_TITLE then arrive() return end
  if key and L.frame % 30 < 6 then emu.setInput({ [key] = true }, 0) end
end), emu.eventType.inputPolled)
