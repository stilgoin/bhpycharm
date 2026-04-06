from game.maps import Hitbox
from game.overlap import moverToMover, Result
from movers.interactive_mover import InteractiveMover
from movers.blocks.block import Block
from movers.mover_classes import Player, MiscMover
from movers.movers import Mover
from system.defs import Facing, Id

"""
class Hammer(Mover):
    active = False

    def check(self, moverToBGFunc = lambda : None):
        pass

class Statue(Block):

    hammer : Hammer = None

    def misc_hitbox(self):
        self.hb = Hitbox(self.xloc, self.yloc, (-8,0,32,16))

    def check(self, floor_found, moverToBGFunc):
        super().check(floor_found, moverToBGFunc)

    def postproc(self):
        # self.trigger_box = Hitbox(self.xloc, self.yloc, (-8,0,32,16))
        if self.action_timer > 0:
            self.action_timer -= 1
            if self.action_timer <= 30:
                self.hammer.xloc = 0xFFFF
        else:
            self.hammer.xloc = 0xFFFF

        # self.hb = Hitbox(self.xloc, self.yloc, (-8,0,32,16))
        for mover in InteractiveMover.any_blocks + Player.movers:
            if mover.id == Id.STATUE.value:
                continue

            result = moverToMover(self, mover)
            if result.result == Result.CONTACT \
                    or result.result == Result.OVERLAP:

                if not self.action_timer:
                    self.action_timer = 60
                    self.hammer.yloc = self.yloc - 0x4
                    if result.facing == Facing.LEFT \
                            or result.side == Facing.LEFT:
                        self.hammer.xloc = self.xloc - 0x8
                    else:
                        self.hammer.xloc = self.xloc + 0x10

        self.make_hitboxes()



    def animate(self):
        return [self.animation_state \
                    .display_entry(self.id, self.xloc, self.yloc,
                                   True if self.facing == Facing.RIGHT else False,
                                   False),
                self.hammer.animation_state.display_entry(self.hammer.id, self.hammer.xloc, self.hammer.yloc,
                                   True if self.hammer.facing == Facing.RIGHT else False,
                                   False)]

    def go(self):
        super().go()

    def __init__(self, anim_inits, anim_init, id = Id.STATUE.value, placeholder = True):
        self.hammer = Hammer(anim_inits[Id.HAMMER], Id.HAMMER.value, True)
        MiscMover.movers.append(self.hammer)
        super().__init__(anim_init, id, placeholder)
        MiscMover.postproc_movers.append(self)
"""