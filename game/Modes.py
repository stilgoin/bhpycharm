import sys

from movers.InteractionListener import InteractionListener
from movers.movers import Mover, AnimationState, Id
from movers.mover_classes import PushingMover, InteractiveMover, Player, Statue
from game.Overlap import spriteToBG


class GameMode:

    loopcounter = 0
    output = ""
    def Loop(self, controls):
        self.loopcounter += 1
        self.display_list.clear()
        InteractionListener.evalInteractions()

        self.mPlayer.proc_input(controls)
        for mover in self.movers:
            if mover.id == Id.BLOCK.value:
                mover.proc_auto(controls)
            mover.go()

        for mover in self.movers:
            mover.make_hitboxes()
            floor_found, result = InteractionListener.moverToMovers(mover)
            mover.check(floor_found, moverToBGFunc = lambda : spriteToBG(mover, self.bghits))

        for mover in self.movers:
            self.display_list.extend(mover.animate())
            self.output += str(mover)

        #print("\rloops: " + str(self.output), end="")
        self.output = ""

        #sys.stdout.flush()

    @property
    def player_id(self):
        return Id.PLAYER

    @property
    def ids(self):
        return Id

    def Init(self, anim_inits):
        self.mPlayer = Player(anim_inits[self.ids.PLAYER], self.ids.PLAYER.value, False)
        self.mPlayer.xloc = 0x80
        self.mPlayer.yloc = 0xA0
        self.movers.append(self.mPlayer)
        block = InteractiveMover(anim_inits[self.ids.BLOCK], self.ids.BLOCK.value, False)
        block.xloc = 0xA0
        block.yloc = 0xA0
        block.test()
        InteractiveMover.movers.append(block)

        statue = Statue(anim_inits, anim_inits[self.ids.STATUE], self.ids.STATUE.value, True)
        statue.xloc = 0x80
        statue.yloc = 0x80
        #InteractiveMover.movers.append(statue)

        self.movers.append(block)
        #self.movers.append(statue)


    def __init__(self):
        self.display_list = []
        self.movers = []
        self.push_movers = []
        self.interact_movers = []
        self.bghits = []

