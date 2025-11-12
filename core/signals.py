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
        self.last_talk_time = 0  # cooldown
        self.started_typing = False  # 👈 prevent premature "focused"

        # --- AI (Ollama) & Face Modules ---
        from ai.ollama_react import OllamaReact
        self.ollama = OllamaReact()

        from core.face_detector import FaceDetector
        self.face_detector = FaceDetector(state_manager, enable_camera=True)
        self.face_detector.start()

        # --- Keyboard Activity Listener ---
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()

        # --- Background Monitoring Thread ---
        self.monitor_thread = threading.Thread(target=self.monitor_activity, daemon=True)
        self.monitor_thread.start()

    # -------------------------------------------------
    # Handle user typing (focus detection)
    # -------------------------------------------------
    def on_key_press(self, key):
        current_state = self.state_manager.get_state()
        self.last_key_time = time.time()
        self.started_typing = True  # 👈 typing detected

        # Ignore welcome back if user was recently happy
        if current_state == "happy" and (time.time() - self.last_focus_state_change < 10):
            return

        was_idle = (current_state not in ["focused", "happy"])

        # If not focused, start new focus session
        if current_state != "focused":
            self.focus_start_time = time.time()
            self.state_manager.set_state("focused")
            self.prev_state = "focused"
            self.last_focus_state_change = time.time()

        # If returning from idle → welcome message (with cooldown)
        if was_idle:
            self._speak_ai("Say a cute, short 'welcome back' message under 6 words. Use emojis.")

    # -------------------------------------------------
    # Monitor user activity and trigger reactions
    # -------------------------------------------------
    def monitor_activity(self):
        # 💤 Wait a bit before checking (prevent startup spam)
        time.sleep(3)

        while self.running:
            now = time.time()
            idle_duration = now - self.last_key_time
            new_state = self.state_manager.get_state()

            # Determine state based on typing inactivity
            if idle_duration > 120:
                new_state = "sleeping"
            elif idle_duration > 20:
                new_state = "idle"
            else:
                # Only set "focused" if user actually typed before
                new_state = "focused" if self.started_typing else self.prev_state or "idle"

            # --- Only act when the state actually changes ---
            if new_state != self.prev_state:
                print(f"[STATE CHANGE] {self.prev_state} → {new_state}")
                self.state_manager.set_state(new_state)
                self.prev_state = new_state
                self.last_focus_state_change = now

                # Handle transitions
                if new_state == "sleeping":
                    self._speak_ai("Say a sleepy message like a cat dozing off. Be cute and soft. Use emojis.")
                    self.focus_start_time = None

                elif new_state == "idle":
                    self._speak_ai("Say something calm like 'taking a small break'. Use emojis.")
                    self.focus_start_time = None

                elif new_state == "focused" and self.started_typing:
                    self._speak_ai("Say something motivating like 'back to work!'. Keep it under 5 words with emojis.")
                    self.focus_start_time = now

            # --- Focus streak rewards ---
            if new_state == "focused" and self.started_typing:
                if self.focus_start_time is None:
                    self.focus_start_time = now

                focus_duration = now - self.focus_start_time

                if 25 < focus_duration < 27:
                    self._speak_ai("Say a short, cute, encouraging message under 5 words. Use emojis.")
                if 60 < focus_duration < 62:
                    self.state_manager.set_state("happy")
                    self.prev_state = "happy"
                    self._speak_ai("Say something excited and celebratory like cheering someone on. Under 5 words. Use emojis.")

            time.sleep(1)

    # -------------------------------------------------
    # Cooldown-based speech wrapper
    # -------------------------------------------------
    def _speak_ai(self, prompt):
        """Speak only if cooldown has passed."""
        now = time.time()
        cooldown_time = 10  # seconds

        if now - self.last_talk_time < cooldown_time:
            return  # still cooling down

        self.last_talk_time = now
        threading.Thread(target=self._show_ai_line, args=(prompt,), daemon=True).start()

    # -------------------------------------------------
    # Actual AI message generator
    # -------------------------------------------------
    def _show_ai_line(self, prompt):
        try:
            ai_line = self.ollama.generate(prompt)
            if ai_line and len(ai_line.strip()) > 0:
                print("AI OUTPUT:", ai_line)
                self.state_manager.app_ref.speech.show(ai_line)
        except Exception as e:
            print("Ollama error:", e)

    # -------------------------------------------------
    # Graceful shutdown
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
