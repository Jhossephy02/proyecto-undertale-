# attack_patterns.py - Patrones de ataque con láser y advertencias

import pygame
import math
import random
import os
from settings import *

def point_in_rect(px, py, rx, ry, rw, rh):
    return rx <= px <= rx + rw and ry <= py <= ry + rh

class Warning:
    """Advertencia visual antes de un ataque"""
    def __init__(self, x, y, width, height, duration=1.0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.duration = duration
        self.timer = 0
        self.active = True
        self.color = (255, 0, 0, 100)  # Rojo semi-transparente
        
    def update(self, dt):
        self.timer += dt
        if self.timer >= self.duration:
            self.active = False
    
    def draw(self, screen):
        if self.active:
            # Efecto de parpadeo
            alpha = int(128 + 127 * math.sin(self.timer * 10))
            surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            surface.fill((255, 0, 0, alpha))
            screen.blit(surface, (int(self.x), int(self.y)))
            
            # Borde rojo
            pygame.draw.rect(screen, RED, (int(self.x), int(self.y), 
                                          int(self.width), int(self.height)), 3)

class LaserBeam:
    """Láser devastador de Yacumama"""
    def __init__(self, x, y, angle, width=30, length=1000, charge_time=1.0):
        self.x = x
        self.y = y
        self.angle = angle
        self.width = width
        self.length = length
        self.charge_time = charge_time
        self.timer = 0
        self.active = True
        self.firing = False
        self.duration = 2.0  # Duración del disparo
        
    def update(self, dt):
        self.timer += dt
        
        if self.timer < self.charge_time:
            # Fase de carga
            self.firing = False
        elif self.timer < self.charge_time + self.duration:
            # Fase de disparo
            self.firing = True
        else:
            # Terminar
            self.active = False
    
    def check_collision(self, player_rect):
        """Verifica colisión con el jugador"""
        if not self.firing:
            return False
        
        # Crear rectángulo del láser
        end_x = self.x + math.cos(self.angle) * self.length
        end_y = self.y + math.sin(self.angle) * self.length
        
        # Puntos del rectángulo del láser
        perp_angle = self.angle + math.pi / 2
        offset_x = math.cos(perp_angle) * self.width / 2
        offset_y = math.sin(perp_angle) * self.width / 2
        
        # Verificar si el jugador está en la línea del láser (simplificado)
        player_center = player_rect.center
        
        # Distancia del jugador a la línea del láser
        dx = end_x - self.x
        dy = end_y - self.y
        length_sq = dx * dx + dy * dy
        
        if length_sq == 0:
            return False
        
        t = max(0, min(1, ((player_center[0] - self.x) * dx + 
                          (player_center[1] - self.y) * dy) / length_sq))
        
        closest_x = self.x + t * dx
        closest_y = self.y + t * dy
        
        dist = math.sqrt((player_center[0] - closest_x) ** 2 + 
                        (player_center[1] - closest_y) ** 2)
        
        return dist < self.width / 2 + player_rect.width / 2
    
    def draw(self, screen):
        if not self.firing and self.timer < self.charge_time:
            # Advertencia durante la carga
            charge_percent = self.timer / self.charge_time
            warning_width = int(self.width * (0.5 + charge_percent))
            
            end_x = self.x + math.cos(self.angle) * self.length
            end_y = self.y + math.sin(self.angle) * self.length
            
            # Línea de advertencia parpadeante
            alpha = int(100 + 155 * math.sin(self.timer * 15))
            for i in range(3):
                offset = i * 2
                pygame.draw.line(screen, (255, 255 - alpha, 0), 
                               (self.x, self.y), (end_x, end_y), 
                               warning_width + offset)
        
        elif self.firing:
            # Láser disparando
            end_x = self.x + math.cos(self.angle) * self.length
            end_y = self.y + math.sin(self.angle) * self.length
            
            # Núcleo blanco brillante
            pygame.draw.line(screen, WHITE, (self.x, self.y), 
                           (end_x, end_y), int(self.width * 0.5))
            
            # Aura azul
            pygame.draw.line(screen, CYAN, (self.x, self.y), 
                           (end_x, end_y), self.width)
            
            # Borde exterior púrpura
            pygame.draw.line(screen, PURPLE, (self.x, self.y), 
                           (end_x, end_y), int(self.width * 1.5))

class Bullet:
    # Cache de sprites cargados
    _sprite_cache = {}
    
    def __init__(self, x, y, angle, speed, color=(255,255,255), bullet_type="normal", sprite_name=None):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.size = BULLET_SIZE
        self.color = color
        self.bullet_type = bullet_type
        self.lifetime = 0
        self.sprite_name = sprite_name
        self.sprite = None
        self.original_sprite = None
        self.active = True
        
        if sprite_name:
            self.load_sprite(sprite_name)
    
    def load_sprite(self, sprite_name):
        """Carga y cachea el sprite"""
        if sprite_name in Bullet._sprite_cache:
            self.original_sprite = Bullet._sprite_cache[sprite_name]
        else:
            if sprite_name in ATTACK_SPRITES:
                sprite_path = ATTACK_SPRITES[sprite_name]
                if os.path.exists(sprite_path):
                    try:
                        img = pygame.image.load(sprite_path).convert_alpha()
                        if self.bullet_type == "large":
                            img = pygame.transform.scale(img, (40, 40))
                        elif self.bullet_type == "wave":
                            img = pygame.transform.scale(img, (35, 35))
                        else:
                            img = pygame.transform.scale(img, (30, 30))
                        Bullet._sprite_cache[sprite_name] = img
                        self.original_sprite = img
                    except:
                        print(f"Error cargando sprite: {sprite_path}")
        
        if self.original_sprite:
            angle_degrees = math.degrees(-self.angle)
            self.sprite = pygame.transform.rotate(self.original_sprite, angle_degrees)
            self.size = max(self.sprite.get_width(), self.sprite.get_height()) // 2
        
    def update(self, dt, speed_multiplier=1.0):
        self.lifetime += dt
        actual_speed = self.speed * speed_multiplier
        
        self.x += math.cos(self.angle) * actual_speed
        self.y += math.sin(self.angle) * actual_speed
        
        if self.bullet_type == "wave":
            self.y += math.sin(self.lifetime * 5) * 10
        elif self.bullet_type == "spiral":
            self.angle += dt * 2
            if self.original_sprite:
                angle_degrees = math.degrees(-self.angle)
                self.sprite = pygame.transform.rotate(self.original_sprite, angle_degrees)
        
        if not point_in_rect(self.x, self.y, ARENA_X - 100, ARENA_Y - 100, 
                            ARENA_WIDTH + 200, ARENA_HEIGHT + 200):
            self.active = False
    
    def draw(self, screen):
        if self.sprite:
            sprite_rect = self.sprite.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(self.sprite, sprite_rect)
        else:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
    
    def get_rect(self):
        if self.sprite:
            return self.sprite.get_rect(center=(int(self.x), int(self.y)))
        return pygame.Rect(self.x - self.size, self.y - self.size, 
                          self.size * 2, self.size * 2)

class AttackPattern:
    @staticmethod
    def create_laser_warning(x, y, angle, length=1000, width=30):
        """Crea advertencia visual para el láser"""
        end_x = x + math.cos(angle) * length
        end_y = y + math.sin(angle) * length
        
        # Calcular rectángulo de advertencia
        min_x = min(x, end_x) - width
        min_y = min(y, end_y) - width
        max_x = max(x, end_x) + width
        max_y = max(y, end_y) + width
        
        return Warning(min_x, min_y, max_x - min_x, max_y - min_y, duration=1.0)
    
    @staticmethod
    def circle_burst(x, y, count, speed, color=(255,255,255)):
        """Explosión circular de FLECHAS"""
        bullets = []
        angle_step = (2 * math.pi) / count
        for i in range(count):
            angle = angle_step * i
            bullets.append(Bullet(x, y, angle, speed, color, "normal", "flechas"))
        return bullets
    
    @staticmethod
    def aimed_shot(x, y, target_x, target_y, speed, color=(255,255,255)):
        """Disparo directo de FLECHA"""
        angle = math.atan2(target_y - y, target_x - x)
        return [Bullet(x, y, angle, speed, color, "normal", "flechas")]
    
    @staticmethod
    def triple_aimed_shot(x, y, target_x, target_y, speed, color=(255,255,255)):
        """Tres SERPIENTES hacia el jugador"""
        angle = math.atan2(target_y - y, target_x - x)
        spread = 0.3
        bullets = []
        bullets.append(Bullet(x, y, angle - spread, speed, color, "normal", "serpiente"))
        bullets.append(Bullet(x, y, angle, speed * 1.2, color, "normal", "serpiente"))
        bullets.append(Bullet(x, y, angle + spread, speed, color, "normal", "serpiente"))
        return bullets
    
    @staticmethod
    def spiral(x, y, count, speed, rotation, color=(255,255,255)):
        """Espiral de SERPIENTES"""
        bullets = []
        angle_step = (2 * math.pi) / count
        for i in range(count):
            angle = angle_step * i + rotation
            bullets.append(Bullet(x, y, angle, speed, color, "spiral", "serpiente"))
        return bullets
    
    @staticmethod
    def water_stream(x, y, target_x, target_y, speed, color=(255,255,255)):
        """Chorro de agua (Yacuruna)"""
        angle = math.atan2(target_y - y, target_x - x)
        bullets = []
        for i in range(5):
            offset_angle = angle + random.uniform(-0.2, 0.2)
            bullets.append(Bullet(x, y, offset_angle, speed * random.uniform(0.9, 1.1), 
                                color, "normal", "chorro_agua"))
        return bullets
    
    @staticmethod
    def poison_rain(start_x, start_y, speed, color=(255,255,255)):
        """Lluvia de VENENO (Chullachaqui)"""
        bullets = []
        for i in range(20):
            x = start_x + random.randint(-200, 200)
            y = start_y - random.randint(0, 100)
            bullets.append(Bullet(x, y, math.pi / 2, speed * random.uniform(0.8, 1.2), 
                                 color, "normal", "veneno"))
        return bullets
    
    @staticmethod
    def wave_attack(start_x, start_y, speed, color=(255,255,255)):
        """Ola de LIANAS"""
        bullets = []
        for i in range(12):
            x = start_x + i * 40
            bullets.append(Bullet(x, start_y, math.pi / 2, speed, color, "wave", "lianas"))
        return bullets
    
    @staticmethod
    def liana_curtain(start_x, start_y, speed, color=(255,255,255)):
        """Cortina de LIANAS (Yacumama)"""
        bullets = []
        spacing = 50
        num_columns = ARENA_WIDTH // spacing
        
        for i in range(num_columns):
            x = ARENA_X + spacing * i + spacing / 2
            bullets.append(Bullet(x, start_y, math.pi / 2, speed, color, "wave", "lianas"))
        return bullets
    
    @staticmethod
    def random_spray(x, y, count, speed, color=(255,255,255)):
        """Spray aleatorio de PIRAÑAS"""
        bullets = []
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            bullet_speed = speed * random.uniform(0.7, 1.3)
            bullets.append(Bullet(x, y, angle, bullet_speed, color, "normal", "piraña"))
        return bullets