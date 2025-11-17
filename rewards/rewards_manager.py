import json
import os
from datetime import datetime


class RewardsManager:
    def __init__(self):
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)

        # File paths
        self.stats_file = os.path.join(self.data_dir, "stats.json")
        self.quests_file = os.path.join(self.data_dir, "quests.json")
        self.unlocks_file = os.path.join(self.data_dir, "unlocks.json")

        # Base defaults — prevents all KeyErrors
        self.stats_defaults = {
            "xp": 0,
            "level": 1,
            "streak": 0,
            "last_focus_date": ""
        }

        self.quests_defaults = {
            "25sec_focus": False,
            "1min_focus": False,
            "daily_focus": False
        }

        self.unlocks_defaults = {
            "skins": [],
            "accessories": []
        }

        # Load
        self.stats = self._load_json(self.stats_file, self.stats_defaults)
        self.quests = self._load_json(self.quests_file, self.quests_defaults)
        self.unlocks = self._load_json(self.unlocks_file, self.unlocks_defaults)

    # --------------------------------------------------
    # JSON LOAD / SAVE
    # --------------------------------------------------
    def _load_json(self, path, defaults):
        """Load file safely, recreate missing keys."""
        if not os.path.exists(path):
            self._save_json(path, defaults)
            return defaults.copy()

        try:
            with open(path, "r") as f:
                data = json.load(f)
        except:
            data = {}

        # Add any missing default keys
        for key, value in defaults.items():
            if key not in data:
                data[key] = value

        self._save_json(path, data)
        return data

    def _save_json(self, path, data):
        with open(path, "w") as f:
            json.dump(data, f, indent=4)

    # --------------------------------------------------
    # XP & LEVEL SYSTEM
    # --------------------------------------------------
    def add_xp(self, amount):
        self.stats["xp"] += amount
        print(f"[XP] Added {amount}, total: {self.stats['xp']}")

        # Level-up every 100 XP
        while self.stats["xp"] >= 100:
            self.stats["xp"] -= 100
            self.stats["level"] += 1
            print(f"[LEVEL UP] → Level {self.stats['level']}")

        self._save_json(self.stats_file, self.stats)

    # --------------------------------------------------
    # STREAK SYSTEM
    # --------------------------------------------------
    def add_streak(self, amount=1):
        if "streak" not in self.stats:
            self.stats["streak"] = 0  # safety

        self.stats["streak"] += amount
        print(f"[STREAK] +{amount}, total = {self.stats['streak']}")
        self._save_json(self.stats_file, self.stats)

    def reset_streak(self):
        self.stats["streak"] = 0
        print("[STREAK] Reset → 0")
        self._save_json(self.stats_file, self.stats)

    # --------------------------------------------------
    # QUESTS SYSTEM
    # --------------------------------------------------
    def complete_quest(self, quest_id):
        if quest_id not in self.quests:
            print(f"[QUEST] Unknown quest '{quest_id}'")
            return

        if self.quests[quest_id] is True:
            return  # already done today

        self.quests[quest_id] = True
        print(f"[QUEST] Completed: {quest_id}")

        # Quest rewards mapping
        quest_rewards = {
            "25sec_focus": 10,
            "1min_focus": 25,
            "daily_focus": 15
        }

        if quest_id in quest_rewards:
            self.add_xp(quest_rewards[quest_id])

        self._save_json(self.quests_file, self.quests)

    def reset_daily_quests(self):
        for key in self.quests_defaults:
            self.quests[key] = False
        print("[QUESTS] Reset daily quests")
        self._save_json(self.quests_file, self.quests)

    # --------------------------------------------------
    # UNLOCKS
    # --------------------------------------------------
    def unlock_item(self, category, item_name):
        if category not in self.unlocks:
            print(f"[UNLOCK] Unknown category '{category}'")
            return

        if item_name not in self.unlocks[category]:
            self.unlocks[category].append(item_name)
            print(f"[UNLOCK] New {category[:-1]} unlocked → {item_name}")

        self._save_json(self.unlocks_file, self.unlocks)
      
