# boss.py - Sistema de bosses actualizado con sprites correctos

import pygame
import random
import os
import math
from settings import *
from attack_patterns import AttackPattern, LaserBeam, Warning

class Boss:
    def __init__(self, x, y, ai_brain, phase=1, difficulty_mod=None, is_spirit=False): 
        self.x = x
        self.y = y
        self.phase = phase
        self.phase_config = BOSS_PHASES[phase]
        self.is_spirit = is_spirit  # Indica si es un boss revivido
        
        mod = difficulty_mod if difficulty_mod else GAME_MODE_MODIFIERS["normal"]
        
        self.hp = int(self.phase_config["hp"] * mod["boss_hp_mult"])
        self.max_hp = self.hp
        
        # Si es espíritu, tiene menos HP
        if self.is_spirit:
            self.hp = self.max_hp // 2
            self.max_hp = self.hp
        
        self.speed_multiplier = self.phase_config["speed_base"] * mod["boss_speed_mult"]
        self.damage_multiplier = self.phase_config["damage_base"] * mod["boss_damage_mult"]
        self.name = self.phase_config["name"]
        
        self.state = "tranquilo"
        self.ai = ai_brain
        self.dialogue_timer = 0 
        self.dialogues = self.get_dialogues_for_phase()
        self.current_dialogue = ""
        
        self.difficulty_mod = mod 
        
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
        
        # Resurrección (solo Yacumama no espíritu)
        self.can_revive = self.phase_config.get("can_revive", False) and not self.is_spirit
        self.has_revived = False
        
        # Sistema de láser (Yacumama)
        self.lasers = []
        self.laser_cooldown = 8.0  # Cooldown entre láseres
        self.laser_timer = 0
        self.warnings = []
        
        # Regeneración (Yacumama cuando revive)
        self.regenerating = False
        self.regen_rate = 0.5  # HP por segundo
        self.regen_target = 0
        
    def get_dialogues_for_phase(self):
        if self.phase == 1:
            return {
                "tranquilo": ["Yoyo noko jakon", "Ati nin yoitima", "Ea jakonai"],
                "furioso": ["¡Ea pikoti yoshi! ⚡", "¡Yoyo íki jato!", "¡Jaton iki!"],
                "enajenado": ["¡YOYO RONO JATO! 💀", "¡JAWE! 🌊", "¡EA WESTIORA!"]
            }
        elif self.phase == 2:
            return {
                "tranquilo": ["Bake shipash jakon 👣", "¿Jatian ea akakin?", "Bakeska jatora"],
                "furioso": ["¡Rao senkin bake! 💚", "¡Bakeskatian!", "¡JATON BAKE!"],
                "enajenado": ["¡OXI BETSÁ! 🍄", "¡JATON NETE! 💢", "¡JATIAN!"]
            }
        else:
            return {
                "tranquilo": ["Rono yoibo jakon 🐍", "Yoyo mama", "Ea westioni kopi"],
                "furioso": ["¡BETAN YOINI! ⚡", "¡Jakonbo betanai!", "¡Ikonbaon!"],
                "enajenado": ["¡WESTIORA RONO! 💀", "¡KOPI WESTIORA! 🔥", "¡JATON JAWE!"]
            }
    
    def load_sprites(self):
        """Carga sprites según el estado y si es espíritu"""
        if self.is_spirit:
            # Sprites especiales para espíritus
            if self.phase == 1:
                sprite_path = "assets/boss/yacuruna-espiritu.png"
            elif self.phase == 2:
                sprite_path = "assets/boss/espiritu-chullachaqui.png"
            else:
                sprite_path = self.phase_config.get("sprite_normal", "")
            
            # Un solo sprite para espíritus
            if os.path.exists(sprite_path):
                try:
                    img = pygame.image.load(sprite_path).convert_alpha()
                    size = 70  # Más pequeños que los originales
                    img = pygame.transform.scale(img, (size, size))
                    # Semi-transparentes
                    img.set_alpha(200)
                    self.sprites["tranquilo"] = img
                    self.sprites["furioso"] = img
                    self.sprites["enajenado"] = img
                except Exception as e:
                    print(f"Error cargando sprite espíritu: {e}")
        else:
            # Sprites normales según el estado
            # Mapeo correcto de estados a sprites
            if self.phase == 1:  # Yacuruna
                sprite_map = {
                    "tranquilo": "assets/boss/boos_tranki.png",
                    "furioso": "assets/boss/boos_furioso.png",
                    "enajenado": "assets/boss/boos_enojado.png"
                }
            elif self.phase == 2:  # Chullachaqui
                sprite_map = {
                    "tranquilo": "assets/boss/CHULLACHAQUI.png",
                    "furioso": "assets/boss/Chullachaqui_furioso.png",
                    "enajenado": "assets/boss/CHULLACHAQUI-ENOJADO.png"
                }
            else:  # Yacumama
                sprite_map = {
                    "tranquilo": "assets/boss/yacumama.png",
                    "furioso": "assets/boss/yacumama_furioso.png",
                    "enajenado": "assets/boss/yacumama-enojado.png"
                }
            
            for state, sprite_path in sprite_map.items():
                if os.path.exists(sprite_path):
                    try:
                        img = pygame.image.load(sprite_path).convert_alpha()
                        size = 80 + (self.phase - 1) * 15
                        img = pygame.transform.scale(img, (size, size))
                        self.sprites[state] = img
                    except Exception as e:
                        print(f"Error cargando {sprite_path}: {e}")
                        self.sprites[state] = None
                else:
                    self.sprites[state] = None
    
    def take_damage(self, amount):
        adjusted_damage = amount / self.damage_multiplier
        self.hp -= adjusted_damage
        self.hit_flash = 0.2
        self.shake_offset = [random.randint(-5, 5), random.randint(-5, 5)]
        
        self.update_state_by_hp()
        
        if self.hp <= 0:
            self.hp = 0
            return True
        return False
    
    def update_state_by_hp(self):
        hp_percent = self.hp / self.max_hp
        
        for state_name, config in BOSS_STATES.items():
            min_hp, max_hp = config["hp_range"]
            if min_hp <= hp_percent <= max_hp:
                if self.state != state_name:
                    self.state = state_name
                    self.show_dialogue()
                break
    
    def start_revival_sequence(self):
        """Inicia la secuencia de resurrección"""
        if not self.can_revive or self.has_revived:
            return []
        
        self.has_revived = True
        self.regenerating = True
        self.regen_target = int(self.max_hp * 0.75)  # Regenerar hasta 75%
        
        revived = []
        mod = self.difficulty_mod
        
        # Revivir Yacuruna como espíritu
        boss1 = Boss(self.x - 150, self.y + 50, self.ai, phase=1, difficulty_mod=mod, is_spirit=True) 
        revived.append(boss1)
        
        # Revivir Chullachaqui como espíritu
        boss2 = Boss(self.x + 150, self.y + 50, self.ai, phase=2, difficulty_mod=mod, is_spirit=True) 
        revived.append(boss2)
        
        print("¡Yacumama invoca a los espíritus de los caídos!")
        return revived

    def update(self, dt, player):
        self.dialogue_timer += dt
        self.rotation += dt * 2
        
        # Regeneración
        if self.regenerating:
            if self.hp < self.regen_target:
                self.hp += self.regen_rate * dt
                if self.hp >= self.regen_target:
                    self.hp = self.regen_target
                    self.regenerating = False
                    print("¡Yacumama completó su regeneración!")
            else:
                self.regenerating = False
        
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
        
        # Actualizar advertencias
        for warning in self.warnings[:]:
            warning.update(dt)
            if not warning.active:
                self.warnings.remove(warning)
        
        # Actualizar láseres
        for laser in self.lasers[:]:
            laser.update(dt)
            if not laser.active:
                self.lasers.remove(laser)
            elif laser.check_collision(player.get_rect()):
                damage = 30 * self.damage_multiplier
                if player.take_damage(damage):
                    pass
        
        # Actualizar balas
        for bullet in self.bullets[:]:
            bullet.update(dt, self.speed_multiplier)
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
        
        # Ataque de láser (Yacumama en estado enajenado)
        if self.phase == 3 and not self.is_spirit:
            self.laser_timer += dt
            if self.laser_timer >= self.laser_cooldown and self.state == "enajenado":
                self.perform_laser_attack(player)
                self.laser_timer = 0
        
        if self.dialogue_timer > 0:
            self.dialogue_timer -= dt
        
    def perform_laser_attack(self, player):
        """Yacumama dispara un láser devastador"""
        # Posiciones posibles alrededor del área de combate
        positions = [
            (ARENA_X - 60, ARENA_Y + ARENA_HEIGHT // 2),  # Izquierda
            (ARENA_X + ARENA_WIDTH + 60, ARENA_Y + ARENA_HEIGHT // 2),  # Derecha
            (ARENA_X + ARENA_WIDTH // 2, ARENA_Y - 60),  # Arriba
        ]
        
        new_pos = random.choice(positions)
        self.x, self.y = new_pos
        
        # Ángulo hacia el jugador
        angle = math.atan2(player.y - self.y, player.x - self.x)
        
        # Crear advertencia
        warning = AttackPattern.create_laser_warning(self.x, self.y, angle)
        self.warnings.append(warning)
        
        # Crear láser
        laser = LaserBeam(self.x, self.y, angle)
        self.lasers.append(laser)
        
        print(f"¡Yacumama dispara láser desde ({int(self.x)}, {int(self.y)})!")
    
    def attack(self, player):
        state_config = BOSS_STATES[self.state]
        speed = BULLET_BASE_SPEED * state_config["speed_mult"] * self.speed_multiplier
        color = self.phase_config["color"]
        
        pred_x, pred_y = self.ai.get_predicted_position(player.x, player.y)
        
        if self.phase == 1:
            pattern = self.get_yacuruna_attack(player, pred_x, pred_y, speed, color)
        elif self.phase == 2:
            pattern = self.get_chullachaqui_attack(player, pred_x, pred_y, speed, color)
        else:
            pattern = self.get_yacumama_attack(player, pred_x, pred_y, speed, color)
        
        self.bullets.extend(pattern)
    
    def get_yacuruna_attack(self, player, pred_x, pred_y, speed, color):
        if self.state == "tranquilo":
            patterns = [
                AttackPattern.circle_burst(self.x, self.y, 8, speed, BLUE),
                AttackPattern.water_stream(self.x, self.y, player.x, player.y, speed, CYAN),
            ]
        elif self.state == "furioso":
            patterns = [
                AttackPattern.spiral(self.x, self.y, 12, speed, self.rotation, CYAN),
                AttackPattern.water_stream(self.x, self.y, pred_x, pred_y, speed * 1.2, BLUE),
            ]
        else:
            patterns = [
                [*AttackPattern.circle_burst(self.x, self.y, 16, speed, BLUE),
                 *AttackPattern.water_stream(self.x, self.y, player.x, player.y, speed, CYAN)],
            ]
        
        pattern = random.choice(patterns)
        if isinstance(pattern, list) and pattern and isinstance(pattern[0], list):
            pattern = [bullet for sublist in pattern for bullet in sublist]
        return pattern
    
    def get_chullachaqui_attack(self, player, pred_x, pred_y, speed, color):
        if self.state == "tranquilo":
            patterns = [
                AttackPattern.poison_rain(WIDTH // 2, ARENA_Y - 50, speed, GREEN),
                AttackPattern.triple_aimed_shot(self.x, self.y, pred_x, pred_y, speed, GREEN),
            ]
        elif self.state == "furioso":
            patterns = [
                AttackPattern.spiral(self.x, self.y, 15, speed, self.rotation, GREEN),
                [*AttackPattern.poison_rain(WIDTH // 2, ARENA_Y - 50, speed, GREEN),
                 *AttackPattern.circle_burst(self.x, self.y, 12, speed, GREEN)],
            ]
        else:
            patterns = [
                [*AttackPattern.poison_rain(WIDTH // 2, ARENA_Y - 50, speed * 1.2, GREEN),
                 *AttackPattern.poison_rain(WIDTH // 2, ARENA_Y - 50, speed * 1.2, GREEN)],
            ]
        
        pattern = random.choice(patterns)
        if isinstance(pattern, list) and pattern and isinstance(pattern[0], list):
            pattern = [bullet for sublist in pattern for bullet in sublist]
        return pattern
    
    def get_yacumama_attack(self, player, pred_x, pred_y, speed, color):
        if self.state == "tranquilo":
            patterns = [
                AttackPattern.spiral(self.x, self.y, 18, speed, self.rotation, PURPLE),
                AttackPattern.wave_attack(ARENA_X, ARENA_Y - 50, speed, PURPLE),
            ]
        elif self.state == "furioso":
            patterns = [
                [*AttackPattern.poison_rain(WIDTH // 2, ARENA_Y - 50, speed, PURPLE),
                 *AttackPattern.water_stream(self.x, self.y, pred_x, pred_y, speed, CYAN)],
                [*AttackPattern.circle_burst(self.x, self.y, 20, speed, PURPLE),
                 *AttackPattern.spiral(self.x, self.y, 15, speed, self.rotation, CYAN)],
            ]
        else:
            patterns = [
                [*AttackPattern.poison_rain(WIDTH // 2, ARENA_Y - 50, speed, PURPLE),
                 *AttackPattern.circle_burst(self.x, self.y, 24, speed, PURPLE)],
            ]
        
        pattern = random.choice(patterns)
        if isinstance(pattern, list) and pattern and isinstance(pattern[0], list):
            pattern = [bullet for sublist in pattern for bullet in sublist]
        return pattern
    
    def show_dialogue(self):
        self.current_dialogue = random.choice(self.dialogues[self.state])
        self.dialogue_timer = 2.0
    
    def draw(self, screen):
        draw_x = int(self.x + self.shake_offset[0])
        draw_y = int(self.y + self.shake_offset[1])
        
        # Advertencias
        for warning in self.warnings:
            warning.draw(screen)
        
        # Láseres
        for laser in self.lasers:
            laser.draw(screen)
        
        # Efecto de regeneración
        if self.regenerating:
            regen_radius = 50 + math.sin(self.dialogue_timer * 5) * 10
            pygame.draw.circle(screen, (0, 255, 100), (draw_x, draw_y), 
                             int(regen_radius), 2)
        
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
        if self.dialogue_timer > 0 and self.current_dialogue:
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
        bar_width = 200 if not self.is_spirit else 150
        bar_height = 20 if not self.is_spirit else 15
        bar_x = WIDTH // 2 - bar_width // 2
        bar_y = 70 + (self.phase - 1) * 30
        
        if self.is_spirit:
            bar_y = 150  # Posición diferente para espíritus
        
        pygame.draw.rect(screen, WHITE, (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4), 2)
        pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height))
        
        hp_percent = self.hp / self.max_hp
        hp_bar_width = int(bar_width * hp_percent)
        hp_color = GREEN if hp_percent > 0.66 else (YELLOW if hp_percent > 0.33 else RED)
        pygame.draw.rect(screen, hp_color, (bar_x, bar_y, hp_bar_width, bar_height))
        
        font = pygame.font.Font(None, 16 if self.is_spirit else 18)
        phase_text = f"{'ESPÍRITU' if self.is_spirit else 'FASE ' + str(self.phase)} | {int(self.hp)}/{self.max_hp}"
        text_surf = font.render(phase_text, True, WHITE)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, bar_y + bar_height // 2))
        screen.blit(text_surf, text_rect)
        
        if not self.is_spirit:
            name_font = pygame.font.Font(None, 24)
            name_surf = name_font.render(self.name, True, BOSS_STATES[self.state]["color"])
            name_rect = name_surf.get_rect(center=(WIDTH // 2, bar_y - 15))
            screen.blit(name_surf, name_rect)