from movers.movers import Mover
from game.Overlap import moverToMover

class PushingMover(Mover):

    movers = []

    def moverToMovers(self):

        for interact_mover in InteractiveMover.movers:
            moverToMover(self, interact_mover)

    def __init__(self, anim_init, id):
        super().__init__(anim_init, id)

class InteractiveMover(Mover):

    movers = []

    hitoffs = (0, 0, 15, 15)

    def __init__(self, anim_init, id):
        super().__init__(anim_init, id)

