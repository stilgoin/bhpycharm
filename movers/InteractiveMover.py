from movers.movers import Mover
from system.defs import Ability, Push, Vel, Facing, Status, Events


class InteractiveMover(Mover):

    movers = []
    springs = []

    hitoffs = (0, 0, 15, 15)
    snap_xloc = 0.0
    push_xloc = 0.0
    pvel = 0.0
    ability = Ability.ITEM.value
    dash_xvel = 0.0

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
            #if self.xvel <= 0:
            #    snapTo8 = True

            if self.xvel <= 0.5:
                if self.xvel <= 0.5:
                    self.xvel = 0.5
                #self.xaccl += (2 ** -8)
                if self.xaccl > 0:
                    self.xaccl = 0
                if int(self.xloc) == self.snap_xloc:
                    snapTo8 = True

            #if self.xvel > 0.5:
            if not snapTo8:
                if self.direction == Facing.LEFT \
                    and self.xloc < self.snap_xloc:
                    self.snap_xloc -= 8
                    if int(self.snap_xloc) & 0x7:
                        self.snap_xloc &= 0xFFF8
                if self.direction == Facing.RIGHT \
                    and self.xloc > self.snap_xloc:
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

    def clamp_pvel(self):
        if self.push_state in (Push.STILL, Push.SKID) \
                or self.move_state == Status.DASH:
            return

        if self.xvel >= self.max_pvel:
            self.xvel = self.max_pvel

    def procInteractionEvents(self):

        if Events.HALT_PUSHING in self.interaction_events:
            self.push_state = Push.STILL

        if Events.MOVER_LEAVE_COIL in self.interaction_events:
            self.push_state = Push.STILL

        if Events.MOVER_RECOIL in self.interaction_events:
            self.xvel = self.dash_xvel
            self.xaccl = 0.05
            self.direction *= -1
            self.facing *= -1
            self.move_state = Status.DASH

        self.interaction_events.clear()

    def initPushing(self, direction, friction, xaccl, move_state, xvel=0):
        self.xvel *= friction
        self.xaccl = xaccl
        if xvel > 0:
            self.xvel = xvel
        self.move_state = move_state
        self.direction = direction
        self.push_state = Push.NUDGE


    def go(self):
        self.lambdas.append(lambda : self.clamp_pvel())
        super().go()

    def test(self):
        #self.push_state = Push.SKID
        #self.xvel = 2.5
        self.direction = Facing.LEFT
        self.snap_xloc = self.xloc - 8
        #self.xaccl = -0.05

    def __init__(self, anim_init, id, placeholder):
        super().__init__(anim_init, id, placeholder)