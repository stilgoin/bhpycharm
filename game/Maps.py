
import math

from enum import Enum
from system.data import CollisionIndex

class AnimationSequence:

    class Terminators(Enum):
        HOLD = 0xFD
        REPEAT = 0xFE
        NULL = 0xFF

    def __init__(self, frames = [], terminator = Terminators.REPEAT):
        self.frames = frames
        self.terminator = terminator

class Rect:
    x0 = 0.0
    x1 = 0.0
    y0 = 0.0
    y1 = 0.0

    def __init__(self, x0 = 0.0, y0 = 0.0, x1 = 0.0, y1 = 0.0):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1

class Hitbox(Rect):
    solid = 0
    xoffs = 0.0
    yoffs = 0.0
    width = 0.0
    height = 0.0

    def __str__(self):
        return "(%.4f,%.4f) (%.4f,%.4f)" % (self.x0, self.y0, self.x1, self.y1)
    def __init__(self, x0 = 0, y0 = 0,
                 hitoffs = (0, 0, 0, 0), solid = 0):
        xoffs = hitoffs[0]
        yoffs = hitoffs[1]
        width = hitoffs[2]
        height = hitoffs[3]
        x1 = math.ceil(x0+width)
        y1 = math.ceil(y0+height)
        x0 = math.floor(x0)
        y0 = math.floor(y0)


        super().__init__(x0+xoffs, y0+yoffs, x1, y1)
        self.width = width
        self.height = height
        self.xoffs = xoffs
        self.yoffs = yoffs
        self.solid = solid

class TilePlacement:
    xloc = 0
    yloc = 0
    tileSize = 1
    tileId = 0
    flipTile = False
    vflipTile = False

    def __init__(self, **kwargs):
        self.xloc = kwargs['xloc']
        self.yloc = kwargs['yloc']
        self.tileSize = kwargs['tileSize']
        self.tileId = kwargs['tileId']
        self.flipTile = kwargs['flipTile']
        self.vflipTile = kwargs['vflipTile']

class MapLayer:
    def __init__(self, tile_placements):
        self.tile_placements = tile_placements.copy()

class TileMap:

    def initHitBoxes(self):
        tile_sizes = [8, 16, 24, 32]
        for layer in self.layers:
            for tipl in layer.tile_placements:
                tileId = tipl.tileId
                solid = CollisionIndex[tipl.tileSize][tileId]
                if not solid:
                    continue
                hb = Hitbox()
                hb.x0 = tipl.xloc
                hb.y0 = tipl.yloc
                hb.x1 = hb.x0 + tile_sizes[tipl.tileSize - 1]
                hb.y1 = hb.y0 + tile_sizes[tipl.tileSize - 1]
                tileId = tipl.tileId
                hb.solid = solid
                self.hitboxes.append(hb)


    def __init__(self, layers):
        self.layers = layers.copy()
        self.hitboxes = []
        self.initHitBoxes()