from math import floor, ceil

from game.Maps import Hitbox
from movers.movers import Mover
from game.Handlers import *
from game.Overlap import moverToMover, OverlapResult, Result
from system.defs import Vertical, Facing, Push, Id, Anim, Jump, Vel, Ability

from collections import defaultdict

class MiscMover(Mover):
    movers = []

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

        if result.result == Result.NULL \
                or self.direction != mva.direction:
            self.expired = True

    def initBlockToMover(self):
        self.mvb.initSkid()

    def blockToMover(self):
        mva : InteractiveMover = self.mva
        mvb : PushingMover = self.mvb
        result: OverlapResult = moverToMover(mva, mvb)

        if result.result == Result.NULL:
            self.expired = True
        else:
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

    def processInteraction(self):
        ida = self.mva.ability
        idb = self.mvb.ability
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
    ability = Ability.ITEM.value

    def dummy(self):
        pass

    def nudge_release(self):

        if self.push_state != Push.NUDGE:
            return

        self.xvel = 1.0
        #self.xaccl = -0.175

        if abs(self.push_xloc - self.xloc) <= 4:
            self.push_state = Push.ROLLBACK
            self.direction *= -1
        elif abs(self.push_xloc - self.xloc) > 4:
            self.push_state = Push.STEP

    def snapToX8(self, val):
        pass

    def initNudge(self, direction):

        if self.push_state != Push.NOPUSH:
            return

        self.push_state = Push.NUDGE
        self.direction = direction
        self.push_xloc = self.xloc
        self.snap_xloc = self.xloc + (8 * self.direction)
        pass

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
            self.push_state = Push.SKID
            self.xvel = 1.75
            self.xaccl = -0.05

    def process_pushing(self):

        snapTo8 = False

        if self.push_state == Push.SKID:
            if self.xvel <= 0:
                snapTo8 = True

            if self.xvel > 0.5:
                if self.direction == Facing.RIGHT:
                    if self.xloc > self.snap_xloc + 8:
                        self.snap_xloc += 8
                else:
                    if self.xloc < self.snap_xloc - 8:
                        self.snap_xloc -= 8

            if self.xvel <= 0.5:
                self.xaccl += (2 ** -8)
                if self.xaccl > 0:
                    self.xaccl = 0
                if self.direction == Facing.LEFT \
                    and self.xloc <= self.snap_xloc - 8:
                    snapTo8 = True
                    self.snap_xloc -= 8
                    if int(self.snap_xloc) & 0x7:
                        self.snap_xloc &= 0xFFF8
                if self.direction == Facing.RIGHT \
                    and self.xloc >= self.snap_xloc + 8:
                    snapTo8 = True
                    self.snap_xloc += 8
                    if int(self.snap_xloc) & 0x7:
                        self.snap_xloc &= 0xFFF8

            if snapTo8:
                self.xloc = self.snap_xloc
                self.push_state = Push.NOPUSH
                self.xvel = 0
                self.pvel = 0
                self.xaccl = 0
                self.snap_xloc = 0

        # halt pushing
        if self.push_state == Push.ROLLBACK \
            or self.push_state == Push.STEP:

            check_val = self.snap_xloc
            if self.push_state == Push.ROLLBACK:
                check_val = self.push_xloc

            if self.direction == Facing.LEFT \
                and self.xloc <= check_val \
                or self.direction == Facing.RIGHT \
                and self.xloc >= check_val:

                self.xloc = check_val
                self.xvel = 0
                self.push_state = Push.NOPUSH
                self.pvel = 0

    def go(self):
        self.lambdas.append(lambda : self.process_pushing())
        super().go()

    def __init__(self, anim_init, id, placeholder):
        self.push_state = Push.SKID
        self.xvel = 1.0
        self.direction = Facing.LEFT
        super().__init__(anim_init, id, placeholder)

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

    def initInteraction(self, interact_mover : InteractiveMover,
                        result : OverlapResult ):
        uuida = self.auuid
        uuidb = interact_mover.auuid
        if (uuida, uuidb) not in InteractionListener.listeners.keys():
            InteractionListener.listeners[(uuida, uuidb)] =\
                InteractionListener(result.mva, result.mvb)
            #interact_mover.initNudge(self.facing)
            #self.initPushing()


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
                pass
                #rollbackXLeft(self, interact_mover.hb)
            if result.facing == Facing.LEFT:
                pass
                #rollbackXRight(self, interact_mover.hb)
            PushingMover.count += 1
        elif result.result == Result.OVERLAP:
            if result.side == Facing.RIGHT:
                rollbackXLeft(result.mva, result.mvb.hb)
            if result.side == Facing.LEFT:
                rollbackXRight(result.mva, result.mvb.hb)
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

        if self.direction == Facing.RIGHT \
            and self.hb.x0 >= interact_mover.hb.x1 \
            or self.direction == Facing.LEFT \
            and self.hb.x1 <= interact_mover.hb.x0:
            return


        if result.result == Result.CONTACT \
            and result.facing != 0 \
            or result.result == Result.OVERLAP \
            and result.side != 0:
            pass
            self.initInteraction(interact_mover, result)

        return floor_found


    def moverToMovers(self) -> tuple[bool, OverlapResult]:
        floor_found = False
        result = OverlapResult()
        for interact_mover in InteractiveMover.movers:
            uuida = self.auuid
            uuidb = interact_mover.auuid
            if (uuida, uuidb) in InteractionListener.listeners.keys():
                continue

            if self.xvel > interact_mover.xvel \
                    or interact_mover.push_state < Push.SKID:
                result : OverlapResult = moverToMover(self, interact_mover)
                result.mva = self
                result.mvb = interact_mover
            else:
                result : OverlapResult = moverToMover(interact_mover, self)
                result.mva = interact_mover
                result.mvb = self

            floor_found = floor_found or \
                          self.findInteraction(interact_mover, result)

        return floor_found, result


    def __init__(self, anim_init, id, placeholder):
        super().__init__(anim_init, id, placeholder)

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



