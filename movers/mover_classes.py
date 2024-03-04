from movers.InteractiveMover import InteractiveMover
from movers.movers import Mover
from system.defs import Id, Anim, Jump, Events, Status, Facing, Push


class MiscMover(Mover):
    movers = []
    postproc_movers = []


class Player(InteractiveMover):
    hitoffs = (4.0, 1.0, 12.0, 14.0)
    movers = []

    def procEvents(self):

        if Events.HOLD_RIGHT in self.events \
            or Events.HOLD_LEFT in self.events:
            if Events.MIN_XVEL in self.events \
                    and Events.PUSHING_COIL_RIGHT not in self.events \
                    and Events.PUSHING_COIL_LEFT not in self.events:
                self.xaccl = self.base_xaccl

                self.move_state = Status.WALK
                if Events.HOLD_LEFT in self.events:
                    self.holding = Facing.LEFT
                if Events.HOLD_RIGHT in self.events:
                    self.holding = Facing.RIGHT

                if self.holding != 0:
                    self.direction = self.holding
                    self.facing = self.holding
        else:
            if self.move_state >= Status.NEUTRAL:
                self.move_state = Status.NEUTRAL
                self.xvel = 0.0
                self.xaccl = 0.0
                self.holding = 0

        if Events.RELEASE_LEFT in self.events \
            or Events.RELEASE_RIGHT in self.events:
            self.push_state = Push.STILL

            #print(self.events)

        if self.direction != self.holding and self.holding != 0:
            self.events.append(Events.REVERSE_DIRECTION)
            self.interaction_events.append(Events.HALT_PUSHING)

            """ Comment out the above and the player can "moonwalk" push
                It's a bug but might be neat
            """

        if self.move_state == Status.WALK:
            if self.push_state == Push.NUDGE:
                self.xaccl = self.base_xaccl / 2.0
            else:
                self.xaccl = self.base_xaccl

            if self.xvel >= self.max_xvel:
                self.xvel = self.max_xvel

        if self.xvel > 0.0:
            zero_xvel = False
            if self.move_state >= Status.NEUTRAL:
                if Events.PUSHING_COIL_LEFT in self.events:
                    if self.holding == Facing.RIGHT:
                        self.holding = 0
                        zero_xvel = True
                        print("Negate holding")

                if Events.PUSHING_COIL_RIGHT in self.events:
                    if self.holding == Facing.LEFT:
                        self.holding = 0
                        zero_xvel = True

            if zero_xvel:
                self.xvel = 0.0
                self.xaccl = 0.0

            if Events.REVERSE_DIRECTION in self.events:
                if self.move_state == Status.WALK:
                    self.xaccl *= -4
                    self.facing = self.holding
                    self.direction = self.holding

                if self.move_state == Status.DASH:
                    self.xaccl += 0.0001
                    if self.xvel <= self.max_xvel:
                        self.xvel = self.max_xvel
                        self.move_state = Status.WALK
        else:
            if Events.HOLD_RIGHT not in self.events \
                and Events.HOLD_LEFT not in self.events:
                if self.move_state == Status.DASH:
                    self.move_state = Status.NEUTRAL
                    self.xaccl = 0.0

        if self.holding == self.direction \
            and self.move_state == Status.DASH:
                if self.xvel <= self.max_xvel:
                    self.move_state = Status.WALK
                    print("UH HERE")
                    self.xaccl = self.base_xaccl

        """
        if Events.HOLD_RIGHT in self.events \
                or Events.HOLD_LEFT in self.events:
            print("uh",self)
        """

        self.events.clear()

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



