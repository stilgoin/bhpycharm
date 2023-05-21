import pygame

from system.defs import *
from PIL import Image

class SurfaceManager:

    pyg_surf : pygame.Surface = None
    map_surf : pygame.Surface = None
    final_surf : pygame.Surface = None
    surfaces = [map_surf, final_surf]

    @classmethod
    def surfaceFromImage(self, image : Image,
                         rect : () ) -> pygame.Surface:
        tx, ty, tw, th = rect
        crop_image = image.crop(
            (tx, ty, tx + tw, ty + th) )
        return pygame.image.frombuffer(
            crop_image.tobytes(),
            crop_image.size, SURF_FORMAT)


    def initSurface(self, surface : pygame.Surface,
                    width, height):
        surface = pygame.Surface( (width, height) )
        surface.convert()
        surface.set_colorkey( (BG_CLEAR) )
        surface.fill( (BG_CLEAR) )

    def __init__(self, width, height):
        self.width = width
        self.height = height
        for surface in self.surfaces:
            self.initSurface(surface, width, height)