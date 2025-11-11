import threading
import time

class StateManager:
    def __init__(self):
        self.state = "idle"
        self.previous_state = "idle"
        self.app_ref = None

    def set_state(self, new_state):
        # Don't auto override pat reaction

        if new_state == "happy":
            self.state = "happy"
            threading.Thread(target=self._return_to_idle, daemon=True).start()
        else:
            self.state = new_state

    def trigger_pat(self):
        self.previous_state = self.state
        self.state = "pat"
        threading.Thread(target=self._pat_animation_duration, daemon=True).start()

    def _pat_animation_duration(self):
        time.sleep(1.2)  # pat lasts 1.2 sec
        self.state = self.previous_state

    def _return_to_idle(self):
        time.sleep(4)
        self.state = "idle"

    def get_state(self):
        return self.state
      
