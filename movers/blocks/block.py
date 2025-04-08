from movers.interactive_mover import InteractiveMover
from system.defs import Status, Push, Events

class Block(InteractiveMover):
    pforce = 2
    mass = 2
    movers = []
    friction = 0
    psteps = 0
    pushByHand = False

    def __str__(self):
        return super().__str__() + f"psteps: {self.psteps}, pvel: {self.pvel}"

    def add_push_steps(self):
        if self.push_state == Push.NUDGE \
                and self.move_state >= Status.NEUTRAL:
            if self.xloc != self.oldXloc:
                self.psteps += 1

    def halt_skidding(self):
        if self.push_state == Push.SKID:
            if self.xvel <= 0.0:
                self.push_state = Push.STILL
                self.xvel = 0.0
                self.xaccl = 0.0
                print("halt skidding")

    def procInteractionEvents(self):
        if Events.HALT_PUSHING in self.interaction_events:
            self.xvel = 0.0
            self.xaccl = 0.0
            self.psteps = 0
            self.pushByHand = False
            print("Halt")

        elif Events.CONTINUE_PUSHING in self.interaction_events:
            pass
            #self.xvel += self.xaccl
            #if self.xvel >= self.MAX_XVEL_PUSH:
            #    self.xvel = self.MAX_XVEL_PUSH

        elif Events.PUSH_TO_SKID in self.interaction_events:
            self.psteps = 0
            if self.move_state != Status.DASH:
            #if True:
                self.push_state = Push.SKID
                self.xaccl = -0.05
                self.xvel = 1.75
                self.move_state = Status.WALK
                self.pushByHand = False
                print("UGH")

        if Events.MOVER_RECOIL in self.interaction_events:
            self.xvel = self.MAX_XVEL_DASH
            self.max_xvel = self.MAX_XVEL_DASH
            self.xaccl = 0.05
            self.direction *= -1
            
        if Events.MOVER_LEAVE_COIL in self.interaction_events:
            self.xaccl = -0.05

        self.interaction_events.clear()

    def procEvents(self):
        self.events.clear()

    def initPushing(self, direction, friction, xaccl, xvel=0, pushByHand = False):
        self.xaccl = xaccl
        self.xvel = xvel * friction
        self.direction = direction
        self.pushByHand = pushByHand
        if xaccl >= 0:
            self.max_xvel = self.MAX_XVEL_PUSH
        else:
            self.max_xvel = self.MAX_XVEL_DASH
        print("PUSHING")

    def go(self):
        super().go()

    def before_move(self):
        super().before_move()
        self.halt_skidding()
        #self.add_push_steps()

    def move(self):
        super().move()
