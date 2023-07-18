from movers.movers import Mover
from game.Handlers import *
from game.Overlap import moverToMover, OverlapResult, Result
from system.defs import Vertical, Facing

class InteractionListener:

    listeners = []

    def __init__(self, mva, mvb):
        self.mva = mva
        self.mvb = mvb

class InteractiveMover(Mover):

    movers = []

    hitoffs = (0, 0, 15, 15)

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


    def moverToMovers(self) -> bool:
        floor_found = False
        for interact_mover in InteractiveMover.movers:
            result : OverlapResult = moverToMover(self, interact_mover)
            floor_found = floor_found or \
                          self.initInteraction(interact_mover, result)

        return floor_found


    def __init__(self, anim_init, id):
        super().__init__(anim_init, id)



