-- Screenshot every story message once it has finished typing (typewriter end at 0x0802F892, docs/re/text.md).
-- Writes msg_<frame>.png into --out and logs "MSG <frame> <file base> <string table entry>".
local M = emu.memType.gbaMemory
local pending = nil
local count = 0
L.on_exec(0x0802F892, 0x0802F892, function()
  -- the code below sets bit 0x80 of 0x03004435 ("message done"); fire only on the first time per message
  if emu.read(0x03004435, M) & 0x80 == 0 and pending == nil then pending = L.frame + (MSG_DELAY or 40) end
end)
L.on_frame(function(f)
  if pending and f >= pending then
    pending = nil
    count = count + 1
    L.shot(string.format("msg_%06d.png", f))
    L.log(string.format("MSG %d base=%08X", f, emu.read32(0x03000BA4, M)))
  end
end)
