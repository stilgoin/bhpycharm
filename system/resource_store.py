from collections import defaultdict

import pygame

from game.maps import TileMap


class ResourceStore:
    tileMaps : list[TileMap]
    tileSets : dict[str, list[pygame.Surface]]
    animations : dict

    def __init__(self):
        self.tileMaps = []
        self.tileSets = defaultdict(list)
        self.animations = {}
