from movers.interactive_mover import InteractiveMover
from movers.movers import Mover
from system.defs import Id, Anim, Jump, Events, Status, Facing, Push
from system.defs import *


JUMPVEL = 1.75

class MiscMover(Mover):
    movers = []
    postproc_movers = []


class Player(InteractiveMover):
    hitoffs = (4.0, 1.0, 12.0, 14.0)
    movers = []

    def procEvents(self):

        if Events.HOLD_RIGHT in self.events \
            or Events.HOLD_LEFT in self.events:

            if not self.xaccl:
                self.xaccl = self.base_xaccl

            if Events.HOLD_LEFT in self.events:
                self.holding = Facing.LEFT
            if Events.HOLD_RIGHT in self.events:
                self.holding = Facing.RIGHT

            if self.holding != 0:
                self.direction = self.holding
                self.facing = self.holding
        else:
            self.xvel = 0.0
            self.xaccl = 0.0
            self.holding = 0

        if self.direction != self.holding and self.holding != 0:
            self.events.append(Events.REVERSE_DIRECTION)
            self.interaction_events.append(Events.HALT_PUSHING)

            """ Comment out the above and the player can "moonwalk" push
                It's a bug but might be neat
            """

        #if self.move_state == Status.WALK:
        #    if self.push_state == Push.NUDGE:
        #        self.xaccl = self.base_xaccl / 2.0
        #    else:
        #        self.xaccl = self.base_xaccl

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

    def procInput(self, control):
        this_frame_control, last_frame_control, \
            keys_pressed, keys_released, launch = control

        if keys_released & Key.RIGHT:
            self.events.append(Events.RELEASE_LEFT)
        if keys_released & Key.LEFT:
            self.events.append(Events.RELEASE_RIGHT)
        if keys_pressed & Key.RIGHT:
            self.events.append(Events.PRESS_RIGHT)
        if keys_pressed & Key.LEFT:
            self.events.append(Events.PRESS_LEFT)

        if this_frame_control & Key.LEFT:
            self.events.append(Events.HOLD_LEFT)
            if Events.RELEASE_LEFT in self.events:
                self.events.remove(Events.RELEASE_LEFT)
            self.holding = Facing.LEFT
        if this_frame_control & Key.RIGHT:
            self.events.append(Events.HOLD_RIGHT)
            if Events.RELEASE_RIGHT in self.events:
                self.events.remove(Events.RELEASE_RIGHT)
            self.holding = Facing.RIGHT

        # Jumping
        if self.jump_state == Jump.FLOOR:
            if not this_frame_control & Key.LEFT \
                and not this_frame_control & Key.RIGHT:
                self.set_anim_idx(Anim.STILL)
            if keys_pressed & Key.LEFT \
                or keys_pressed & Key.RIGHT:
                self.set_anim_idx(Anim.WALK)

        if keys_pressed & Key.JUMP \
            and not self.jump_lock \
            and self.jump_state == Jump.FLOOR:
            self.set_jump(JUMPVEL)
            #self.move_state = 0
            self.set_anim_idx(Anim.JUMP)

        if not keys_pressed & Key.JUMP \
            and self.jump_state == Jump.FLOOR:
            self.jump_lock = False

        if keys_released & Key.JUMP \
                and self.jump_state == Jump.JUMP:
            self.set_fall(1.75)
            self.set_anim_idx(Anim.STILL)

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



