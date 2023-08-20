from game.Handlers import rollbackXRight, rollbackXLeft, rollbackYUp
from game.Overlap import OverlapResult, moverToMover, Result
from movers.InteractiveMover import InteractiveMover
from movers.movers import Mover
from system.defs import Facing, Vertical, Push, Vel, Ability

"""
Very stupid class only exists to evade a circular import
"""
class InteractionCheck:
    mva : Mover = None
    mvb : Mover = None
    result : OverlapResult = None



class PushingMover(Mover):

    movers = []
    count = 0
    ability = Ability.PUSHING.value

    def initPushing(self):
        self.xvel = 0.0
        self.push_state = Push.NUDGE

    def haltPushing(self):
        self.pvel = 0
        self.push_state = Push.NOPUSH

    def initSkid(self):
        self.xvel = 0
        self.push_state = Push.SKID

    def continueSkid(self, xvel, direction):
        self.xvel = xvel
        self.direction = direction

    def nudge_continue(self):
        if not self.pvel:
            self.xvel = 1
            self.pvel += 1

        if self.pvel >= 1 and self.pvel <= 3:
            self.xvel += Vel.SHOVE.value
            if self.xvel >= 1:
                self.xvel = Vel.SHOVE.value
                self.pvel += 1
        else:
            self.push_state = Push.NOPUSH




    def __init__(self, anim_init, id, placeholder):
        super().__init__(anim_init, id, placeholder)