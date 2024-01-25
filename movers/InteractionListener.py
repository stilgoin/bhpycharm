from game.Handlers import rollbackYUp, rollbackXLeft, rollbackXRight
from game.Overlap import OverlapResult, moverToMover, Result
from movers.InteractiveMover import InteractiveMover
from movers.PushingMover import PushingMover
from movers.movers import Mover
from system.defs import Push, Ability, Vertical, Facing, Status


class InteractionListener:

    listeners = {}
    expired = False
    direction = 0

    def __init__(self, mva, mvb):
        self.mva = mva
        self.mvb = mvb
        """
        self.direction = mva.direction
        
        ida = self.mva.ability
        idb = self.mvb.ability
        if (ida, idb) in self.init_table.keys():
            init = self.init_table[(ida, idb)]
            init(self)
        """

    def initPushingMoverToBlock(self):

        if self.mva.xvel == 0 \
            or self.mvb.push_state not in (Push.NOPUSH, Push.SKID):
            self.expired = True
            return

        if self.mva.direction == Facing.RIGHT \
            and self.mva.hb.x0 >= self.mvb.hb.x1 \
            or self.mva.direction == Facing.LEFT \
            and self.mva.hb.x1 <= self.mvb.hb.x0:
            self.expired = True
            return

        self.mva.initPushing()
        self.mvb.initNudge(self.mva.direction)

    def pushingMoverToBlock(self):
        mva : PushingMover = self.mva
        mvb : InteractiveMover = self.mvb
        result: OverlapResult = moverToMover(mva, mvb)
        if result.result == Result.NULL \
                or mva.xvel == 0 and mva.push_state != Push.NUDGE \
                or mva.direction != self.direction:
            mvb.lambdas.append(lambda : mvb.nudge_release())
            mva.lambdas.append(lambda : mva.haltPushing())
        else:
            mva.pvel = mvb.pvel
            mvb.lambdas.append(lambda : mvb.nudge_continue())
            mva.lambdas.append(lambda : mva.nudge_continue())

        #print(mva.xloc, " ", mvb.xloc, " ", mva.hb.x0, " ", mvb.hb.x1, " ", mva.phb.x0, " ", mvb.phb.x1, " ", result.result)
        result.mva = self.mva
        result.mvb = self.mvb
        #self.check_sides(result)

        if result.result == Result.NULL \
                or self.direction != mva.direction:
            self.expired = True

    def initBlockToMover(self):
        self.mvb.initSkid()
        self.mvb.xaccl = self.mva.xaccl

    def blockToMover(self):
        mva : InteractiveMover = self.mva
        mvb : PushingMover = self.mvb
        result: OverlapResult = moverToMover(mva, mvb)

        if result.result == Result.NULL:
            self.expired = True
        else:
            if mvb.move_state == Status.WALK \
                and mvb.facing == mva.direction * -1:

                if mva.xvel != mvb.xvel:
                    pass
                else:
                    pass

                if mva.xvel > 0.5:
                    mva.xaccl += -0.01
                    mvb.xaccl += -0.01
            xvel = mva.xvel
            direction = mva.direction
            mvb.lambdas.append(lambda: mvb.continueSkid(xvel, direction))


    handlers = {(Ability.PUSHING.value, Ability.ITEM.value) : pushingMoverToBlock,
                (Ability.ITEM.value, Ability.PUSHING.value) : blockToMover,
    }

    init_table = {
        (Ability.PUSHING.value, Ability.ITEM.value) : initPushingMoverToBlock,
        (Ability.ITEM.value, Ability.PUSHING.value) : initBlockToMover
    }

    def termBlockToMover(self):
        mva = self.mva
        mvb = self.mvb
        if mva.push_state == Push.NOPUSH:
            mvb.xaccl = 0
            mvb.xvel = 0
            self.expired = True
            return

    def termMoverToBlock(self):
        pass

    term_table = {
        (Ability.PUSHING.value, Ability.ITEM.value): termMoverToBlock,
        (Ability.ITEM.value, Ability.PUSHING.value): termBlockToMover
    }

    def checkTerm(self):
        ida = self.mva.ability
        idb = self.mvb.ability
        if (ida, idb) in self.term_table.keys():
            term = self.term_table[(ida, idb)]
            term(self)

    def processInteraction(self):

        ma : Mover = self.mva
        mb : Mover = self.mvb

        if ma.push_state == Push.STILL \
            and mb.push_state != Push.STILL \
            or mb.push_state == Push.STILL \
            and ma.push_state != Push.STILL \
            or ma.hb.y0 > mb.hb.y1 \
            or ma.hb.y1 < mb.hb.y0:
            ma.push_state = Push.STILL
            mb.push_state = Push.STILL
            self.expired = True
            if not ma.move_state:
                ma.xvel = 0.0
                ma.xaccl = 0.0
            if not mb.move_state:
                mb.xvel = 0.0
                mb.xaccl = 0.0

        if ma.xvel >= ma.max_pvel \
            or mb.xvel >= mb.max_pvel:
            if ma.mass > mb.mass:
                mskid = ma
                mhalt = mb
            else:
                mskid = mb
                mhalt = ma

            mskid.push_state = Push.SKID
            mskid.xaccl = -0.05
            mskid.xvel = 1.75
            mhalt.push_state = Push.STILL
            self.expired = True



        """
        if self.expired:
            return

        ida = self.mva.ability
        idb = self.mvb.ability
        if (ida, idb) in self.handlers.keys():
            handler = self.handlers[(ida, idb)]
            handler(self)
        """

    @classmethod
    def evalInteractions(cls):
        for key in cls.listeners.keys():
            listener = cls.listeners[key]
            listener.processInteraction()

        # delete dict entry without exception
        cls.listeners = dict(filter(lambda x: not x[1].expired, cls.listeners.items()))

    @classmethod
    def evalTerminations(cls):
        for key in cls.listeners.keys():
            listener = cls.listeners[key]
            #listener.checkTerm()

        # delete dict entry without exception
        cls.listeners = dict(filter(lambda x: not x[1].expired, cls.listeners.items()))

    @classmethod
    def initInteraction(self, ma : Mover, mb : Mover,
                        result : OverlapResult ):
        uuida = ma.auuid
        uuidb = mb.auuid
        if (uuida, uuidb) in InteractionListener.listeners.keys():
            return

        if not ma.move_state and not mb.move_state:
            return

        print("Interaction init")

        InteractionListener.listeners[(uuida, uuidb)] =\
            InteractionListener(result.mva, result.mvb)

        ma.push_state = Push.NUDGE
        mb.push_state = Push.NUDGE

        xaccl = 0.0
        if ma.xvel >= mb.xvel:
            mb.direction = ma.direction
            xaccl = ma.base_xaccl / 2.0
        else:
            ma.direction = mb.direction
            xaccl = mb.base_xaccl / 2.0

        ma.xvel *= mb.friction
        mb.xvel *= ma.friction
        ma.xaccl = xaccl
        mb.xaccl = xaccl








    @classmethod
    def check_sides(cls, result: OverlapResult):
        if result.result == Result.CONTACT:
            if result.facing == Facing.RIGHT:
                pass
                rollbackXLeft(result.mva, result.mvb.hb)
            if result.facing == Facing.LEFT:
                pass
                rollbackXRight(result.mva, result.mvb.hb)
        elif result.result == Result.OVERLAP:
            if result.side == Facing.RIGHT:
                rollbackXLeft(result.mva, result.mvb.hb)
            elif result.side == Facing.LEFT:
                rollbackXRight(result.mva, result.mvb.hb)
            else:
                if result.mva.direction != result.mva.facing \
                        and result.mva.facing == Facing.LEFT:
                    rollbackXRight(result.mva, result.mvb.hb)
                if result.mva.direction != result.mva.facing \
                        and result.mva.facing == Facing.RIGHT:
                    rollbackXLeft(result.mva, result.mvb.hb)

    @classmethod
    def findInteraction(self, ma : Mover, mb : Mover,
                        result : OverlapResult) -> bool:
        floor_found = False
        if result.result == Result.CONTACT \
            and result.standing == Vertical.DOWN \
            or result.result == Result.OVERLAP \
            and result.vert == Vertical.DOWN:

            rollbackYUp(ma, mb.hb)
            floor_found = True

        self.check_sides(result)

        if result.result == Result.CONTACT \
            and result.facing != 0 \
            or result.result == Result.OVERLAP \
            and result.side != 0:
            pass
            InteractionListener\
                .initInteraction(ma, mb, result)

        return floor_found


    @classmethod
    def moverToMovers(self, ma : Mover,
                      movers : [Mover]) -> tuple[bool, OverlapResult]:

        floor_found = False
        result = OverlapResult()
        for mb in movers:
            result : OverlapResult = moverToMover(ma, mb)

        floor_found = floor_found or \
                      InteractionListener \
                          .findInteraction(ma, mb, result)

        return floor_found, result

