import threading
import time
from pynput import keyboard


class Signals:
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.last_key_time = time.time()
        self.focus_start_time = None  
        self.running = True

        from ai.reactions import Reactions
        self.react = Reactions()

        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()

        self.monitor_thread = threading.Thread(target=self.monitor_activity, daemon=True)
        self.monitor_thread.start()

    def on_key_press(self, key):
        current_state = self.state_manager.get_state()
        was_idle = (current_state != "focused")

        self.last_key_time = time.time()

        # If focus was NOT already active, start a new focus session timer
        if current_state != "focused":
            self.focus_start_time = time.time()

        # Switch to focused state
        self.state_manager.set_state("focused")

        # If returning from idle → say welcome back
        if was_idle:
            try:
                msg = self.react.get_welcome_back()
                self.state_manager.app_ref.speech.show(msg)
            except:
                pass

    def monitor_activity(self):
        while self.running:
            now = time.time()
            idle_duration = now - self.last_key_time

            # ---- IDLE & SLEEP STATES ----

            # No typing for 2 minutes → sleeping
            if idle_duration > 120:
                self.state_manager.set_state("sleeping")
                self.focus_start_time = None  # reset focus timer

            # No typing for 20 seconds → idle
            elif idle_duration > 20:
                self.state_manager.set_state("idle")
                self.focus_start_time = None  # reset focus timer

            else:
                # ---- FOCUS STATE ----
                # If typing AND not already timing focus, start new timer
                if self.focus_start_time is None:
                    self.focus_start_time = now  # start new focus session

                focus_duration = now - self.focus_start_time

                # 25 minutes focus → small encouragement
                if 25 < focus_duration < 27 :
                    try:
                        msg = self.react.get_focus_reward()
                        self.state_manager.app_ref.speech.show(msg + " 🐾")
                    except:
                        pass

                # 60 minutes focus → big celebration + happy animation
                if 60 < focus_duration < 62:
                    self.state_manager.set_state("happy")
                    try:
                        self.state_manager.app_ref.speech.show("WOOO you're on fire!! 😻🔥")
                    except:
                        pass

            time.sleep(1)
      
