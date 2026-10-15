"""Exploration helper: print NUL-separated cp932 strings in a ROM range. usage: strdump.py ROM START END"""
import sys
d = open(sys.argv[1], 'rb').read()
o, end = int(sys.argv[2], 16), int(sys.argv[3], 16)
while o < end:
    if d[o] == 0:
        o += 1
        continue
    e = d.index(b'\0', o)
    s = d[o:e]
    try:
        t = s.decode('cp932')
    except UnicodeDecodeError:
        t = '<<' + s.hex() + '>>'
    print('%06X' % o, repr(t))
    o = e
