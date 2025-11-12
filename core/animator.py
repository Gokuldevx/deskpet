import os
import tkinter as tk
from PIL import Image, ImageTk
from config import SKIN_PATH, FPS

class Animator:
    def __init__(self, root, state_manager):
        self.root = root
        self.state_manager = state_manager

        # Pet display label
        self.label = tk.Label(root, bg="white", bd=0, highlightthickness=0)
        self.label.place(x=43, y=75)

        # Bind click → pat reaction
        self.label.bind("<Button-1>", self.on_click)

        self.animations = self.load_all_frames()
        self.frame_index = 0
        self.prev_state = None

    def load_all_frames(self):
        animations = {}
        
        for state_name in os.listdir(SKIN_PATH):
            state_folder = os.path.join(SKIN_PATH, state_name)
            if os.path.isdir(state_folder):
                frames = []
                for file in sorted(os.listdir(state_folder)):
                    if file.endswith(".png"):
                        img = Image.open(os.path.join(state_folder, file))
                        img = img.resize((64, 64), Image.NEAREST)  # keep pixel crisp
                        frames.append(ImageTk.PhotoImage(img))
                animations[state_name] = frames
        return animations
        
    def update_frame(self):
        state = self.state_manager.get_state()

        # If state changed → restart animation
        if state != self.prev_state:
            self.frame_index = 0
        self.prev_state = state

        frames = self.animations[state]
        self.label.config(image=frames[self.frame_index])
        self.frame_index = (self.frame_index + 1) % len(frames)

        self.root.after(FPS, self.update_frame)

    def on_click(self, event):
        # Trigger pat animation + speech bubble
        self.state_manager.trigger_pat()
        try:
            self.state_manager.app_ref.speech.show("Pat pat 😺💗")
        except:
            pass
                        
