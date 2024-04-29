from movers.blocks.block import Block
from system.defs import Events, Push, Id, Facing, Status


class SideSpring(Block):
    base_xaccl = 0.05
    max_pvel = 0.25

    def clamp_pvel(self):
        if self.push_state == Push.STILL \
                or self.push_state == Push.ROLLBACK:
            return

        if self.xvel >= self.max_pvel:
            self.xvel = self.max_pvel

    def go(self):
        if not self.xvel and self.move_state == Status.DASH:
            self.push_state = Push.STILL
            self.move_state = Status.NEUTRAL
        super().go()

    def __init__(self, anim_init, id, placeholder, facing = Facing.RIGHT):
        super().__init__(anim_init, id, placeholder)
        self.facing = facing

class SpringBox(Block):
    base_xaccl = 0.0    # disable pushing, but keep the capability

    def procInteractionEvents(self):

        if Events.MOVER_LEAVE_COIL in self.spring.interaction_events:
            if self.spring.push_state == Push.NUDGE:
                self.spring.push_state = Push.ROLLBACK
                self.spring.xvel = self.spring.psteps / 16.0
                self.spring.xaccl = 0.05
                self.spring.direction = self.spring.direction * -1
                print("Leave coil")
            self.spring.psteps = 0

        if Events.MOVER_RECOIL in self.spring.interaction_events:
            self.spring.haltMovement()
            self.spring.psteps = 0
            self.spring.interaction_events.remove(Events.MOVER_RECOIL)

        super().procInteractionEvents()

    def go(self):
        super().go()

        if self.spring.xloc <= self.xloc + 4:
            self.spring.xloc = self.xloc + 4

        if self.spring.xloc > self.xloc + 0x10:
            self.spring.xloc = self.xloc + 0x10
            if self.spring.push_state == Push.ROLLBACK:
                self.spring.push_state = Push.STILL
                self.spring.dash_xvel = self.spring.xvel
                self.spring.haltMovement()


            """
            if self.spring.push_state == Push.ROLLBACK:
                self.spring.push_state = Push.STILL
                self.spring.xvel = 0.0
                self.spring.xaccl = 0.0
                self.spring.move_state = Status.NEUTRAL
            """

    def animate(self):
        return [self.animation_state \
                    .display_entry(self.id, self.xloc, self.yloc,
                                   True if self.facing == Facing.RIGHT else False,
                                   False),
                self.spring.animation_state.display_entry(self.spring.id, self.spring.xloc, self.spring.yloc,
                                   True if self.spring.facing == Facing.RIGHT else False,
                                   False)]
    def __init__(self, anim_inits, anim_init, id = Id.STATUE.value, placeholder = True, facing = Facing.RIGHT):
        self.spring = SideSpring(anim_inits[Id.SIDECOIL], Id.SIDECOIL.value, True, facing)
        super().__init__(anim_init, id, placeholder)