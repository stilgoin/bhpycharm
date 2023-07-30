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

    auuid = uuid.uuid4()
    id = ""

    move_state = 0
    push_state = 0
    jump_state = 0
    jump_lock = False
    facing = Facing.LEFT
    vertical = Vertical.UP

    hitoffs = (4.0, 1.0, 12.0, 14.0)
    hb = Hitbox(0.0, 0.0, (0, 0, 0, 0))
    phb = Hitbox(0.0, 0.0, (0, 0, 0, 0))

    def __str__(self):
        return str(self.animation_state)

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
        self.xloc += (self.xvel * self.facing)
        self.yloc += (self.yvel * self.vertical)

        if self.jump_state == Jump.JUMP:
            self.yvel -= GRAVITY
            if self.yvel < 0.0:
                self.set_fall(1.75)
                self.set_anim_idx(Anim.STILL)

            if self.yvel <= 1.50\
                    and not self.animation_state\
                    .check_anim_idx(Anim.PEAK):
                pass
                self.set_anim_idx(Anim.PEAK)

    def anim_state(self):
        if self.jump_state == Jump.FLOOR:
            self.animation_state.set_anim_idx(0)

    def set_anim_idx(self, state):
        self.animation_state.set_anim_idx(state)

    def call_lambdas(self):
        for call_lambda in self.lambdas:
            call_lambda()
        self.lambdas.clear()

    def go(self):
        self.oldXloc = self.xloc
        self.oldYloc = self.yloc
        self.animation_state.add_frameticks()
        self.call_lambdas()
        self.move()


    def check(self, moverToBGFunc):
        self.hb = Hitbox(self.xloc, self.yloc,
                         self.hitoffs)
        self.phb = Hitbox(self.oldXloc, self.oldYloc,
                          self.hitoffs)

        floor_found, result = self.moverToMovers()

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
        return self.animation_state\
            .display_entry(self.id, self.xloc, self.yloc,
                           True if self.facing == Facing.RIGHT else False,
                           False)

    def proc_input(self, control):
        this_frame_control, last_frame_control,\
            keys_pressed, keys_released = control

        do_accl = False

        #self.yvel = 1.25
        if this_frame_control & Key.LEFT:
            self.facing = Facing.LEFT
            self.move_state = Status.WALK
            do_accl = True
        elif this_frame_control & Key.RIGHT:
            self.facing = Facing.RIGHT
            self.move_state = Status.WALK
            do_accl = True
        else:
            self.xvel = 0.0
            self.move_state = 0

        if do_accl:
            self.xvel += 0.10
            if self.xvel >= 1.0:
                self.xvel = 1.0

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
            self.move_state = 0
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

    def __init__(self, anim_init, id = Id.PLAYER.value):
        self.animation_state = AnimationState(anim_init)
        self.id = id
        self.set_fall(1.75)
        self.set_anim_idx(Anim.STILL)
        self.lambdas = []