# player.py - Lógica del jugador

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
