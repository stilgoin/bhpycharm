from collections import defaultdict
from enum import Enum

class BGColl(Enum):
    BGONLY = 0
    SOLID = 1
    SEMISOLID = 2


CollisionIndex = defaultdict(int, {
    1 : defaultdict(int, {
        0x0 : 1, 0x1 : 1, 0x40 : 1, 0x41 : 1, 0x80 : 1, 0x81 : 1, 0xC0 : 1, 0xC1 : 1
    }),

    2 : defaultdict(int, {
        0x0 : 1, 0x1 : 1, 0x20 : 1, 0x21 : 1
    }),

    4 : defaultdict(int, {
        0xC0 : 2, 0xC1 : 2
    })
})