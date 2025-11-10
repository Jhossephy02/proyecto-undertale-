# settings.py - Configuración del juego UNIFICADA

import os

# Ventana
WIDTH = 800
HEIGHT = 600
FPS = 60

# Arena de combate
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
SPECIAL_ATTACK_DODGES = 100  # Esquivos para desbloquear ataque
SPECIAL_ATTACK_WINDOW = 20.0  # Duración del modo ataque (segundos)
SPECIAL_ATTACK_DAMAGE = 150

# Boss - Estados
BOSS_HP = 300
BOSS_DAMAGE = 10
BOSS_STATES = {
    "tranquilo": {
        "hp_range": (0.66, 1.0),
        "speed_mult": 1.0,
        "attack_mult": 1.2,
        "color": GREEN,
        "sprite": "assets/boss/boos_tranki.png",
        "dialogue": ["Facilito causa 😏", "Muévete ps", "Ta' suave"]
    },
    "furioso": {
        "hp_range": (0.33, 0.66),
        "speed_mult": 1.5,
        "attack_mult": 1.8,
        "color": YELLOW,
        "sprite": "assets/boss/boos_furioso.png",
        "dialogue": ["¡Ya me picaste! 😤", "¡Ahora sí!", "¡Te agarro!"]
    },
    "enajenado": {
        "hp_range": (0.0, 0.33),
        "speed_mult": 2.2,
        "attack_mult": 2.5,
        "color": RED,
        "sprite": "assets/boss/boos_enojado.png",
        "dialogue": ["¡TE QUIEBRO! 💀", "¡MUERE! 🔥", "¡YA FUE!"]
    }
}

# Sistema de 3 Fases
BOSS_PHASES = {
    1: {
        "name": "Boss Selvático",
        "hp": 500,
        "speed_base": 1.0,
        "damage_base": 1.0,
        "color": GREEN,
        "folder": "boss"
    },
    2: {
        "name": "Boss Furioso",
        "hp": 600,
        "speed_base": 1.5,
        "damage_base": 1.5,
        "color": ORANGE,
        "folder": "boss"
    },
    3: {
        "name": "Boss Supremo",
        "hp": 800,
        "speed_base": 1.3,
        "damage_base": 1.3,
        "color": PURPLE,
        "can_revive": True,
        "folder": "boss"
    }
}

# Ataques
BULLET_BASE_SPEED = 3
BULLET_SIZE = 8
PLAYER_BULLET_SPEED = 8
PLAYER_BULLET_DAMAGE = 20

# Assets
ATTACK_SPRITES = {
    "flechas": "assets/attacks/flechas.png",
    "lianas": "assets/attacks/lianas.png",
    "piraña": "assets/attacks/piraña.png",
    "serpiente": "assets/attacks/serpiente.png",
    "tronco": "assets/attacks/tronco.png",
    "veneno": "assets/attacks/veneno.png"
}

PLAYER_SPRITE = "assets/attacks/attackplayer.png"

# =========================
# SISTEMA DE TURNOS
# =========================

# Duración de la fase donde el jugador ataca
ATTACK_PHASE_DURATION = 3.0   # 3 segundos

# Duración de la fase donde el jugador esquiva ataques
DODGE_PHASE_DURATION = 7.0    # 7 segundos

# Tiempo de transición entre bosses
PHASE_TRANSITION_TIME = 2.5   # 2.5 segundos para mostrar mensaje

# Intervalo en el que la IA analiza comportamiento del jugador
AI_ANALYSIS_INTERVAL = 4.0    # cada 4 segundos


# IA
AI_ANALYSIS_INTERVAL = 3.0
AI_STATE_CHANGE_THRESHOLD = 0.3

# =========================
# LISTA DE BOSSES COMPATIBLE CON game.py
# =========================

BOSS_LIST = [
    {
        "name": BOSS_PHASES[1]["name"],
        "max_hp": BOSS_PHASES[1]["hp"],
        "speed": BOSS_PHASES[1]["speed_base"],
        "pattern": "basic",
        "color": BOSS_PHASES[1]["color"],
        "intro": "🌿 La selva despierta..."
    },
    {
        "name": BOSS_PHASES[2]["name"],
        "max_hp": BOSS_PHASES[2]["hp"],
        "speed": BOSS_PHASES[2]["speed_base"],
        "pattern": "spread",
        "color": BOSS_PHASES[2]["color"],
        "intro": "🔥 La furia toma forma..."
    },
    {
        "name": BOSS_PHASES[3]["name"],
        "max_hp": BOSS_PHASES[3]["hp"],
        "speed": BOSS_PHASES[3]["speed_base"],
        "pattern": "spiral",
        "color": BOSS_PHASES[3]["color"],
        "intro": "💀 El dominio absoluto emerge..."
    }
]
