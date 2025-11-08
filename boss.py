# boss.py - Lógica del jefe

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
