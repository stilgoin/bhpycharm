from movers.movers import Mover
from system.defs import Ability, Push, Vel, Facing, Status, Events, Id


class InteractiveMover(Mover):

    any_blocks = []
    springs = []

    hitoffs = (0, 0, 15, 15)
    snap_xloc = 0.0
    push_xloc = 0.0
    pcounter = 0
    pcounterAction = 0
    dash_xvel = 2.5
    push_xvel = 0.0
    onFallPlat = False
    default_xloc = 0.0

    def dummy(self):
        pass

    def modify_interaction(self):
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
        if self.push_state in (Push.STILL, Push.SKID):
            return

        if self.xvel >= self.max_pvel:
            self.xvel = self.max_pvel
            print(f"{self.id}, {self.max_pvel}")
            
    def procInteractionEvents(self):

        if Events.CONTINUE_PUSHING in self.interaction_events:
            pass
            #self.pcounter += 1
            #if self.pcounter == self.pcounterAction:
            #    self.xvel = self.push_xvel
            """
            if not self.pcounter % 60:
                self.xvel = 0.01
                self.xaccl = 0.01
            else:
                self.xaccl = self.base_xaccl
            self.pcounter -= 1
            if self.pcounter <= 0:
                self.pcounter = 0
            print(self.pcounter)
            """


        if Events.HALT_PUSHING in self.interaction_events:
            if self.xvel < self.MAX_XVEL_WALK:
                self.max_xvel = self.MAX_XVEL_WALK
                self.xaccl = self.base_xaccl
            else:
                self.xaccl = -0.05
                print("UGH")

        if Events.MOVER_LEAVE_COIL in self.interaction_events:
            pass

        if Events.MOVER_RECOIL in self.interaction_events:
            self.xvel = self.MAX_XVEL_DASH
            self.max_xvel = self.MAX_XVEL_DASH
            self.xaccl = 0.05
            self.direction *= -1
            self.facing *= -1
            
        if Events.MOVER_LEAVE_COIL in self.interaction_events:
            self.xaccl = -0.05

        self.interaction_events.clear()

    def initPushing(self, direction, friction, xaccl, xvel=0):
        self.xaccl = xaccl
        self.xvel = xvel * friction
        self.push_xvel = xvel * friction
        self.direction = direction
        #self.max_xvel = self.MAX_XVEL_PUSH
        if not friction:
            self.max_xvel = self.MAX_XVEL_PUSH
        else:
            self.max_xvel = self.MAX_XVEL_DASH
        self.pcounter = 0


    def go(self):
        super().go()

    def move(self):
        super().move()

    def test(self):
        #self.push_state = Push.SKID
        #self.xvel = 2.5
        self.direction = Facing.LEFT
        self.snap_xloc = self.xloc - 8
        #self.xaccl = -0.05

    def __init__(self, anim_init, id, placeholder, facing = Facing.LEFT):
        super().__init__(anim_init, id, placeholder)
        self.facing = facing

    def __setattr__(self, key, value):
        if key == "xaccl" and self.id == Id.RAMP.value:
            #print("xvel", value)
            pass
        self.__dict__[key] = value
