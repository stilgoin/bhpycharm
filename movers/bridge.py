from movers.interactive_mover import InteractiveMover
from system.defs import Id, Status

"""
class BridgeSegment(InteractiveMover):
    bounce_val = 0.0625
    shake_vel = 0.75
    save_yloc = 0.0
    load_count = 0
    hitoffs = (0, 0, 15, 6)
    def go(self):

        if self.move_state == Status.SHAKE:
            self.yvel -= self.bounce_val
            if self.yvel < 0.0:
                self.yvel = self.shake_vel
                self.vertical *= -1
        else:
            self.yvel = 0.0

        super().go()

    def check(self, floor_found, moverToBGFunc):
        pass

    def __init__(self, anim_init, id = Id.BRIDGEPLAT.value, placeholder = True):
        super().__init__(anim_init, id, placeholder)
"""