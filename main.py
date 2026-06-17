import pygame
import sys
import time
import math
import random
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    COLOR_BG, COLOR_TEXT, COLOR_TEXT_MUTED,
    COLOR_UI_GOLD, COLOR_UI_RED, COLOR_SHIELD_GOLD, COLOR_FLAME_ORANGE,
    INITIAL_MAZE_SIZE, MAZE_MAX_SIZE,
    STATE_MENU, STATE_PLAYING, STATE_STORY, STATE_RESULTS, STATE_PAUSE, STATE_WIN,
    STATE_ENEMY_QUIZ,
    CELL_EXIT, CELL_FLOOR, TILE_SIZE, INTELLIGENCES
)
from maze import Maze
from player import Player
from enemy import Enemy
from renderer import Renderer
from particles import ParticleSystem
from ai_client import AIClient

class Game:
    def __init__(self):
        pygame.init()
        
        # Inicialización de audio
        self.music_enabled = True
        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"Advertencia: No se pudo inicializar el mezclador de audio: {e}")
            self.music_enabled = False
        self.current_track = None
        
        # Permitir redimensionar ventana
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Mazmorra de Inteligencias Múltiples con IA")
        self.clock = pygame.time.Clock()
        
        # Dimensiones actuales
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        
        # Sistemas principales
        self.renderer = Renderer(self.width, self.height)
        self.particle_system = ParticleSystem()
        self.ai_client = AIClient()
        
        # Estado inicial del juego
        self.state = STATE_MENU
        self.current_level = 1
        self.maze_size = INITIAL_MAZE_SIZE
        
        # Inicialización del mapa y jugador
        self.maze = Maze(self.maze_size, self.maze_size)
        self.player = Player(self.maze.start_pos[0], self.maze.start_pos[1])
        
        # Perfiles, historial de retos e inteligencias múltiples
        self.scores = {intel: 0 for intel in INTELLIGENCES}
        self.player_history = []
        self.story_rooms = []       # Coordenadas (col, row) de salas con desafíos narrativos
        self.current_room = None    # Sala narrativa activa
        
        # Atributos del enemigo
        self.enemy = None
        self.enemy_quiz_questions = []
        self.current_quiz_idx = 0
        self.quiz_selected_option = 0
        self.quiz_correct_answers = 0
        self.enemy_message = ""
        self.enemy_message_timer = 0.0
        self.enemy_grace_steps = 0
        
        # Controles de UI para la historia
        self.chosen_option_idx = 0  # Opción seleccionada (0-2 para fijas, 3 para libre)
        self.custom_text = ""       # Texto de respuesta libre que escribe el usuario
        self.result_text = ""       # Texto del desenlace tras elegir
        
        # Reporte de personalidad MBTI
        self.personality_report = None
        
        # Estadísticas básicas
        self.steps = 0
        self.start_time = 0
        self.elapsed_time = 0
        
        # Fuentes para HUD y menús
        self.init_fonts()
        
        # Menú
        self.menu_options = ["ENTRAR AL CALABOZO", "INSTRUCCIONES", "SALIR"]
        self.selected_menu_option = 0
        self.show_help = False

    def init_fonts(self):
        """Inicializa las fuentes de juego del sistema."""
        font_names = ["consolas", "courier new", "monospace"]
        self.font_title = pygame.font.SysFont(font_names, 56, bold=True)
        self.font_subtitle = pygame.font.SysFont(font_names, 28, bold=True)
        self.font_ui = pygame.font.SysFont(font_names, 20, bold=False)
        self.font_hud = pygame.font.SysFont(font_names, 22, bold=True)

    def update_music(self):
        """Asegura que suena la música correcta según el estado actual."""
        if not self.music_enabled:
            return
            
        # Determinar el archivo de música según el estado del juego
        if self.state in (STATE_PLAYING, STATE_PAUSE):
            target_track = "mapWalkingFF4.mp3"
        elif self.state == STATE_STORY:
            target_track = "questDesafio.mp3"
        elif self.state == STATE_ENEMY_QUIZ:
            target_track = "bossGosht.mp3"
        else: # STATE_MENU, STATE_RESULTS
            target_track = "intro.mp3"
            
        if self.current_track != target_track:
            self.current_track = target_track
            try:
                # Cargar y reproducir en loop
                pygame.mixer.music.load(f"music/{target_track}")
                pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"Error cargando o reproduciendo música {target_track}: {e}")

    def handle_resize(self, width, height):
        """Maneja el cambio de tamaño de la ventana."""
        self.width = max(640, width)
        self.height = max(480, height)
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        self.renderer.width = self.width
        self.renderer.height = self.height

    def draw_glitch_text(self, text, font, color_front, color_back, center_x, y):
        """Dibuja texto con relieve."""
        text_back = font.render(text, True, color_back)
        rect_back = text_back.get_rect(center=(center_x - 3, y + 2))
        self.screen.blit(text_back, rect_back)
        
        text_front = font.render(text, True, color_front)
        rect_front = text_front.get_rect(center=(center_x, y))
        self.screen.blit(text_front, rect_front)

    def render_menu(self):
        self.screen.fill(COLOR_BG)
        
        # Partículas decorativas en el menú
        if pygame.time.get_ticks() % 10 == 0:
            self.particle_system.emit_gold_sparkles(
                self.width // 2 + int(math.sin(pygame.time.get_ticks() * 0.002) * (self.width // 3)), 
                self.height - 50
            )
        self.particle_system.update()
        self.particle_system.draw(self.screen)
        
        # Título
        title_y = int(self.height * 0.22)
        self.draw_glitch_text("CALABOZO COGNITIVO", self.font_title, COLOR_UI_GOLD, COLOR_UI_RED, self.width // 2, title_y)
        
        # Subtítulo decorativo
        sub_text = "PRUEBA DE INTELIGENCIAS MÚLTIPLES E IA"
        sub_surf = self.font_ui.render(sub_text, True, COLOR_TEXT_MUTED)
        sub_rect = sub_surf.get_rect(center=(self.width // 2, title_y + 60))
        self.screen.blit(sub_surf, sub_rect)
        
        # Indicación sobre Ollama
        status_text = "ORÁCULO OLLAMA (PHI3.5): CONECTADO" if not self.ai_client.offline_mode else "ORÁCULO EN MODO OFFLINE (FALLBACK LOCAL)"
        status_color = (0, 240, 255) if not self.ai_client.offline_mode else COLOR_UI_RED
        status_surf = self.font_ui.render(status_text, True, status_color)
        self.screen.blit(status_surf, status_surf.get_rect(center=(self.width // 2, title_y + 100)))
        
        if self.show_help:
            # Dibujar Instrucciones
            instructions = [
                "CONTROLES DE MOVIMIENTO CARDINAL:",
                "  Flecha Arriba    -> Mover hacia ARRIBA",
                "  Flecha Izquierda -> Mover hacia la IZQUIERDA",
                "  Flecha Abajo     -> Mover hacia ABAJO",
                "  Flecha Derecha   -> Mover hacia la DERECHA",
                "",
                "DESAFÍOS NARRATIVOS (CÁMARAS DORADAS):",
                "  Responde acertijos seleccionando opciones o escribiendo",
                "  tus propias acciones para probar tus talentos cognitivos.",
                "  Completa los desafíos para llegar al Cofre del Tesoro.",
                "",
                "Presiona ESCAPE / ENTER para volver al menú."
            ]
            
            box_width = int(self.width * 0.8)
            box_height = len(instructions) * 28 + 40
            box_x = (self.width - box_width) // 2
            box_y = int(self.height * 0.45)
            
            # Caja de instrucciones con borde dorado
            pygame.draw.rect(self.screen, (15, 10, 20), (box_x, box_y, box_width, box_height))
            pygame.draw.rect(self.screen, COLOR_UI_GOLD, (box_x, box_y, box_width, box_height), 2)
            
            for i, line in enumerate(instructions):
                line_surf = self.font_ui.render(line, True, COLOR_TEXT if not line.endswith(":") else COLOR_UI_GOLD)
                self.screen.blit(line_surf, (box_x + 30, box_y + 20 + i * 28))
        else:
            # Dibujar opciones de menú
            start_y = int(self.height * 0.5)
            for i, option in enumerate(self.menu_options):
                is_selected = (i == self.selected_menu_option)
                color = COLOR_UI_GOLD if is_selected else COLOR_TEXT
                prefix = "> " if is_selected else "  "
                
                if is_selected and pygame.time.get_ticks() % 500 < 100:
                    color = (255, 255, 255)
                    
                opt_surf = self.font_subtitle.render(prefix + option, True, color)
                opt_rect = opt_surf.get_rect(center=(self.width // 2, start_y + i * 60))
                self.screen.blit(opt_surf, opt_rect)

    def render_hud(self):
        # Dibujar barra superior para el HUD
        hud_height = 55
        hud_surf = pygame.Surface((self.width, hud_height), pygame.SRCALPHA)
        hud_surf.fill((10, 8, 10, 210))
        self.screen.blit(hud_surf, (0, 0))
        pygame.draw.line(self.screen, COLOR_UI_GOLD, (0, hud_height), (self.width, hud_height), 2)
        
        # Textos del HUD
        level_str = "PRUEBA COGNITIVA"
        steps_str = f"PASOS: {self.steps:03d} | RETOS: {len(self.player_history):01d}/{len(self.player_history) + len(self.story_rooms):01d}"
        
        minutes = int(self.elapsed_time) // 60
        seconds = int(self.elapsed_time) % 60
        time_str = f"TIEMPO: {minutes:02d}:{seconds:02d}"
        
        level_surf = self.font_hud.render(level_str, True, COLOR_UI_RED)
        steps_surf = self.font_hud.render(steps_str, True, COLOR_TEXT)
        time_surf = self.font_hud.render(time_str, True, COLOR_UI_GOLD)
        
        self.screen.blit(level_surf, (20, 15))
        self.screen.blit(steps_surf, (self.width // 2 - steps_surf.get_width() // 2, 15))
        self.screen.blit(time_surf, (self.width - time_surf.get_width() - 20, 15))
        
        help_surf = self.font_ui.render("ESC: Pausa  |  Camina hacia las runas doradas en el suelo", True, COLOR_TEXT_MUTED)
        self.screen.blit(help_surf, (20, self.height - 30))
        
        if self.enemy_grace_steps > 0:
            grace_str = f"ACECHANTE DORMIDO: {self.enemy_grace_steps:02d} PASOS"
            grace_surf = self.font_hud.render(grace_str, True, (190, 80, 255))
            self.screen.blit(grace_surf, (self.width - grace_surf.get_width() - 20, self.height - 32))

    def render_pause(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((5, 5, 8, 190))
        self.screen.blit(overlay, (0, 0))
        
        box_w, box_h = 350, 180
        box_x = (self.width - box_w) // 2
        box_y = (self.height - box_h) // 2
        
        pygame.draw.rect(self.screen, (15, 12, 15), (box_x, box_y, box_w, box_h))
        pygame.draw.rect(self.screen, COLOR_UI_GOLD, (box_x, box_y, box_w, box_h), 2)
        
        self.draw_glitch_text("PAUSA", self.font_subtitle, COLOR_UI_GOLD, COLOR_UI_RED, self.width // 2, box_y + 40)
        
        res_text = "PRESIONA ESC PARA REANUDAR"
        menu_text = "PRESIONA ENTER PARA VOLVER AL MENÚ"
        
        res_surf = self.font_ui.render(res_text, True, COLOR_TEXT)
        menu_surf = self.font_ui.render(menu_text, True, COLOR_TEXT_MUTED)
        
        self.screen.blit(res_surf, res_surf.get_rect(center=(self.width // 2, box_y + 95)))
        self.screen.blit(menu_surf, menu_surf.get_rect(center=(self.width // 2, box_y + 135)))

    def start_new_game(self, reset_all=True):
        if reset_all:
            self.current_level = 1
            self.maze_size = INITIAL_MAZE_SIZE
            self.scores = {intel: 0 for intel in INTELLIGENCES}
            self.player_history = []
        else:
            self.current_level += 1
            self.maze_size = min(MAZE_MAX_SIZE, INITIAL_MAZE_SIZE + (self.current_level - 1) * 2)
            
        self.maze = Maze(self.maze_size, self.maze_size)
        self.player.reset(self.maze.start_pos[0], self.maze.start_pos[1])
        self.steps = 0
        self.start_time = time.time()
        self.elapsed_time = 0
        self.particle_system.clear()
        
        # Generar salas de desafíos de Inteligencias
        # Recolectar celdas transitables libres (suelos)
        walkable_cells = []
        for r in range(self.maze.height):
            for c in range(self.maze.width):
                if (self.maze.get_cell(c, r) == CELL_FLOOR and 
                    (c, r) != self.maze.start_pos and 
                    (c, r) != self.maze.exit_pos):
                    walkable_cells.append((c, r))
                    
        # Colocar exactamente 8 cámaras de retos según disponibilidad (una para cada inteligencia múltiple)
        num_challenges = min(8, len(walkable_cells))
        self.story_rooms = random.sample(walkable_cells, num_challenges)
        self.current_room = None
        
        # Spawnear enemigo lejos del jugador
        enemy_cells = []
        min_dist = max(6, self.maze.width // 2)
        for r in range(self.maze.height):
            for c in range(self.maze.width):
                if (self.maze.is_walkable(c, r) and 
                    (c, r) != self.maze.start_pos and 
                    (c, r) != self.maze.exit_pos and 
                    (c, r) not in self.story_rooms):
                    dist = abs(c - self.maze.start_pos[0]) + abs(r - self.maze.start_pos[1])
                    if dist >= min_dist:
                        enemy_cells.append((c, r))
                        
        if not enemy_cells:
            for r in range(self.maze.height):
                for c in range(self.maze.width):
                    if (self.maze.is_walkable(c, r) and 
                        (c, r) != self.maze.start_pos and 
                        (c, r) != self.maze.exit_pos and 
                        (c, r) not in self.story_rooms):
                        dist = abs(c - self.maze.start_pos[0]) + abs(r - self.maze.start_pos[1])
                        if dist >= 4:
                            enemy_cells.append((c, r))
                            
        if not enemy_cells:
            for r in range(self.maze.height):
                for c in range(self.maze.width):
                    if (self.maze.is_walkable(c, r) and 
                        (c, r) != self.maze.start_pos and 
                        (c, r) != self.maze.exit_pos and 
                        (c, r) not in self.story_rooms):
                        enemy_cells.append((c, r))
                        
        if enemy_cells:
            ex_sp, ey_sp = random.choice(enemy_cells)
        else:
            ex_sp, ey_sp = self.maze.exit_pos
            
        self.enemy = Enemy(ex_sp, ey_sp)
        self.enemy_message = ""
        self.enemy_message_timer = 0.0
        self.enemy_grace_steps = 0
        self.state = STATE_PLAYING

    def draw_loading_screen(self, title_text, desc_text):
        """Dibuja un cartel de carga premium para llamadas bloqueantes al LLM."""
        active_enemy = self.enemy if self.enemy_grace_steps == 0 else None
        self.renderer.render(self.screen, self.maze, self.player, active_enemy, self.particle_system, self.story_rooms)
        self.render_hud()
        
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((10, 8, 12, 210))
        self.screen.blit(overlay, (0, 0))
        
        box_w, box_h = 500, 130
        box_x = (self.width - box_w) // 2
        box_y = (self.height - box_h) // 2
        
        pygame.draw.rect(self.screen, (20, 16, 25), (box_x, box_y, box_w, box_h))
        pygame.draw.rect(self.screen, COLOR_UI_GOLD, (box_x, box_y, box_w, box_h), 2)
        
        t_surf = self.font_subtitle.render(title_text, True, COLOR_UI_GOLD)
        d_surf = self.font_ui.render(desc_text, True, COLOR_TEXT)
        
        self.screen.blit(t_surf, t_surf.get_rect(center=(self.width // 2, box_y + 40)))
        self.screen.blit(d_surf, d_surf.get_rect(center=(self.width // 2, box_y + 85)))
        pygame.display.flip()

    def trigger_story_room(self):
        """Detiene al jugador y carga el desafío interactivo de la IA."""
        self.draw_loading_screen(
            "INVOCANDO AL ORÁCULO...",
            "Generando desafío cognitivo en tiempo real..."
        )
        
        # Solicitar sala a Ollama/Contingencia
        self.current_room = self.ai_client.generate_room(self.player_history)
        self.chosen_option_idx = 0
        self.custom_text = ""
        self.result_text = ""
        self.state = STATE_STORY

    def complete_story_room(self):
        """Termina el desafío y devuelve al caballero al modo exploración."""
        if self.current_room:
            self.player_history.append(self.current_room)
        self.current_room = None
        self.state = STATE_PLAYING
        # Evitar contar el tiempo que el jugador pasó leyendo/escribiendo
        self.start_time = time.time() - self.elapsed_time
        
        # Desactivar al Acechante por completo al completar todos los retos
        if len(self.story_rooms) == 0:
            self.enemy = None

    def trigger_mbti_report(self):
        """Invoca a la IA al finalizar para diagnosticar la personalidad MBTI."""
        self.draw_loading_screen(
            "COMPLETANDO PRUEBA COGNITIVA...",
            "El Oráculo de la IA está evaluando tu personalidad..."
        )
        
        self.personality_report = self.ai_client.generate_personality_report(self.scores)
        self.state = STATE_RESULTS

    def trigger_enemy_encounter(self):
        """Activa el encuentro con el enemigo y carga las preguntas de sombra."""
        self.draw_loading_screen(
            "EL ACECHANTE TE CONFRONTA...",
            "El espectro te corta el paso con preguntas del abismo..."
        )
        self.enemy_quiz_questions = self.ai_client.generate_enemy_quiz()
        self.current_quiz_idx = 0
        self.quiz_selected_option = 0
        self.quiz_correct_answers = 0
        self.state = STATE_ENEMY_QUIZ

    def respawn_enemy_away(self):
        """Mueve al enemigo a un casillero transitable aleatorio lejos de la posición del jugador."""
        walkable_cells = []
        min_dist = max(6, self.maze.width // 2)
        for r in range(self.maze.height):
            for c in range(self.maze.width):
                if (self.maze.is_walkable(c, r) and 
                    (c, r) != (self.player.col, self.player.row) and 
                    (c, r) != self.maze.exit_pos and 
                    (c, r) != self.maze.start_pos and 
                    (c, r) not in self.story_rooms):
                    dist = abs(c - self.player.col) + abs(r - self.player.row)
                    if dist >= min_dist:
                        walkable_cells.append((c, r))
                        
        if not walkable_cells:
            # Fallback 1: distancia mínima menor (4)
            for r in range(self.maze.height):
                for c in range(self.maze.width):
                    if (self.maze.is_walkable(c, r) and 
                        (c, r) != (self.player.col, self.player.row) and 
                        (c, r) != self.maze.exit_pos and 
                        (c, r) != self.maze.start_pos and 
                        (c, r) not in self.story_rooms):
                        dist = abs(c - self.player.col) + abs(r - self.player.row)
                        if dist >= 4:
                            walkable_cells.append((c, r))
                            
        if not walkable_cells:
            # Fallback 2: cualquier celda transitable libre de jugador, inicio, salida y runas
            for r in range(self.maze.height):
                for c in range(self.maze.width):
                    if (self.maze.is_walkable(c, r) and 
                        (c, r) != (self.player.col, self.player.row) and 
                        (c, r) != self.maze.exit_pos and 
                        (c, r) != self.maze.start_pos and 
                        (c, r) not in self.story_rooms):
                        walkable_cells.append((c, r))
                        
        if not walkable_cells:
            # Fallback 3: cualquier celda transitable libre de la posición actual del jugador
            for r in range(self.maze.height):
                for c in range(self.maze.width):
                    if (self.maze.is_walkable(c, r) and 
                        (c, r) != (self.player.col, self.player.row)):
                        walkable_cells.append((c, r))

        if walkable_cells:
            ec, er = random.choice(walkable_cells)
            self.enemy.reset(ec, er)
        else:
            # Si es totalmente imposible, ponerlo en el inicio o salida, lejos de donde esté el jugador
            fallback_pos = self.maze.start_pos if (self.player.col, self.player.row) != self.maze.start_pos else self.maze.exit_pos
            self.enemy.reset(fallback_pos[0], fallback_pos[1])

    def get_camera_offset(self):
        """Calcula el desplazamiento de la cámara para centrar el laberinto/jugador."""
        player_x = self.player.current_col * TILE_SIZE + TILE_SIZE // 2
        player_y = self.player.current_row * TILE_SIZE + TILE_SIZE // 2
        
        maze_pixel_width = self.maze.width * TILE_SIZE
        maze_pixel_height = self.maze.height * TILE_SIZE
        
        if maze_pixel_width < self.width:
            offset_x = (self.width - maze_pixel_width) // 2
        else:
            offset_x = self.width // 2 - player_x
            offset_x = max(self.width - maze_pixel_width, min(0, offset_x))
            
        if maze_pixel_height < self.height:
            offset_y = (self.height - maze_pixel_height) // 2
        else:
            offset_y = self.height // 2 - player_y
            offset_y = max(self.height - maze_pixel_height, min(0, offset_y))
            
        return offset_x, offset_y

    def handle_input(self):
        if self.state == STATE_PLAYING:
            keys = pygame.key.get_pressed()
            d_col, d_row = 0, 0
            
            if keys[pygame.K_UP]:
                d_col, d_row = 0, -1
            elif keys[pygame.K_LEFT]:
                d_col, d_row = -1, 0
            elif keys[pygame.K_DOWN]:
                d_col, d_row = 0, 1
            elif keys[pygame.K_RIGHT]:
                d_col, d_row = 1, 0
                
            if d_col != 0 or d_row != 0:
                if self.player.move(d_col, d_row, self.maze):
                    self.steps += 1
                    if self.enemy and len(self.story_rooms) > 0:
                        if self.enemy_grace_steps > 0:
                            self.enemy_grace_steps -= 1
                        else:
                            self.enemy.move_towards(self.player.col, self.player.row, self.maze)

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            
            # Actualizar música de fondo según el estado
            self.update_music()
            
            # --- MANEJO DE EVENTOS ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.VIDEORESIZE:
                    self.handle_resize(event.w, event.h)
                    
                elif event.type == pygame.KEYDOWN:
                    # Menú Principal
                    if self.state == STATE_MENU:
                        if self.show_help:
                            if event.key in [pygame.K_ESCAPE, pygame.K_RETURN]:
                                self.show_help = False
                        else:
                            if event.key == pygame.K_UP:
                                self.selected_menu_option = (self.selected_menu_option - 1) % len(self.menu_options)
                            elif event.key == pygame.K_DOWN:
                                self.selected_menu_option = (self.selected_menu_option + 1) % len(self.menu_options)
                            elif event.key == pygame.K_RETURN:
                                if self.selected_menu_option == 0:
                                    self.start_new_game(reset_all=True)
                                elif self.selected_menu_option == 1:
                                    self.show_help = True
                                elif self.selected_menu_option == 2:
                                    running = False
                                    
                    elif self.state == STATE_PLAYING:
                        if event.key == pygame.K_ESCAPE:
                            self.state = STATE_PAUSE
                            
                    elif self.state == STATE_PAUSE:
                        if event.key == pygame.K_ESCAPE:
                            self.state = STATE_PLAYING
                            self.start_time = time.time() - self.elapsed_time
                        elif event.key == pygame.K_RETURN:
                            self.state = STATE_MENU
                            
                    # Interacción Narrativa / Sala de Diálogos
                    elif self.state == STATE_STORY:
                        if self.result_text:
                            # Ya se mostró el desenlace, presiona ENTER para seguir caminando
                            if event.key in [pygame.K_RETURN, pygame.K_ESCAPE]:
                                self.complete_story_room()
                        else:
                            # Seleccionando opciones
                            if event.key == pygame.K_UP:
                                self.chosen_option_idx = (self.chosen_option_idx - 1) % 4
                            elif event.key == pygame.K_DOWN:
                                self.chosen_option_idx = (self.chosen_option_idx + 1) % 4
                            
                            # Si está seleccionada la escritura libre (opción 3)
                            elif self.chosen_option_idx == 3:
                                if event.key == pygame.K_BACKSPACE:
                                    self.custom_text = self.custom_text[:-1]
                                elif event.key == pygame.K_RETURN:
                                    if self.custom_text.strip():
                                        # Enviar respuesta personalizada a la IA para evaluación
                                        self.draw_loading_screen(
                                            "EVALUANDO ACCIÓN PERSONALIZADA...",
                                            "El Oráculo analiza tus intenciones..."
                                        )
                                        res = self.ai_client.evaluate_custom_response(
                                            self.current_room["narrativa"],
                                            self.current_room["inteligencia_evaluada"],
                                            self.custom_text
                                        )
                                        # Aplicar puntajes
                                        for intel, score in res["puntaje"].items():
                                            self.scores[intel] = self.scores.get(intel, 0) + score
                                        self.result_text = res["respuesta_resultado"]
                                else:
                                    # Teclado libre: capturar caracteres normales
                                    if event.unicode.isprintable() and len(self.custom_text) < 70:
                                        self.custom_text += event.unicode
                                        
                            # Si es una opción fija
                            elif self.chosen_option_idx < 3:
                                if event.key == pygame.K_RETURN:
                                    opt = self.current_room["opciones"][self.chosen_option_idx]
                                    # Aplicar puntajes
                                    for intel, score in opt["puntaje"].items():
                                        self.scores[intel] = self.scores.get(intel, 0) + score
                                    self.result_text = opt["respuesta_resultado"]

                    # Resultados Finales / MBTI
                    elif self.state == STATE_RESULTS:
                        if event.key == pygame.K_RETURN:
                            self.state = STATE_MENU
                            
                    # Encuentro con el Enemigo (Enigma de las Sombras)
                    elif self.state == STATE_ENEMY_QUIZ:
                        if event.key == pygame.K_UP:
                            self.quiz_selected_option = (self.quiz_selected_option - 1) % 3
                        elif event.key == pygame.K_DOWN:
                            self.quiz_selected_option = (self.quiz_selected_option + 1) % 3
                        elif event.key == pygame.K_RETURN:
                            current_q = self.enemy_quiz_questions[self.current_quiz_idx]
                            correct_idx = current_q.get("correcta_idx", 0)
                            
                            if self.quiz_selected_option == correct_idx:
                                self.quiz_correct_answers += 1
                                self.particle_system.emit_burst(self.width // 2, self.height // 2, COLOR_SHIELD_GOLD, count=15)
                            else:
                                self.particle_system.emit_burst(self.width // 2, self.height // 2, COLOR_UI_RED, count=15)
                                
                            self.current_quiz_idx += 1
                            self.quiz_selected_option = 0
                            
                            if self.current_quiz_idx == 3:
                                if self.quiz_correct_answers == 3:
                                    self.player.reset(self.maze.exit_pos[0], self.maze.exit_pos[1])
                                    self.enemy_message = "¡ENIGMAS RESUELTOS! Has sido teletransportado al cofre final."
                                    self.enemy_message_timer = 4.0
                                    self.respawn_enemy_away()
                                    self.particle_system.emit_burst(self.width // 2, self.height // 2, COLOR_SHIELD_GOLD, count=50)
                                    self.enemy_grace_steps = 30
                                else:
                                    self.player.reset(self.maze.start_pos[0], self.maze.start_pos[1])
                                    self.enemy_message = "¡FALLASTE! El Acechante te destierra al inicio del laberinto."
                                    self.enemy_message_timer = 4.0
                                    self.respawn_enemy_away()
                                    self.particle_system.emit_burst(self.width // 2, self.height // 2, COLOR_UI_RED, count=50)
                                    self.enemy_grace_steps = 40
                                    
                                self.state = STATE_PLAYING
                                self.start_time = time.time() - self.elapsed_time

            # --- MANEJO DE ENTRADA DE MOVIMIENTO CONTINUO ---
            self.handle_input()

            # --- LÓGICA DE ACTUALIZACIÓN ---
            if self.state == STATE_PLAYING:
                self.player.update()
                if self.enemy:
                    self.enemy.update()
                self.elapsed_time = time.time() - self.start_time
                
                # Descontar el timer del mensaje de teletransporte
                if self.enemy_message_timer > 0:
                    self.enemy_message_timer -= 1.0 / FPS
                
                # Posición cenital en pantalla del caballero
                offset_x, offset_y = self.get_camera_offset()
                screen_px = self.player.current_col * TILE_SIZE + offset_x + TILE_SIZE // 2
                screen_py = self.player.current_row * TILE_SIZE + offset_y + TILE_SIZE // 2 - int(self.player.bob_offset)
                
                # Partículas de antorcha
                if self.player.is_moving():
                    self.particle_system.emit_torch(screen_px, screen_py)
                    self.particle_system.emit_torch(screen_px, screen_py)
                else:
                    if pygame.time.get_ticks() % 4 == 0:
                        self.particle_system.emit_torch(screen_px, screen_py)
                
                # Colisión con celdas de desafíos
                current_tile = (self.player.col, self.player.row)
                if current_tile in self.story_rooms:
                    self.story_rooms.remove(current_tile)
                    self.trigger_story_room()
                
                # Colisión con el enemigo Acechante (solo si quedan desafíos pendientes)
                if self.enemy and len(self.story_rooms) > 0 and self.enemy_grace_steps == 0:
                    # Detectar si están en el mismo casillero o se cruzan
                    dist_logical = abs(self.player.col - self.enemy.col) + abs(self.player.row - self.enemy.row)
                    dist_physical = math.hypot(self.player.current_col - self.enemy.current_col, self.player.current_row - self.enemy.current_row)
                    if dist_logical == 0 or dist_physical < 0.35:
                        self.trigger_enemy_encounter()
                
                # Comprobar si se ha alcanzado el cofre del tesoro al final
                if not self.player.is_moving():
                    if (self.player.col, self.player.row) == self.maze.exit_pos:
                        if len(self.story_rooms) == 0:
                            ex = self.maze.exit_pos[0] * TILE_SIZE + TILE_SIZE // 2
                            ey = self.maze.exit_pos[1] * TILE_SIZE + TILE_SIZE // 2
                            offset_x, offset_y = self.get_camera_offset()
                            
                            self.particle_system.emit_burst(ex + offset_x, ey + offset_y, COLOR_SHIELD_GOLD, count=60)
                            self.trigger_mbti_report()

            self.particle_system.update()

            # --- RENDERIZADO ---
            if self.state == STATE_MENU:
                self.render_menu()
            elif self.state == STATE_RESULTS:
                self.renderer.render_results(self.screen, self.scores, self.personality_report)
            else:
                # Dibujar calabozo cenital
                active_enemy = self.enemy if self.enemy_grace_steps == 0 else None
                self.renderer.render(self.screen, self.maze, self.player, active_enemy, self.particle_system, self.story_rooms)
                self.render_hud()
                
                # Si hay un mensaje flotante de teletransportación del enemigo
                if self.enemy_message_timer > 0:
                    msg_surf = self.font_hud.render(self.enemy_message, True, COLOR_UI_GOLD if "RESOLU" in self.enemy_message else COLOR_UI_RED)
                    msg_rect = msg_surf.get_rect(center=(self.width // 2, 90))
                    bg_rect = pygame.Rect(msg_rect.x - 10, msg_rect.y - 6, msg_rect.width + 20, msg_rect.height + 12)
                    bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
                    bg_surf.fill((10, 8, 12, 220))
                    self.screen.blit(bg_surf, (bg_rect.x, bg_rect.y))
                    pygame.draw.rect(self.screen, COLOR_UI_GOLD if "RESOLU" in self.enemy_message else COLOR_UI_RED, bg_rect, 1)
                    self.screen.blit(msg_surf, msg_rect)
                
                # Si el jugador está sobre el cofre y sigue cerrado, dibujar aviso
                if not self.player.is_moving() and (self.player.col, self.player.row) == self.maze.exit_pos:
                    if len(self.story_rooms) > 0:
                        warn_text = f"EL COFRE ESTÁ SELLADO. DEBES RESOLVER TODOS LOS RETOS ({len(self.player_history)}/{len(self.player_history) + len(self.story_rooms)})"
                        warn_surf = self.font_hud.render(warn_text, True, COLOR_UI_RED)
                        warn_rect = warn_surf.get_rect(center=(self.width // 2, self.height - 85))
                        bg_rect = pygame.Rect(warn_rect.x - 15, warn_rect.y - 8, warn_rect.width + 30, warn_rect.height + 16)
                        pygame.draw.rect(self.screen, (15, 8, 10), bg_rect)
                        pygame.draw.rect(self.screen, COLOR_UI_RED, bg_rect, 1)
                        self.screen.blit(warn_surf, warn_rect)
                
                # Overlays
                if self.state == STATE_PAUSE:
                    self.render_pause()
                elif self.state == STATE_STORY:
                    self.renderer.render_story_ui(
                        self.screen, 
                        self.current_room, 
                        self.chosen_option_idx, 
                        self.custom_text, 
                        self.result_text,
                        self.ai_client.offline_mode
                    )
                elif self.state == STATE_ENEMY_QUIZ:
                    self.renderer.render_enemy_quiz_ui(
                        self.screen,
                        self.enemy_quiz_questions[self.current_quiz_idx],
                        self.quiz_selected_option,
                        self.current_quiz_idx + 1,
                        self.ai_client.offline_mode
                    )
                    
            pygame.display.flip()
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
