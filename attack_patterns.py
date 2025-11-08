# attack_patterns.py - Patrones de ataque

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
