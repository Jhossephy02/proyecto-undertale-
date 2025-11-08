# utils.py - Funciones auxiliares

import math
import random

def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def angle_to(x1, y1, x2, y2):
    return math.atan2(y2 - y1, x2 - x1)

def clamp(value, min_val, max_val):
    return max(min_val, min(max_val, value))

def lerp(a, b, t):
    return a + (b - a) * t

def random_direction():
    return random.uniform(0, 2 * math.pi)

def point_in_rect(px, py, rx, ry, rw, rh):
    return rx <= px <= rx + rw and ry <= py <= ry + rh
