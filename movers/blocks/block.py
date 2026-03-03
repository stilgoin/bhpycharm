from movers.interactive_mover import InteractiveMover
from movers.movers import JUMPVEL
from system.defs import Status, Push, Events, Facing, Anim, Jump, PushAction

class BlockNode:
    nodes = []
    block = None
    right = None
    left = None

    def __init__(self, block):
        self.block = block

class Block(InteractiveMover):
    any_blocks = []
    friction = 0

    defaultPushAction = PushAction.SKID
    pcounterAction = defaultPushAction

    def __str__(self):
        return super().__str__()

    def halt_skidding(self):
        if self.push_state == Push.SKID:
            if self.xvel <= 0.0:
                self.push_state = Push.STILL
                self.xvel = 0.0
                self.xaccl = 0.0

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
        if not self.pcounterAction:
            self.xaccl = xaccl
            self.xvel = xvel * friction
        else:
            self.xaccl = xaccl
            self.xvel = 1.0
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
                self.snap_xloc = 0

    def before_move(self):
        super().before_move()
        self.halt_skidding()
        #self.add_push_steps()

    def move(self):
        super().move()

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
            #else:
            #    self.set_anim_idx(Anim.WALK)

        if not floor_found and self.jump_state == Jump.FLOOR:
            self.xvel = 0.0
            self.xaccl = 0.0
            self.set_fall(JUMPVEL)
            self.set_anim_idx(Anim.STILL)
