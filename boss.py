# boss.py - Sistema de bosses con 3 fases

import pygame
import random
import os
import math
from settings import *
from attack_patterns import AttackPattern

class Boss:
    def __init__(self, x, y, ai_brain, phase=1):
        self.x = x
        self.y = y
        self.phase = phase
        self.phase_config = BOSS_PHASES[phase]
        
        self.hp = self.phase_config["hp"]
        self.max_hp = self.phase_config["hp"]
        self.speed_multiplier = self.phase_config["speed_base"]
        self.damage_multiplier = self.phase_config["damage_base"]
        
        self.state = "tranquilo"
        self.ai = ai_brain
        
        # Sprites
        self.sprites = {}
        self.load_sprites()
        
        # Combate
        self.bullets = []
        self.attack_timer = 0
        self.attack_cooldown = 2.0 / self.speed_multiplier
        self.rotation = 0
        
        # Efectos
        self.hit_flash = 0
        self.shake_offset = [0, 0]
        
        # Resurrección (solo fase 3)
        self.can_revive = self.phase_config.get("can_revive", False)
        self.has_revived_phase1 = False
        self.has_revived_phase2 = False
        self.revived_bosses = []
        
        # Diálogos por fase
        self.dialogues = self.get_dialogues_for_phase()
        self.current_dialogue = ""
        self.dialogue_timer = 0
        
    def get_dialogues_for_phase(self):
        """Retorna diálogos según la fase"""
        if self.phase == 1:
            return {
                "tranquilo": ["Facilito causa 😎", "Muévete ps jaja", "Ta' suave nomás"],
                "furioso": ["¡Ya me picaste! 😤", "¡Ahora sí! 💢", "¡Te voy a atrapar!"],
                "enajenado": ["¡TE QUEBRO! 💀", "¡MUEREEE! 🔥", "¡YA FUE!"]
            }
        elif self.phase == 2:
            return {
                "tranquilo": ["¿Pensaste que era fácil? 😏", "¡Ahora va en serio!", "Nivel 2 activado"],
                "furioso": ["¡MÁS RÁPIDO! ⚡", "¡NO ESCAPAS! 💥", "¡TE ALCANZO!"],
                "enajenado": ["¡MÁXIMA POTENCIA! 🔥", "¡MODO BERSERK! 💢", "¡DESTRUCCIÓN!"]
            }
        else:  # Fase 3
            return {
                "tranquilo": ["Soy el jefe supremo 👑", "Mis aliados volverán", "Poder definitivo"],
                "furioso": ["¡RESURRECCIÓN! ⚡", "¡Regresen a la batalla!", "¡Juntos somos invencibles!"],
                "enajenado": ["¡TODO MI PODER! 💀", "¡APOCALIPSIS! 🔥", "¡FIN DEL JUEGO!"]
            }
    
    def load_sprites(self):
        """Carga sprites del boss"""
        for state, config in BOSS_STATES.items():
            sprite_path = config["sprite"]
            if os.path.exists(sprite_path):
                try:
                    img = pygame.image.load(sprite_path).convert_alpha()
                    base_size = 80
                    # Boss más grande en fases superiores
                    size = base_size + (self.phase - 1) * 10
                    img = pygame.transform.scale(img, (size, size))
                    self.sprites[state] = img
                except:
                    self.sprites[state] = None
            else:
                self.sprites[state] = None
    
    def take_damage(self, amount):
        """Recibe daño"""
        adjusted_damage = amount / self.damage_multiplier
        self.hp -= adjusted_damage
        self.hit_flash = 0.2
        self.shake_offset = [random.randint(-5, 5), random.randint(-5, 5)]
        
        if self.hp <= 0:
            self.hp = 0
            return True
        return False
    
    def revive_previous_bosses(self):
        """Resucita los bosses anteriores (solo fase 3)"""
        if not self.can_revive:
            return []
        
        revived = []
        
        # Revivir Boss Fase 1 (solo una vez)
        if not self.has_revived_phase1:
            boss1 = Boss(self.x - 150, self.y + 100, self.ai, phase=1)
            boss1.hp = boss1.max_hp // 2  # Mitad de HP
            revived.append(boss1)
            self.has_revived_phase1 = True
            print("¡Boss Fase 1 revivido!")
        
        # Revivir Boss Fase 2 (solo una vez)
        if not self.has_revived_phase2 and self.hp < self.max_hp * 0.3:
            boss2 = Boss(self.x + 150, self.y + 100, self.ai, phase=2)
            boss2.hp = boss2.max_hp // 2  # Mitad de HP
            revived.append(boss2)
            self.has_revived_phase2 = True
            print("¡Boss Fase 2 revivido!")
        
        return revived
    
    def update(self, dt, player):
        self.rotation += dt * 2
        
        # Actualizar estado
        self.state = self.ai.decide_boss_state(player.hp, self.hp, self.dialogue_timer)
        
        # Efectos visuales
        if self.hit_flash > 0:
            self.hit_flash -= dt
        if self.shake_offset != [0, 0]:
            self.shake_offset[0] *= 0.9
            self.shake_offset[1] *= 0.9
            if abs(self.shake_offset[0]) < 0.5 and abs(self.shake_offset[1]) < 0.5:
                self.shake_offset = [0, 0]
        
        # Actualizar balas
        for bullet in self.bullets[:]:
            bullet.update(dt)
            if not bullet.active:
                self.bullets.remove(bullet)
            elif bullet.get_rect().colliderect(player.get_rect()):
                damage = 10 * self.damage_multiplier
                if player.take_damage(damage):
                    pass
                self.bullets.remove(bullet)
        
        # Colisiones con balas del jugador
        for bullet in player.bullets[:]:
            boss_rect = pygame.Rect(self.x - 40, self.y - 40, 80, 80)
            if bullet.get_rect().colliderect(boss_rect):
                self.take_damage(bullet.damage)
                bullet.active = False
                player.bullets.remove(bullet)
        
        # Colisiones con ataques especiales
        for special in player.special_attacks[:]:
            if not special.has_hit:
                boss_center = pygame.math.Vector2(self.x, self.y)
                special_center = pygame.math.Vector2(special.x, special.y)
                distance = boss_center.distance_to(special_center)
                
                if distance <= special.radius + 40:
                    self.take_damage(special.damage)
                    special.has_hit = True
        
        # Sistema de ataque
        self.attack_timer += dt
        if self.attack_timer >= self.attack_cooldown:
            self.attack(player)
            self.attack_timer = 0
            self.show_dialogue()
        
        if self.dialogue_timer > 0:
            self.dialogue_timer -= dt
    
    def attack(self, player):
        """Genera ataques según fase y estado"""
        state_config = BOSS_STATES[self.state]
        speed = BULLET_BASE_SPEED * state_config["speed_mult"] * self.speed_multiplier
        color = self.phase_config["color"]
        
        pred_x, pred_y = self.ai.get_predicted_position(player.x, player.y)
        
        # Ataques por fase
        if self.phase == 1:
            pattern = self.get_phase1_attack(player, pred_x, pred_y, speed, color)
        elif self.phase == 2:
            pattern = self.get_phase2_attack(player, pred_x, pred_y, speed, color)
        else:  # Fase 3
            pattern = self.get_phase3_attack(player, pred_x, pred_y, speed, color)
        
        self.bullets.extend(pattern)
    
    def get_phase1_attack(self, player, pred_x, pred_y, speed, color):
        """Ataques normales fase 1"""
        if self.state == "tranquilo":
            patterns = [
                AttackPattern.circle_burst(self.x, self.y, 8, speed, color),
                AttackPattern.aimed_shot(self.x, self.y, player.x, player.y, speed, color),
            ]
        elif self.state == "furioso":
            patterns = [
                AttackPattern.spiral(self.x, self.y, 12, speed, self.rotation, color),
                AttackPattern.triple_aimed_shot(self.x, self.y, pred_x, pred_y, speed, color),
            ]
        else:
            patterns = [
                AttackPattern.circle_burst(self.x, self.y, 16, speed, color),
                AttackPattern.random_spray(self.x, self.y, 25, speed, color),
            ]
        return random.choice(patterns)
    
    def get_phase2_attack(self, player, pred_x, pred_y, speed, color):
        """Ataques más rápidos fase 2"""
        if self.state == "tranquilo":
            patterns = [
                AttackPattern.double_burst(self.x, self.y, 10, speed, color),
                AttackPattern.wave_attack(ARENA_X, ARENA_Y, speed, color),
            ]
        elif self.state == "furioso":
            patterns = [
                AttackPattern.spiral_double(self.x, self.y, 15, speed, self.rotation, color),
                AttackPattern.pirana_circle(self.x, self.y, 12, speed, color),
                AttackPattern.converging_attack(player.x, player.y, speed * 1.2, color),
            ]
        else:
            patterns = [
                AttackPattern.laser_grid(ARENA_X, ARENA_Y, speed, color),
                AttackPattern.random_spray(self.x, self.y, 40, speed, color),
                [*AttackPattern.wall(ARENA_X + ARENA_WIDTH // 2, ARENA_Y, True, 12, speed, 25, color),
                 *AttackPattern.circle_burst(self.x, self.y, 20, speed, color)]
            ]
        
        pattern = random.choice(patterns)
        if isinstance(pattern, list) and pattern and isinstance(pattern[0], list):
            pattern = [bullet for sublist in pattern for bullet in sublist]
        return pattern
    
    def get_phase3_attack(self, player, pred_x, pred_y, speed, color):
        """Ataques supremos fase 3"""
        if self.state == "tranquilo":
            patterns = [
                AttackPattern.spiral_double(self.x, self.y, 18, speed, self.rotation, color),
                AttackPattern.liana_curtain(ARENA_X, ARENA_Y - 50, speed, color),
            ]
        elif self.state == "furioso":
            patterns = [
                [*AttackPattern.poison_rain(WIDTH // 2, ARENA_Y - 50, speed, color),
                 *AttackPattern.snake_wave(ARENA_X, ARENA_Y, speed, color)],
                [*AttackPattern.pirana_circle(self.x, self.y, 15, speed, color),
                 *AttackPattern.converging_attack(pred_x, pred_y, speed * 1.3, color)],
            ]
        else:
            patterns = [
                [*AttackPattern.laser_grid(ARENA_X, ARENA_Y, speed, color),
                 *AttackPattern.circle_burst(self.x, self.y, 24, speed, color)],
                [*AttackPattern.random_spray(self.x, self.y, 50, speed, color),
                 *AttackPattern.wall(ARENA_X + ARENA_WIDTH // 2, ARENA_Y, True, 15, speed, 20, color),
                 *AttackPattern.wall(ARENA_X + ARENA_WIDTH // 2, ARENA_Y, False, 15, speed, 20, color)],
            ]
        
        pattern = random.choice(patterns)
        if isinstance(pattern, list) and pattern and isinstance(pattern[0], list):
            pattern = [bullet for sublist in pattern for bullet in sublist]
        return pattern
    
    def show_dialogue(self):
        """Muestra diálogo"""
        self.current_dialogue = random.choice(self.dialogues[self.state])
        self.dialogue_timer = 2.0
    
    def draw(self, screen):
        """Dibuja el boss"""
        draw_x = int(self.x + self.shake_offset[0])
        draw_y = int(self.y + self.shake_offset[1])
        
        # Sprite
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
            # Fallback
            color = self.phase_config["color"]
            if self.hit_flash > 0:
                color = WHITE
            
            size = 40 + (self.phase - 1) * 5
            pygame.draw.circle(screen, color, (draw_x, draw_y), size)
            pygame.draw.circle(screen, BLACK, (draw_x, draw_y), size, 3)
        
        # Balas
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
        
        # Barra HP
        self.draw_hp_bar(screen)
    
    def draw_hp_bar(self, screen):
        """Dibuja barra de HP"""
        bar_width = 200
        bar_height = 20
        bar_x = WIDTH // 2 - bar_width // 2
        bar_y = 70 + (self.phase - 1) * 30
        
        pygame.draw.rect(screen, WHITE, (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4), 2)
        pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height))
        
        hp_percent = self.hp / self.max_hp
        hp_bar_width = int(bar_width * hp_percent)
        hp_color = GREEN if hp_percent > 0.5 else (YELLOW if hp_percent > 0.25 else RED)
        pygame.draw.rect(screen, hp_color, (bar_x, bar_y, hp_bar_width, bar_height))
        
        # Texto
        font = pygame.font.Font(None, 18)
        phase_text = f"FASE {self.phase} | {int(self.hp)}/{self.max_hp}"
        text_surf = font.render(phase_text, True, WHITE)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, bar_y + bar_height // 2))
        screen.blit(text_surf, text_rect)