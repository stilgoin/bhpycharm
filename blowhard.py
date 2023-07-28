
from game.Modes import GameMode

from system.Control import Control
from system.defs import *
from system.resload import ResourceLoader
from system.SurfaceManager import SurfaceManager
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
    sm = SurfaceManager(SCR_W, SCR_H)
    resloader.initMap(sm)
    game = GameMode()
    game.bghits = resloader.tileMaps[0].hitboxes
    resloader.initMoverAnims(game)


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
        resloader.drawAnims(sm, game)
        sm.drawScreen(pygame.display.get_surface() )
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()