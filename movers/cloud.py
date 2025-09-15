import uuid

from movers.blocks.block import Block
from movers.events import MiscEvent
from movers.helpers.animation_state import AnimationState
from movers.movers import Mover
from system.defs import Anim, Status


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

    cloud : Cloud = None
    block : Block = None

    def __init__(self, cloud : Cloud, block : Block):
        self.cloud = cloud
        self.block = block

    def run_event(self):
        if self.cloud.spawn_switch:
            self.cloud.spawn_switch = False
            self.cloud.spawn_enable = False
            self.block.xloc = self.cloud.xloc
            self.block.yloc = self.cloud.yloc
            self.block.move_state = 0
            self.block.set_fall(1.75)

        if self.block.move_state == Status.EXPIRED:
            self.block.xloc = 0xFF
            self.block.yloc = 0xFF
            self.cloud.spawn_enable = True



