from movers.events import MiscEvent
from movers.interactive_mover import InteractiveMover
from system.defs import Facing, TrapDoorStates


class Gate(InteractiveMover):
    angle = 0.0
    base_xaccl = 0.0
    hitoffs = (0, 0, 0x10, 0x4)

    def make_hitboxes(self):
        if self.facing == Facing.RIGHT:
            self.hitoffs = (-0x10, 0, 0x0, 0xF)
        super().make_hitboxes()

    def modify_interaction(self):
        self.move_state = TrapDoorStates.DROP_UPPER
        self.action_timer = 60

    @property
    def fallthrough_trap_door(self):
        return not self.move_state

    def move(self):

        if self.action_timer > 0:
            self.action_timer -= 1
            if not self.action_timer:
                self.move_state = TrapDoorStates.RAISE_UPPER

        if Facing.LEFT == self.facing:
            pass
            #self.angle -= 5
            # self.angle = -45
            # if self.angle < -165:
            #    self.angle = 0
            # if self.angle >= -90:
            #    self.xloc = self.default_xloc + int(self.angle / 16.0)

        if Facing.RIGHT == self.facing:
            pass
            #self.angle -= 5
            # self.angle = 45
            # if self.angle > 165:
            #    self.angle = 0
            # if self.angle <= 90:
            #    self.xloc = self.default_xloc + int(self.angle / 16.0)
            # self.yloc = self.default_yloc - int(self.angle / 8.0) + 16

class TrapDoorManager(MiscEvent):

    gates : [Gate]
    move_state = 0

    def rotate_planks(self, left_gate, right_gate, rvel, check_angle):
        next_state = False
        if left_gate.angle > check_angle * -1 or not check_angle:
            left_gate.angle -= rvel
        else:
            next_state = True
        if right_gate.angle > check_angle * -1 or not check_angle:
            right_gate.angle -= rvel
        else:
            next_state = True
        return next_state

    def run_event(self):
        if TrapDoorStates.DROP_UPPER == self.gates[0].move_state \
            and self.gates[1].move_state != TrapDoorStates.RAISE_UPPER \
            or TrapDoorStates.DROP_UPPER == self.gates[1].move_state\
            and self.gates[0].move_state != TrapDoorStates.RAISE_UPPER:
            self.gates[0].move_state = TrapDoorStates.DROP_UPPER
            self.gates[1].move_state = TrapDoorStates.DROP_UPPER
            if self.rotate_planks(self.gates[0], self.gates[1], 7.5, 150):
                pass

        if TrapDoorStates.RAISE_UPPER == self.gates[0].move_state \
            or TrapDoorStates.RAISE_UPPER == self.gates[1].move_state:
            self.gates[0].move_state = TrapDoorStates.RAISE_UPPER
            self.gates[1].move_state = TrapDoorStates.RAISE_UPPER
            if self.rotate_planks(self.gates[0], self.gates[1], -7.5, 0):
                pass

            if self.gates[0].angle >= 0.0:
                self.gates[0].move_state = 0
                self.gates[1].move_state = 0
                self.gates[0].angle = 0.0
                self.gates[1].angle = 0.0


                #for gate in self.gates:
                #    gate.angle = 0
        """
        if TrapDoorStates.DROP_LOWER == self.move_state:
            self.rotate_planks(self.gates[0], self.gates[1], 4.0, 90)
            if self.rotate_planks(self.gates[2], self.gates[3], 7.5, 160):
                self.move_state = TrapDoorStates.DROP_UPPER
                for gate in self.gates:
                    gate.angle = 0
        """



    def __init__(self, gates):
        self.gates = gates
