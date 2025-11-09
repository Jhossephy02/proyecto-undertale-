# attack_patterns.py - Patrones de ataque estilo Undertale/Sans con sprites

import pygame
import math
import random
import os
from settings import *

def point_in_rect(px, py, rx, ry, rw, rh):
    return rx <= px <= rx + rw and ry <= py <= ry + rh

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
        self.active = True
        self.bullet_type = bullet_type
        self.lifetime = 0
        self.sprite_name = sprite_name
        self.sprite = None
        self.original_sprite = None
        
        # Cargar sprite si se especifica
        if sprite_name:
            self.load_sprite(sprite_name)
        # Cargar sprite si se especifica
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
                        # Escalar según el tipo
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
        
        # Rotar sprite según el ángulo
        if self.original_sprite:
            angle_degrees = math.degrees(-self.angle)
            self.sprite = pygame.transform.rotate(self.original_sprite, angle_degrees)
            self.size = max(self.sprite.get_width(), self.sprite.get_height()) // 2
        
    def update(self, dt, speed_multiplier=1.0):
        self.lifetime += dt
        
        # Aplicar multiplicador de velocidad
        actual_speed = self.speed * speed_multiplier
        
        # Movimiento básico
        self.x += math.cos(self.angle) * actual_speed
        self.y += math.sin(self.angle) * actual_speed
        
        # Comportamientos especiales
        if self.bullet_type == "homing":
            # Futuro: balas que siguen al jugador
            pass
        elif self.bullet_type == "wave":
            # Movimiento ondulatorio (lianas)
            self.y += math.sin(self.lifetime * 5) * 2
        elif self.bullet_type == "spiral":
            # Rotación adicional en espiral
            self.angle += dt * 2
            if self.original_sprite:
                angle_degrees = math.degrees(-self.angle)
                self.sprite = pygame.transform.rotate(self.original_sprite, angle_degrees)
        
        # Desactivar si sale del área extendida
        if not point_in_rect(self.x, self.y, ARENA_X - 100, ARENA_Y - 100, 
                            ARENA_WIDTH + 200, ARENA_HEIGHT + 200):
            self.active = False
    
    def draw(self, screen):
        if self.sprite:
            # Dibujar sprite rotado
            sprite_rect = self.sprite.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(self.sprite, sprite_rect)
        else:
            # Fallback: dibujar círculo
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
    
    def get_rect(self):
        if self.sprite:
            return self.sprite.get_rect(center=(int(self.x), int(self.y)))
        return pygame.Rect(self.x - self.size, self.y - self.size, 
                          self.size * 2, self.size * 2)

