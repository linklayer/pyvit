from canard.proto.cantp import CanTpProtocol
from canard.proto.cantp import CanTpMessage
from canard import can 

p = CanTpProtocol()


f = can.Frame(0x100)
f.data = [3,1,2,3]
f.dlc = 4

#print(p.parse_frame(f))

f.data = [0x10, 20, 1, 2, 3, 4, 5, 6]
f.dlc = 8
print(p.parse_frame(f))
f.data = [0x21, 7, 8, 9, 10, 11, 12, 13]
#print(p.parse_frame(f))
f.data = [0x22, 7, 8, 9, 10, 11, 12, 13]
#print(p.parse_frame(f))

m = CanTpMessage(0x100)
m.data = range(1,0xFF)
m.length = 0x1FF
for fr in p.generate_frames(m):
    print fr
