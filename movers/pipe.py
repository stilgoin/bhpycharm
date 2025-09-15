import uuid

from movers.helpers.animation_state import AnimationState
from movers.interactive_mover import InteractiveMover
from system.defs import Anim


class Pipe(InteractiveMover):

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