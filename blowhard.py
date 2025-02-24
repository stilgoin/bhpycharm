
from game.modes import GameMode
from system import draw

from system.control import Control
from system.defs import *
from system.resload import ResourceLoader
from system.resource_store import ResourceStore
from system.surface_manager import SurfaceManager
def main():
    pygame.mixer.pre_init(96000, -16, 4, 4096)
    pygame.init()
    pygame.font.init()
    font_obj = pygame.font.SysFont("arial",14)

    pyg_screen = \
        pygame.display.set_mode( (SCALE_W, SCALE_H) )

    pygame.display.set_caption("Blowhard")
    pygame.mouse.set_visible(0)
    pygame.key.set_repeat(True)
    pyg_screen.set_colorkey( BG_CLEAR )
    pyg_clock = pygame.time.Clock()
    control = Control()

    resloader = ResourceLoader("data/try.bin")
    resource_store = ResourceStore()
    resloader.loadAnims(resource_store.animations)
    resource_store.tileMaps = resloader.loadTileMaps()
    resloader.loadTilesets(resource_store.tileSets)

    sm = SurfaceManager(SCR_W, SCR_H)
    draw.initMap(sm, resource_store.tileMaps,
                 resource_store.tileSets, 0)
    game = GameMode()
    game.bghits = resource_store.tileMaps[0].hitboxes
    draw.initMoverAnims(game, resource_store.animations)


    running = True
    while running:
        pyg_clock.tick(60)

        pyg_screen.fill((BG_FILL))

        for event in pygame.event.get():
            if QUIT == event.type:
                running = False
                break

        if not running:
            break

        control.control(pygame)
        game.Loop(control.controls)
        draw.drawAnims(sm, game, resource_store.animations)
        sm.drawScreen(pygame.display.get_surface() )
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()