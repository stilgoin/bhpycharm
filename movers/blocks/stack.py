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