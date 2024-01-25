import sys

from movers.AllMovers import AllMovers
from movers.Block import Block, Statue
from movers.InteractionListener import InteractionListener
from movers.movers import Mover, AnimationState, Id
from movers.mover_classes import PushingMover, InteractiveMover, MiscMover, Player
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
            mover.make_hitboxes()

        InteractionListener.evalTerminations()

        for mover in self.movers:

            floor_found = False
            if mover.id == Id.PLAYER.value:
                floor_found, result = InteractionListener.moverToMovers(mover, AllMovers.blocks)
            mover.check(floor_found, moverToBGFunc = lambda : spriteToBG(mover, self.bghits))

        for mover in MiscMover.postproc_movers:
            mover.misc_hitbox()
            mover.postproc()




        for mover in self.movers:
            self.display_list.extend(mover.animate())
            if mover.xvel > 0.0:
                self.output += str(mover)
        if self.output != "":
            print(str(self.output), end="\n")
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
        PushingMover.movers.append(self.mPlayer)

        self.movers.append(self.mPlayer)
        block = InteractiveMover(anim_inits[self.ids.BLOCK], self.ids.BLOCK.value, False)
        block.xloc = 0x80
        block.yloc = 0x80
        block.test()
        #InteractiveMover.movers.append(block)
        #self.movers.append(block)

        statue = Statue(anim_inits, anim_inits[self.ids.STATUE], self.ids.STATUE.value, True)
        statue.xloc = 0x80
        statue.yloc = 0x80
        statue.test()
        Block.movers.append(statue)
        self.movers.append(statue)





    def __init__(self):
        self.display_list = []
        self.movers = []
        self.push_movers = []
        self.interact_movers = []
        self.bghits = []

