from movers.interactive_mover import InteractiveMover
from system.defs import Terminators, Facing


class Breath(InteractiveMover):
    hitoffs = (0,0,8,8)

    expirationTimer = 20

    def go(self):
        super().go()

        if self.xvel <= 0:
            self.xloc = 0xFFFF
            self.yloc = 0xFFFF
            self.xvel = 0
            self.xaccl = 0

    def __init__(self, anim_init, id, placeholder, facing = Facing.LEFT):
        super().__init__(anim_init, id, placeholder, facing)