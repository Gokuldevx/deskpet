import tkinter as tk

class SpeechBubble:
    def __init__(self, root):
        self.root = root
        self.label = tk.Label(
            root,
            text="",
            font=("Arial", 10, "bold"),
            bg="#ffff88",       # Yellow bubble (visible)
            fg="#000000",
            bd=2,
            relief="solid",
            padx=6,
            pady=3
        )
        self.visible = False

    def show(self, message, duration=3000):
        self.label.config(text=message)

        # Ensure bubble is above pet (z-order)
        self.label.lift()

        # Position bubble relative to pet
        # x = left/right, y = up/down
        self.label.place(x=35, y=20)

        self.visible = True
        self.root.after(duration, self.hide)

    def hide(self):
        if self.visible:
            self.label.place_forget()
            self.visible = False
          
