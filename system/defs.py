import pygame
from pygame.constants import *

from enum import Enum

BG_CLEAR = pygame.Color(0,0,1,0)
BG_FILL = pygame.Color(96,160,255)
SCR_W = 256
SCR_H = 256
SURF_FORMAT = "RGBA"

class Key(Enum):
    JUMP = 1
    FIRE = 2
    ENTER = 4
    LEFT = 0x10
    RIGHT = 0x20
    UP = 0x40
    DOWN = 0x80