from game.Handlers import rollbackYUp, rollbackXLeft, rollbackXRight
from game.Overlap import OverlapResult, moverToMover, Result
from movers.InteractiveMover import InteractiveMover
from movers.PushingMover import PushingMover
from system.defs import Push, Ability, Vertical, Facing, Status


class InteractionListener:

    listeners = {}
    expired = False
    direction = 0

    def __init__(self, mva, mvb):
        self.mva = mva
        self.mvb = mvb
        self.direction = mva.direction

        ida = self.mva.ability
        idb = self.mvb.ability
        if (ida, idb) in self.init_table.keys():
            init = self.init_table[(ida, idb)]
            init(self)

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

        if self.expired:
            return

        ida = self.mva.ability
        idb = self.mvb.ability
        if (ida, idb) in self.handlers.keys():
            handler = self.handlers[(ida, idb)]
            handler(self)

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
            listener.checkTerm()

        # delete dict entry without exception
        cls.listeners = dict(filter(lambda x: not x[1].expired, cls.listeners.items()))

    @classmethod
    def initInteraction(self, pushing_mover : PushingMover, interact_mover : InteractiveMover,
                        result : OverlapResult ):
        uuida = pushing_mover.auuid
        uuidb = interact_mover.auuid
        if (uuida, uuidb) not in InteractionListener.listeners.keys():
            pass
            InteractionListener.listeners[(uuida, uuidb)] =\
                InteractionListener(result.mva, result.mvb)

    @classmethod
    def check_sides(cls, result: OverlapResult):
        if result.result == Result.CONTACT:
            if result.facing == Facing.RIGHT:
                pass
                rollbackXLeft(result.mva, result.mvb.hb)
            if result.facing == Facing.LEFT:
                pass
                rollbackXRight(result.mva, result.mvb.hb)
            PushingMover.count += 1
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
            PushingMover.count += 1
        else:
            if PushingMover.count > 0:
                """
                print("\nno hit found: ", str(self.xloc), " ", interact_mover.xloc, "\n",
                      interact_mover.push_state, "\n",
                      interact_mover.xvel, "\n",
                      interact_mover.facing, "\n",
                      interact_mover.oldXloc, "\n",
                      self.hb, "\n", self.phb, "\n",
                      interact_mover.hb, "\n", interact_mover.phb, "\n",
                      str(result))
                """
                PushingMover.count = 0

    @classmethod
    def findInteraction(self, pushing_mover : PushingMover, interact_mover : InteractiveMover,
                        result : OverlapResult) -> bool:
        floor_found = False
        if result.result == Result.CONTACT \
            and result.standing == Vertical.DOWN \
            or result.result == Result.OVERLAP \
            and result.vert == Vertical.DOWN:

            rollbackYUp(pushing_mover, interact_mover.hb)
            floor_found = True

        self.check_sides(result)

        if result.result == Result.CONTACT \
            and result.facing != 0 \
            or result.result == Result.OVERLAP \
            and result.side != 0:
            pass
            InteractionListener\
                .initInteraction(pushing_mover, interact_mover, result)

        return floor_found


    @classmethod
    def moverToMovers(self, pushing_mover : PushingMover) -> tuple[bool, OverlapResult]:

        floor_found = False
        result = OverlapResult()
        for interact_mover in InteractiveMover.movers:
            uuida = pushing_mover.auuid
            uuidb = interact_mover.auuid
            if (uuida, uuidb) in InteractionListener.listeners.keys()\
                    or uuida == uuidb:
                continue

            if pushing_mover.xvel > interact_mover.xvel \
                    or interact_mover.push_state < Push.SKID:
                result : OverlapResult = moverToMover(pushing_mover, interact_mover)
                result.mva = pushing_mover
                result.mvb = interact_mover

            else:
                result : OverlapResult = moverToMover(interact_mover, pushing_mover)
                result.mva = interact_mover
                result.mvb = pushing_mover

            floor_found = floor_found or \
                          InteractionListener\
                              .findInteraction(pushing_mover, interact_mover, result)

        return floor_found, result







