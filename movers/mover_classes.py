from movers.movers import Mover
from game.Handlers import *
from game.Overlap import moverToMover, OverlapResult, Result
from system.defs import Vertical, Facing, Push


class InteractionListener:

    listeners = []

    def __init__(self, mva, mvb):
        self.mva = mva
        self.mvb = mvb

class InteractiveMover(Mover):

    movers = []

    hitoffs = (0, 0, 15, 15)
    snap_xloc = 0.0
    push_xloc = 0.0
    pvel = 0.0

    def nudge_release(self):
        self.xvel = 1.0
        self.xaccl = -0.175

        if abs(self.push_xloc - self.xloc) <= 4:
            self.push_state = Push.ROLLBACK
            self.facing *= -1
        elif abs(self.push_xloc - self.xloc) > 4:
            self.push_state = Push.STEP

    def nudge_continue(self):
        if not self.pvel:
            self.xvel = 1
            self.pvel += 1

        if self.pvel >= 1 and self.pvel <= 3:
            self.xvel += 0.175
            if self.xvel >= 1:
                self.xvel = 0
                self.pvel += 1

    def __init__(self, anim_init, id):
        super().__init__(anim_init, id)

class PushingMover(Mover):

    movers = []

    def initInteraction(self, interact_mover : InteractiveMover,
                        result : OverlapResult) -> bool:
        floor_found = False
        if result.result == Result.CONTACT \
            and result.standing == Vertical.DOWN or \
            result.result == Result.OVERLAP \
            and result.vert == Vertical.DOWN:

            rollbackYUp(self, interact_mover.hb)
            floor_found = True
        return floor_found


    def moverToMovers(self) -> tuple[bool, OverlapResult]:
        floor_found = False
        result = OverlapResult()
        for interact_mover in InteractiveMover.movers:
            result : OverlapResult = moverToMover(self, interact_mover)
            floor_found = floor_found or \
                          self.initInteraction(interact_mover, result)

        return floor_found, result


    def __init__(self, anim_init, id):
        super().__init__(anim_init, id)



