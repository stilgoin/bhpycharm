import sys

import pygame

from game.overlap import spriteToBG
from movers.blocks.block import Block
from movers.blocks.spring import SpringBox, SideSpring
from movers.gate import Gate
from movers.interaction_listener import InteractionListener
from movers.mover_classes import MiscMover, Player
from movers.movers import Id, Mover
from system.defs import Facing


class GameMode:
    loopcounter = 0
    output = ""

    def Loop(self, controls, surface : pygame.Surface):
        self.loopcounter += 1
        self.display_list.clear()

        self.mPlayer.procInput(controls)

        springs = list(filter(lambda item: item.id in (Id.SIDECOIL.value, Id.VERTCOIL), Block.movers))

        """ All movers must "go" before checking interactions
        """
        for mover in self.movers:
            mover.go()

        for mover in self.movers:

            floor_found = False
            if mover.id == Id.PLAYER.value:
                floor_found, result = InteractionListener.moverToMovers(mover, Block.movers + self.interact_movers)

            if mover.id in (Id.BLOCK.value):
                floor_found, result = InteractionListener.moverToMovers(mover, springs + self.interact_movers)
            mover.check(floor_found, moverToBGFunc=lambda: spriteToBG(mover, self.bghits))

        # self.output += \
        InteractionListener.evalInteractions()

        for mover in self.movers:
            mover.procInteractionEvents()
            self.display_list.extend(mover.animate())
            if mover.xvel > 0 and mover.id in (Id.PLAYER.value, Id.BLOCK.value, Id.SIDECOIL.value):
                self.output += str(mover) + "\n"
            """ Debug:  Draw hitboxes
            """
            #pygame.draw.rect(surface, "#FF0000FF", (mover.hb.x0,mover.hb.y0,mover.hb.width,mover.hb.height))
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

    def Init(self, anim_inits : dict, movers_dict : dict):
        self.mPlayer = Player(anim_inits[self.ids.PLAYER], self.ids.PLAYER.value, False)
        self.mPlayer.xloc = 0x80
        self.mPlayer.yloc = 0xA0
        Player.movers.append(self.mPlayer)
        self.movers.append(self.mPlayer)

        mover_datas = movers_dict[0]

        for mover_data in mover_datas:
            if "block" == mover_data.id:
                new_mover = Block(anim_inits[self.ids.BLOCK], self.ids.BLOCK.value, False)
            if "springbox" == mover_data.id:
                new_mover = SpringBox(anim_inits, anim_inits[self.ids.SPRINGBOX], self.ids.SPRINGBOX.value, True,
                              facing=Facing.RIGHT)
            if "sidecoil" == mover_data.id:
                new_mover = SideSpring(anim_inits[Id.SIDECOIL], Id.SIDECOIL.value, True
                               , facing = Facing.RIGHT if mover_data.facing == 1 else Facing.LEFT)
                new_mover.default_xloc = mover_data.xloc

            if "gate" == mover_data.id:
                new_mover = Gate(anim_inits[Id.GATE], Id.GATE.value, True
                                , facing = Facing.RIGHT if mover_data.facing == 1 else Facing.LEFT)
                new_mover.default_xloc = mover_data.xloc
                new_mover.default_yloc = mover_data.yloc

                self.interact_movers.append(new_mover)

            new_mover.xloc = mover_data.xloc
            new_mover.yloc = mover_data.yloc

            if mover_data.id in ["sidecoil", "springbox", "block"]:
                Block.movers.append(new_mover)

            self.movers.append(new_mover)

    def __init__(self):
        self.display_list = []
        self.movers = []
        self.push_movers = []
        self.interact_movers = []
        self.bghits = []
