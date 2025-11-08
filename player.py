# player.py - Lógica del jugador con disparos

import pygame
import math
from settings import *
from utils import clamp

class PlayerBullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = PLAYER_BULLET_SPEED
        self.size = 6
        self.color = CYAN
        self.active = True
        self.damage = PLAYER_BULLET_DAMAGE
        
    def update(self, dt):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        
        # Desactivar si sale de la pantalla
        if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
            self.active = False
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, 
                          self.size * 2, self.size * 2)

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
        
        # Sistema de disparo
        self.bullets = []
        self.shoot_cooldown = 0
        
        # Estadísticas para IA
        self.dodges = {"left": 0, "right": 0, "up": 0, "down": 0}
        self.hits_taken = 0
        self.shots_fired = 0
        
    def update(self, dt, keys):
        dx = 0
        dy = 0
        
        # Movimiento
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed
            self.dodges["left"] += 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed
            self.dodges["right"] += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= self.speed
            self.dodges["up"] += 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += self.speed
            self.dodges["down"] += 1
        
        self.x = clamp(self.x + dx, ARENA_X, ARENA_X + ARENA_WIDTH - self.size)
        self.y = clamp(self.y + dy, ARENA_Y, ARENA_Y + ARENA_HEIGHT - self.size)
        
        # Sistema de invulnerabilidad
        if self.invulnerable:
            self.invuln_timer += dt
            if self.invuln_timer >= self.invuln_duration:
                self.invulnerable = False
                self.invuln_timer = 0
        
        # Sistema de disparo (Z o ESPACIO)
        self.shoot_cooldown = max(0, self.shoot_cooldown - dt)
        if (keys[pygame.K_z] or keys[pygame.K_SPACE]) and self.shoot_cooldown <= 0:
            self.shoot()
            self.shoot_cooldown = PLAYER_SHOOT_COOLDOWN
        
        # Actualizar balas
        for bullet in self.bullets[:]:
            bullet.update(dt)
            if not bullet.active:
                self.bullets.remove(bullet)
    
    def shoot(self):
        """Dispara hacia arriba (hacia el boss)"""
        center_x = self.x + self.size // 2
        center_y = self.y + self.size // 2
        angle = -math.pi / 2  # Hacia arriba
        
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
        color = RED
        if self.invulnerable:
            color = RED if int(self.invuln_timer * 10) % 2 == 0 else (255, 100, 100)
        
        # Corazón del jugador (soul)
        pygame.draw.polygon(screen, color, [
            (self.x + self.size // 2, self.y + self.size),
            (self.x, self.y + self.size // 2),
            (self.x + self.size // 4, self.y),
            (self.x + self.size // 2, self.y + self.size // 4),
            (self.x + self.size * 3 // 4, self.y),
            (self.x + self.size, self.y + self.size // 2)
        ])
        
        # Dibujar balas del jugador
        for bullet in self.bullets:
            bullet.draw(screen)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)