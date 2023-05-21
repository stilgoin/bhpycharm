
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
    def __init__(self, layers):
        self.layers = layers.copy()