from pyvit.proto.isotp import IsoTpProtocol, IsoTpMessage
from pyvit import can

p = IsoTpProtocol()

f = can.Frame(0x100)
f.data = [3, 1, 2, 3]

print(p.parse_frame(f))

f.data = [0x10, 20, 1, 2, 3, 4, 5, 6]
print(p.parse_frame(f))
f.data = [0x21, 7, 8, 9, 10, 11, 12, 13]
print(p.parse_frame(f))
f.data = [0x22, 7, 8, 9, 10, 11, 12, 13]
print(p.parse_frame(f))

m = IsoTpMessage(0x100)
m.data = range(1, 0xFF)
m.length = 0xFF
for fr in p.generate_frames(m):
    print fr

m.data = [1, 2, 3, 4]
m.length = 4
for fr in p.generate_frames(m):
    print fr
