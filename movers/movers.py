from enum import Enum
from system.defs import Key
from game.Maps import Hitbox

class Push(Enum):
    NOPUSH = 1
    NUDGE = 2
    ROLLBACK = 4
    STEP = 8
    SKID = 0x10

class Facing(Enum):
    LEFT = -1
    RIGHT = 1

class Vertical(Enum):
    UP = -1
    DOWN = 1

class Jump(Enum):
    FLOOR = 0
    JUMP = 0x40
    FALL = 0x80

class Tick(Enum):
    DELAY = 10

class Id(Enum):
    PLAYER = "player"

class DisplayEntry:
    id = ""
    animIdx = 0
    frameIdx = 0
    xloc = 0.0
    yloc = 0.0

    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.animIdx = kwargs['animIdx']
        self.frameIdx = kwargs['frameIdx']
        self.xloc = kwargs['xloc']
        self.yloc = kwargs['yloc']

class AnimationState:
    animIdx = 0
    frameTicks = 0
    maxFrames = 0

    @property
    def current_frame(self):
        frameIdx = int(self.frameTicks / Tick.DELAY.value)
        if frameIdx >= self.maxFrames[self.animIdx]:
            self.frameTicks = 0
            frameIdx = 0
        return frameIdx

    def display_entry(self, id, xloc, yloc):
        frameIdx = self.current_frame
        return DisplayEntry(id=id, animIdx=self.animIdx,
                            frameIdx=frameIdx, xloc=xloc, yloc=yloc)

    #TODO: Process terminator

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

    move_state = 0
    push_state = 0
    jump_state = 0
    facing = Facing.LEFT.value
    vertical = Vertical.UP.value

    def move(self):
        self.xloc += (self.xvel * self.facing)
        self.yloc += (self.yvel * self.vertical)

    def go(self, exec):
        self.oldXloc = self.xloc
        self.oldYloc = self.yloc
        self.animation_state.add_frameticks()
        self.move()
        self.hb = Hitbox(self.xloc, self.yloc,
                         4.0, 1.0, 12.0, 15.0)
        self.phb = Hitbox(self.oldXloc, self.oldYloc,
                          4.0, 1.0, 12.0, 15.0)
        exec()
        return self.animation_state\
            .display_entry(self.id, self.xloc, self.yloc)

    def proc_input(self, control):
        this_frame_control, last_frame_control,\
            keys_pressed, keys_released = control

        self.xvel = 1.25
        self.yvel = 1.25
        if this_frame_control & Key.LEFT.value:
            self.facing = Facing.LEFT.value
        elif this_frame_control & Key.RIGHT.value:
            self.facing = Facing.RIGHT.value
        else:
            self.xvel = 0.0

        if this_frame_control & Key.UP.value:
            self.vertical = Vertical.UP.value
        elif this_frame_control & Key.DOWN.value:
            self.vertical = Vertical.DOWN.value
        else:
            self.yvel = 0.0

    def __init__(self, anim_init, id = Id.PLAYER.value):
        self.animation_state = AnimationState(anim_init)
        self.id = id