from system.defs import *
from game.Maps import Hitbox
from game.Overlap import OverlapResult

import uuid

JUMPVEL = 1.75
GRAVITY = .046875

class DisplayEntry:
    id = ""
    animIdx = 0
    frameIdx = 0
    xloc = 0.0
    yloc = 0.0
    fliph = False
    flipv = False

    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.animIdx = kwargs['animIdx']
        self.frameIdx = kwargs['frameIdx']
        self.xloc = kwargs['xloc']
        self.yloc = kwargs['yloc']
        self.fliph = kwargs['fliph'] \
            if 'fliph' in kwargs else False
        self.flipv = kwargs['flipv'] \
            if 'flipv' in kwargs else False



class AnimationState:
    animIdx = 0
    frameTicks = 0
    maxFrames = 0

    def __str__(self):
        return "animIdx: " + str(self.animIdx) + ", frameTicks: " + str(self.frameTicks)


    def process_terminator(self):
        terminator = self.terminators[self.animIdx]
        if terminator == Terminators.HOLD:
            return self.maxFrames[self.animIdx] - 1
        if terminator == Terminators.REPEAT:
            self.frameTicks = 0
            return 0
        if terminator == Terminators.EXPIRE:
            return Terminators.EXPIRE
    @property
    def current_frame(self):
        frameIdx = int(self.frameTicks / Tick.DELAY)
        if frameIdx >= self.maxFrames[self.animIdx]:
            return self.process_terminator()
        return frameIdx

    def set_anim_idx(self, animIdx):
        self.animIdx = animIdx
        self.frameTicks = 0

    def check_anim_idx(self, animIdx) -> bool:
        return self.animIdx == animIdx

    def display_entry(self, id, xloc, yloc, fliph = False, flipv = False):
        frameIdx = self.current_frame
        if id == Id.BLOCK.value:
            fliph = False
        return DisplayEntry(id=id, animIdx=self.animIdx,
                            frameIdx=frameIdx, xloc=xloc, yloc=yloc,
                            fliph=fliph, flipv=flipv)

    def add_frameticks(self):
        self.frameTicks += 1

    def __init__(self, anim_init):
        maxFrames, terminators = anim_init
        self.maxFrames = maxFrames
        self.terminators = terminators

