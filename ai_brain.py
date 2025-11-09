# ai_brain.py - IA Adaptativa con aprendizaje de patrones

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
            "preferred_direction": "none",
            "movement_history": [],
            "dodge_patterns": {},
            "reaction_time": 0.5
        }
        self.load_behavior()
        
        # Variables para análisis en tiempo real
        self.last_positions = []
        self.max_history = 20
        
    def load_behavior(self):
        if os.path.exists(self.behavior_file):
            try:
                with open(self.behavior_file, 'r') as f:
                    data = json.load(f)
                    if data:
                        # Asegurar que todos los campos nuevos existan
                        if "movement_history" not in data:
                            data["movement_history"] = []
                        if "dodge_patterns" not in data:
                            data["dodge_patterns"] = {}
                        if "reaction_time" not in data:
                            data["reaction_time"] = 0.5
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
        
        # Guardar posición actual para análisis
        self.last_positions.append((player.x, player.y))
        if len(self.last_positions) > self.max_history:
            self.last_positions.pop(0)
        
        self.save_behavior()
    
    def analyze_movement_pattern(self, player, current_time):
        """Analiza patrones de movimiento en tiempo real"""
        if len(self.last_positions) < 3:
            return
        
        # Asegurar que dodge_patterns existe
        if "dodge_patterns" not in self.player_data:
            self.player_data["dodge_patterns"] = {}
        
        # Detectar patrones de movimiento (zigzag, circular, lateral, etc.)
        movements = []
        for i in range(1, len(self.last_positions)):
            prev_x, prev_y = self.last_positions[i-1]
            curr_x, curr_y = self.last_positions[i]
            
            dx = curr_x - prev_x
            dy = curr_y - prev_y
            
            if abs(dx) > abs(dy):
                movements.append("horizontal")
            elif abs(dy) > abs(dx):
                movements.append("vertical")
            else:
                movements.append("diagonal")
        
        # Detectar patrón más común
        if movements:
            from collections import Counter
            pattern_count = Counter(movements)
            most_common = pattern_count.most_common(1)[0][0]
            self.player_data["movement_history"] = movements[-10:]
            
            # Actualizar patrones detectados
            if most_common not in self.player_data["dodge_patterns"]:
                self.player_data["dodge_patterns"][most_common] = 0
            self.player_data["dodge_patterns"][most_common] += 1
        
        self.save_behavior()
    
    def get_predicted_position(self, player_x, player_y):
        """Predice posición futura basado en patrones aprendidos"""
        direction = self.player_data["preferred_direction"]
        
        # Ajustar offset según patrones de movimiento detectados
        base_offset = 50
        
        # Si detectamos patrones, aumentar la predicción
        patterns = self.player_data.get("dodge_patterns", {})
        if patterns:
            most_common_pattern = max(patterns, key=patterns.get)
            
            if most_common_pattern == "horizontal":
                base_offset = 70
            elif most_common_pattern == "vertical":
                base_offset = 70
            elif most_common_pattern == "diagonal":
                base_offset = 60
        
        # Usar historial reciente si existe
        history = self.player_data.get("movement_history", [])
        if len(history) >= 3:
            recent = history[-3:]
            if recent.count("horizontal") >= 2:
                base_offset *= 1.3
            elif recent.count("vertical") >= 2:
                base_offset *= 1.3
        
        offset = base_offset
        
        if direction == "left":
            return player_x - offset, player_y
        elif direction == "right":
            return player_x + offset, player_y
        elif direction == "up":
            return player_x, player_y - offset
        elif direction == "down":
            return player_x, player_y + offset
        else:
            # Sin dirección preferida, predecir basado en patrones
            if patterns:
                most_common = max(patterns, key=patterns.get)
                if most_common == "horizontal":
                    return player_x + offset, player_y
                elif most_common == "vertical":
                    return player_x, player_y - offset
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