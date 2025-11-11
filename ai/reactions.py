import random

class Reactions:
    def __init__(self):
        self.focus_rewards = [
            "Nice work! 🎉",
            "Yesss keep going! 😺✨",
            "Proud of you rn 😼💗",
            "You’re doing amazing bb 🌟",
            "Look at you being productive 😻"
        ]

        self.welcome_back = [
            "Hey hey you’re back! 😺",
            "Missed you! 🐾",
            "Ready round 2? 💪",
        ]

        self.sleep_messages = [
            "Zzzz... 💤",
            "*soft snoring noises*",
            "rest time.."
        ]

    def get_focus_reward(self):
        return random.choice(self.focus_rewards)

    def get_welcome_back(self):
        return random.choice(self.welcome_back)

    def get_sleep_message(self):
        return random.choice(self.sleep_messages)
      
