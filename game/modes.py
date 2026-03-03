import sys

import pygame

from game.overlap import spriteToBG, overlap
from movers.blocks.block import Block, BlockNode
from movers.blocks.gem import Gem
from movers.blocks.spring import SpringBox, SideSpring
from movers.breath import Breath
from movers.cloud import Cloud, SpawnBlock
from movers.events import MiscEvent
from movers.gate import Gate, TrapDoorManager
from movers.goal import Goal, GoalKeeper
from movers.interaction_listener import InteractionListener
from movers.mover_classes import Player
from movers.movers import Id
from movers.pipe import Pipe
from movers.ramp import Ramp
from system.defs import Facing, Move, Terminators


class GameMode:
    loopcounter = 0
    output = ""

    misc_events : [MiscEvent]

    goal_keeper : GoalKeeper

    breath = None

    def loop(self, controls, surface : pygame.Surface):
        self.loopcounter += 1
        self.display_list.clear()

        if self.mPlayer.procInput(controls):
            self.breath.xloc = self.mPlayer.xloc
            self.breath.yloc = self.mPlayer.yloc
            self.breath.xvel = 2.5
            self.breath.yvel = 0
            self.breath.xaccl = -0.05
            self.breath.max_xvel = 3.5
            self.breath.direction = self.mPlayer.facing

        self.movers = list(filter(lambda mover: mover.move_state != Terminators.EXPIRE, self.movers))

        springs = list(filter(lambda item: item.id in (Id.SIDECOIL.value, Id.VERTCOIL), Block.any_blocks))

        blocks = list(filter(lambda item: item.id in (Id.BLOCK.value, Id.GEM.value), Block.any_blocks))

        for misc_event in self.misc_events:
            misc_event.run_event()
            """
            if "SpawnBlock" in str(type(misc_event)):
                if controls[3] & Key.FIRE:
                    spawn_block : SpawnBlock = misc_event
                    spawn_block.cloud.spawn_switch = True
                    spawn_block.run_event()
            """


        """ All movers must "go" before checking interactions
        """
        for mover in self.movers:
            mover.go()

        for mover in self.movers:

            floor_found = False
            if mover.id == Id.PLAYER.value:
                floor_found, result = InteractionListener.moverToMovers(mover, Block.any_blocks + self.event_movers, BlockNode.nodes)

            """
            if mover.id == Id.BREATH.value:
                check_movers = list(filter(lambda item: item.id in (Id.GEM.value), Block.any_blocks))
                check_movers += list(filter(lambda item: item.id in (Id.CLOUD.value), self.movers))
                spawn_events = list(filter(lambda item: "SpawnBlock" in str(type(item)), self.misc_events))
                floor_found, result = InteractionListener.moverToMovers(mover, check_movers, BlockNode.nodes, spawn_events)
            """

            if mover.id in (Id.BLOCK.value, Id.GEM.value):
                floor_found, result = InteractionListener.blockToBlocks(mover, BlockNode.nodes)

                if not floor_found:
                    floor_found, result = InteractionListener.moverToMovers(mover, springs + self.event_movers, BlockNode.nodes)

                if mover.move_state != Move.GOAL:
                    if overlap(mover.hb, self.goal_keeper.goal.hb):
                        mover.move_state = Move.GOAL

            if mover.id not in (Id.GOAL.value):
                mover.check(floor_found, moverToBGFunc=lambda: spriteToBG(mover, self.bghits))

        # self.output += \
        InteractionListener.evalInteractions(BlockNode.nodes)

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

        #InteractionListener.evalBlockNodes(BlockNode.nodes)

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

    def init(self, anim_inits : dict, movers_dict : dict, moversIdx = 0):

        self.movers.clear()
        Block.any_blocks.clear()
        BlockNode.nodes.clear()
        self.misc_events.clear()
        self.event_movers.clear()

        self.mPlayer = Player(anim_inits[self.ids.PLAYER], self.ids.PLAYER.value, False)
        self.mPlayer.xloc = 0x80
        self.mPlayer.yloc = 0x50
        Player.movers.append(self.mPlayer)
        self.movers.append(self.mPlayer)

        mover_datas = movers_dict[moversIdx]

        gates = []

        new_mover = Breath(anim_inits[self.ids.BREATH], Id.BREATH.value, False)
        new_mover.xloc = 0xFFFF
        new_mover.yloc = 0xFFFF
        self.breath = new_mover
        self.movers.append(new_mover)

        for mover_data in mover_datas:
            addToMovers = True
            if "cloud" == mover_data.id:
                new_mover = Cloud(anim_inits[self.ids.CLOUD], self.ids.CLOUD.value, False)
                new_block = Block(anim_inits[self.ids.BLOCK], self.ids.BLOCK.value, False)
                new_block.xloc = 0xFFFF
                new_block.yloc = 0xFFFF
                new_event = SpawnBlock(new_mover, new_block)
                self.misc_events.append(new_event)
                Block.any_blocks.append(new_block)
                self.movers.append(new_block)

            if "block" == mover_data.id:
                new_mover = Block(anim_inits[self.ids.BLOCK], self.ids.BLOCK.value, False)
                BlockNode.nodes.append(BlockNode(new_mover))
            if "gem" == mover_data.id:
                new_mover = Gem(anim_inits[self.ids.GEM], self.ids.GEM.value, False)
                new_block = Block(anim_inits[self.ids.BLOCK], self.ids.BLOCK.value, False)
                new_block.xloc = 0xFFFF
                new_block.yloc = 0xFFFF
                new_event = SpawnBlock(new_mover, new_block)
                self.misc_events.append(new_event)
                Block.any_blocks.append(new_block)
                Block.any_blocks.append(new_mover)
                self.movers.append(new_block)
                BlockNode.nodes.append(BlockNode(new_mover))
            if "pipe" == mover_data.id:
                new_mover = Pipe(anim_inits[self.ids.DISPOSAL], self.ids.DISPOSAL.value, False)
                self.event_movers.append(new_mover)
            if "ramp" == mover_data.id:
                new_mover = Ramp(anim_inits[self.ids.RAMP], self.ids.RAMP.value, False)
                self.event_movers.append(new_mover)

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

            if mover_data.id in ["sidecoil", "springbox", "block", "gem"]:
                Block.any_blocks.append(new_mover)

            if addToMovers:
                self.movers.append(new_mover)

    def __init__(self):
        self.display_list = []
        self.movers = []
        self.event_movers = []
        self.bghits = []
        self.misc_events = []
