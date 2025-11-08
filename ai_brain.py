# ai_brain.py - IA Adaptativa

import json
import os
from settings import *

class AIBrain:
    def __init__(self):
        self.behavior_file = "data/behavior.json"
        self.player_data = {
            "dodges": {"left": 0, "right": 0, "up": 0, "down": 0},
            "hits_taken": 0,
            "survival_time": 0,
            "preferred_direction": "none"
        }
        self.load_behavior()
        
    def load_behavior(self):
        if os.path.exists(self.behavior_file):
            try:
                with open(self.behavior_file, 'r') as f:
                    data = json.load(f)
                    if data:
                        self.player_data = data
            except:
                pass
    
    def save_behavior(self):
        os.makedirs("data", exist_ok=True)
        with open(self.behavior_file, 'w') as f:
            json.dump(self.player_data, f, indent=2)
    
    def analyze_player(self, player, survival_time):
        self.player_data["dodges"] = player.dodges.copy()
        self.player_data["hits_taken"] = player.hits_taken
        self.player_data["survival_time"] = survival_time
        
        dodges = player.dodges
        max_dodges = max(dodges.values()) if dodges.values() else 0
        if max_dodges > 0:
            self.player_data["preferred_direction"] = max(dodges, key=dodges.get)
        
        self.save_behavior()
    
    def get_predicted_position(self, player_x, player_y):
        direction = self.player_data["preferred_direction"]
        offset = 50
        
        if direction == "left":
            return player_x - offset, player_y
        elif direction == "right":
            return player_x + offset, player_y
        elif direction == "up":
            return player_x, player_y - offset
        elif direction == "down":
            return player_x, player_y + offset
        else:
            return player_x, player_y
    
    def decide_boss_state(self, player_hp, boss_hp, survival_time):
        player_hp_percent = player_hp / PLAYER_HP
        boss_hp_percent = boss_hp / BOSS_HP
        
        if player_hp_percent > 0.7 and boss_hp_percent < 0.5:
            return "furioso"
        
        if boss_hp_percent < 0.3:
            return "enajenado"
        
        total_dodges = sum(self.player_data["dodges"].values())
        if total_dodges > 100 and self.player_data["hits_taken"] < 3:
            return "furioso"
        
        return "tranquilo"
