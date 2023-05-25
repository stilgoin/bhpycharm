import pygame

from enum import Enum
from system.defs import *
from PIL import Image

class SurfaceManager:
    class Surfaces(Enum):
        MAP = 0
        FINAL = 1

    @classmethod
    def surfaceFromImage(self, image : Image,
                         rect : () ) -> pygame.Surface:
        tx, ty, tw, th = rect
        crop_image = image.crop(
            (tx, ty, tx + tw, ty + th) )
        return pygame.image.frombuffer(
            crop_image.tobytes(),
            crop_image.size, SURF_FORMAT)

    def drawScreen(self, screen : pygame.Surface):
        final_surf = self.surfaces[self.Surfaces.FINAL.value]
        map_surf = self.surfaces[self.Surfaces.MAP.value]
        final_surf.blit(map_surf, (0, 0) )
        screen.blit(final_surf, (0, 0) )

    def blitSurface(self, surfIdx : int, onSurf : pygame.Surface, rect : () = (0, 0)):
        surface = self.surfaces[surfIdx]
        x0, y0 = rect
        surface.blit(onSurf, (x0, y0) )

    def initSurface(self, width, height):
        surface = pygame.Surface( (width, height) )
        surface.convert()
        surface.set_colorkey( (BG_CLEAR) )
        surface.fill( (BG_CLEAR) )
        return surface

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.surfaces = []
        for surfIdx in self.Surfaces:
            self.surfaces.append(self.initSurface(width, height) )