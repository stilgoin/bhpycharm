import uuid

from movers.events import MiscEvent
from movers.helpers.animation_state import AnimationState
from movers.movers import Mover
from system.defs import Id, Anim


class Goal(Mover):
    
    hitoffs = (0,-40,32,40)

    def check(self, floor_found, moverToBGFunc):
        pass

    def __init__(self, anim_init, id = Id.PLAYER.value, placeholder = False):
        self.animation_state = AnimationState(anim_init)
        self.id = id
        self.set_fall(0)
        self.set_anim_idx(Anim.STILL)
        self.events = []
        self.interaction_events = []
        self.placeholder = placeholder
        self.auuid = uuid.uuid4()

    def go(self):
        self.oldXloc = self.xloc
        self.oldYloc = self.yloc
        self.make_hitboxes()

class GoalKeeper(MiscEvent):

    gemsGathered = 0
    gemsVanished = 0
    gemsActive = 10
    targetsGathered = 0
    targetsVanished = 0
    targetsActive = 10

    goal : Goal = None
    def __init__(self, goal : Goal):
        self.goal = goal