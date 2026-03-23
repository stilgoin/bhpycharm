from movers.helpers.animation_state import AnimationState
from movers.helpers.display_entry import DisplayEntry
from system.defs import *
from game.maps import Hitbox
from game.overlap import OverlapResult

import uuid

JUMPVEL = 1.75
GRAVITY = .046875

class Mover:
    xloc = 0.0
    yloc = 0.0
    xvel = 0.0
    yvel = 0.0
    xaccl = 0.0
    yaccl = 0.0
    snap_xloc = 0.0
    snap_yloc = 0.0
    base_xaccl = 0.1
    friction = 1
    max_pvel = 0.5
    MAX_PVEL_CONST = 0.5
    MAX_XVEL_WALK = 1.25
    MAX_XVEL_DASH = 3.25
    MAX_XVEL_PUSH = 1.0
    max_xvel = 1.0
    max_dvel = 2.5
    hitoffs = (0, 0, 15, 15)
    id = ""
    angle = 0.0

    move_state = 0
    push_state = 0
    jump_state = 0
    onFallPlat = False
    action_timer = 0
    jump_lock = False
    facing = Facing.LEFT
    direction = Facing.LEFT
    vertical = Vertical.UP
    holding = 0
    lock = 0

    angle = 0

    placeholder = False

    hb = Hitbox(0.0, 0.0, (0, 0, 0, 0))
    phb = Hitbox(0.0, 0.0, (0, 0, 0, 0))

    spawn_switch = False
    spawn_enable = True

    def __str__(self):
        #return str(self.animation_state)
        return f"id: {self.id} xloc: %.4f xvel: %.4f, xaccl: %.4f move: {self.move_state} push: {self.push_state} \
holding {self.holding} max_xvel {self.max_xvel} facing {self.facing} dir {self.direction} \"" \
               f"events {self.events}" % \
            (self.xloc, self.xvel, self.xaccl)

    def set_jump(self, yvel):
        self.jump_state = Jump.JUMP
        self.vertical = Vertical.UP
        self.yvel = yvel

    def set_fall(self, yvel):
        self.jump_state = Jump.FALL
        self.vertical = Vertical.DOWN
        self.yvel = yvel

    def moverToMovers(self):
        return False, OverlapResult()

    def checkEvents(self):
        pass

    def haltMovement(self):
        self.move_state = 0
        self.push_state = 0
        self.xvel = 0.0
        self.xaccl = 0.0

    def procEvents(self):
        pass

    def procInteractionEvents(self):
        pass

    def move(self):
        self.xloc += (self.xvel * self.direction)
        self.yloc += (self.yvel * self.vertical)

        self.xvel += self.xaccl

        if self.xvel > self.max_xvel:
            self.xvel = self.max_xvel

        if self.xaccl < 0:
            if self.xvel < self.MAX_XVEL_WALK:
                self.max_xvel = self.MAX_XVEL_WALK

        #if self.id == Id.BLOCK.value and self.xaccl != 0:
        #    print(self.xvel,self.xaccl)

        if self.xvel <= 0.0:
            self.xvel = 0.0
            self.xaccl = 0.0
            self.max_xvel = self.MAX_XVEL_WALK
            if Events.MIN_XVEL not in self.events:
                self.events.append(Events.MIN_XVEL)
            #if self.push_state == Push.STILL:
            #    self.move_state = Status.NEUTRAL

        if self.jump_state == Jump.JUMP:
            self.yvel -= GRAVITY
            if self.yvel < 0.0:
                self.set_fall(1.75)
                self.set_anim_idx(Anim.STILL)

    def anim_state(self):
        if self.jump_state == Jump.FLOOR:
            self.animation_state.set_anim_idx(0)

    def set_anim_idx(self, state):
        self.animation_state.set_anim_idx(state)

    def go(self):
        self.procEvents()
        self.animation_state.add_frameticks()

        self.oldXloc = self.xloc
        self.oldYloc = self.yloc
        self.move()
        
        self.make_hitboxes()


    def make_hitboxes(self):
        self.hb = Hitbox(self.xloc, self.yloc,
                         self.hitoffs)
        self.phb = Hitbox(self.oldXloc, self.oldYloc,
                          self.hitoffs)

    def check(self, floor_found, moverToBGFunc):

        #floor_found, result = self.moverToMovers()

        floor_found = floor_found or moverToBGFunc()

        if floor_found and self.onFallPlat:
            moverToBGFunc()

        if floor_found and self.jump_state == Jump.FALL:
            self.jump_state = Jump.FLOOR
            self.yvel = 0.0
            self.jump_lock = False
            if not self.xvel:
                self.set_anim_idx(Anim.STILL)
            else:
                self.set_anim_idx(Anim.WALK)

        if not floor_found and self.jump_state == Jump.FLOOR:
            self.set_fall(JUMPVEL)
            self.set_anim_idx(Anim.STILL)

    def animate(self) -> [DisplayEntry]:
        return [self.animation_state\
            .display_entry(self.id, self.xloc, self.yloc,
                           True if self.facing == Facing.RIGHT else False,
                           False, self.angle)]

    def proc_auto(self, control):
        this_frame_control, last_frame_control, \
            keys_pressed, keys_released, launch = control
        if self.id == Id.BLOCK.value:
            if launch:
                self.facing = Facing.RIGHT
                self.xvel = 5.25
                self.xaccl = -0.05
                self.push_state = Push.SKID
            return

    def __init__(self, anim_init, id = Id.PLAYER.value, placeholder = False):
        self.animation_state = AnimationState(anim_init)
        self.id = id
        self.set_fall(1.75)
        self.set_anim_idx(Anim.STILL)
        self.events = []
        self.interaction_events = []
        self.placeholder = placeholder
        self.auuid = uuid.uuid4()

