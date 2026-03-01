import uuid

from movers.blocks.block import Block
from movers.events import MiscEvent
from movers.helpers.animation_state import AnimationState
from movers.movers import Mover
from system.defs import Anim, Status, Id


class Cloud(Mover):

    spawn_switch = False
    spawn_enable = True

    def __init__(self, anim_init, id, placeholder = False):
        self.animation_state = AnimationState(anim_init)
        self.id = id
        self.set_anim_idx(Anim.STILL)
        self.events = []
        self.interaction_events = []
        self.placeholder = placeholder
        self.auuid = uuid.uuid4()

    def check(self, floor_found, moverToBGFunc):
        pass

class SpawnBlock(MiscEvent):

    mover : Mover = None
    block : Block = None

    def __init__(self, mover : Mover, block : Block):
        self.mover = mover
        self.block = block

    def run_event(self):
        if self.mover.spawn_switch:
            self.mover.spawn_switch = False
            self.mover.spawn_enable = False
            self.block.xloc = self.mover.xloc
            self.block.yloc = self.mover.yloc
            self.block.move_state = 0
            self.block.set_fall(1.75)

            if self.mover.id != Id.CLOUD.value:
                self.mover.xloc = 0xFFFF
                self.mover.yloc = 0xFFFF

        if self.block.move_state == Status.EXPIRED:
            self.block.xloc = 0xFFFF
            self.block.yloc = 0xFFFF
            self.mover.spawn_enable = True



