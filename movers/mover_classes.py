from movers.movers import Mover
from game.Handlers import *
from game.Overlap import moverToMover, OverlapResult, Result
from system.defs import Vertical, Facing, Push, Id

from collections import defaultdict

class InteractionListener:

    listeners = {}
    expired = False

    def __init__(self, mva, mvb):
        self.mva = mva
        self.mvb = mvb

    def pushingMoverToBlock(self):
        mva : PushingMover = self.mva
        mvb : InteractiveMover = self.mvb
        result: OverlapResult = moverToMover(mva, mvb)
        if result.result == Result.NULL \
                or mva.xvel == 0:
            mvb.lambdas.append(lambda : mvb.nudge_release())
            self.expired = True
        else:
            mvb.lambdas.append(lambda : mvb.nudge_continue())

            """
            if result.result == Result.CONTACT:
                if result.facing == Facing.RIGHT:
                    mva.lambdas.append(lambda : rollbackXLeft(mva, mvb.hb))
                if result.facing == Facing.LEFT:
                    mva.lambdas.append(lambda : rollbackXRight(mva, mvb.hb))
            if result.result == Result.OVERLAP:
                if result.side == Facing.RIGHT:
                    mva.lambdas.append(lambda : rollbackXLeft(mva, mvb.hb))
                if result.side == Facing.LEFT:
                    mva.lambdas.append(lambda : rollbackXRight(mva, mvb.hb))
            """



    handlers = {(Id.PLAYER.value, Id.BLOCK.value) : pushingMoverToBlock}

    def processInteraction(self):
        ida = self.mva.id
        idb = self.mvb.id
        if (ida, idb) in self.handlers.keys():
            handler = self.handlers[(ida, idb)]
            handler(self)

    @classmethod
    def evalInteractions(cls):
        # delete dict entry without exception
        cls.listeners = dict(filter(lambda x : not x[1].expired, cls.listeners.items()))

        for key in cls.listeners.keys():
            listener = cls.listeners[key]
            listener.processInteraction()




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

    def init_nudge(self, facing):

        if self.push_state != Push.NOPUSH:
            return

        self.push_state = Push.NUDGE
        self.facing = facing
        self.push_xloc = self.xloc
        self.snap_xloc = self.xloc + (8 * self.facing)

    def nudge_continue(self):
        if not self.pvel:
            self.xvel = 1
            self.pvel += 1

        if self.pvel >= 1 and self.pvel <= 3:
            self.xvel += 0.175
            if self.xvel >= 1:
                self.xvel = 0
                self.pvel += 1

    def process_pushing(self):
        if self.push_state == Push.ROLLBACK:
            if self.facing == Facing.LEFT \
                and self.xloc <= self.push_xloc \
                or self.facing == Facing.RIGHT \
                and self.xloc >= self.push_xloc:

                self.xloc = self.push_xloc
                self.xvel = 0
                self.push_state = Push.NOPUSH



    def go(self, moverToBGFunc):
        #self.xvel = 0.5
        self.lambdas.append(lambda : self.process_pushing())
        return super().go(moverToBGFunc)

    def __init__(self, anim_init, id):
        super().__init__(anim_init, id)

class PushingMover(Mover):

    movers = []

    def initInteraction(self, interact_mover : InteractiveMover):
        uuida = self.auuid
        uuidb = interact_mover.auuid
        if (uuida, uuidb) not in InteractionListener.listeners.keys():
            InteractionListener.listeners[(uuida, uuidb)] =\
                InteractionListener(self, interact_mover)
            interact_mover.init_nudge(self.facing)


    def findInteraction(self, interact_mover : InteractiveMover,
                        result : OverlapResult) -> bool:
        floor_found = False
        if result.result == Result.CONTACT \
            and result.standing == Vertical.DOWN \
            or result.result == Result.OVERLAP \
            and result.vert == Vertical.DOWN:

            rollbackYUp(self, interact_mover.hb)
            floor_found = True

        if result.result == Result.CONTACT:
            if result.facing == Facing.RIGHT:
                rollbackXLeft(self, interact_mover.hb)
            if result.facing == Facing.LEFT:
                rollbackXRight(self, interact_mover.hb)
        if result.result == Result.OVERLAP:
            if result.side == Facing.RIGHT:
                rollbackXLeft(self, interact_mover.hb)
            if result.side == Facing.LEFT:
                rollbackXRight(self, interact_mover.hb)

        if result.result == Result.CONTACT \
            and result.facing == 0 \
            or result.result == Result.OVERLAP \
            and result.side != 0:
            pass
            self.initInteraction(interact_mover)



        return floor_found


    def moverToMovers(self) -> tuple[bool, OverlapResult]:
        floor_found = False
        result = OverlapResult()
        for interact_mover in InteractiveMover.movers:
            result : OverlapResult = moverToMover(self, interact_mover)
            floor_found = floor_found or \
                          self.findInteraction(interact_mover, result)

        return floor_found, result


    def __init__(self, anim_init, id):
        super().__init__(anim_init, id)



