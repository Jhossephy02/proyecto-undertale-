# settings.py - Configuración del juego

import os

# Ventana
WIDTH = 800
HEIGHT = 600
FPS = 60

# Arena de combate (donde se mueve el jugador)
ARENA_X = 200
ARENA_Y = 150
ARENA_WIDTH = 400
ARENA_HEIGHT = 300

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (200, 0, 200)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GOLD = (255, 215, 0)

# Player
PLAYER_SIZE = 20
PLAYER_SPEED = 5
PLAYER_HP = 100
PLAYER_SHOOT_COOLDOWN = 0.3

# Sistema de poder especial
SPECIAL_ATTACK_DODGES = 100  # Esquivos necesarios para desbloquear ataque
SPECIAL_ATTACK_WINDOW = 20.0  # Segundos de duración del modo ataque
SPECIAL_ATTACK_DAMAGE = 150  # Daño del poder especial

# Boss
BOSS_HP = 500
BOSS_STATES = {
    "tranquilo": {
        "speed_mult": 0.7, 
        "attack_mult": 1.0, 
        "color": GREEN,
        "sprite": "assets/boss/boos_tranki.png"
    },
    "furioso": {
        "speed_mult": 1.2, 
        "attack_mult": 1.5, 
        "color": YELLOW,
        "sprite": "assets/boss/boos_furioso.png"
    },
    "enajenado": {
        "speed_mult": 1.8, 
        "attack_mult": 2.5, 
        "color": RED,
        "sprite": "assets/boss/boos_enojado.png"
    }
}

# Configuración de los 3 bosses
BOSS_PHASES = {
    1: {
        "name": "Boss Selvático",
        "hp": 500,
        "speed_base": 1.0,
        "damage_base": 1.0,
        "color": GREEN
    },
    2: {
        "name": "Boss Furioso",
        "hp": 600,
        "speed_base": 1.5,
        "damage_base": 1.5,
        "color": ORANGE
    },
    3: {
        "name": "Boss Supremo",
        "hp": 800,
        "speed_base": 1.3,
        "damage_base": 1.3,
        "color": PURPLE,
        "can_revive": True
    }
}

# Ataques
BULLET_BASE_SPEED = 3
BULLET_SIZE = 8
PLAYER_BULLET_SPEED = 8
PLAYER_BULLET_DAMAGE = 20

# Assets paths
ATTACK_SPRITES = {
    "flechas": "assets/attacks/flechas.png",
    "lianas": "assets/attacks/lianas.png",
    "piraña": "assets/attacks/piraña.png",
    "serpiente": "assets/attacks/serpiente.png",
    "tronco": "assets/attacks/tronco.png",
    "veneno": "assets/attacks/veneno.png"
}

# IA
AI_ANALYSIS_INTERVAL = 3.0
AI_STATE_CHANGE_THRESHOLD = 0.3