import tkinter as tk

class SpeechBubble:
    def __init__(self, root):
        self.root = root
        self.label = tk.Label(
            root,
            text="",
            font=("Arial", 9, "bold"),
            bg="#ffffaa",       # Soft yellow bubble
            fg="#000000",
            bd=2,
            relief="solid",
            padx=6,
            pady=3,
            justify="left",      # Wrap lines left-aligned
            wraplength=120       # ← controls max bubble width
        )
        self.visible = False

    def show(self, message, duration=4000):
        """Display the speech bubble with wrapped text."""
        self.label.config(text=message)
        self.label.lift()

        # Place near the top of the window
        self.label.place(x=10, y=10)
        self.visible = True

        # Auto-hide after duration
        self.root.after(duration, self.hide)

    def hide(self):
        if self.visible:
            self.label.place_forget()
            self.visible = False
