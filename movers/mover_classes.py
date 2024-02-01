from movers.InteractiveMover import InteractiveMover
from movers.movers import Mover
from system.defs import Id, Anim, Jump


class MiscMover(Mover):
    movers = []
    postproc_movers = []


class Player(InteractiveMover):
    hitoffs = (4.0, 1.0, 12.0, 14.0)
    movers = []
    def move(self):
        super().move()
        if self.jump_state == Jump.JUMP:
            if self.yvel <= 1.50 \
                    and not self.animation_state \
                    .check_anim_idx(Anim.PEAK):
                pass
                self.set_anim_idx(Anim.PEAK)

    def __init__(self, anim_init, id = Id.PLAYER.value, placeholder = False):
        super().__init__(anim_init, id, placeholder)



