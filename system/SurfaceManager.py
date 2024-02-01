from PIL import Image

from system.defs import *


class Surfaces(IntEnum):
    MAP = 0
    SPRITE = 1
    FINAL = 2
    SCALE = 3


class SurfaceManager:

    @classmethod
    def surfaceFromImage(self, image: Image,
                         rect: ()) -> pygame.Surface:
        tx, ty, tw, th = rect
        crop_image = image.crop(
            (tx, ty, tx + tw, ty + th))

        return pygame.image.frombuffer(
            crop_image.tobytes(),
            crop_image.size, SURF_FORMAT)

    @classmethod
    def surfaceFromPlaceholder(self, color, rect:()) -> pygame.Surface:
        tx, ty, tw, th = rect
        surface = self.initSurface(self, tw, th)
        pygame.draw.rect(surface, color, pygame.Rect(tx,ty,tw,th))
        return surface

    def drawSprite(self, sprite, xloc, yloc):
        sprite_surf = self.surfaces[Surfaces.SPRITE.value]
        sprite_surf.blit(sprite, (xloc, yloc))

    def clearSpriteSurf(self):
        sprite_surf = self.surfaces[Surfaces.SPRITE]
        sprite_surf.fill((BG_CLEAR))

    def drawScreen(self, screen: pygame.Surface):
        final_surf = self.surfaces[Surfaces.FINAL]
        map_surf = self.surfaces[Surfaces.MAP]
        sprite_surf = self.surfaces[Surfaces.SPRITE]
        scale_surf = self.surfaces[Surfaces.SCALE]
        final_surf.fill((BG_CLEAR))
        final_surf.blit(map_surf, (0, 0))
        final_surf.blit(sprite_surf, (0, 0))
        pygame.transform.scale(final_surf, (SCALE_W, SCALE_H), scale_surf)
        screen.blit(scale_surf, (0, 0) )

    def blitSurface(self, surfIdx: int, onSurf: pygame.Surface, rect: () = (0, 0)):
        surface = self.surfaces[surfIdx]
        x0, y0 = rect
        surface.blit(onSurf, (x0, y0))

    def initSurface(self, width, height):
        surface = pygame.Surface((width, height))
        surface.convert()
        surface.set_colorkey((BG_CLEAR))
        surface.fill((BG_CLEAR))
        return surface

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.surfaces = []
        for surfIdx in Surfaces:

            if surfIdx == Surfaces.SCALE:
                width = SCALE_W
                height = SCALE_H

            self.surfaces.append(self.initSurface(width, height))
