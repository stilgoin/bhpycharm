import pygame
from pygame.constants import *

from enum import Enum, IntEnum

BG_CLEAR = pygame.Color(0,0,1,0)
BG_FILL = pygame.Color(96,160,255)
SCR_W = 256
SCR_H = 256
SCALE_W = 1080
SCALE_H = 768
SURF_FORMAT = "RGBA"

class Key(IntEnum):
    JUMP = 1
    FIRE = 2
    ENTER = 4
    LEFT = 0x10
    RIGHT = 0x20
    UP = 0x40
    DOWN = 0x80

class Push(IntEnum):
    NOPUSH = 0
    NUDGE = 1
    ROLLBACK = 2
    STEP = 4
    SKID = 8

class Facing(IntEnum):
    LEFT = -1
    RIGHT = 1

class Vertical(IntEnum):
    UP = -1
    DOWN = 1

class Jump(IntEnum):
    FLOOR = 0
    JUMP = 0x40
    FALL = 0x80

class Anim(IntEnum):
    STILL = 0
    WALK = 1
    JUMP = 2
    PEAK = 3

class Tick(IntEnum):
    DELAY = 10

class Status(IntEnum):
    WALK = 0x1
    EXPIRED = 0xFF

class Terminators(IntEnum):
    HOLD = 0xFD
    REPEAT = 0xFE
    EXPIRE = 0xFF

class Id(Enum):
    PLAYER = "player"
    BLOCK = "block"