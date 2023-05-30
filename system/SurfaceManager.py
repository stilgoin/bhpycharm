import pygame

from enum import Enum
from system.defs import *
from PIL import Image

class Surfaces(Enum):
    MAP = 0
    SPRITE = 1
    FINAL = 2

class SurfaceManager:

    @classmethod
    def surfaceFromImage(self, image : Image,
                         rect : () ) -> pygame.Surface:
        tx, ty, tw, th = rect
        crop_image = image.crop(
            (tx, ty, tx + tw, ty + th) )

        return pygame.image.frombuffer(
            crop_image.tobytes(),
            crop_image.size, SURF_FORMAT)

    def drawSprite(self, sprite, xloc, yloc):
        sprite_surf = self.surfaces[Surfaces.SPRITE.value]
        sprite_surf.blit(sprite, (xloc, yloc))

    def clearSpriteSurf(self):
        sprite_surf = self.surfaces[Surfaces.SPRITE.value]
        sprite_surf.fill( (BG_CLEAR) )

    def drawScreen(self, screen : pygame.Surface):
        final_surf = self.surfaces[Surfaces.FINAL.value]
        map_surf = self.surfaces[Surfaces.MAP.value]
        sprite_surf = self.surfaces[Surfaces.SPRITE.value]
        final_surf.fill( (BG_CLEAR) )
        final_surf.blit(map_surf, (0, 0) )
        final_surf.blit(sprite_surf, (0, 0) )
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
        for surfIdx in Surfaces:
            self.surfaces.append(self.initSurface(width, height) )