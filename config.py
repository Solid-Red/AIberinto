import pygame

# Dimensiones de la pantalla
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Colores del tema Calabozo Medieval
COLOR_BG = (12, 10, 12)            # Vacío oscuro de mazmorra profunda
COLOR_WALL_TOP = (100, 100, 105)   # Color de bloque de piedra base
COLOR_WALL_LEFT = (75, 75, 80)     # Ladrillo de piedra (sombre medio)
COLOR_WALL_RIGHT = (55, 55, 60)    # Ladrillo de piedra (sombre fuerte)

COLOR_FLOOR = (65, 65, 69)         # Baldosa de piedra
COLOR_FLOOR_GRID = (40, 40, 44)    # Mortero/Unión de las baldosas de piedra
COLOR_STONE_FLOOR = (48, 48, 52)   # Tono base de baldosa de piedra oscura
COLOR_DIRT = (90, 70, 50)          # Suelo de tierra base
COLOR_DIRT_DETAIL = (70, 50, 35)   # Detalle de tierra/grava
COLOR_SHADOW_BODY = (25, 20, 32)   # Cuerpo del enemigo acechante (sombra)
COLOR_SHADOW_EYES = (245, 20, 20)  # Ojos del enemigo acechante (rojo brillante)

# Colores de la antorcha y fuego (Espectro cálido)
COLOR_FLAME_RED = (210, 40, 10)
COLOR_FLAME_ORANGE = (245, 120, 10)
COLOR_FLAME_YELLOW = (255, 210, 40)
COLOR_SMOKE = (80, 78, 82)

# Colores del Caballero y Equipamiento
COLOR_STEEL = (175, 180, 185)       # Armadura brillante
COLOR_STEEL_DARK = (110, 115, 120)  # Sombras de la armadura / Visor
COLOR_SHIELD_BLUE = (25, 75, 170)   # Escudo real
COLOR_SHIELD_GOLD = (220, 175, 30)  # Heráldica en escudo / Cofre de oro
COLOR_PLUME = (210, 20, 40)         # Penacho rojo brillante del casco

# Interfaz y Texto
COLOR_TEXT = (225, 225, 235)
COLOR_TEXT_MUTED = (110, 115, 125)
COLOR_UI_GOLD = (225, 185, 40)      # Acento dorado premium de la UI
COLOR_UI_RED = (190, 40, 40)

# Configuración 2D Cenital
TILE_SIZE = 40  # Tamaño en píxeles del lado de cada celda cuadrada

# Configuración del Jugador
PLAYER_SPEED = 0.15          # Velocidad de interpolación (Lerp) para movimiento fluido
PLAYER_BOB_SPEED = 0.08       # Velocidad de respiración/flotación del jugador (sinusoidal)
PLAYER_BOB_HEIGHT = 2         # Amplitud de la flotación en 2D

# Lógica del Laberinto
# Nota: Deben ser números impares para el algoritmo de tallado (carving)
INITIAL_MAZE_SIZE = 17
MAZE_MAX_SIZE = 45

# Tipos de celdas
CELL_FLOOR = 0
CELL_WALL = 1
CELL_START = 2
CELL_EXIT = 3

# Estados del Juego
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_STORY = "story"              # Estado de interacción narrativa con IA
STATE_RESULTS = "results"          # Estado de análisis final de personalidad
STATE_PAUSE = "pause"
STATE_WIN = "win"
STATE_GAMEOVER = "gameover"
STATE_ENEMY_QUIZ = "enemy_quiz"    # Estado para el cuestionario del Enemigo Acechante

# Configuración de Ollama
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi3.5"

# Categorías de Inteligencias Múltiples (Teoría de Gardner)
INT_LOGICAL = "Lógico-Matemática"
INT_LINGUISTIC = "Lingüística"
INT_SPATIAL = "Espacial"
INT_MUSICAL = "Musical"
INT_KINESTHETIC = "Corporal-Cinestésica"
INT_INTRAPERSONAL = "Intrapersonal"
INT_INTERPERSONAL = "Interpersonal"
INT_NATURALIST = "Naturalista"

INTELLIGENCES = [
    INT_LOGICAL,
    INT_LINGUISTIC,
    INT_SPATIAL,
    INT_MUSICAL,
    INT_KINESTHETIC,
    INT_INTRAPERSONAL,
    INT_INTERPERSONAL,
    INT_NATURALIST
]
