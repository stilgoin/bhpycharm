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
    onFallPlat = False

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

    def clamp_pvel(self):
        if self.push_state in (Push.STILL, Push.SKID) \
                or self.move_state == Status.DASH:
            return

        if self.xvel >= self.max_pvel:
            self.xvel = self.max_pvel
            print(f"{self.id}, {self.max_pvel}")
            
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

    def initPushing(self, direction, friction, xaccl, xvel=0, pushByHand = False):
        self.xaccl = xaccl
        self.xvel = xvel * friction
        self.direction = direction


    def go(self):
        super().go()

    def before_move(self):
        self.clamp_pvel()

    def move(self):
        super().move()

    def test(self):
        #self.push_state = Push.SKID
        #self.xvel = 2.5
        self.direction = Facing.LEFT
        self.snap_xloc = self.xloc - 8
        #self.xaccl = -0.05

    def __init__(self, anim_init, id, placeholder):
        super().__init__(anim_init, id, placeholder)
