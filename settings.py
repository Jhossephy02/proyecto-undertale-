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

# Player
PLAYER_SIZE = 20
PLAYER_SPEED = 5
PLAYER_HP = 100
PLAYER_SHOOT_COOLDOWN = 0.3

# Sistema de Turnos (como Undertale)
ATTACK_PHASE_DURATION = 3.0  # 3 segundos para atacar
DODGE_PHASE_DURATION = 20.0  # 20 segundos para esquivar
PHASE_TRANSITION_TIME = 1.0   # 1 segundo de transición

# Boss
BOSS_HP = 300
BOSS_DAMAGE = 5  # Daño reducido a 5
BOSS_STATES = {
    "tranquilo": {
        "hp_range": (0.66, 1.0),  # 66%-100% HP
        "speed_mult": 1.0,  # Más rápido desde el inicio
        "attack_mult": 1.2, 
        "color": GREEN,
        "sprite": "assets/boss/boos_tranki.png",
        "dialogue": ["Facilito causa 😏", "Muévete ps", "Ta' suave"]
    },
    "furioso": {
        "hp_range": (0.33, 0.66),  # 33%-66% HP
        "speed_mult": 1.5,  # Más rápido
        "attack_mult": 1.8, 
        "color": YELLOW,
        "sprite": "assets/boss/boos_furioso.png",
        "dialogue": ["¡Ya me picaste! 😤", "¡Ahora sí!", "¡Te agarro!"]
    },
    "enajenado": {
        "hp_range": (0.0, 0.33),  # 0%-33% HP
        "speed_mult": 2.2,  # Mucho más rápido
        "attack_mult": 2.5, 
        "color": RED,
        "sprite": "assets/boss/boos_enojado.png",
        "dialogue": ["¡TE QUIEBRO! 💀", "¡MUERE! 🔥", "¡YA FUE!"]
    }
}

# Lista de bosses progresivos
BOSS_LIST = [
    {
        "name": "Boss Selva 1",
        "hp": 300,
        "folder": "boss",
        "intro": "¡Apareció el guardián de la selva!"
    },
    {
        "name": "Boss Selva 2",
        "hp": 400,
        "folder": "boss2",
        "intro": "¡Un enemigo más poderoso aparece!"
    },
    {
        "name": "Boss Selva 3",
        "hp": 500,
        "folder": "boss3",
        "intro": "¡El jefe final te desafía!"
    }
]

# Ataques
BULLET_BASE_SPEED = 3
BULLET_SIZE = 8
PLAYER_BULLET_SPEED = 8
PLAYER_BULLET_DAMAGE = 20

# Aceleración progresiva del juego
SPEED_INCREASE_PER_BOSS = 0.20  # 20% más rápido por cada boss
SPEED_INCREASE_PER_20_SEC = 0.10  # 10% más rápido cada 20 segundos

# Assets paths
ATTACK_SPRITES = {
    "flechas": "assets/attacks/flechas.png",
    "lianas": "assets/attacks/lianas.png",
    "piraña": "assets/attacks/piraña.png",
    "serpiente": "assets/attacks/serpiente.png",
    "tronco": "assets/attacks/tronco.png",
    "veneno": "assets/attacks/veneno.png"
}

# Sprite del jugador
PLAYER_SPRITE = "assets/attacks/rock.png"  # Roca como proyectil

# IA
AI_ANALYSIS_INTERVAL = 3.0
AI_STATE_CHANGE_THRESHOLD = 0.3