import sys

from movers.movers import Mover, AnimationState, Id
from movers.mover_classes import PushingMover, InteractiveMover
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

    @property
    def ids(self):
        return Id

    def Init(self, anim_inits):
        self.mPlayer = PushingMover(anim_inits[self.ids.PLAYER], self.ids.PLAYER.value)
        self.movers.append(self.mPlayer)
        block = InteractiveMover(anim_inits[self.ids.BLOCK], self.ids.BLOCK.value)
        block.xloc = 0x40
        block.yloc = 0xA0
        InteractiveMover.movers.append(block)
        self.movers.append(block)


    def __init__(self):
        self.display_list = []
        self.movers = []
        self.push_movers = []
        self.interact_movers = []
        self.bghits = []

