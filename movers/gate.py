from movers.interactive_mover import InteractiveMover
from system.defs import Id, Facing


class Gate(InteractiveMover):

    angle = 0.0

    hitbox_offs=(0,0,0x10,0x4)

    def make_hitboxes(self):
        if self.facing == Facing.RIGHT:
            self.hitoffs=(-0x10,0,0x10,0xF)
        super().make_hitboxes()



    def move(self):

        if Facing.LEFT == self.facing:
            pass
            #self.angle -= 1
            #self.angle = -45
            #if self.angle < -165:
            #    self.angle = 0
            #if self.angle >= -90:
            #    self.xloc = self.default_xloc + int(self.angle / 16.0)

        if  Facing.RIGHT == self.facing:
            pass
            #self.angle -= 1
            #self.angle = 45
            #if self.angle > 165:
            #    self.angle = 0
            #if self.angle <= 90:
            #    self.xloc = self.default_xloc + int(self.angle / 16.0)
            #self.yloc = self.default_yloc - int(self.angle / 8.0) + 16
