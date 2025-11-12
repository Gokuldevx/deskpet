import cv2
import threading
import time


class FaceDetector:
    def __init__(self, state_manager, enable_camera=True):
        self.state_manager = state_manager
        self.enable_camera = enable_camera
        self.running = False
        self.last_face_time = time.time()
        self.smile_counter = 0  # 👈 Track how long smile persists
        self.away_message_shown = False

        # Haar cascades (lightweight & local)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")

    def start(self):
        """Starts the face detection thread."""
        if not self.enable_camera:
            print("[FaceDetector] Camera disabled.")
            return

        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print("[FaceDetector] Started.")

    def stop(self):
        """Stops detection and releases camera."""
        self.running = False
        print("[FaceDetector] Stopped.")

    def _run(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("⚠️ Camera not accessible.")
            return

        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

            # ------------------------------
            # No face detected → “away” state
            # ------------------------------
            if len(faces) == 0:
                if time.time() - self.last_face_time > 10 and not self.away_message_shown:
                    try:
                        self.state_manager.app_ref.speech.show("Hey, still there? 👀 Focus time!")
                        self.away_message_shown = True
                    except:
                        pass
                time.sleep(1)
                continue

            # ------------------------------
            # Face detected → reset timers
            # ------------------------------
            self.last_face_time = time.time()
            self.away_message_shown = False

            for (x, y, w, h) in faces:
                face_roi = gray[y:y + h, x:x + w]

                # Stricter smile detection
                smiles = self.smile_cascade.detectMultiScale(
                    face_roi,
                    scaleFactor=1.8,   # more strict, less false positives
                    minNeighbors=25,   # require many smile features
                )

                # ------------------------------
                # Smile logic with persistence
                # ------------------------------
                if len(smiles) > 0:
                    self.smile_counter += 1
                else:
                    self.smile_counter = 0

                # Only trigger after 3 consecutive smile detections
                if self.smile_counter >= 3:
                    self.smile_counter = 0
                    self._trigger_smile_reaction()
                    break

            time.sleep(0.8)

        cap.release()
        cv2.destroyAllWindows()

    # -------------------------------------------------
    # Trigger Ollama response for smile
    # -------------------------------------------------
    def _trigger_smile_reaction(self):
        try:
            self.state_manager.set_state("happy")
            from ai.ollama_react import OllamaReact
            ollama = OllamaReact()
            msg = ollama.generate("Say something sweet noticing my smile. Keep it short and cute with emojis.")
            if msg and len(msg.strip()) > 0:
                self.state_manager.app_ref.speech.show(msg)
                print("AI OUTPUT (smile):", msg)
        except Exception as e:
            print("Smile AI error:", e)
        time.sleep(3)  # prevent back-to-back triggers
        
