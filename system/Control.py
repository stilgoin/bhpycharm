from enum import Enum
from pygame.locals import *

from system.defs import Key

class Control:

    this_frame_ctrl = 0
    last_frame_ctrl = 0
    keys_pressed = 0
    keys_released = 0
    autoLeft = False
    autoRight = False
    launch = False
    ext_keys_pressed = 0
    ext_keys_released = 0
    ext_frame_ctrl = 0
    ext_last_frame = 0

    @property
    def controls(self):
        return (self.this_frame_ctrl, self.last_frame_ctrl,
                self.keys_pressed, self.keys_released, self.launch)

    def control(self, pygame):
        keys_pressed = pygame.key.get_pressed()

        self.last_frame_ctrl = self.this_frame_ctrl
        self.this_frame_ctrl = 0
        self.ext_last_frame = self.ext_frame_ctrl
        self.ext_frame_ctrl = 0

        if keys_pressed[K_a]:
            self.ext_frame_ctrl |= 0x1

        if keys_pressed[K_d]:
            self.ext_frame_ctrl |= 0x2

        if keys_pressed[K_e]:
            self.ext_frame_ctrl |= 0x4

        self.launch = False

        self.ext_keys_released = (self.ext_frame_ctrl ^ self.ext_last_frame) & self.ext_last_frame
        if self.ext_keys_released & 0x2:
            self.autoRight = not self.autoRight
        if self.ext_keys_released & 0x1:
            self.autoLeft = not self.autoLeft
        if self.ext_keys_released & 0x4:
            self.launch = True

        if keys_pressed[K_z]:
            self.this_frame_ctrl |= Key.JUMP.value

        if keys_pressed[K_x]:
            self.this_frame_ctrl |= Key.FIRE.value

        if keys_pressed[K_LEFT] or self.autoLeft:
            self.this_frame_ctrl |= Key.LEFT.value

        if keys_pressed[K_RIGHT] or self.autoRight:
            self.this_frame_ctrl |= Key.RIGHT.value

        if keys_pressed[K_UP]:
            self.this_frame_ctrl |= Key.UP.value

        if keys_pressed[K_DOWN]:
            self.this_frame_ctrl |= Key.DOWN.value

        if keys_pressed[K_RETURN]:
            self.this_frame_ctrl |= Key.ENTER.value

        """
        if keys_pressed[K_s]:
            self.this_frame_ctrl |= BTN_SWITCH

        if keys_pressed[K_t]:
            self.this_frame_ctrl |= BTN_TUMBLE

        if keys_pressed[K_a]:
            self.this_frame_ctrl |= BTN_PERMA_LEFT

        if keys_pressed[K_d]:
            self.this_frame_ctrl |= BTN_PERMA_RIGHT
        """
        keys_changed = self.last_frame_ctrl ^ self.this_frame_ctrl
        self.keys_pressed = keys_changed & self.this_frame_ctrl
        self.keys_released = keys_changed & self.last_frame_ctrl
