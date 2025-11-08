# settings.py - Configuración del juego

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

# Player
PLAYER_SIZE = 20
PLAYER_SPEED = 5
PLAYER_HP = 100

# Boss
BOSS_HP = 500
BOSS_STATES = {
    "tranquilo": {"speed_mult": 0.7, "attack_mult": 1.0, "color": GREEN},
    "furioso": {"speed_mult": 1.2, "attack_mult": 1.5, "color": YELLOW},
    "enajenado": {"speed_mult": 1.8, "attack_mult": 2.5, "color": RED}
}

# Ataques
BULLET_BASE_SPEED = 3
BULLET_SIZE = 8

# IA
AI_ANALYSIS_INTERVAL = 3.0
AI_STATE_CHANGE_THRESHOLD = 0.3
