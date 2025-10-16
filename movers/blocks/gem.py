from movers.blocks.block import Block
from system.defs import Facing, Anim


class Gem(Block):

    def __init__(self, anim_init, id, placeholder, facing=Facing.LEFT):
        super().__init__(anim_init, id, placeholder)
        self.facing = facing
        self.set_anim_idx(Anim.STILL)
