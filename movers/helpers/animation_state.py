from movers.helpers.display_entry import DisplayEntry
from system.defs import Terminators, Tick, Id


class AnimationState:
    animIdx = 0
    frameTicks = 0
    maxFrames = 0

    def __str__(self):
        return "animIdx: " + str(self.animIdx) + ", frameTicks: " + str(self.frameTicks)


    def process_terminator(self):
        terminator = self.terminators[self.animIdx]
        if terminator == Terminators.HOLD:
            return self.maxFrames[self.animIdx] - 1
        if terminator == Terminators.REPEAT:
            self.frameTicks = 0
            return 0
        if terminator == Terminators.EXPIRE:
            return Terminators.EXPIRE
    @property
    def current_frame(self):
        frameIdx = int(self.frameTicks / Tick.DELAY)
        if frameIdx >= self.maxFrames[self.animIdx]:
            return self.process_terminator()
        return frameIdx

    def set_anim_idx(self, animIdx):
        self.animIdx = animIdx
        self.frameTicks = 0

    def check_anim_idx(self, animIdx) -> bool:
        return self.animIdx == animIdx

    def display_entry(self, id, xloc, yloc, fliph = False, flipv = False, angle = 0.0):
        frameIdx = self.current_frame
        if id == Id.BLOCK.value:
            fliph = False
        return DisplayEntry(id=id, animIdx=self.animIdx,
                            frameIdx=frameIdx, xloc=xloc, yloc=yloc,
                            fliph=fliph, flipv=flipv, angle=angle)

    def add_frameticks(self):
        self.frameTicks += 1

    def __init__(self, anim_init):
        maxFrames, terminators = anim_init
        self.maxFrames = maxFrames
        self.terminators = terminators