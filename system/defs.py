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
    SKID = -1
    STILL = 0
    NUDGE = 1
    ROLLBACK = 2
    STEP = 4
    REST = 8

class Move(IntEnum):
    NEUTRAL = 0
    DASH = 1

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
    DASH = -1
    NEUTRAL = 0x0
    WALK = 0x1
    EXPIRED = 0xFF

class Terminators(IntEnum):
    HOLD = 0xFD
    REPEAT = 0xFE
    EXPIRE = 0xFF

class Events(Enum):
    HOLD_LEFT = "hold_left"
    HOLD_RIGHT = "hold_right"
    PRESS_LEFT = "press_left"
    PRESS_RIGHT = "press_right"
    RELEASE_LEFT = "release_left"
    RELEASE_RIGHT = "release_right"
    REVERSE_DIRECTION = "reverse_direction"
    MAX_XVEL = "max_xvel"
    MIN_XVEL = "min_xvel"
    ACCELERATE = "accelerate"
    DECCELERATE = "deccelerate"
    XVEL_GT = "xvel_greater_than"
    XVEL_LT = "xvel_less_than"
    HALT_PUSHING = "halt_pushing"
    PUSH_TO_SKID = "push_to_skid"
    PUSHING_COIL_LEFT = "pushing_coil"
    PUSHING_COIL_RIGHT = "pushing_coil"
    NO_CHECK_COIL = "no_check_coil"
    MOVER_LEAVE_COIL = "no_contact_coil"
    MOVER_RECOIL = "mover_recoil"
    COIL_CONTACT = "coil_contact"

class Id(Enum):
    PLAYER = "player"
    BLOCK = "block"
    STATUE = "statue"
    HAMMER = "hammer"
    SIDECOIL = "sidecoil"
    VERTCOIL = "vertcoil"
    SPRINGBOX = "springbox"

class Ability(Enum):
    PUSHING = "pushing"
    ITEM = "item"

class Statue(IntEnum):
    PASSIVE = 0
    ARMED = 1

class Vel(float, Enum):
    SHOVE = 0.175