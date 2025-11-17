import threading
import time
from pynput import keyboard


class Signals:
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.last_key_time = time.time()
        self.focus_start_time = None
        self.running = True
        self.prev_state = None
        self.last_focus_state_change = time.time()
        self.last_talk_time = 0
        self.started_typing = False

        # ================================
        #  AI MODULE (Ollama)
        # ================================
        from ai.ollama_react import OllamaReact
        self.ollama = OllamaReact()

        # ================================
        #  REWARDS / QUESTS SYSTEM
        # ================================
        from rewards.rewards_manager import RewardsManager
        self.rewards = RewardsManager()

        # Reward flags
        self.reward_25_given = False
        self.reward_60_given = False

        # ================================
        #  FACE DETECTOR
        # ================================
        from core.face_detector import FaceDetector
        self.face_detector = FaceDetector(state_manager, enable_camera=True)
        self.face_detector.start()

        # ================================
        #  KEYBOARD LISTENER
        # ================================
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()

        # ================================
        #  MONITOR THREAD
        # ================================
        self.monitor_thread = threading.Thread(target=self.monitor_activity, daemon=True)
        self.monitor_thread.start()

    # -------------------------------------------------
    # KEY PRESS HANDLER
    # -------------------------------------------------
    def on_key_press(self, key):
        current_state = self.state_manager.get_state()
        self.last_key_time = time.time()
        self.started_typing = True

        # Ignore welcome back if just celebrated
        if current_state == "happy" and (time.time() - self.last_focus_state_change < 10):
            return

        # Was idle?
        was_idle = current_state not in ["focused", "happy"]

        # Switch to focus if not already
        if current_state != "focused":
            self.focus_start_time = time.time()
            self.state_manager.set_state("focused")
            self.prev_state = "focused"
            self.last_focus_state_change = time.time()

            # Reset reward flags
            self.reward_25_given = False
            self.reward_60_given = False

        # Welcome back reward
        if was_idle:
            self.rewards.add_xp(2)   # +2 XP
            self._speak_ai(
                "Say a cute, short 'welcome back' message under 6 words. Use emojis."
            )

    # -------------------------------------------------
    # MAIN MONITOR LOOP
    # -------------------------------------------------
    def monitor_activity(self):
        time.sleep(3)

        while self.running:
            now = time.time()
            idle_duration = now - self.last_key_time
            new_state = self.state_manager.get_state()

            # Determine new state
            if idle_duration > 120:
                new_state = "sleeping"
            elif idle_duration > 20:
                new_state = "idle"
            else:
                new_state = "focused" if self.started_typing else self.prev_state or "idle"

            # Handle state change
            if new_state != self.prev_state:
                print(f"[STATE CHANGE] {self.prev_state} → {new_state}")
                self.state_manager.set_state(new_state)
                self.prev_state = new_state
                self.last_focus_state_change = now

                if new_state == "sleeping":
                    self._speak_ai(
                        "Say a sleepy message like a cat dozing off. Be cute and soft. Use emojis."
                    )
                    self.focus_start_time = None

                elif new_state == "idle":
                    self._speak_ai(
                        "Say something calm like 'taking a small break'. Use emojis."
                    )
                    self.focus_start_time = None

                elif new_state == "focused" and self.started_typing:
                    self._speak_ai(
                        "Say something motivating like 'back to work!'. Keep it under 5 words with emojis."
                    )
                    self.focus_start_time = now
                    self.reward_25_given = False
                    self.reward_60_given = False

            # -------------------------------------------------
            # FOCUS REWARD SYSTEM
            # -------------------------------------------------
            if new_state == "focused" and self.started_typing:

                if self.focus_start_time is None:
                    self.focus_start_time = now

                focus_duration = now - self.focus_start_time

                # ---- 25 SECOND REWARD ----
                if 25 < focus_duration < 27 and not self.reward_25_given:
                    self.reward_25_given = True
                    self.rewards.add_xp(5)
                    self.rewards.complete_quest("25sec_focus")
                    self._speak_ai(
                        "Say an encouraging short message under 5 words. Use emojis."
                    )

                # ---- 60 SECOND REWARD ----
                if 60 < focus_duration < 62 and not self.reward_60_given:
                    self.reward_60_given = True

                    self.rewards.add_xp(10)
                    self.rewards.add_streak(1)
                    self.rewards.complete_quest("1min_focus")

                    self.state_manager.set_state("happy")
                    self.prev_state = "happy"

                    self._speak_ai(
                        "Say something excited and celebratory in under 5 words. Use emojis."
                    )

            time.sleep(1)

    # -------------------------------------------------
    # SPEECH WRAPPER (COOLDOWN)
    # -------------------------------------------------
    def _speak_ai(self, prompt):
        now = time.time()
        if now - self.last_talk_time < 10:
            return
        self.last_talk_time = now

        threading.Thread(
            target=self._show_ai_line,
            args=(prompt,),
            daemon=True
        ).start()

    # -------------------------------------------------
    # OLLAMA CALL
    # -------------------------------------------------
    def _show_ai_line(self, prompt):
        try:
            msg = self.ollama.generate(prompt)
            if msg and len(msg.strip()) > 0:
                print("AI OUTPUT:", msg)
                self.state_manager.app_ref.speech.show(msg)
        except Exception as e:
            print("Ollama error:", e)

    # -------------------------------------------------
    # STOP EVERYTHING
    # -------------------------------------------------
    def stop(self):
        self.running = False
        try:
            self.listener.stop()
        except:
            pass
        try:
            self.face_detector.stop()
        except:
            pass
            
