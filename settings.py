# settings.py - Configuración del juego actualizada

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
PLAYER_HP = 400
PLAYER_SHOOT_COOLDOWN = 0.3

# Sistema de poder especial
SPECIAL_ATTACK_DODGES = 60
SPECIAL_ATTACK_WINDOW = 20.0
SPECIAL_ATTACK_DAMAGE = 200

# Boss
BOSS_HP = 300
BOSS_DAMAGE = 5
BOSS_STATES = {
    "tranquilo": {
        "hp_range": (0.66, 1.0),
        "speed_mult": 1.0,
        "attack_mult": 1.2, 
        "color": GREEN,
        "dialogue": ["Facilito causa 😏", "Muévete ps", "Ta' suave"]
    },
    "furioso": {
        "hp_range": (0.33, 0.66),
        "speed_mult": 1.5,
        "attack_mult": 1.8, 
        "color": YELLOW,
        "dialogue": ["¡Ya me picaste! 😤", "¡Ahora sí!", "¡Te agarro!"]
    },
    "enajenado": {
        "hp_range": (0.0, 0.33),
        "speed_mult": 2.2,
        "attack_mult": 2.5, 
        "color": RED,
        "dialogue": ["¡TE QUIEBRO! 💀", "¡MUERE! 🔥", "¡YA FUE!"]
    }
}

# Configuración de los 3 bosses (Yacuruna, Chullachaqui, Yacumama)
BOSS_PHASES = {
    1: {
        "name": "Yacuruna",
        "sprite_normal": "assets/boss/yacuruna-espiritu.png",
        "sprite_furioso": "assets/boss/yacuruna-espiritu.png",
        "sprite_enajenado": "assets/boss/yacuruna-espiritu.png",
        "hp": 500,
        "speed_base": 1.0,
        "damage_base": 1.0,
        "color": CYAN
    },
    2: {
        "name": "Chullachaqui",
        "sprite_normal": "assets/boss/CHULLACHAQUI.png",
        "sprite_furioso": "assets/boss/Chullachaqui_furioso.png",
        "sprite_enajenado": "assets/boss/CHULLACHAQUI-ENOJADO.png",
        "hp": 600,
        "speed_base": 1.5,
        "damage_base": 1.5,
        "color": GREEN
    },
    3: {
        "name": "Yacumama",
        "sprite_normal": "assets/boss/yacumama.png",
        "sprite_furioso": "assets/boss/yacumama_furioso.png",
        "sprite_enajenado": "assets/boss/yacumama-enojado.png",
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
    "veneno": "assets/attacks/veneno.png",
    "chorro_agua": "assets/attacks/chorro de agua.png",
    "ola": "assets/attacks/ola-yacumama.png",
    "remolino": "assets/attacks/remolino-con-hojas.png"
}

# Sprite del jugador
PLAYER_SPRITE = "assets/player/player.png"

# IA
AI_ANALYSIS_INTERVAL = 3.0
AI_STATE_CHANGE_THRESHOLD = 0.3

# Configuración global
GAME_CONFIG = {
    "game_mode": "normal",  # 'practica', 'normal', 'genocida'
    "telegraph_enabled": True,
    "sound_enabled": True,
    "music_enabled": True,
    "show_hitboxes": False
}

# Modificadores de modos de juego
GAME_MODE_MODIFIERS = {
    "practica": {
        "player_hp_mult": 1.5,
        "boss_hp_mult": 0.7,
        "boss_speed_mult": 0.7,
        "boss_damage_mult": 0.6
    },
    "normal": {
        "player_hp_mult": 1.0,
        "boss_hp_mult": 1.0,
        "boss_speed_mult": 1.0,
        "boss_damage_mult": 1.0
    },
    "genocida": {
        "player_hp_mult": 0.5,
        "boss_hp_mult": 1.5,
        "boss_speed_mult": 1.5,
        "boss_damage_mult": 2.0
    }
}

# Advertencias de ataques
WARNING_DURATION = 1.0
WARNING_COLOR = (255, 0, 0, 100)