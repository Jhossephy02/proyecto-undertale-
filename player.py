# player.py - Jugador con sistema de poder especial

import pygame
import math
import os
from settings import *
from utils import clamp

class SpecialAttack:
    """Poder especial del jugador"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 20
        self.max_radius = 200
        self.expansion_speed = 300
        self.damage = SPECIAL_ATTACK_DAMAGE
        self.active = True
        self.has_hit = False
        
    def update(self, dt):
        self.radius += self.expansion_speed * dt
        if self.radius >= self.max_radius:
            self.active = False
    
    def draw(self, screen):
        # Dibujar onda expansiva dorada
        for i in range(3):
            alpha = int(255 * (1 - self.radius / self.max_radius))
            color = GOLD
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 
                             int(self.radius - i * 10), 3)

class PlayerBullet:
    def __init__(self, x, y, angle, sprite_path="assets/attacks/attackplayer.png"):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = PLAYER_BULLET_SPEED
        self.size = 12
        self.color = CYAN
        self.active = True
        self.damage = PLAYER_BULLET_DAMAGE
        
        # Cargar sprite
        self.sprite = None
        if os.path.exists(sprite_path):
            try:
                self.sprite = pygame.image.load(sprite_path).convert_alpha()
                self.sprite = pygame.transform.scale(self.sprite, (20, 20))
                angle_deg = math.degrees(self.angle)
                self.sprite = pygame.transform.rotate(self.sprite, -angle_deg)
            except:
                pass
        
    def update(self, dt):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        
        if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
            self.active = False
    
    def draw(self, screen):
        if self.sprite:
            rect = self.sprite.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(self.sprite, rect)
        else:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
    
    def get_rect(self):
        if self.sprite:
            return self.sprite.get_rect(center=(int(self.x), int(self.y)))
        return pygame.Rect(self.x - self.size, self.y - self.size, 
                          self.size * 2, self.size * 2)

class Player:
    def __init__(self, x, y, sprite_path="assets/player/player.png"):
        self.x = x
        self.y = y
        self.size = PLAYER_SIZE
        self.speed = PLAYER_SPEED
        self.hp = PLAYER_HP
        self.max_hp = PLAYER_HP
        self.invulnerable = False
        self.invuln_timer = 0
        self.invuln_duration = 1.0
        
        # Cargar sprites
        self.sprite = None
        self.sprite_invuln = None
        self.load_sprite(sprite_path)
        
        # Sistema de disparo
        self.bullets = []
        self.shoot_cooldown = 0
        self.special_attacks = []  # IMPORTANTE: Lista de ataques especiales
        
        # Sistema de poder especial
        self.total_dodges = 0
        self.dodges_for_special = 0
        self.attack_mode = False
        self.attack_mode_timer = 0
        self.can_use_special = False
        
        # Estadísticas
        self.dodges = {"left": 0, "right": 0, "up": 0, "down": 0}
        self.hits_taken = 0
        self.shots_fired = 0
        self.last_movement = {"dx": 0, "dy": 0}
        
    def load_sprite(self, sprite_path):
        """Carga el sprite del jugador"""
        possible_paths = [sprite_path, "assets/player/player.png", "assets/player.png"]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    self.sprite = pygame.image.load(path).convert_alpha()
                    sprite_size = PLAYER_SIZE * 2
                    self.sprite = pygame.transform.scale(self.sprite, (sprite_size, sprite_size))
                    self.sprite_invuln = self.sprite.copy()
                    self.sprite_invuln.set_alpha(128)
                    print(f"✓ Sprite del jugador cargado desde: {path}")
                    break
                except Exception as e:
                    print(f"Error cargando sprite: {e}")
    
    def update(self, dt, keys):
        dx = 0
        dy = 0
        moved = False
        
        # Movimiento
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed
            moved = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed
            moved = True
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= self.speed
            moved = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += self.speed
            moved = True
        
        # Contar esquivos (solo si cambió de dirección)
        if moved:
            if (dx != self.last_movement["dx"] or dy != self.last_movement["dy"]):
                if dx < 0:
                    self.dodges["left"] += 1
                    self.dodges_for_special += 1
                    self.total_dodges += 1
                elif dx > 0:
                    self.dodges["right"] += 1
                    self.dodges_for_special += 1
                    self.total_dodges += 1
                if dy < 0:
                    self.dodges["up"] += 1
                    self.dodges_for_special += 1
                    self.total_dodges += 1
                elif dy > 0:
                    self.dodges["down"] += 1
                    self.dodges_for_special += 1
                    self.total_dodges += 1
            
            self.last_movement = {"dx": dx, "dy": dy}
        
        self.x = clamp(self.x + dx, ARENA_X, ARENA_X + ARENA_WIDTH - self.size)
        self.y = clamp(self.y + dy, ARENA_Y, ARENA_Y + ARENA_HEIGHT - self.size)
        
        # Sistema de modo ataque
        if self.dodges_for_special >= SPECIAL_ATTACK_DODGES and not self.attack_mode:
            self.activate_attack_mode()
        
        if self.attack_mode:
            self.attack_mode_timer += dt
            if self.attack_mode_timer >= SPECIAL_ATTACK_WINDOW:
                self.deactivate_attack_mode()
        
        # Invulnerabilidad
        if self.invulnerable:
            self.invuln_timer += dt
            if self.invuln_timer >= self.invuln_duration:
                self.invulnerable = False
                self.invuln_timer = 0
        
        # Sistema de disparo (solo en modo ataque)
        self.shoot_cooldown = max(0, self.shoot_cooldown - dt)
        if self.attack_mode:
            if (keys[pygame.K_z] or keys[pygame.K_SPACE]) and self.shoot_cooldown <= 0:
                self.shoot()
                self.shoot_cooldown = PLAYER_SHOOT_COOLDOWN
            
            # Poder especial con X
            if keys[pygame.K_x] and self.can_use_special:
                self.use_special_attack()
        
        # Actualizar balas
        for bullet in self.bullets[:]:
            bullet.update(dt)
            if not bullet.active:
                self.bullets.remove(bullet)
        
        # Actualizar ataques especiales
        for special in self.special_attacks[:]:
            special.update(dt)
            if not special.active:
                self.special_attacks.remove(special)
    
    def activate_attack_mode(self):
        """Activa el modo ataque"""
        self.attack_mode = True
        self.attack_mode_timer = 0
        self.can_use_special = True
        print("¡MODO ATAQUE ACTIVADO! 20 segundos para atacar")
    
    def deactivate_attack_mode(self):
        """Desactiva el modo ataque"""
        self.attack_mode = False
        self.attack_mode_timer = 0
        self.dodges_for_special = 0
        self.can_use_special = False
        self.clear_bullets()
        print("Modo ataque desactivado")
    
    def use_special_attack(self):
        """Usa el poder especial"""
        center_x = self.x + self.size // 2
        center_y = self.y + self.size // 2
        special = SpecialAttack(center_x, center_y)
        self.special_attacks.append(special)
        self.can_use_special = False
        print("¡PODER ESPECIAL USADO!")
    
    def clear_bullets(self):
        """Elimina todas las balas"""
        self.bullets.clear()
    
    def shoot(self):
        """Dispara hacia arriba"""
        center_x = self.x + self.size // 2
        center_y = self.y + self.size // 2
        angle = -math.pi / 2
        
        bullet = PlayerBullet(center_x, center_y, angle)
        self.bullets.append(bullet)
        self.shots_fired += 1
    
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
        center_x = self.x + self.size // 2
        center_y = self.y + self.size // 2
        
        # Aura de modo ataque
        if self.attack_mode:
            aura_radius = 30 + math.sin(self.attack_mode_timer * 10) * 5
            pygame.draw.circle(screen, GOLD, (int(center_x), int(center_y)), 
                             int(aura_radius), 2)
        
        # Sprite del jugador
        if self.sprite:
            current_sprite = self.sprite_invuln if (self.invulnerable and int(self.invuln_timer * 10) % 2 == 0) else self.sprite
            rect = current_sprite.get_rect(center=(center_x, center_y))
            screen.blit(current_sprite, rect)
        else:
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
        
        # Balas
        for bullet in self.bullets:
            bullet.draw(screen)
        
        # Ataques especiales
        for special in self.special_attacks:
            special.draw(screen)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)
    
    def reset_for_new_phase(self):
        """Resetea el jugador para una nueva fase del boss"""
        self.dodges_for_special = 0
        self.attack_mode = False
        self.attack_mode_timer = 0
        self.can_use_special = False
        self.clear_bullets()
        self.special_attacks.clear()