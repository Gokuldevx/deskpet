import tkinter as tk
from tkinter import scrolledtext
import threading


class ChatWindow:
    def __init__(self, root, ollama, speech=None):
        self.root = root
        self.ollama = ollama
        self.speech = speech  # optional speech bubble link
        self.window = None

    def open(self):
        if self.window and tk.Toplevel.winfo_exists(self.window):
            self.window.lift()
            return

        self.window = tk.Toplevel(self.root)
        self.window.title("Chat with Your Pet 🐾")
        self.window.geometry("350x400")
        self.window.resizable(False, False)

        # --- Chat log box ---
        self.chat_box = scrolledtext.ScrolledText(
            self.window,
            wrap=tk.WORD,
            width=42,
            height=18,
            font=("Consolas", 10)
        )
        self.chat_box.pack(padx=8, pady=5)
        self.chat_box.config(state=tk.DISABLED)

        # --- Entry box ---
        self.entry = tk.Entry(self.window, font=("Arial", 11))
        self.entry.pack(padx=8, pady=5, fill=tk.X)
        self.entry.bind("<Return>", self.on_send)

        # --- Send button ---
        send_btn = tk.Button(
            self.window,
            text="Send",
            font=("Arial", 10, "bold"),
            command=self.on_send
        )
        send_btn.pack(pady=5)

        # Greet the user once
        self._append_text("Pet", "Hi there! I’m your desk buddy 😺. What’s up?")

    # -------------------------------
    def _append_text(self, sender, text):
        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.insert(tk.END, f"{sender}: {text}\n\n")
        self.chat_box.config(state=tk.DISABLED)
        self.chat_box.yview(tk.END)

    # -------------------------------
    def on_send(self, event=None):
        user_input = self.entry.get().strip()
        if not user_input:
            return

        self.entry.delete(0, tk.END)
        self._append_text("You", user_input)

        threading.Thread(target=self._get_response, args=(user_input,), daemon=True).start()

    # -------------------------------
    def _get_response(self, user_input):
        try:
            prompt = (
                f"You are a cute pixel cat pet named Mrs. Mewlette who lives on the user's desktop. "
                f"Keep your replies short, warm, and positive. Use emojis sometimes. "
                f"Reply to: {user_input}"
            )
            response = self.ollama.generate(prompt)
            if not response:
                response = "😿 ...I'm a bit tired right now."

            self._append_text("Pet", response)

            # Optionally show in the bubble
            if self.speech:
                self.speech.show(response)

        except Exception as e:
            print("Chat error:", e)
            self._append_text("Pet", "Oops, something went wrong 🥲")
          
