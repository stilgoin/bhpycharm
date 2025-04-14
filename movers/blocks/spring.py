from movers.blocks.block import Block
from system.defs import Events, Push, Id, Facing, Status


class SideSpring(Block):
    base_xaccl = 0.05
    max_pvel = 0.25
    MAX_PVEL_CONST = 0.25
    default_xloc = 0.0
    snap_xloc = 0.0

    def clamp_pvel(self):
        if self.push_state == Push.STILL \
                or self.push_state == Push.ROLLBACK:
            return

        if self.xvel >= self.max_pvel:
            self.xvel = self.max_pvel
            print(f"{self.id}, {self.max_pvel}")
            
    def procInteractionEvents(self):
        
        halt_pushing = False
        
        if Events.CONTINUE_PUSHING in self.interaction_events:
            
            halt_pushing = self.lockInPlace()
            
            if halt_pushing:
                self.interaction_events.remove(Events.CONTINUE_PUSHING)
                self.interaction_events.append(Events.HALT_PUSHING)
        else:
            self.lockInPlace()
                
        super().procInteractionEvents()
        
    def lockInPlace(self):
        if self.xloc > self.default_xloc:
            self.xloc = self.default_xloc
            return True
        if self.xloc < self.default_xloc - 0xC:
            self.xloc = self.default_xloc - 0xC
            return True
        
        return False
            
    def go(self):
        super().go()

    def __init__(self, anim_init, id, placeholder, facing = Facing.RIGHT):
        super().__init__(anim_init, id, placeholder)
        self.facing = facing

class SpringBox(Block):
    base_xaccl = 0.0    # disable pushing, but keep the capability

    def go(self):
        super().go()

    def animate(self):
        return [self.animation_state \
                    .display_entry(self.id, self.xloc, self.yloc,
                                   True if self.facing == Facing.RIGHT else False,
                                   False)]
    def __init__(self, anim_inits, anim_init, id = Id.SPRINGBOX.value, placeholder = True, facing = Facing.RIGHT):
        super().__init__(anim_init, id, placeholder)
