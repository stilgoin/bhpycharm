from game.Maps import Hitbox
from game.Overlap import Result, moverToMover
from movers.InteractiveMover import InteractiveMover
from movers.mover_classes import MiscMover, Player
from movers.movers import Mover
from system.defs import Id, Facing, Push, Status, Events


class Block(InteractiveMover):
    pforce = 2
    mass = 2
    movers = []
    friction = 0
    psteps = 0

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

    def procInteractionEvents(self):
        if Events.HALT_PUSHING in self.interaction_events:
            self.xvel = 0.0
            self.xaccl = 0.0
            self.push_state = Push.STILL
            self.move_state = Status.NEUTRAL
            self.psteps = 0

        elif Events.PUSH_TO_SKID in self.interaction_events:
            self.push_state = Push.SKID
            self.xaccl = -0.05
            self.xvel = 1.75
            self.psteps = 0
            self.move_state = Status.WALK

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
        self.lambdas.append(lambda : self.halt_skidding())
        self.lambdas.append(lambda : self.add_push_steps())
        super().go()

class Hammer(Mover):
    active = False

    def check(self, moverToBGFunc = lambda : None):
        pass

class Statue(Block):

    hammer : Hammer = None

    def misc_hitbox(self):
        self.hb = Hitbox(self.xloc, self.yloc, (-8,0,32,16))

    def check(self, floor_found, moverToBGFunc):
        super().check(floor_found, moverToBGFunc)

    def postproc(self):
        # self.trigger_box = Hitbox(self.xloc, self.yloc, (-8,0,32,16))
        if self.action_timer > 0:
            self.action_timer -= 1
            if self.action_timer <= 30:
                self.hammer.xloc = 0xFFFF
        else:
            self.hammer.xloc = 0xFFFF

        # self.hb = Hitbox(self.xloc, self.yloc, (-8,0,32,16))
        for mover in InteractiveMover.movers + Player.movers:
            if mover.id == Id.STATUE.value:
                continue

            result = moverToMover(self, mover)
            if result.result == Result.CONTACT \
                    or result.result == Result.OVERLAP:

                if not self.action_timer:
                    self.action_timer = 60
                    self.hammer.yloc = self.yloc - 0x4
                    if result.facing == Facing.LEFT \
                            or result.side == Facing.LEFT:
                        self.hammer.xloc = self.xloc - 0x8
                    else:
                        self.hammer.xloc = self.xloc + 0x10

        self.make_hitboxes()



    def animate(self):
        return [self.animation_state \
                    .display_entry(self.id, self.xloc, self.yloc,
                                   True if self.facing == Facing.RIGHT else False,
                                   False),
                self.hammer.animation_state.display_entry(self.hammer.id, self.hammer.xloc, self.hammer.yloc,
                                   True if self.hammer.facing == Facing.RIGHT else False,
                                   False)]

    def go(self):
        super().go()

    def __init__(self, anim_inits, anim_init, id = Id.STATUE.value, placeholder = True):
        self.hammer = Hammer(anim_inits[Id.HAMMER], Id.HAMMER.value, True)
        MiscMover.movers.append(self.hammer)
        super().__init__(anim_init, id, placeholder)
        MiscMover.postproc_movers.append(self)

class SideSpring(Block):
    base_xaccl = 0.05
    max_pvel = 0.25

    def clamp_pvel(self):
        if self.push_state == Push.STILL \
                or self.push_state == Push.ROLLBACK:
            return

        if self.xvel >= self.max_pvel:
            self.xvel = self.max_pvel

    def __init__(self, anim_init, id, placeholder, facing = Facing.RIGHT):
        super().__init__(anim_init, id, placeholder)
        self.facing = facing

class SpringBox(Block):
    base_xaccl = 0.0    # disable pushing, but keep the capability

    def go(self):
        super().go()

        if self.spring.xloc <= self.xloc + 4:
            self.spring.xloc = self.xloc + 4

        if self.spring.xloc > self.xloc + 0x10:
            self.spring.xloc = self.xloc + 0x10
            if self.spring.push_state == Push.ROLLBACK:
                self.spring.push_state = Push.STILL

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