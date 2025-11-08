# boss.py - Lógica del jefe con sprites y daño

import pygame
import random
import os
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
        
        # Cargar sprites
        self.sprites = {}
        self.load_sprites()
        self.current_sprite = None
        
        # Sistema de combate
        self.bullets = []
        self.attack_timer = 0
        self.attack_cooldown = 2.0
        self.rotation = 0
        
        # Efectos visuales
        self.hit_flash = 0
        self.shake_offset = [0, 0]
        
        # Diálogos peruanos
        self.dialogues = {
            "tranquilo": [
                "Facilito causa 😏", 
                "Muévete ps jaja", 
                "Ta' suave nomás",
                "¿Eso es todo?",
                "Muy flojo causa"
            ],
            "furioso": [
                "¡Ya me picaste mano! 😤", 
                "¡Ahora sí! 💢", 
                "¡Te voy a atrapar!",
                "¡Ya te la buscaste! 😠",
                "¡Me hiciste enojar!"
            ],
            "enajenado": [
                "¡TE VOY A QUEBRAR! 💀", 
                "¡MUEREEE! 🔥", 
                "¡YA FUE!",
                "¡NO ESCAPAS! ☠️",
                "¡AHORA SÍ CAUSA! 💥"
            ]
        }
        self.current_dialogue = ""
        self.dialogue_timer = 0
        
    def load_sprites(self):
        """Carga los sprites del boss"""
        for state, config in BOSS_STATES.items():
            sprite_path = config["sprite"]
            if os.path.exists(sprite_path):
                try:
                    img = pygame.image.load(sprite_path)
                    # Escalar a tamaño apropiado
                    img = pygame.transform.scale(img, (80, 80))
                    self.sprites[state] = img
                except:
                    print(f"No se pudo cargar sprite: {sprite_path}")
                    self.sprites[state] = None
            else:
                self.sprites[state] = None
        
    def take_damage(self, amount):
        """Recibe daño y muestra efectos visuales"""
        self.hp -= amount
        self.hit_flash = 0.2  # Flash de 0.2 segundos
        
        # Shake effect
        self.shake_offset = [random.randint(-5, 5), random.randint(-5, 5)]
        
        if self.hp <= 0:
            self.hp = 0
            return True
        return False
        
    def update(self, dt, player):
        self.rotation += dt * 2
        
        # Actualizar estado basado en IA
        self.state = self.ai.decide_boss_state(player.hp, self.hp, self.dialogue_timer)
        
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
            bullet.update(dt)
            if not bullet.active:
                self.bullets.remove(bullet)
            elif bullet.get_rect().colliderect(player.get_rect()):
                if player.take_damage(10):
                    pass
                self.bullets.remove(bullet)
        
        # Verificar colisiones con balas del jugador
        for bullet in player.bullets[:]:
            boss_rect = pygame.Rect(self.x - 40, self.y - 40, 80, 80)
            if bullet.get_rect().colliderect(boss_rect):
                self.take_damage(bullet.damage)
                bullet.active = False
                player.bullets.remove(bullet)
        
        # Sistema de ataque
        self.attack_timer += dt
        if self.attack_timer >= self.attack_cooldown:
            self.attack(player)
            self.attack_timer = 0
            self.show_dialogue()
        
        if self.dialogue_timer > 0:
            self.dialogue_timer -= dt
    
    def attack(self, player):
        """Genera patrones de ataque según el estado usando sprites específicos"""
        state_config = BOSS_STATES[self.state]
        speed = BULLET_BASE_SPEED * state_config["speed_mult"]
        color = state_config["color"]
        
        # Obtener predicción de posición del jugador
        pred_x, pred_y = self.ai.get_predicted_position(player.x, player.y)
        
        if self.state == "tranquilo":
            # Ataques básicos - FLECHAS simples
            patterns = [
                AttackPattern.circle_burst(self.x, self.y, 8, speed, color),  # Flechas en círculo
                AttackPattern.aimed_shot(self.x, self.y, player.x, player.y, speed, color),  # Flecha directa
                AttackPattern.double_burst(self.x, self.y, 6, speed, color),  # Doble ráfaga de flechas
                AttackPattern.cross_pattern(self.x, self.y, speed, color)  # Cruz de flechas
            ]
            pattern = random.choice(patterns)
            
        elif self.state == "furioso":
            # Ataques medios - Mezcla de SERPIENTES, LIANAS y PIRAÑAS
            patterns = [
                AttackPattern.spiral(self.x, self.y, 12, speed, self.rotation, color),  # Espiral de serpientes
                AttackPattern.triple_aimed_shot(self.x, self.y, pred_x, pred_y, speed, color),  # 3 serpientes
                AttackPattern.wave_attack(ARENA_X, ARENA_Y, speed, color),  # Ola de lianas
                AttackPattern.pirana_circle(self.x, self.y, 10, speed, color),  # Círculo de pirañas
                AttackPattern.snake_wave(ARENA_X, ARENA_Y, speed, color),  # Serpientes en zigzag
                AttackPattern.converging_attack(player.x, player.y, speed, color)  # Troncos convergentes
            ]
            pattern = random.choice(patterns)
            
        else:  # enajenado
            # Ataques extremos - CAOS TOTAL con todos los sprites
            patterns = [
                AttackPattern.random_spray(self.x, self.y, 30, speed, color),  # Spray de pirañas
                AttackPattern.laser_grid(ARENA_X, ARENA_Y, speed, color),  # Rejilla de veneno
                AttackPattern.spiral_double(self.x, self.y, 15, speed, self.rotation, color),  # Doble espiral serpientes
                AttackPattern.wall(ARENA_X + ARENA_WIDTH // 2, ARENA_Y, True, 10, speed, 30, color),  # Muro de troncos
                AttackPattern.poison_rain(WIDTH // 2, ARENA_Y - 50, speed, color),  # Lluvia de veneno
                AttackPattern.liana_curtain(ARENA_X, ARENA_Y - 50, speed, color),  # Cortina de lianas
                AttackPattern.circle_burst(self.x, self.y, 20, speed, color),  # 20 flechas en círculo
                # Combo attacks
                [*AttackPattern.snake_wave(ARENA_X, ARENA_Y, speed, color),
                 *AttackPattern.wave_attack(ARENA_X, ARENA_Y + 100, speed, color)]  # Combo lianas+serpientes
            ]
            pattern = random.choice(patterns)
            # Si elegimos un combo (lista de listas), aplanarlo
            if isinstance(pattern, list) and pattern and isinstance(pattern[0], list):
                pattern = [bullet for sublist in pattern for bullet in sublist]
        
        self.bullets.extend(pattern)
    
    def show_dialogue(self):
        """Muestra un diálogo aleatorio según el estado"""
        self.current_dialogue = random.choice(self.dialogues[self.state])
        self.dialogue_timer = 2.0
    
    def draw(self, screen):
        """Dibuja el boss con sprite o círculo de respaldo"""
        draw_x = int(self.x + self.shake_offset[0])
        draw_y = int(self.y + self.shake_offset[1])
        
        # Usar sprite si está disponible
        if self.sprites.get(self.state):
            sprite = self.sprites[self.state]
            
            # Flash blanco cuando recibe daño
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
            # Respaldo: dibujar círculo si no hay sprite
            color = BOSS_STATES[self.state]["color"]
            if self.hit_flash > 0:
                color = WHITE
            
            pygame.draw.circle(screen, color, (draw_x, draw_y), 40)
            pygame.draw.circle(screen, BLACK, (draw_x, draw_y), 40, 3)
            
            # Ojos
            eye_color = WHITE if self.state != "enajenado" else RED
            pygame.draw.circle(screen, eye_color, (draw_x - 15, draw_y - 10), 8)
            pygame.draw.circle(screen, eye_color, (draw_x + 15, draw_y - 10), 8)
        
        # Dibujar balas
        for bullet in self.bullets:
            bullet.draw(screen)
        
        # Dibujar diálogo
        if self.dialogue_timer > 0:
            font = pygame.font.Font(None, 24)
            text = font.render(self.current_dialogue, True, WHITE)
            text_rect = text.get_rect(center=(self.x, self.y - 80))
            
            # Fondo del diálogo
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(screen, BLACK, bg_rect)
            pygame.draw.rect(screen, WHITE, bg_rect, 2)
            
            screen.blit(text, text_rect)
        
        # Barra de HP del boss
        self.draw_hp_bar(screen)
    
    def draw_hp_bar(self, screen):
        """Dibuja la barra de HP del boss"""
        bar_width = 200
        bar_height = 20
        bar_x = WIDTH // 2 - bar_width // 2
        bar_y = 70
        
        # Borde
        pygame.draw.rect(screen, WHITE, (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4), 2)
        
        # Fondo
        pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height))
        
        # HP actual
        hp_percent = self.hp / self.max_hp
        hp_bar_width = int(bar_width * hp_percent)
        hp_color = GREEN if hp_percent > 0.5 else (YELLOW if hp_percent > 0.25 else RED)
        pygame.draw.rect(screen, hp_color, (bar_x, bar_y, hp_bar_width, bar_height))
        
        # Texto de HP
        font = pygame.font.Font(None, 20)
        hp_text = f"{int(self.hp)}/{self.max_hp}"
        text_surf = font.render(hp_text, True, WHITE)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, bar_y + bar_height // 2))
        screen.blit(text_surf, text_rect)