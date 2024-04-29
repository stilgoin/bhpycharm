from movers.InteractiveMover import InteractiveMover
from system.defs import Status, Push, Events

class Block(InteractiveMover):
    pforce = 2
    mass = 2
    movers = []
    friction = 0
    psteps = 0
    pushByHand = False

    def __str__(self):
        return super().__str__() + f"psteps: {self.psteps}"

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
            self.push_state = Push.STILL
            if self.move_state != Status.DASH:
                self.xvel = 0.0
                self.xaccl = 0.0
                self.move_state = Status.NEUTRAL
                self.psteps = 0
                self.pushByHand = False
            print("Halt")

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
            self.xvel = self.dash_xvel
            self.xaccl = 0.05
            self.direction *= -1
            self.facing *= -1
            self.move_state = Status.DASH

        self.interaction_events.clear()

    def procEvents(self):
        self.events.clear()

    def initPushing(self, direction, friction, xaccl, move_state, xvel=0, pushByHand = False):
        self.xvel *= friction
        self.xaccl = xaccl
        if xvel > 0:
            self.xvel = xvel
        if self.move_state == Status.NEUTRAL:
            self.move_state = move_state
        self.direction = direction
        self.push_state = Push.NUDGE
        self.pushByHand = pushByHand
        print("PUSHING")

    def go(self):
        self.lambdas.append(lambda : self.halt_skidding())
        self.lambdas.append(lambda : self.add_push_steps())
        super().go()