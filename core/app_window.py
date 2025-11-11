import tkinter as tk
import ttkbootstrap as ttk
from core.animator import Animator
from core.state_manager import StateManager
from core.signals import Signals
from core.speech_bubble import SpeechBubble

class AppWindow:
    def __init__(self):
        self.root = ttk.Window(themename="cosmo")
        self.root.title("Desk Pet")
        self.root.geometry("150x170")  # width x height


        self.state_manager = StateManager()
        self.state_manager.app_ref = self
        self.animator = Animator(self.root, self.state_manager)
        self.speech = SpeechBubble(self.root)
        self.signals = Signals(self.state_manager)

        # Always on top
        self.root.attributes("-topmost", True)

        # Remove standard window frame
        self.root.overrideredirect(True)

        # Make draggable
        self.root.bind("<ButtonPress-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        self.root.geometry(f"+{event.x_root - self.x}+{event.y_root - self.y}")

    def run(self):
        self.animator.update_frame()
        self.root.mainloop()
      
