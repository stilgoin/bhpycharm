from game.overlap import spriteToBG
from movers.interactive_mover import InteractiveMover
from movers.movers import JUMPVEL
from system.defs import Events, Facing, Anim, Jump, PushAction, Id, Move

from math import floor, ceil

class Block(InteractiveMover):
    any_blocks = []
    friction = 0

    defaultPushAction = PushAction.SKID
    pcounterAction = defaultPushAction

    def __str__(self):
        return super().__str__()

    def setPushXVel(self):
        self.xvel = self.push_xvel

    def procInteractionEvents(self):
        if Events.HALT_PUSHING in self.interaction_events:
            self.xvel = 0.0
            self.xaccl = 0.0
            self.pcounterAction = self.defaultPushAction

        if Events.CONTINUE_PUSHING in self.interaction_events:
            pass
            #self.pcounter += 1
            #if self.pcounter == self.pcounterAction:
            #    self.xvel = self.push_xvel
            #self.xvel += self.xaccl
            #if self.xvel >= self.MAX_XVEL_PUSH:
            #    self.xvel = self.MAX_XVEL_PUSH

        elif Events.PUSH_TO_SKID in self.interaction_events:
            #if True:
            self.xaccl = -0.05
            self.xvel = 2.25
            self.max_xvel = self.MAX_XVEL_DASH
            print("Skid")

        if Events.MOVER_RECOIL in self.interaction_events:
            self.xvel = self.MAX_XVEL_DASH
            self.max_xvel = self.MAX_XVEL_DASH
            self.xaccl = 0.05
            self.direction *= -1
            
        if Events.MOVER_LEAVE_COIL in self.interaction_events:
            self.xaccl = -0.05
            #self.set_jump(1.25)

        self.interaction_events.clear()

    def procEvents(self):
        self.events.clear()

    def initPushing(self, direction, friction, xaccl, xvel=0):
        if not self.xvel:
            self.pcounter = 0
        if not self.pcounterAction.value:
            self.xaccl = xaccl
            self.xvel = xvel * friction
        else:
            self.xaccl = xaccl
            self.xvel = 1.0 if not self.xvel else self.xvel
        self.push_xvel = xvel * friction
        self.direction = direction
        if not friction:
            self.max_xvel = self.MAX_XVEL_PUSH
        else:
            self.max_xvel = self.MAX_XVEL_DASH
        #print("PUSHING")

    def go(self):
        super().go()
        snapped = False
        if self.snap_xloc > 0:
            if Facing.LEFT == self.direction and self.xloc <= self.snap_xloc:
                snapped = True
            if Facing.RIGHT == self.direction and self.xloc >= self.snap_xloc:
                snapped = True

            if snapped:
                self.xloc = self.snap_xloc
                self.xvel = 0.0
                self.xaccl = 0.0
                self.snap_xloc = 0
                if self.move_state == Move.GOAL:
                    self.move_state = Move.EXPIRED

    def move(self):
        super().move()

    def check(self, floor_found, moverToBGFunc, bighits = [], event_movers = []):

        floor_found = floor_found or moverToBGFunc()

        if floor_found and self.jump_state == Jump.FALL:
            self.jump_state = Jump.FLOOR
            self.yvel = 0.0
            self.jump_lock = False
            if not self.xvel:
                self.set_anim_idx(Anim.STILL)
            #else:
            #    self.set_anim_idx(Anim.WALK)

        if not floor_found and self.jump_state == Jump.FLOOR:
            self.xvel = 0.0
            self.xaccl = 0.0
            self.set_fall(JUMPVEL)
            self.set_anim_idx(Anim.STILL)

