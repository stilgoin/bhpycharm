import base64
import io
import json
from collections import defaultdict
from types import SimpleNamespace

import pygame
from PIL import Image

from game.maps import TilePlacement, MapLayer, TileMap, AnimationSequence
from system.surface_manager import SurfaceManager as sm


class ResourceLoader:
    tileMaps: list[TileMap]
    tileSets: dict[str, list[pygame.Surface]]

    def __getitem__(self, item):
        if item in self.tileset_keys:
            return self.tileSets[item]


    def loadTiles(self, image, tile_size, tileset_key,
                  tileSets: dict[str, list[pygame.Surface]]):
        ty = 0
        while ty < image.height:
            tx = 0
            while tx < image.width:
                tile_surf = \
                    sm.surfaceFromImage(image,
                                        (tx, ty, tile_size, tile_size))
                tileSets[tileset_key] \
                    .append(tile_surf)
                tx += tile_size
            ty += tile_size

    def loadTilesets(self, tileSets: [str, list[pygame.Surface]]):
        tile_sizes = [8, 16, 32]
        ti = 0
        for tile_size in tile_sizes:
            image = self.tile_sheets[ti]
            self.loadTiles(image, tile_size,
                           self.tileset_keys[ti], tileSets)
            ti += 1

    def loadBinImage(self, bin_image) -> Image:
        return Image.open(bin_image,
                          formats=["PNG"])

    """
    Recursively builds an object from json starting with the inner-most json {} string
    """

    def decodeMapsJson(self, fields_dict: dict) -> dict[str, pygame.Surface]:
        if 'xloc' in fields_dict:
            return TilePlacement(**fields_dict)
        if 'tilePlacements' in fields_dict.keys():
            return MapLayer(fields_dict['tilePlacements']['shadowList'])
        if 'mapLayers' in fields_dict.keys():
            return TileMap(fields_dict['mapLayers']['shadowList'])
        return fields_dict

    def loadTileMaps(self) -> list[TileMap]:
        json_strr = "[{\"xloc\":0,\"yloc\":224,\"tileSize\":2,\"tileId\":0,\"flipTile\":false,\"vflipTile\":false}" \
                    ",{\"xloc\":80,\"yloc\":240,\"tileSize\":2,\"tileId\":1,\"flipTile\":false,\"vflipTile\":false}]"
        tilemaps_strr = self.maps_dict.tileMapEditor
        return json.loads(tilemaps_strr,
                          object_hook=self.decodeMapsJson)


    def loadAnimSeq(self, anim_seqs, sheet, terminators, anim_seq, ti, size):
        frames = []
        terminator = terminators[ti]
        ti += 1
        for frame in anim_seq:
            xloc = int(frame.xloc)
            yloc = int(frame.yloc)
            sprite = sm.surfaceFromImage(sheet, (xloc, yloc, size, size))
            frames.append(sprite)
        anim_seqs.append(AnimationSequence(frames, terminator))


    # Placeholder drawing
    def drawPlaceholder(self, sprite, color, rects):
        for rect in rects:
            pygame.draw.rect(sprite, color, rect)
            
    def loadScenery(self, idx, scenery : list):
        scenery.clear()
        scenery+=self.scenery[idx]
        

    def loadAnims(self, animations : dict):
        sheet = Image.open("data/master.bmp")
        sheet = sheet.convert("RGBA")

        for anim_data in self.anim_dict:
            anim_seqs = []
            size = int(anim_data.size)
            terminators = anim_data.terminators
            id = anim_data.id
            ti = 0
            if anim_data.placeholder:
                if not anim_data.complex:
                    frames = []
                    terminator = terminators[0]
                    for anim_seq in anim_data.sequences:
                        if not len(anim_data.rects):
                            color = anim_data.color
                        else:
                            color = "#00000100"
                        sprite = sm.surfaceFromPlaceholder(color, (0, 0, size, size))
                        self.drawPlaceholder(sprite, anim_data.color, anim_data.rects)
                        frames.append(sprite)
                        anim_seqs.append(AnimationSequence(frames, terminator))
                else:
                    frames = []
                    terminator = terminators[0]
                    for anim_seq in anim_data.sequences:
                        if len(anim_data.rects) > 0:
                            draw_polygon = False
                            for rect in anim_data.rects:
                                if len(rect) == 3:
                                    sprite = sm.surfaceFromPlaceholder((0,0,1), (0, 0, size, size))
                                    pygame.draw.circle(sprite, anim_data.color, (5,5), 5)
                                if len(rect) == 2:
                                    draw_polygon = True
                                    continue
                            if draw_polygon:
                                sprite = sm.surfaceFromPlaceholder((0, 0, 1), (0, 0, 16, 16))
                                pygame.draw.polygon(sprite, anim_data.color, anim_data.rects)
                            frames.append(sprite)
                        anim_seqs.append(AnimationSequence(frames, terminator))
            else:
                for anim_seq in anim_data.sequences:
                    self.loadAnimSeq(anim_seqs, sheet, terminators, anim_seq, ti, size)
                    ti += 1
            animations[id] = anim_seqs


    def __init__(self, filename):

        self.tiles_map = {}
        self.tile_sheets = []
        self.animations = {}
        tileset_keys = ["8x8", "16x16", "32x32"]
        self.tileset_keys = tileset_keys
        self.tileSets = defaultdict(list)

        maps_file = io.FileIO(filename, "r")
        self.maps_dict = json.load(maps_file,
                              object_hook=lambda d: SimpleNamespace(**d))
        maps_file.close()

        anim_file = io.FileIO("data/anims.json", "r")
        self.anim_dict = json.load(anim_file,
                              object_hook=lambda d: SimpleNamespace(**d))
                              
        scenery_file = io.FileIO("data/scenery.json", "r")
        self.scenery = json.load(scenery_file,
                              object_hook=lambda d: SimpleNamespace(**d))

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
