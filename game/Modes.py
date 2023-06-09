import sys

from movers.movers import Mover, AnimationState, Id
from game.Overlap import spriteToBG
class GameMode:

    loopcounter = 0
    output = ""
    def Loop(self, controls):
        self.loopcounter += 1
        self.display_list.clear()
        keys_this_frame, keys_last_frame, keys_pressed, keys_released = controls
        self.mPlayer.proc_input(controls)
        for mover in self.movers:
            display_entry = mover.go(
                moverToBGFunc = lambda : spriteToBG(mover, self.bghits)
            )
            self.display_list.append(display_entry)
            self.output += str(mover)
        print("\rloops: " + str(self.output), end="")
        self.output = ""

        #sys.stdout.flush()

    @property
    def player_id(self):
        return Id.PLAYER

    def Init(self, anim_init):
        self.mPlayer = Mover(anim_init)
        self.movers.append(self.mPlayer)

    def __init__(self):
        self.display_list = []
        self.movers = []
        self.bghits = []