class Mover:
    xloc = 0.0
    yloc = 0.0
    xvel = 0.0
    yvel = 0.0
    xaccl = 0.0
    yaccl = 0.0
    base_xaccl = 0.1
    pforce = 1
    mass = 1
    friction = 1
    max_pvel = 0.5
    max_xvel = 1.0
    max_dvel = 2.5

    id = ""

    move_state = 0
    push_state = 0
    jump_state = 0
    action_timer = 0
    jump_lock = False
    facing = Facing.LEFT
    direction = Facing.LEFT
    vertical = Vertical.UP
    lock = 0

    placeholder = False

    hb = Hitbox(0.0, 0.0, (0, 0, 0, 0))
    phb = Hitbox(0.0, 0.0, (0, 0, 0, 0))

    def __str__(self):
        #return str(self.animation_state)
        return f"xloc: %.4f xvel: %.4f, xaccl: %.4f status: {self.push_state} " % \
            (self.xloc, self.xvel, self.xaccl)

    def set_jump(self, yvel):
        self.jump_state = Jump.JUMP
        self.vertical = Vertical.UP
        self.yvel = yvel

    def set_fall(self, yvel):
        self.jump_state = Jump.FALL
        self.vertical = Vertical.DOWN
        self.yvel = yvel

    def moverToMovers(self):
        return False, OverlapResult()

    def move(self):
        max_xvels = [self.max_xvel, self.max_xvel, self.max_xvel]
        self.xloc += (self.xvel * self.direction)
        self.yloc += (self.yvel * self.vertical)

        self.xvel += self.xaccl * self.move_state
        if self.xvel <= 0.0:
            self.xvel = 0.0
            if self.push_state == Push.STILL:
                self.move_state = Status.NEUTRAL

        if self.jump_state == Jump.JUMP:
            self.yvel -= GRAVITY
            if self.yvel < 0.0:
                self.set_fall(1.75)
                self.set_anim_idx(Anim.STILL)

    def anim_state(self):
        if self.jump_state == Jump.FLOOR:
            self.animation_state.set_anim_idx(0)

    def set_anim_idx(self, state):
        self.animation_state.set_anim_idx(state)

    def restToStill(self):
        if self.action_timer > 0:
            self.action_timer -= 1
            if self.action_timer <= 0:
                self.push_state = Push.STILL

    def call_lambdas(self):
        for call_lambda in self.lambdas:
            call_lambda()
        self.lambdas.clear()

    def go(self):
        self.animation_state.add_frameticks()
        self.call_lambdas()

        self.oldXloc = self.xloc
        self.oldYloc = self.yloc
        self.move()
        self.restToStill()

    def make_hitboxes(self):
        self.hb = Hitbox(self.xloc, self.yloc,
                         self.hitoffs)
        self.phb = Hitbox(self.oldXloc, self.oldYloc,
                          self.hitoffs)

    def check(self, floor_found, moverToBGFunc):

        #floor_found, result = self.moverToMovers()

        floor_found = floor_found or moverToBGFunc()
        if floor_found and self.jump_state == Jump.FALL:
            self.jump_state = Jump.FLOOR
            self.yvel = 0.0
            self.jump_lock = False
            if self.move_state == Status.WALK:
                self.set_anim_idx(Anim.WALK)
            else:
                self.set_anim_idx(Anim.STILL)

        if not floor_found and self.jump_state == Jump.FLOOR:
            self.set_fall(JUMPVEL)
            self.set_anim_idx(Anim.STILL)

    def animate(self):
        return [self.animation_state\
            .display_entry(self.id, self.xloc, self.yloc,
                           True if self.facing == Facing.RIGHT else False,
                           False)]

    def proc_auto(self, control):
        this_frame_control, last_frame_control, \
            keys_pressed, keys_released, launch = control
        if self.id == Id.BLOCK.value:
            if launch:
                self.facing = Facing.RIGHT
                self.xvel = 5.25
                self.xaccl = -0.05
                self.push_state = Push.SKID
            return

    def proc_input(self, control):
        this_frame_control, last_frame_control,\
            keys_pressed, keys_released, launch = control

        do_accl = False
        xaccl_here = self.xaccl * self.move_state

        if keys_released & Key.LEFT \
            or keys_released & Key.RIGHT:
            self.push_state = Push.STILL

        #self.yvel = 1.25
        if this_frame_control & Key.LEFT:
            self.facing = Facing.LEFT
            self.move_state *= Status.WALK
            self.move_state |= Status.WALK
            do_accl = True
        elif this_frame_control & Key.RIGHT:
            self.facing = Facing.RIGHT
            self.move_state *= Status.WALK
            self.move_state |= Status.WALK
            do_accl = True
        else:
            self.push_state = Push.STILL
            if self.move_state >= Status.NEUTRAL:
                self.move_state = Status.NEUTRAL
                self.xvel = 0.0
            self.pvel = 0.0

        if do_accl:
            if self.move_state == Status.WALK:
                if self.push_state == Push.NUDGE:
                    self.xaccl = self.base_xaccl / 2.0
                else:
                    self.xaccl = self.base_xaccl

            if self.direction != self.facing:
                if self.move_state >= Status.NEUTRAL:
                    self.xaccl *= -4
                else:
                    self.xaccl += .0001
            else:
                #self.xvel += self.xaccl * self.move_state
                if self.xvel <= self.max_xvel:
                    self.move_state = Status.WALK
                    self.xvel = self.max_xvel
            """
            if self.move_state == Status.DASH:
                pass
            else:
                self.direction = self.facing
            """

            if self.xvel <= 0.0:
                self.direction = self.facing
                self.xaccl *= -1
                self.xvel = self.xaccl
                self.move_state = Status.WALK

            if self.push_state in [Push.NUDGE, Push.SKID]:
                if self.xvel >= self.max_pvel:
                    self.xvel = self.max_pvel
            elif self.move_state in [Status.DASH]:
                if self.xvel >= self.max_dvel:
                    self.xvel = self.max_dvel
            else:
                if self.xvel >= self.max_xvel:
                    self.xvel = self.max_xvel

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

        """
        if this_frame_control & Key.UP:
            self.vertical = Vertical.UP
        elif this_frame_control & Key.DOWN:
            self.vertical = Vertical.DOWN
        else:
            self.yvel = 0.0
        """

    def __init__(self, anim_init, id = Id.PLAYER.value, placeholder = False):
        self.animation_state = AnimationState(anim_init)
        self.id = id
        self.set_fall(1.75)
        self.set_anim_idx(Anim.STILL)
        self.lambdas = []
        self.placeholder = placeholder
        self.auuid = uuid.uuid4()

