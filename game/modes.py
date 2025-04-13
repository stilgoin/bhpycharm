import sys

from game.overlap import spriteToBG
from movers.blocks.block import Block
from movers.blocks.spring import SpringBox
from movers.interaction_listener import InteractionListener
from movers.mover_classes import MiscMover, Player
from movers.movers import Id, Mover
from system.defs import Facing


class GameMode:
    loopcounter = 0
    output = ""

    def Loop(self, controls):
        self.loopcounter += 1
        self.display_list.clear()

        self.mPlayer.procInput(controls)

        springs = list(filter(lambda item: item.id in (Id.SIDECOIL.value, Id.VERTCOIL), Block.movers))

        for mover in self.movers:
            mover.go()

        for mover in self.movers:

            floor_found = False
            if mover.id == Id.PLAYER.value:
                floor_found, result = InteractionListener.moverToMovers(mover, Block.movers + self.interact_movers)

            if mover.id in (Id.BLOCK.value):
                floor_found, result = InteractionListener.moverToMovers(mover, springs + self.interact_movers)
            mover.check(floor_found, moverToBGFunc=lambda: spriteToBG(mover, self.bghits))

        for mover in MiscMover.postproc_movers:
            pass
            #mover.misc_hitbox()
            #mover.postproc()

        # self.output += \
        InteractionListener.evalInteractions()

        for mover in self.movers:
            mover.procInteractionEvents()
            self.display_list.extend(mover.animate())
            if mover.xvel > 0 and mover.id in (Id.PLAYER.value, Id.BLOCK.value, Id.SIDECOIL.value):
                self.output += str(mover) + "\n"
            # if mover.xvel > 0.0:
            #    self.output += str(mover)
            # if mover.push_state == Push.ROLLBACK:
            #    self.output += str(mover)
        if self.output != "" and self.loopcounter % 1 == 0:
            pass
            print(str(self.output), end="\n")
            print("----------------------------")
        self.output = ""
        sys.stdout.flush()

    @property
    def player_id(self):
        return Id.PLAYER

    @property
    def ids(self):
        return Id

    """TODO: Replace with JSON data to load spawn positions of Movers based on round
    """

    def Init(self, anim_inits):
        self.mPlayer = Player(anim_inits[self.ids.PLAYER], self.ids.PLAYER.value, False)
        self.mPlayer.xloc = 0x80
        self.mPlayer.yloc = 0xA0
        Player.movers.append(self.mPlayer)
        self.movers.append(self.mPlayer)

        hinge = Mover(anim_inits[self.ids.HINGE], self.ids.HINGE.value, True)
        hinge.xloc = 0x60
        hinge.yloc = 0x60
        self.movers.append(hinge)

        gate = Mover(anim_inits[self.ids.GATE], self.ids.GATE.value, True)
        gate.xloc = 0x80
        gate.default_xloc = 0x80
        gate.yloc = 0xA0
        self.movers.append(gate)

        rightgate = Mover(anim_inits[self.ids.GATERIGHT], self.ids.GATERIGHT.value, True)
        rightgate.xloc = 0x90
        rightgate.default_xloc = 0x90
        rightgate.yloc = 0xA0
        rightgate.default_yloc = 0xA0
        self.movers.append(rightgate)

        block = Block(anim_inits[self.ids.BLOCK], self.ids.BLOCK.value, False)
        block.xloc = 0x60
        block.yloc = 0xc0
        block.test()
        # InteractiveMover.movers.append(block)
        self.movers.append(block)
        Block.movers.append(block)

        block2 = Block(anim_inits[self.ids.BLOCK], self.ids.BLOCK.value, False)
        block2.xloc = 0x60
        block2.yloc = 0x80
        block2.test()
        # InteractiveMover.movers.append(block)
        self.movers.append(block2)
        Block.movers.append(block2)

        springbox = SpringBox(anim_inits, anim_inits[self.ids.SPRINGBOX], self.ids.SPRINGBOX.value, True,
                              facing=Facing.RIGHT)
        springbox.xloc = 0x10
        springbox.yloc = 0xA0
        springbox.spring.xloc = 0x20
        springbox.spring.yloc = 0xB0
        springbox.spring.default_xloc = 0x20
        # Block.movers.append(springbox)
        self.movers.append(springbox)
        Block.movers.append(springbox.spring)
        self.movers.append(springbox.spring)

    def __init__(self):
        self.display_list = []
        self.movers = []
        self.push_movers = []
        self.interact_movers = []
        self.bghits = []
