
class MiscEvent:

    move_state = 0

    def run_event(self):
        pass

    @property
    def move_state(self, move_state):
        self.move_state = move_state