class AttackPattern:
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
    def double_burst(x, y, count, speed, color=(255,255,255)):
        """Dos explosiones circulares de FLECHAS desfasadas"""
        bullets = []
        angle_step = (2 * math.pi) / count
        offset = angle_step / 2
        
        for i in range(count):
            angle = angle_step * i
            bullets.append(Bullet(x, y, angle, speed, color, "normal", "flechas"))
            bullets.append(Bullet(x, y, angle + offset, speed * 0.8, color, "normal", "flechas"))
        return bullets
    
    @staticmethod
    def aimed_shot(x, y, target_x, target_y, speed, color=(255,255,255)):
        """Disparo directo de FLECHA al jugador"""
        angle = math.atan2(target_y - y, target_x - x)
        return [Bullet(x, y, angle, speed, color, "normal", "flechas")]
    
    @staticmethod
    def triple_aimed_shot(x, y, target_x, target_y, speed, color=(255,255,255)):
        """Tres SERPIENTES hacia el jugador con spread"""
        angle = math.atan2(target_y - y, target_x - x)
        spread = 0.3
        bullets = []
        bullets.append(Bullet(x, y, angle - spread, speed, color, "normal", "serpiente"))
        bullets.append(Bullet(x, y, angle, speed * 1.2, color, "normal", "serpiente"))
        bullets.append(Bullet(x, y, angle + spread, speed, color, "normal", "serpiente"))
        return bullets
    
    @staticmethod
    def spiral(x, y, count, speed, rotation, color=(255,255,255)):
        """Espiral rotante de SERPIENTES"""
        bullets = []
        angle_step = (2 * math.pi) / count
        for i in range(count):
            angle = angle_step * i + rotation
            bullets.append(Bullet(x, y, angle, speed, color, "spiral", "serpiente"))
        return bullets
    
    @staticmethod
    def spiral_double(x, y, count, speed, rotation, color=(255,255,255)):
        """Doble espiral de SERPIENTES (sentido horario y antihorario)"""
        bullets = []
        angle_step = (2 * math.pi) / count
        for i in range(count):
            angle1 = angle_step * i + rotation
            angle2 = -angle_step * i - rotation
            bullets.append(Bullet(x, y, angle1, speed, color, "spiral", "serpiente"))
            bullets.append(Bullet(x, y, angle2, speed * 0.9, color, "spiral", "serpiente"))
        return bullets
    
    @staticmethod
    def wall(x, y, horizontal, count, speed, spacing, color=(255,255,255)):
        """Muro de TRONCOS (horizontal o vertical)"""
        bullets = []
        if horizontal:
            for i in range(count):
                bx = x + (i - count // 2) * spacing
                bullets.append(Bullet(bx, y, math.pi / 2, speed, color, "large", "tronco"))
        else:
            for i in range(count):
                by = y + (i - count // 2) * spacing
                bullets.append(Bullet(x, by, 0, speed, color, "large", "tronco"))
        return bullets
    
    @staticmethod
    def cross_pattern(x, y, speed, color=(255,255,255)):
        """Patrón en cruz de FLECHAS (4 direcciones + diagonales)"""
        bullets = []
        angles = [0, math.pi/2, math.pi, -math.pi/2,  # Cardinales
                 math.pi/4, 3*math.pi/4, -3*math.pi/4, -math.pi/4]  # Diagonales
        for angle in angles:
            bullets.append(Bullet(x, y, angle, speed, color, "normal", "flechas"))
        return bullets
    
    @staticmethod
    def wave_attack(start_x, start_y, speed, color=(255,255,255)):
        """Ola de LIANAS ondulantes desde arriba"""
        bullets = []
        for i in range(15):
            x = start_x + i * 30
            bullets.append(Bullet(x, start_y, math.pi / 2, speed, color, "wave", "lianas"))
        return bullets
    
    @staticmethod
    def laser_grid(start_x, start_y, speed, color=(255,255,255)):
        """Patrón de rejilla con VENENO"""
        bullets = []
        # Líneas horizontales
        for i in range(4):
            y = start_y + i * 80
            for j in range(10):
                x = start_x + j * 40
                bullets.append(Bullet(x, y, 0, speed, color, "normal", "veneno"))
        
        # Líneas verticales
        for i in range(5):
            x = start_x + i * 80
            for j in range(8):
                y = start_y + j * 40
                bullets.append(Bullet(x, y, math.pi / 2, speed, color, "normal", "veneno"))
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
    
    @staticmethod
    def pirana_circle(x, y, count, speed, color=(255,255,255)):
        """Círculo de PIRAÑAS giratorias"""
        bullets = []
        angle_step = (2 * math.pi) / count
        for i in range(count):
            angle = angle_step * i
            bullets.append(Bullet(x, y, angle, speed, color, "spiral", "piraña"))
        return bullets
    
    @staticmethod
    def converging_attack(target_x, target_y, speed, color=(255,255,255)):
        """TRONCOS que convergen hacia un punto desde los bordes"""
        bullets = []
        positions = [
            (ARENA_X, target_y),  # Izquierda
            (ARENA_X + ARENA_WIDTH, target_y),  # Derecha
            (target_x, ARENA_Y),  # Arriba
            (target_x, ARENA_Y + ARENA_HEIGHT)  # Abajo
        ]
        
        for px, py in positions:
            angle = math.atan2(target_y - py, target_x - px)
            bullets.append(Bullet(px, py, angle, speed, color, "large", "tronco"))
        return bullets
    
    @staticmethod
    def snake_wave(start_x, start_y, speed, color=(255,255,255)):
        """Ola de SERPIENTES que se mueven en zigzag"""
        bullets = []
        for i in range(12):
            x = start_x + i * 35
            angle = math.pi / 2 + math.sin(i * 0.5) * 0.3
            bullets.append(Bullet(x, start_y, angle, speed, color, "wave", "serpiente"))
        return bullets
    
    @staticmethod
    def poison_rain(start_x, start_y, speed, color=(255,255,255)):
        """Lluvia de VENENO cayendo"""
        bullets = []
        for i in range(20):
            x = start_x + random.randint(-200, 200)
            y = start_y - random.randint(0, 100)
            bullets.append(Bullet(x, y, math.pi / 2, speed * random.uniform(0.8, 1.2), 
                                color, "normal", "veneno"))
        return bullets
    
    @staticmethod
    def liana_curtain(start_x, start_y, speed, color=(255,255,255)):
        """Cortina de LIANAS cayendo en cascada"""
        bullets = []
        for i in range(10):
            x = start_x + i * 40
            for j in range(3):
                y = start_y - j * 30
                bullets.append(Bullet(x, y, math.pi / 2, speed, color, "wave", "lianas"))
        return bullets