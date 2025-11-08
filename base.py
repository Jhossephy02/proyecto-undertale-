#!/usr/bin/env python3
# fix_all_files.py - Genera todos los archivos del juego

import os

archivos = {
    "settings.py": '''# settings.py - Configuración del juego

# Ventana
WIDTH = 800
HEIGHT = 600
FPS = 60

# Arena de combate (donde se mueve el jugador)
ARENA_X = 200
ARENA_Y = 150
ARENA_WIDTH = 400
ARENA_HEIGHT = 300

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (200, 0, 200)

# Player
PLAYER_SIZE = 20
PLAYER_SPEED = 5
PLAYER_HP = 100

# Boss
BOSS_HP = 500
BOSS_STATES = {
    "tranquilo": {"speed_mult": 0.7, "attack_mult": 1.0, "color": GREEN},
    "furioso": {"speed_mult": 1.2, "attack_mult": 1.5, "color": YELLOW},
    "enajenado": {"speed_mult": 1.8, "attack_mult": 2.5, "color": RED}
}

# Ataques
BULLET_BASE_SPEED = 3
BULLET_SIZE = 8

# IA
AI_ANALYSIS_INTERVAL = 3.0
AI_STATE_CHANGE_THRESHOLD = 0.3
''',

    "utils.py": '''# utils.py - Funciones auxiliares

import math
import random

def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def angle_to(x1, y1, x2, y2):
    return math.atan2(y2 - y1, x2 - x1)

def clamp(value, min_val, max_val):
    return max(min_val, min(max_val, value))

def lerp(a, b, t):
    return a + (b - a) * t

def random_direction():
    return random.uniform(0, 2 * math.pi)

def point_in_rect(px, py, rx, ry, rw, rh):
    return rx <= px <= rx + rw and ry <= py <= ry + rh
''',

    "player.py": '''# player.py - Lógica del jugador

import pygame
from settings import *
from utils import clamp

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = PLAYER_SIZE
        self.speed = PLAYER_SPEED
        self.hp = PLAYER_HP
        self.max_hp = PLAYER_HP
        self.invulnerable = False
        self.invuln_timer = 0
        self.invuln_duration = 1.0
        
        self.dodges = {"left": 0, "right": 0, "up": 0, "down": 0}
        self.hits_taken = 0
        
    def update(self, dt, keys):
        dx = 0
        dy = 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += self.speed
        
        if dx < 0:
            self.dodges["left"] += 1
        elif dx > 0:
            self.dodges["right"] += 1
        if dy < 0:
            self.dodges["up"] += 1
        elif dy > 0:
            self.dodges["down"] += 1
        
        self.x = clamp(self.x + dx, ARENA_X, ARENA_X + ARENA_WIDTH - self.size)
        self.y = clamp(self.y + dy, ARENA_Y, ARENA_Y + ARENA_HEIGHT - self.size)
        
        if self.invulnerable:
            self.invuln_timer += dt
            if self.invuln_timer >= self.invuln_duration:
                self.invulnerable = False
                self.invuln_timer = 0
    
    def take_damage(self, amount):
        if not self.invulnerable:
            self.hp -= amount
            self.hits_taken += 1
            self.invulnerable = True
            self.invuln_timer = 0
            if self.hp <= 0:
                self.hp = 0
                return True
        return False
    
    def draw(self, screen):
        color = RED
        if self.invulnerable:
            color = RED if int(self.invuln_timer * 10) % 2 == 0 else (255, 100, 100)
        
        pygame.draw.polygon(screen, color, [
            (self.x + self.size // 2, self.y + self.size),
            (self.x, self.y + self.size // 2),
            (self.x + self.size // 4, self.y),
            (self.x + self.size // 2, self.y + self.size // 4),
            (self.x + self.size * 3 // 4, self.y),
            (self.x + self.size, self.y + self.size // 2)
        ])
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)
''',

    "attack_patterns.py": '''# attack_patterns.py - Patrones de ataque

import pygame
import math
import random
from settings import *

def point_in_rect(px, py, rx, ry, rw, rh):
    return rx <= px <= rx + rw and ry <= py <= ry + rh

class Bullet:
    def __init__(self, x, y, angle, speed, color=(255,255,255)):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.size = BULLET_SIZE
        self.color = color
        self.active = True
        
    def update(self, dt):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        
        if not point_in_rect(self.x, self.y, ARENA_X - 50, ARENA_Y - 50, 
                            ARENA_WIDTH + 100, ARENA_HEIGHT + 100):
            self.active = False
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, 
                          self.size * 2, self.size * 2)

class AttackPattern:
    @staticmethod
    def circle_burst(x, y, count, speed, color=(255,255,255)):
        bullets = []
        angle_step = (2 * math.pi) / count
        for i in range(count):
            angle = angle_step * i
            bullets.append(Bullet(x, y, angle, speed, color))
        return bullets
    
    @staticmethod
    def aimed_shot(x, y, target_x, target_y, speed, color=(255,255,255)):
        angle = math.atan2(target_y - y, target_x - x)
        return [Bullet(x, y, angle, speed, color)]
    
    @staticmethod
    def spiral(x, y, count, speed, rotation, color=(255,255,255)):
        bullets = []
        angle_step = (2 * math.pi) / count
        for i in range(count):
            angle = angle_step * i + rotation
            bullets.append(Bullet(x, y, angle, speed, color))
        return bullets
    
    @staticmethod
    def wall(x, y, horizontal, count, speed, spacing, color=(255,255,255)):
        bullets = []
        if horizontal:
            for i in range(count):
                bx = x + (i - count // 2) * spacing
                bullets.append(Bullet(bx, y, math.pi / 2, speed, color))
        else:
            for i in range(count):
                by = y + (i - count // 2) * spacing
                bullets.append(Bullet(x, by, 0, speed, color))
        return bullets
    
    @staticmethod
    def random_spray(x, y, count, speed, color=(255,255,255)):
        bullets = []
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            bullets.append(Bullet(x, y, angle, speed, color))
        return bullets
''',

    "ai_brain.py": '''# ai_brain.py - IA Adaptativa

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
''',

    "boss.py": '''# boss.py - Lógica del jefe

import pygame
import random
from settings import *
from attack_patterns import AttackPattern

class Boss:
    def __init__(self, x, y, ai_brain):
        self.x = x
        self.y = y
        self.hp = BOSS_HP
        self.max_hp = BOSS_HP
        self.state = "tranquilo"
        self.ai = ai_brain
        
        self.bullets = []
        self.attack_timer = 0
        self.attack_cooldown = 2.0
        self.rotation = 0
        
        self.dialogues = {
            "tranquilo": ["Facilito causa 😏", "Muévete ps jaja", "Ta' suave"],
            "furioso": ["¡Ya me picaste mano! 😤", "¡Ahora sí! 💢", "¡Te voy a atrapar!"],
            "enajenado": ["¡TE VOY A QUEBRAR! 💀", "¡MUEREEE! 🔥", "¡YA FUE!"]
        }
        self.current_dialogue = ""
        self.dialogue_timer = 0
        
    def update(self, dt, player):
        self.rotation += dt * 2
        
        self.state = self.ai.decide_boss_state(player.hp, self.hp, self.dialogue_timer)
        
        for bullet in self.bullets[:]:
            bullet.update(dt)
            if not bullet.active:
                self.bullets.remove(bullet)
            elif bullet.get_rect().colliderect(player.get_rect()):
                if player.take_damage(10):
                    pass
                self.bullets.remove(bullet)
        
        self.attack_timer += dt
        if self.attack_timer >= self.attack_cooldown:
            self.attack(player)
            self.attack_timer = 0
            self.show_dialogue()
        
        if self.dialogue_timer > 0:
            self.dialogue_timer -= dt
    
    def attack(self, player):
        state_config = BOSS_STATES[self.state]
        speed = BULLET_BASE_SPEED * state_config["speed_mult"]
        color = state_config["color"]
        
        pred_x, pred_y = self.ai.get_predicted_position(player.x, player.y)
        
        if self.state == "tranquilo":
            pattern = random.choice([
                AttackPattern.circle_burst(self.x, self.y, 8, speed, color),
                AttackPattern.aimed_shot(self.x, self.y, player.x, player.y, speed, color)
            ])
        elif self.state == "furioso":
            pattern = random.choice([
                AttackPattern.spiral(self.x, self.y, 12, speed, self.rotation, color),
                AttackPattern.aimed_shot(self.x, self.y, pred_x, pred_y, speed * 1.5, color)
            ])
        else:
            pattern = random.choice([
                AttackPattern.circle_burst(self.x, self.y, 20, speed, color),
                AttackPattern.random_spray(self.x, self.y, 30, speed, color),
                AttackPattern.wall(ARENA_X + ARENA_WIDTH // 2, ARENA_Y, True, 10, speed, 30, color)
            ])
        
        self.bullets.extend(pattern)
    
    def show_dialogue(self):
        self.current_dialogue = random.choice(self.dialogues[self.state])
        self.dialogue_timer = 2.0
    
    def draw(self, screen):
        color = BOSS_STATES[self.state]["color"]
        
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 40)
        pygame.draw.circle(screen, (0,0,0), (int(self.x), int(self.y)), 40, 3)
        
        eye_color = (255,255,255) if self.state != "enajenado" else (255,0,0)
        pygame.draw.circle(screen, eye_color, (int(self.x - 15), int(self.y - 10)), 8)
        pygame.draw.circle(screen, eye_color, (int(self.x + 15), int(self.y - 10)), 8)
        
        for bullet in self.bullets:
            bullet.draw(screen)
        
        if self.dialogue_timer > 0:
            font = pygame.font.Font(None, 24)
            text = font.render(self.current_dialogue, True, (255,255,255))
            screen.blit(text, (self.x - text.get_width() // 2, self.y - 80))
''',

    "core/input_handler.py": '''# core/input_handler.py

import pygame

class InputHandler:
    def __init__(self):
        self.keys = pygame.key.get_pressed()
        
    def update(self):
        self.keys = pygame.key.get_pressed()
        
    def get_keys(self):
        return self.keys
''',

    "core/sound_manager.py": '''# core/sound_manager.py

import pygame

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        
    def load_sound(self, name, path):
        try:
            self.sounds[name] = pygame.mixer.Sound(path)
        except:
            print(f"No se pudo cargar: {path}")
    
    def play(self, name):
        if name in self.sounds:
            self.sounds[name].play()
''',

    "game.py": '''# game.py - Loop principal

import pygame
import sys
from settings import *
from player import Player
from boss import Boss
from ai_brain import AIBrain
from core.input_handler import InputHandler
from core.sound_manager import SoundManager

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("BOSS FIGHT - IA Adaptativa")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.input_handler = InputHandler()
        self.sound_manager = SoundManager()
        self.ai_brain = AIBrain()
        
        self.player = Player(ARENA_X + ARENA_WIDTH // 2, ARENA_Y + ARENA_HEIGHT // 2)
        self.boss = Boss(WIDTH // 2, 100, self.ai_brain)
        
        self.game_time = 0
        self.ai_analysis_timer = 0
        self.game_over = False
        self.victory = False
        
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.game_time += dt
            
            self.handle_events()
            if not self.game_over:
                self.update(dt)
            self.draw()
        
        pygame.quit()
        sys.exit()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_r and self.game_over:
                    self.__init__()
    
    def update(self, dt):
        self.input_handler.update()
        keys = self.input_handler.get_keys()
        
        self.player.update(dt, keys)
        self.boss.update(dt, self.player)
        
        self.ai_analysis_timer += dt
        if self.ai_analysis_timer >= AI_ANALYSIS_INTERVAL:
            self.ai_brain.analyze_player(self.player, self.game_time)
            self.ai_analysis_timer = 0
        
        if self.player.hp <= 0:
            self.game_over = True
            self.victory = False
        if self.boss.hp <= 0:
            self.game_over = True
            self.victory = True
    
    def draw(self):
        self.screen.fill(BLACK)
        
        pygame.draw.rect(self.screen, WHITE, 
                        (ARENA_X, ARENA_Y, ARENA_WIDTH, ARENA_HEIGHT), 3)
        
        self.player.draw(self.screen)
        self.boss.draw(self.screen)
        
        self.draw_ui()
        
        if self.game_over:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_ui(self):
        font = pygame.font.Font(None, 36)
        
        hp_text = font.render(f"HP: {self.player.hp}/{self.player.max_hp}", True, RED)
        self.screen.blit(hp_text, (20, 20))
        
        boss_hp_text = font.render(f"BOSS: {self.boss.hp}/{self.boss.max_hp}", True, GREEN)
        self.screen.blit(boss_hp_text, (WIDTH - 250, 20))
        
        state_text = font.render(f"Estado: {self.boss.state.upper()}", True, YELLOW)
        self.screen.blit(state_text, (WIDTH // 2 - 100, 20))
    
    def draw_game_over(self):
        font = pygame.font.Font(None, 72)
        small_font = pygame.font.Font(None, 36)
        
        if self.victory:
            text = font.render("¡VICTORIA!", True, GREEN)
            msg = small_font.render("¡Le ganaste al boss! 🎉", True, WHITE)
        else:
            text = font.render("GAME OVER", True, RED)
            msg = small_font.render("El boss te quebró 💀", True, WHITE)
        
        restart = small_font.render("Presiona R para reiniciar", True, YELLOW)
        
        self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 100))
        self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))
        self.screen.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT // 2 + 50))

if __name__ == "__main__":
    game = Game()
    game.run()
'''
}

# Crear carpetas
carpetas = ["data", "core", "assets/player", "assets/boss", "assets/attacks", 
            "assets/effects", "assets/ui", "assets/voice"]

for carpeta in carpetas:
    os.makedirs(carpeta, exist_ok=True)

# Crear archivos
for nombre, contenido in archivos.items():
    with open(nombre, 'w', encoding='utf-8') as f:
        f.write(contenido)
    print(f"✅ Creado: {nombre}")

# Crear behavior.json vacío
with open("data/behavior.json", "w") as f:
    f.write("{}")

print("\n🎉 ¡TODOS LOS ARCHIVOS CREADOS!")
print("\nAhora ejecuta:\n  python game.py")