from movers.blocks.block import Block


class Stack:
    stacks : [] = []
    blocks : []
    expired = False

    def __init__(self):
        self.blocks = []

    @property
    def top_block(self) -> Block:
        if not len(self.blocks):
            raise Exception("Uh you have a stack with no blocks")

        return self.blocks[0]

    @classmethod
    def run_stacks(self):
        for stack in self.stacks:
            bie = len(stack.blocks) - 1
            if bie <= 0:
                raise Exception("Stack with no blocks - how did we get here?")
            base_block : Block = stack.blocks[bie]
            bi = 0
            while bi < len(stack.blocks) - 1:
                block : Block = stack.blocks[bi]
                if not block.snap_xloc:
                    block.xvel = base_block.xvel
                    block.xaccl = base_block.xaccl
                    block.yvel = base_block.yvel
                    block.yaccl = base_block.yaccl
                    block.direction = base_block.direction
                bi += 1


