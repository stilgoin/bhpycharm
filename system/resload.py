import base64
import io
import json
import re
from collections import defaultdict, namedtuple
from types import SimpleNamespace
from PIL import Image
from PIL import ImageFile

from game.Maps import TilePlacement, MapLayer, TileMap

from system.SurfaceManager import SurfaceManager as sm
class ResourceLoader:

    def __getitem__(self, item):
        if item in self.tileset_keys:
            return self.tilesets[item]

    def loadTiles(self, image, tile_size, tileset_key):
        ty = 0
        while ty < image.height:
            tx = 0
            while tx < image.width:
                tile_surf = \
                    sm.surfaceFromImage(image,
                                    (tx, ty, tile_size, tile_size))
                self.tilesets[tileset_key]\
                    .append(tile_surf)
                tx += tile_size
            ty += tile_size

    def loadTilesets(self):
        tile_sizes = [8, 16, 32]
        ti = 0
        for tile_size in tile_sizes:
            image = self.tile_sheets[ti]
            self.loadTiles(image, tile_size,
                           self.tileset_keys[ti])
            ti += 1

    def loadBinImage(self, bin_image):
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        return Image.open(bin_image,
                          formats=["PNG"])

    def decodeMapsJson(self, fields_dict : dict):
        if 'xloc' in fields_dict:
            return TilePlacement(**fields_dict)
        if 'tilePlacements' in fields_dict.keys():
            return MapLayer(fields_dict['tilePlacements']['shadowList'])
        if 'mapLayers' in fields_dict.keys():
            return TileMap(fields_dict['mapLayers']['shadowList'])
        return fields_dict

    def loadTileMaps(self, maps_dict):
        json_strr = "[{\"xloc\":0,\"yloc\":224,\"tileSize\":2,\"tileId\":0,\"flipTile\":false,\"vflipTile\":false}" \
                    ",{\"xloc\":80,\"yloc\":240,\"tileSize\":2,\"tileId\":1,\"flipTile\":false,\"vflipTile\":false}]"
        tilemaps_strr = maps_dict.tileMapEditor
        return json.loads(tilemaps_strr,
                   object_hook=self.decodeMapsJson)


    def __init__(self, filename):

        self.tiles_map = {}
        self.tile_sheets = []
        tileset_keys = ["8x8", "16x16", "32x32"]
        self.tileset_keys = tileset_keys
        self.tilesets = defaultdict(list)

        maps_file = io.FileIO(filename, "r")
        maps_dict = json.load(maps_file,
                              object_hook=lambda d: SimpleNamespace(**d))
        maps_file.close()

        self.tilemaps = self.loadTileMaps(maps_dict)

        gfx_file = io.FileIO(filename + ".images", "r")
        gfx_dict = json.load(gfx_file)
        gfx_file.close()

        for key in tileset_keys:
            blo = io.BytesIO(
                bytes(
                    base64.b64decode(
                        gfx_dict[key])))

            image = self.loadBinImage(
                blo
            )
            self.tile_sheets.append(image)

        self.loadTilesets()
        pass



