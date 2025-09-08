import sys

import pygame

from game.overlap import spriteToBG, overlap
from movers.blocks.block import Block
from movers.blocks.spring import SpringBox, SideSpring
from movers.events import MiscEvent
from movers.gate import Gate, TrapDoorManager
from movers.goal import Goal, GoalKeeper
from movers.interaction_listener import InteractionListener
from movers.mover_classes import MiscMover, Player
from movers.movers import Id, Mover
from system.defs import Facing, TrapDoorStates, Move


class GameMode:
    loopcounter = 0
    output = ""

    misc_events : [MiscEvent]

    goal_keeper : GoalKeeper

    def Loop(self, controls, surface : pygame.Surface):
        self.loopcounter += 1
        self.display_list.clear()

        self.mPlayer.procInput(controls)

        springs = list(filter(lambda item: item.id in (Id.SIDECOIL.value, Id.VERTCOIL), Block.any_blocks))

        blocks = list(filter(lambda item: item.id in (Id.BLOCK.value), Block.any_blocks))

        for misc_event in self.misc_events:
            misc_event.run_event()

        """ All movers must "go" before checking interactions
        """
        for mover in self.movers:
            mover.go()

        for mover in self.movers:

            floor_found = False
            if mover.id == Id.PLAYER.value:
                floor_found, result = InteractionListener.moverToMovers(mover, Block.any_blocks + self.event_movers)

            if mover.id in (Id.BLOCK.value):
                floor_found, result = InteractionListener.blockToBlocks(mover, blocks)

                if not floor_found:
                    floor_found, result = InteractionListener.moverToMovers(mover, springs + self.event_movers)


                if mover.move_state != Move.GOAL:
                    if overlap(mover.hb, self.goal_keeper.goal.hb):
                        mover.move_state = Move.GOAL

            if mover.id not in (Id.GOAL.value):
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

        gates = []

        for mover_data in mover_datas:
            addToMovers = True
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

                self.event_movers.append(new_mover)
                gates.append(new_mover)

                if len(gates) == 2:
                    self.misc_events.append(TrapDoorManager(gates) )
                    #self.misc_events[len(self.misc_events)-1].move_state = TrapDoorStates.DROP_UPPER
                    gates = []

            if "goal" == mover_data.id:
                new_mover = Goal(anim_inits[Id.GOAL], Id.GOAL.value, True)
                #self.misc_events.append(GoalKeeper())
                self.goal_keeper = GoalKeeper(new_mover)

            new_mover.xloc = mover_data.xloc
            new_mover.yloc = mover_data.yloc

            if mover_data.id in ["sidecoil", "springbox", "block"]:
                Block.any_blocks.append(new_mover)

            if addToMovers:
                self.movers.append(new_mover)

    def __init__(self):
        self.display_list = []
        self.movers = []
        self.push_movers = []
        self.event_movers = []
        self.bghits = []
        self.misc_events = []
