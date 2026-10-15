"""AC bytecode walker: which face (portrait = speaker) is up when each message string is shown.
Opcodes (table 0x0846888C, [handler, name, op] rows with the op column one row late): message 0x0001(str),
face_open 0x3202(slot, face), face_change 0x3212(slot, face), face_close 0x3201(slot), face_closeall 0x3200.
Instruction length = (op & 0xF)*2 + 2, except 0xFxxx expression tokens (4 bytes)."""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import textlib as T  # noqa: E402


def ops(d, i):
    base = T.u32(d, T.AC_TABLE + 4 * i) - T.ROMBASE
    nl, ol, ns, os_ = struct.unpack_from('<4H', d, base + 4)
    pc, out = 12, []
    while pc < ol:
        op = T.u16(d, base + pc)
        n = 4 if op & 0xF000 == 0xF000 else (op & 0xF) * 2 + 2
        out.append((pc, op, [T.u16(d, base + pc + 2 + 2 * k) for k in range((n - 2) // 2)]))
        pc += n
    assert pc == ol
    return out


def speakers(d, i):
    """{string index: face id or None} (last face opened/changed before the message)."""
    face, res = None, {}
    for pc, op, a in ops(d, i):
        if op in (0x3202, 0x3212):
            face = a[1]
        elif op == 0x3200:
            face = None
        elif op == 0x3201:
            face = None
        elif op == 0x0001:
            res.setdefault(a[0], face)
    return res


if __name__ == '__main__':
    d = T.rom()
    i = int(sys.argv[1])
    f = T.ac_parse(d, i)
    sp = speakers(d, i)
    for k, s in enumerate(f['strings']):
        print(k, sp.get(k), T.decode(s).replace('%n', ' ')[:40])
