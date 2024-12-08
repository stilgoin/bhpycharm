import sys

from game.overlap import spriteToBG
from movers.AllMovers import AllMovers
from movers.blocks.block import Block
from movers.blocks.spring import SpringBox
from movers.bridge import BridgeSegment
from movers.interaction_listener import InteractionListener
from movers.mover_classes import InteractiveMover, MiscMover, Player
from movers.movers import Id
from system.defs import Facing


class GameMode:

    loopcounter = 0
    output = ""
    def Loop(self, controls):
        self.loopcounter += 1
        self.display_list.clear()


        self.mPlayer.procInput(controls)
        for mover in self.movers:
            if mover.id == Id.BLOCK.value:
                mover.proc_auto(controls)
            mover.procEvents()
            mover.go()
            mover.make_hitboxes()

        springs = list(filter(lambda item: item.id in (Id.SIDECOIL.value, Id.VERTCOIL), AllMovers.blocks) )
        for mover in self.movers:

            floor_found = False
            if mover.id == Id.PLAYER.value:
                floor_found, result = InteractionListener.moverToMovers(mover, AllMovers.blocks + self.interact_movers)

            if mover.id in (Id.BLOCK.value):
                floor_found, result = InteractionListener.moverToMovers(mover, springs + self.interact_movers)
            mover.check(floor_found, moverToBGFunc = lambda : spriteToBG(mover, self.bghits))

        for mover in MiscMover.postproc_movers:
            mover.misc_hitbox()
            mover.postproc()

        InteractionListener.evalInteractions()

        for mover in self.movers:
            mover.procInteractionEvents()
            self.display_list.extend(mover.animate())
            if mover.xvel > 0 and mover.id in (Id.PLAYER.value):
                self.output += str(mover)
            #if mover.xvel > 0.0:
            #    self.output += str(mover)
            #if mover.push_state == Push.ROLLBACK:
            #    self.output += str(mover)
        if self.output != "" and self.loopcounter % 10 == 0:
            pass
            print(str(self.output), end="\n")
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

        bridge = BridgeSegment(anim_inits[self.ids.BRIDGEPLAT], self.ids.BRIDGEPLAT.value, True)
        bridge.xloc = 0x70
        bridge.yloc = 0xC0
        self.movers.append(bridge)
        self.interact_movers.append(bridge)
        bridge = BridgeSegment(anim_inits[self.ids.BRIDGEPLAT], self.ids.BRIDGEPLAT.value, True)
        bridge.xloc = 0x80
        bridge.yloc = 0xC0
        self.movers.append(bridge)
        self.interact_movers.append(bridge)
        bridge = BridgeSegment(anim_inits[self.ids.BRIDGEPLAT], self.ids.BRIDGEPLAT.value, True)
        bridge.xloc = 0x90
        bridge.yloc = 0xC0
        self.movers.append(bridge)
        self.interact_movers.append(bridge)

        block = Block(anim_inits[self.ids.BLOCK], self.ids.BLOCK.value, False)
        block.xloc = 0x60
        block.yloc = 0x80
        block.test()
        #InteractiveMover.movers.append(block)
        self.movers.append(block)
        Block.movers.append(block)

        springbox = SpringBox(anim_inits, anim_inits[self.ids.SPRINGBOX], self.ids.SPRINGBOX.value, True,
                              facing=Facing.RIGHT)
        springbox.xloc = 0x10
        springbox.yloc = 0xA0
        springbox.spring.xloc = 0x20
        springbox.spring.yloc = 0xB0
        Block.movers.append(springbox)
        self.movers.append(springbox)
        Block.movers.append(springbox.spring)
        self.movers.append(springbox.spring)



    def __init__(self):
        self.display_list = []
        self.movers = []
        self.push_movers = []
        self.interact_movers = []
        self.bghits = []

