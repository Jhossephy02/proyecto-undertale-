# boss.py - Lógica del jefe con ataques múltiples y rápidos

import pygame
import random
import os
from settings import *
from attack_patterns import AttackPattern

class Boss:
    def __init__(self, x, y, ai_brain, boss_config):
        self.x = x
        self.y = y
        self.max_hp = boss_config["hp"]
        self.hp = self.max_hp
        self.name = boss_config["name"]
        self.folder = boss_config["folder"]
        self.state = "tranquilo"
        self.ai = ai_brain
        
        # Cargar sprites
        self.sprites = {}
        self.load_sprites()
        self.current_sprite = None
        
        # Sistema de combate
        self.bullets = []
        self.attack_timer = 0
        self.attack_cooldown = 1.8  # Más tiempo entre ataques (balanceado)
        self.rotation = 0
        
        # Efectos visuales
        self.hit_flash = 0
        self.shake_offset = [0, 0]
        
        self.current_dialogue = ""
        self.dialogue_timer = 0
        
    def load_sprites(self):
        """Carga los sprites del boss desde su carpeta"""
        for state, config in BOSS_STATES.items():
            sprite_path = f"assets/{self.folder}/boos_{state[0]}.png"
            
            if not os.path.exists(sprite_path):
                sprite_path = config["sprite"]
            
            if os.path.exists(sprite_path):
                try:
                    img = pygame.image.load(sprite_path).convert_alpha()
                    img = pygame.transform.scale(img, (80, 80))
                    self.sprites[state] = img
                except Exception as e:
                    print(f"Error cargando sprite: {sprite_path} - {e}")
                    self.sprites[state] = None
            else:
                self.sprites[state] = None
        
    def take_damage(self, amount):
        """Recibe daño y muestra efectos visuales"""
        self.hp -= amount
        self.hit_flash = 0.2
        self.shake_offset = [random.randint(-5, 5), random.randint(-5, 5)]
        
        self.update_state_by_hp()
        
        if self.hp <= 0:
            self.hp = 0
            return True
        return False
    
    def update_state_by_hp(self):
        """Actualiza el estado según el HP actual"""
        hp_percent = self.hp / self.max_hp
        
        for state_name, config in BOSS_STATES.items():
            min_hp, max_hp = config["hp_range"]
            if min_hp <= hp_percent <= max_hp:
                if self.state != state_name:
                    self.state = state_name
                    self.show_dialogue()
                break
        
    def update(self, dt, player, game_phase, speed_multiplier=1.0):
        """Actualiza el boss (solo ataca en fase DODGE)"""
        self.rotation += dt * 2
        
        # Actualizar efectos visuales
        if self.hit_flash > 0:
            self.hit_flash -= dt
        if self.shake_offset != [0, 0]:
            self.shake_offset[0] *= 0.9
            self.shake_offset[1] *= 0.9
            if abs(self.shake_offset[0]) < 0.5 and abs(self.shake_offset[1]) < 0.5:
                self.shake_offset = [0, 0]
        
        # Actualizar balas del boss
        for bullet in self.bullets[:]:
            bullet.update(dt, speed_multiplier)
            if not bullet.active:
                self.bullets.remove(bullet)
            elif bullet.get_rect().colliderect(player.get_rect()):
                if player.take_damage(BOSS_DAMAGE):
                    pass
                bullet.active = False
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
        
        # Solo atacar en fase DODGE
        if game_phase == "DODGE":
            self.attack_timer += dt
            if self.attack_timer >= self.attack_cooldown:
                self.attack(player, speed_multiplier)
                self.attack_timer = 0
        
        # Actualizar diálogo
        if self.dialogue_timer > 0:
            self.dialogue_timer -= dt
    
    def attack(self, player, speed_multiplier=1.0):
        """Genera patrones de ataque múltiples y no predecibles"""
        state_config = BOSS_STATES[self.state]
        base_speed = BULLET_BASE_SPEED * state_config["speed_mult"] * speed_multiplier
        color = state_config["color"]
        
        # Obtener predicción mejorada de la IA
        pred_x, pred_y = self.ai.get_predicted_position(player.x, player.y)
        
        if self.state == "tranquilo":
            # 1-2 patrones simultáneos (más manejable)
            num_patterns = random.randint(1, 2)
            patterns = [
                AttackPattern.circle_burst(self.x, self.y, 8, base_speed, color),
                AttackPattern.aimed_shot(self.x, self.y, pred_x, pred_y, base_speed * 1.2, color),
                AttackPattern.cross_pattern(self.x, self.y, base_speed, color),
            ]
            
        elif self.state == "furioso":
            # 2-3 patrones simultáneos
            num_patterns = random.randint(2, 3)
            patterns = [
                AttackPattern.spiral(self.x, self.y, 12, base_speed, self.rotation, color),
                AttackPattern.double_burst(self.x, self.y, 10, base_speed, color),
                AttackPattern.triple_aimed_shot(self.x, self.y, pred_x, pred_y, base_speed, color),
                AttackPattern.snake_wave(ARENA_X, ARENA_Y, base_speed, color),
                AttackPattern.pirana_circle(self.x, self.y, 10, base_speed * 0.9, color),
            ]
            
        else:  # enajenado
            # 3-4 patrones simultáneos (caos controlado)
            num_patterns = random.randint(3, 4)
            patterns = [
                AttackPattern.spiral_double(self.x, self.y, 15, base_speed, self.rotation, color),
                AttackPattern.random_spray(self.x, self.y, 25, base_speed, color),
                AttackPattern.poison_rain(WIDTH // 2, ARENA_Y - 50, base_speed * 0.8, color),
                AttackPattern.converging_attack(pred_x, pred_y, base_speed * 1.2, color),
                AttackPattern.cross_pattern(self.x, self.y, base_speed * 1.3, color),
            ]
        
        # Seleccionar patrones aleatorios sin repetir
        selected_patterns = random.sample(patterns, min(num_patterns, len(patterns)))
        
        for pattern in selected_patterns:
            self.bullets.extend(pattern)
    
    def show_dialogue(self):
        """Muestra un diálogo según el estado"""
        dialogues = BOSS_STATES[self.state]["dialogue"]
        self.current_dialogue = random.choice(dialogues)
        self.dialogue_timer = 2.0
    
    def clear_bullets(self):
        """Elimina todas las balas"""
        self.bullets.clear()
    
    def draw(self, screen, game_phase):
        """Dibuja el boss"""
        draw_x = int(self.x + self.shake_offset[0])
        draw_y = int(self.y + self.shake_offset[1])
        
        # Usar sprite si está disponible
        if self.sprites.get(self.state):
            sprite = self.sprites[self.state]
            
            if self.hit_flash > 0:
                sprite_copy = sprite.copy()
                sprite_copy.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_ADD)
                screen.blit(sprite_copy, 
                           (draw_x - sprite.get_width() // 2, 
                            draw_y - sprite.get_height() // 2))
            else:
                screen.blit(sprite, 
                           (draw_x - sprite.get_width() // 2, 
                            draw_y - sprite.get_height() // 2))
        else:
            # Fallback: círculo
            color = BOSS_STATES[self.state]["color"]
            if self.hit_flash > 0:
                color = WHITE
            
            pygame.draw.circle(screen, color, (draw_x, draw_y), 40)
            pygame.draw.circle(screen, BLACK, (draw_x, draw_y), 40, 3)
            
            eye_color = WHITE if self.state != "enajenado" else RED
            pygame.draw.circle(screen, eye_color, (draw_x - 15, draw_y - 10), 8)
            pygame.draw.circle(screen, eye_color, (draw_x + 15, draw_y - 10), 8)
        
        # Dibujar balas solo en fase DODGE
        if game_phase == "DODGE":
            for bullet in self.bullets:
                bullet.draw(screen)
        
        # Diálogo
        if self.dialogue_timer > 0:
            font = pygame.font.Font(None, 24)
            text = font.render(self.current_dialogue, True, WHITE)
            text_rect = text.get_rect(center=(self.x, self.y - 80))
            
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(screen, BLACK, bg_rect)
            pygame.draw.rect(screen, WHITE, bg_rect, 2)
            
            screen.blit(text, text_rect)
        
        # Barra de HP
        self.draw_hp_bar(screen)
    
    def draw_hp_bar(self, screen):
        """Dibuja la barra de HP del boss"""
        bar_width = 200
        bar_height = 20
        bar_x = WIDTH // 2 - bar_width // 2
        bar_y = 70
        
        pygame.draw.rect(screen, WHITE, (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4), 2)
        pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height))
        
        hp_percent = self.hp / self.max_hp
        hp_bar_width = int(bar_width * hp_percent)
        hp_color = GREEN if hp_percent > 0.66 else (YELLOW if hp_percent > 0.33 else RED)
        pygame.draw.rect(screen, hp_color, (bar_x, bar_y, hp_bar_width, bar_height))
        
        font = pygame.font.Font(None, 20)
        hp_text = f"{int(self.hp)}/{self.max_hp}"
        text_surf = font.render(hp_text, True, WHITE)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, bar_y + bar_height // 2))
        screen.blit(text_surf, text_rect)
        
        # Nombre del boss
        name_font = pygame.font.Font(None, 24)
        name_surf = name_font.render(self.name, True, BOSS_STATES[self.state]["color"])
        name_rect = name_surf.get_rect(center=(WIDTH // 2, bar_y - 15))
        screen.blit(name_surf, name_rect)