import math
from collections import defaultdict

from game.handlers import rollbackYUp, rollbackXLeft, rollbackXRight
from game.overlap import OverlapResult, moverToMover, Result
from movers.interactive_mover import InteractiveMover
from movers.movers import Mover
from system.defs import Push, Vertical, Facing, Id, Status, Events, Jump


class InteractionListener:

    listeners = {}
    result = None
    expired = False
    direction = 0

    def __init__(self, mva, mvb, result):
        self.mva = mva
        self.mvb = mvb
        self.result = result

    def __str__(self):
        return "interaction: " + str(self.mva) + " " + str(self.mvb)

    def processMoverToCoil(self):
        
        ma : Mover = self.mva
        mb : Mover = self.mvb
        
        if not ma.xaccl and mb.xvel < mb.dash_xvel:
            ma.interaction_events.append(Events.MOVER_RECOIL)
            mb.interaction_events.append(Events.MOVER_RECOIL)
        elif ma.hb.y0 > mb.hb.y1 \
            or ma.hb.y1 < mb.hb.y0:
            ma.interaction_events.append(Events.HALT_PUSHING)
            mb.interaction_events.append(Events.MOVER_RECOIL)
            self.expired = True
        else:
            if int(mb.xloc) != mb.default_xloc:
                InteractionListener.check_sides(self.result)
            else:
                if ma.xvel >= mb.MAX_XVEL_PUSH:
                    ma.interaction_events.append(Events.MOVER_LEAVE_COIL)
                    self.expired = True
                    mb.xaccl = 0
                    mb.xvel = 0
                    return
            self.processMoverToBlock()

    def processMoverToBlock(self):

        ma : Mover = self.mva
        mb : Mover = self.mvb

        if not ma.xaccl \
                or ma.direction != mb.direction \
                or ma.hb.y0 > mb.hb.y1 \
                or ma.hb.y1 < mb.hb.y0:
            ma.interaction_events.append(Events.HALT_PUSHING)
            mb.interaction_events.append(Events.HALT_PUSHING)
            self.expired = True
            return

        if mb.xvel != ma.xvel:
            InteractionListener.check_sides(self.result)

        InteractionListener.check_sides(self.result)
        ma.interaction_events.append(Events.CONTINUE_PUSHING)
        mb.interaction_events.append(Events.CONTINUE_PUSHING)

    interactions = defaultdict(lambda : InteractionListener.processMoverToBlock,
                               {Id.SIDECOIL.value : processMoverToCoil})

    @classmethod
    def evalInteractions(cls):
        out = ""
        for listener in cls.listeners.values():
            key = listener.mvb.id
            interaction = cls.interactions[key]
            interaction(listener)
            out += str(listener) + "\n"

        # delete dict entry without exception
        cls.listeners = dict(filter(lambda x: not x[1].expired, cls.listeners.items()))
        return out

    @classmethod
    def initInteraction(self, ma : InteractiveMover, mb : InteractiveMover,
                        result : OverlapResult ):
        uuida = ma.auuid
        uuidb = mb.auuid
        if (uuida, uuidb) in InteractionListener.listeners.keys():
            return

        if not ma.xvel and not mb.xvel:
            return

        InteractionListener.listeners[(uuida, uuidb)] = \
            InteractionListener(result.mva, result.mvb, result)

        if mb.xvel >= ma.MAX_XVEL_WALK:
            direction = mb.direction
            xaccl = mb.base_xaccl / 8.0
            friction = ma.friction
            xvel = mb.xvel
        else:
            direction = ma.direction
            if ma.xaccl >= 0:
                friction = mb.friction
                xaccl = ma.base_xaccl / 8.0
            else:
                friction = 1
                xaccl = ma.xaccl    
            xvel = ma.xvel

        ma.initPushing(direction, friction, xaccl, xvel)
        mb.initPushing(direction, friction, xaccl, xvel, pushByHand = True)

    @classmethod
    def check_sides(cls, result: OverlapResult):

        if result.result == Result.CONTACT:
            if result.facing == Facing.RIGHT:
                pass
                rollbackXLeft(result.mva, result.mvb.hb)
                print("ROLLBACK LEFT 198", str(result.mva), str(result.mvb))
            if result.facing == Facing.LEFT:
                pass
                rollbackXRight(result.mva, result.mvb.hb)
                print("ROLLBACK RIGHT 200", str(result.mva), str(result.mvb))
        elif result.result == Result.OVERLAP:
            if result.side == Facing.RIGHT:
                rollbackXLeft(result.mva, result.mvb.hb)
                print("ROLLBACK LEFT 205", str(result.mva), str(result.mvb))
            elif result.side == Facing.LEFT:
                rollbackXRight(result.mva, result.mvb.hb)
                print("ROLLBACK RIGHT 207", str(result.mva), str(result.mvb))
            else:
                if result.vert == Vertical.DOWN:
                    return

                if result.mva.xloc > result.mvb.xloc:
                    rollbackXRight(result.mva, result.mvb.hb)
                    print("ROLLBACK LEFT 218", str(result.mva), str(result.mvb))
                else:
                    rollbackXLeft(result.mva, result.mvb.hb)
                    print("ROLLBACK RIGHT 218", str(result.mva), str(result.mvb))

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

            if (uuida == uuidb):
                continue

            if (uuida, uuidb) in InteractionListener.listeners.keys():
                listener = InteractionListener.listeners[(uuida, uuidb)]
                #print("check sides in listener", ma, mb.id)
                #self.check_sides(listener.result)
                continue

            result : OverlapResult = moverToMover(ma, mb)

            floor_found = floor_found or \
                          InteractionListener \
                              .findInteraction(ma, mb, result)

        return floor_found, result

