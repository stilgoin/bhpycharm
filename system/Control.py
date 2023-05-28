from enum import Enum
from pygame.locals import *

from system.defs import Key

class Control:

    this_frame_ctrl = 0
    last_frame_ctrl = 0
    keys_pressed = 0
    keys_released = 0

    @property
    def controls(self):
        return (self.this_frame_ctrl, self.last_frame_ctrl,
                self.keys_pressed, self.keys_released)

    def control(self, pygame):
        keys_pressed = pygame.key.get_pressed()

        self.last_frame_ctrl = self.this_frame_ctrl
        self.this_frame_ctrl = 0

        if keys_pressed[K_z]:
            self.this_frame_ctrl |= Key.JUMP.value

        if keys_pressed[K_x]:
            self.this_frame_ctrl |= Key.FIRE.value

        if keys_pressed[K_LEFT]:
            self.this_frame_ctrl |= Key.LEFT.value

        if keys_pressed[K_RIGHT]:
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