# Get it?  It's funny?
class BlockChain(Block):
    blocks : []
    blockchains = []
    anim_dict = {}
    auuid = 1
    save_xvel = 0
    save_xaccl = 0
    advancing_block : Block = None
    id = Id.BLOCKCHAIN.value
    floor_found_count = 0

    def __init__(self):
        self.interaction_events = []
        self.blocks = []
        # Todo: needed for bad inheritance bug.  Maybe get rid of
        self.events = []
        super().__init__(BlockChain.anim_dict, Id.BLOCKCHAIN.value, False)

    def go(self):

        self.oldXloc = self.xloc
        self.oldYloc = self.yloc

        if not len(self.blocks):
            self.move_state = Move.EXPIRED
            return

        for block in self.blocks:
            block.defaultPushAction = PushAction.SKID
            block.pcounterAction = PushAction.SKID
            block.oldXloc = block.xloc
            block.oldYloc = block.yloc

            if self.save_xvel > 0:
                if not block.xvel and block != self.advancing_block:
                    block.xvel = 0.5
                    block.xaccl  = 0.1

            block.move()
            block.make_hitboxes()
            #print(str(block))

        if self.save_xvel > 0:
            all_in_place = True
            for block in self.blocks:
                if block != self.advancing_block:
                    if block.direction == Facing.LEFT \
                        and block.xloc < self.advancing_block.xloc \
                        or block.direction == Facing.RIGHT \
                        and block.xloc > self.advancing_block.xloc:
                        block.xloc = self.advancing_block.xloc
                        block.xvel = 0
                        block.xaccl = 0

                if block.xloc != self.advancing_block.xloc:
                    all_in_place = False

            if all_in_place:
                for block in self.blocks:
                    block.set_fall(1.75)

            self.hitoffs = (0, 0, 0xF, 0xF)
        else:
            self.hitoffs = (0, 0, 0xF * len(self.blocks), 0xF)
        self.blocks = sorted(self.blocks, key=lambda block: block.xloc)
        self.setattr_singluar("xloc", self.blocks[0].xloc)
        self.setattr_singluar("yloc", self.blocks[0].yloc)
        self.setattr_singluar("xvel", self.blocks[0].xvel)
        self.setattr_singluar("yvel", self.blocks[0].yvel)
        self.setattr_singluar("xaccl", self.blocks[0].xaccl)
        self.blocks[len(self.blocks) - 1].xloc + 0xF

        self.make_hitboxes()

    def check_falling_chain(self, floor_found, moverToBGFunc
                            ,blockToGateCheck, bghits = []):

        floor_found = floor_found or moverToBGFunc()

        advancing_block : Block = None
        if self.xvel > 0:
            if self.direction == Facing.LEFT:
                advancing_block = self.blocks[0]
            else:
                advancing_block = self.blocks[len(self.blocks)-1]

        if advancing_block and not self.save_xvel:
            advancing_block.make_hitboxes()
            floor_found, result = blockToGateCheck(advancing_block)

            if result.mvb.id == Id.DISPOSAL.value:
                self.blocks.remove(advancing_block)
                for block in self.blocks:
                    block.xvel = 0
                    block.xaccl = 0
                    self.xvel = 0
                    self.xaccl = 0
            else:
                if not floor_found:
                    if not spriteToBG(advancing_block, bghits):
                        self.save_xvel = advancing_block.xvel
                        self.save_xaccl = advancing_block.xaccl
                        advancing_block.xvel = 0
                        advancing_block.xaccl = 0
                        self.advancing_block = advancing_block

        if self.save_xvel > 0:
            if spriteToBG(self.advancing_block, bghits):
                for block in self.blocks:
                    spriteToBG(block, bghits)
                offset = len(self.blocks) * 0x10
                if self.direction == Facing.LEFT:
                    offset *= -1
                self.advancing_block.snap_xloc = self.xloc + offset
                #self.advancing_block.xvel = 0.5
                #self.advancing_block.xaccl = 0.1
                self.save_xvel = 0
                self.advancing_block = None

                for block in self.blocks:
                    self.yvel = 0
                    self.yaccl = 0
                    self.jump_state = Jump.FLOOR
                    block.yvel = 0
                    block.yaccl = 0
                    block.jump_state = Jump.FLOOR

                if self.direction == Facing.RIGHT:
                    lent = int(floor(len(self.blocks) / 2 ))
                    bmid = int(ceil(len(self.blocks) / 2 ))
                    bi = 0
                    offs = lent
                    while bi < lent:
                        if lent == 1 and lent == bmid:
                            break
                        block = self.blocks[bi]
                        block.snap_xloc = int(block.xloc - (offs * 0x10))
                        block.xvel = 0.5
                        block.direction = Facing.LEFT
                        bi += 1
                        offs -= 1
                    bi = bmid
                    offs = 1
                    while bi < len(self.blocks):
                        block = self.blocks[bi]
                        block.snap_xloc = int(block.xloc + (offs * 0x10))
                        block.xvel = 0.5
                        block.direction = Facing.RIGHT
                        offs += 1
                        bi += 1
        """
        if floor_found and self.jump_state == Jump.FALL:
            self.jump_state = Jump.FLOOR
            self.yvel = 0.0
            self.jump_lock = False
            if not self.xvel:
                self.set_anim_idx(Anim.STILL)
            #else:
            #    self.set_anim_idx(Anim.WALK)

        if not floor_found and self.jump_state == Jump.FLOOR:
            self.xvel = 0.0
            self.xaccl = 0.0
            self.set_fall(JUMPVEL)
            self.set_anim_idx(Anim.STILL)
        """

    #def initPushing(self, direction, friction, xaccl, xvel=0):
    #    for block in self.blocks:
    #        block.initPushing(direction, friction, xaccl, xvel)

    def procInteractionEvents(self):

        if self.advancing_block:
            return

        for block in self.blocks:
            block.interaction_events.extend(self.interaction_events)
            block.procInteractionEvents()
        super().procInteractionEvents()
        self.interaction_events.clear()

    def setattr_singluar(self, name, value):
        self.__dict__[name] = value

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        
        if "blocks" not in self.__dict__.keys():
            return

        if name in ("xvel", "yvel", \
                    "xaccl", "yaccl", "max_xvel", "direction", "facing"
                    , "push_xvel", "pcounterAction", "pcounter"):
            for block in self.blocks:
                block.__dict__[name] = value

        offset = 0
        if name in ("xloc"):
            for block in self.blocks:
                block.__dict__[name] = value + offset
                offset += 0x10