from collections import defaultdict

from game.Handlers import rollbackYUp, rollbackXLeft, rollbackXRight
from game.Overlap import OverlapResult, moverToMover, Result
from movers.movers import Mover
from system.defs import Push, Vertical, Facing, Id, Status


class InteractionListener:

    listeners = {}
    result = None
    expired = False
    direction = 0

    def __init__(self, mva, mvb, result):
        self.mva = mva
        self.mvb = mvb
        self.result = result

    def processMoverToCoil(self):
        ma: Mover = self.mva
        mb: Mover = self.mvb

        if ma.hb.y0 > mb.hb.y1 \
           or ma.hb.y1 < mb.hb.y0:
            ma.push_state = Push.STILL
            mb.move_state = Push.ROLLBACK
            mb.xvel = mb.psteps / 16.0
            mb.direction = mb.direction * -1
            mb.psteps = 0
            self.expired = True
            return

        if ma.push_state == Push.STILL \
                and mb.push_state == Push.NUDGE:
            mb.push_state = Push.ROLLBACK
            mb.xaccl = 0.05
            mb.xvel = mb.psteps / 16.0
            mb.direction = mb.direction * -1
            return

        if mb.push_state == Push.ROLLBACK:
            if ma.direction == mb.direction:
                pass

        if mb.push_state == Push.STILL \
                and mb.psteps > 0:
            ma.xvel = mb.xvel
            ma.xaccl = 0.05
            ma.direction *= -1
            ma.facing *= -1
            ma.move_state = Status.DASH
            mb.xvel = 0.0
            mb.xaccl = 0.0
            mb.psteps = 0
            self.expired = True




    def processMoverToBlock(self):

        ma : Mover = self.mva
        mb : Mover = self.mvb

        mb.move_state = ma.move_state

        if ma.move_state >= Status.NEUTRAL:
            if ma.push_state == Push.STILL \
                and mb.push_state != Push.STILL \
                or mb.push_state == Push.STILL \
                and ma.push_state != Push.STILL \
                or ma.hb.y0 > mb.hb.y1 \
                or ma.hb.y1 < mb.hb.y0:
                ma.push_state = Push.STILL
                mb.push_state = Push.STILL
                self.expired = True
                mb.psteps = 0
                if not ma.move_state:
                    ma.xvel = 0.0
                    ma.xaccl = 0.0

                mb.xvel = 0.0
                mb.xaccl = 0.0
                mb.move_state = Status.WALK
                return

        if ma.xvel >= ma.max_pvel \
            or mb.xvel >= mb.max_pvel:
            if mb.psteps >= 40:
                if ma.mass > mb.mass:
                    mskid = ma
                    mhalt = mb
                else:
                    mskid = mb
                    mhalt = ma

                mskid.push_state = Push.SKID
                mskid.xaccl = -0.05
                mskid.xvel = 1.75
                mskid.psteps = 0
                mskid.move_state = Status.WALK
                mhalt.push_state = Push.STILL
                #mhalt.push_state = Push.REST
                #mhalt.action_timer = 5
                self.expired = True

    interactions = defaultdict(lambda : InteractionListener.processMoverToBlock,
                               {Id.SIDECOIL.value : processMoverToCoil})

    @classmethod
    def evalInteractions(cls):
        for listener in cls.listeners.values():
            key = listener.mvb.id
            interaction = cls.interactions[key]
            interaction(listener)

        #for key in cls.listeners.keys():
            #listener = cls.listeners[key]
            #listener.processInteraction()

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

        if not ma.xaccl and not mb.xaccl:
            return

        if ma.facing == Facing.RIGHT:
            if ma.xloc > mb.xloc:
                if ma.facing != ma.direction:
                    if ma.xvel < 0.5 \
                        or ma.move_state == Status.DASH:
                        ma.xvel = 0.0
                        ma.xaccl = 0.0
                        return

        if ma.facing == Facing.LEFT:
            if ma.xloc < mb.xloc:
                if ma.facing != ma.direction:
                    if ma.xvel < 0.5 \
                        or ma.move_state == Status.DASH:
                        ma.xvel = 0.0
                        ma.xaccl = 0.0
                        return

        """This check is to prevent pushing a block again immediately after launching it
        (And still be able to reach the skidding block and resume pushing it)
            It sucks but whaddya gonna do.
        """
        if Push.SKID == ma.push_state and ma.xvel >= 0.5:
            if ma.hb.x0 >= mb.hb.x1 \
                and ma.direction == Facing.RIGHT \
                or ma.hb.x1 <= mb.hb.x0 \
                and ma.direction == Facing.LEFT:
                pass
                return

        if Push.SKID == mb.push_state and mb.xvel >= 0.5:
            if mb.hb.x0 >= ma.hb.x1 \
                and mb.direction == Facing.RIGHT \
                or mb.hb.x1 <= ma.hb.x0 \
                and mb.direction == Facing.LEFT:
                pass
                return

        #print(result,'\n--------\n')

        InteractionListener.listeners[(uuida, uuidb)] =\
            InteractionListener(result.mva, result.mvb, result)

        ma.push_state = Push.NUDGE
        mb.push_state = Push.NUDGE

        if mb.xvel > 0:
            mb.psteps = 20

        xaccl = 0.0
        if ma.xvel >= mb.xvel:
            mb.direction = ma.direction
            xaccl = ma.base_xaccl / 2.0
        else:
            ma.direction = mb.direction
            xaccl = mb.base_xaccl / 2.0

        if ma.move_state >= Status.NEUTRAL:
            ma.xvel *= mb.friction
            mb.xvel *= ma.friction
            ma.xaccl = xaccl
            mb.xaccl = xaccl
        else:
            mb.xvel = ma.xvel
            mb.xaccl = ma.xaccl
        mb.move_state = ma.move_state








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

                if result.vert == Vertical.DOWN:
                    return

                if result.mva.xloc > result.mva.xloc:
                    rollbackXLeft(result.mva, result.mvb.hb)
                else:
                    rollbackXRight(result.mva, result.mvb.hb)
                pass
                """
                if result.mvb.direction == Facing.RIGHT:
                    rollbackXLeft(result.mva, result.mvb.hb)
                if result.mvb.direction == Facing.LEFT:
                    rollbackXRight(result.mva, result.mvb.hb)
                """
                """
                if result.mva.direction != result.mva.facing \
                        and result.mva.facing == Facing.LEFT:
                    rollbackXRight(result.mva, result.mvb.hb)
                if result.mva.direction != result.mva.facing \
                        and result.mva.facing == Facing.RIGHT:
                    rollbackXLeft(result.mva, result.mvb.hb)
                """

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

            uuida = ma.auuid
            uuidb = mb.auuid
            if (uuida, uuidb) in InteractionListener.listeners.keys():
                listener = InteractionListener.listeners[(uuida, uuidb)]
                self.check_sides(listener.result)
                continue

            result : OverlapResult = moverToMover(ma, mb)

            floor_found = floor_found or \
                          InteractionListener \
                              .findInteraction(ma, mb, result)

        return floor_found, result

