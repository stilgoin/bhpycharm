from game.Maps import Hitbox
from game.Overlap import moverToMover, OverlapResult, Result
from movers.InteractiveMover import InteractiveMover
from movers.PushingMover import PushingMover
from movers.movers import Mover
from system.defs import Facing, Push, Id, Anim, Jump, Ability


class MiscMover(Mover):
    movers = []

class Statue(InteractiveMover):

    class Hammer(Mover):
        active = False

        def check(self, moverToBGFunc = lambda : None):
            pass

    hammer : Hammer = None

    def check(self, moverToBGFunc):
        #self.trigger_box = Hitbox(self.xloc, self.yloc, (-8,0,32,16))
        if self.action_timer > 0:
            self.action_timer -= 1
            if self.action_timer <= 30:
                self.hammer.xloc = 0xFFFF
        else:
            self.hammer.xloc = 0xFFFF

        self.hb = Hitbox(self.xloc, self.yloc, (-8,0,32,16))
        for mover in InteractiveMover.movers + PushingMover.movers:
            result = moverToMover(self, mover)
            if result.result == Result.CONTACT \
                or result.result == Result.OVERLAP:

                if not self.action_timer:
                    self.action_timer = 60
                    self.hammer.yloc = self.yloc - 0x4
                    if result.facing == Facing.LEFT \
                        or result.side == Facing.LEFT:
                        self.hammer.xloc = self.xloc - 0x10
                    else:
                        self.hammer.xloc = self.xloc + 0x10

        super().check(moverToBGFunc)

    def animate(self):
        return [self.animation_state \
                    .display_entry(self.id, self.xloc, self.yloc,
                                   True if self.facing == Facing.RIGHT else False,
                                   False),
                self.hammer.animation_state.display_entry(self.hammer.id, self.hammer.xloc, self.hammer.yloc,
                                   True if self.hammer.facing == Facing.RIGHT else False,
                                   False)]

    def __init__(self, anim_inits, anim_init, id = Id.STATUE.value, placeholder = True):
        self.hammer = self.Hammer(anim_inits[Id.HAMMER], Id.HAMMER.value, True)
        MiscMover.movers.append(self.hammer)
        super().__init__(anim_init, id, placeholder)


class Player(PushingMover):

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



