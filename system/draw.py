import pygame

from game.maps import MapLayer, TilePlacement, TileMap, Hitbox
from game.modes import GameMode
from system.surface_manager import SurfaceManager as sm, Surfaces

def drawAnims(surfMgmt : sm, game : GameMode,
              animations: dict):
    surfMgmt.clearSpriteSurf()
    display_list = game.display_list
    for entry in display_list:
        if 0xFF == entry.frameIdx:
            continue
        animation = animations[entry.id]
        sprite = animation[entry.animIdx].frames[entry.frameIdx]
        xloc = entry.xloc
        yloc = entry.yloc
        sprite = pygame.transform.rotate(sprite, entry.angle)
        sprite = pygame.transform.flip(sprite, entry.fliph, entry.flipv)
        surfMgmt.drawSprite(sprite, xloc, yloc)

def initMoverAnims(game : GameMode, animations : dict):
    anim_inits = {}
    for id in game.ids:
        #anim_seqs = self.animations[game.player_id.value]
        anim_seqs = animations[id.value]
        maxFrames = []
        terminators = []
        for anim_seq in anim_seqs:
            maxFrames.append(len(anim_seq.frames) )
            terminators.append(anim_seq.terminator)
        anim_inits[id] = (maxFrames, terminators)
    game.Init( anim_inits )

def initMap(surfMgmt : sm,
            tileMaps : list[TileMap],
            tileSets : dict[str, list[pygame.Surface]],
            scenery : list,
            mapIdx : int = 0):
    layer : MapLayer
    tipl : TilePlacement
    tileset_keys = ["8x8", "16x16", "24x24", "32x32"]
    tileMap = tileMaps[mapIdx]
    tileSurf : pygame.Surface
    
    for shape in scenery:
        surf = sm.surfaceFromPlaceholder(shape.color, (0,0,shape.width,shape.height))
        surfMgmt.blitSurface(Surfaces.MAP.value, surf, (shape.xloc, shape.yloc) )
        hb = Hitbox()
        hb.x0 = shape.xloc
        hb.x1 = shape.xloc + shape.width
        hb.y0 = shape.yloc
        hb.y1 = shape.yloc + shape.height
        hb.solid = shape.collision
        tileMap.hitboxes.append(hb)
    
    for layer in tileMap.layers:
        for tipl in layer.tile_placements:
            tkey = tileset_keys[tipl.tileSize - 1]
            tileSurf = tileSets[tkey][tipl.tileId]
            xloc = tipl.xloc
            yloc = tipl.yloc
            #surfMgmt.blitSurface(Surfaces.MAP.value, tileSurf, (xloc, yloc) )

