import pygame
import math
import random
import os
from config import (
    TILE_SIZE,
    COLOR_BG, COLOR_WALL_TOP, COLOR_WALL_LEFT, COLOR_WALL_RIGHT,
    COLOR_FLOOR, COLOR_FLOOR_GRID, COLOR_STEEL, COLOR_STEEL_DARK,
    COLOR_SHIELD_BLUE, COLOR_SHIELD_GOLD, COLOR_PLUME,
    COLOR_FLAME_ORANGE, COLOR_FLAME_YELLOW, COLOR_TEXT, COLOR_TEXT_MUTED,
    COLOR_UI_GOLD, COLOR_UI_RED,
    COLOR_DIRT, COLOR_DIRT_DETAIL, COLOR_STONE_FLOOR,
    COLOR_SHADOW_BODY, COLOR_SHADOW_EYES,
    CELL_WALL, CELL_EXIT, CELL_START, INTELLIGENCES
)

class Renderer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Superficie de sombra precalculada para el jugador (cenital)
        self.shadow_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(
            self.shadow_surface, 
            (0, 0, 0, 130), 
            (TILE_SIZE // 2, TILE_SIZE // 2), 
            TILE_SIZE // 3
        )
        
        # Radios de iluminación
        self.light_radius = 5.8
        self.chest_light_radius = 4.5
        self.flicker_val = 0.0
        
        # Inicializar fuentes locales del renderizador
        pygame.font.init()
        self.init_fonts()
        
        # Cargar assets del calabozo
        self.load_assets()

    def load_assets(self):
        assets_dir = "assets"
        tiles_dir = os.path.join(assets_dir, "Tiles")
        
        self.use_assets = False
        try:
            if os.path.exists(tiles_dir):
                self.tile_wall = self.load_and_scale(tiles_dir, "wall.png", make_transparent=False)
                self.tile_stone = self.load_and_scale(tiles_dir, "floor_mushrom.png", make_transparent=False)
                self.tile_dirt = self.load_and_scale(tiles_dir, "dirt.png", make_transparent=False)
                self.tile_player = self.load_and_scale(tiles_dir, "knight.png", make_transparent=True)
                self.tile_enemy = self.load_and_scale(tiles_dir, "stalker.png", make_transparent=True)
                self.tile_chest_closed = self.load_and_scale(tiles_dir, "chest.png", make_transparent=True)
                self.tile_chest_open = self.load_and_scale(tiles_dir, "open chest.png", make_transparent=True)
                self.tile_rune = self.load_and_scale(tiles_dir, "key.png", make_transparent=True)
                self.use_assets = True
                print("Kenney 1-Bit assets loaded successfully with transparency.")
        except Exception as e:
            print(f"Error loading assets: {e}. Falling back to procedural rendering.")
            self.use_assets = False
            
    def load_and_scale(self, directory, filename, make_transparent=False):
        path = os.path.join(directory, filename)
        img = pygame.image.load(path).convert_alpha()
        
        if make_transparent:
            # Reemplazar el color de fondo (píxel 0,0) por transparencia total
            bg_color = img.get_at((0, 0))
            transparent_img = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            for x in range(img.get_width()):
                for y in range(img.get_height()):
                    color = img.get_at((x, y))
                    if color == bg_color:
                        transparent_img.set_at((x, y), (0, 0, 0, 0))
                    else:
                        transparent_img.set_at((x, y), color)
            img = transparent_img
            
        return pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))

    def blit_with_lighting(self, surface, sprite, dest_x, dest_y, intensity, tint_color=None, tint_factor=0.0):
        # 1. Calcular el color de la iluminación mezclando luces
        illum_color = self.blend_color((255, 255, 255), intensity, tint_color, tint_factor)
        
        # 2. Copiar el sprite y preparar la superficie de luz
        sprite_copy = sprite.copy()
        light_surf = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
        light_surf.fill(illum_color)
        
        # 3. Aplicar multiplicación de color (preserva el canal alpha)
        sprite_copy.blit(light_surf, (0, 0), special_flags=pygame.BLEND_MULT)
        
        # 4. Dibujar en pantalla
        surface.blit(sprite_copy, (dest_x, dest_y))

    def init_fonts(self):
        """Inicializa las fuentes del sistema para interfaces y textos narrativos."""
        font_names = ["consolas", "courier new", "monospace"]
        self.font_title = pygame.font.SysFont(font_names, 36, bold=True)
        self.font_subtitle = pygame.font.SysFont(font_names, 24, bold=True)
        self.font_ui = pygame.font.SysFont(font_names, 16, bold=False)
        self.font_small = pygame.font.SysFont(font_names, 13, bold=False)
        self.font_mbti = pygame.font.SysFont(font_names, 28, bold=True)

    def draw_wrapped_text(self, surface, text, x, y, max_width, font, color, line_spacing=22):
        """Dibuja un párrafo adaptando saltos de línea de forma automática."""
        words = text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            # Manejar saltos de línea manuales \n
            if '\n' in word:
                parts = word.split('\n')
                for j, part in enumerate(parts):
                    test_line = current_line + " " + part if current_line else part
                    if j == 0:
                        if font.size(test_line)[0] < max_width:
                            current_line = test_line
                        else:
                            lines.append(current_line)
                            current_line = part
                    else:
                        lines.append(current_line)
                        current_line = part
            else:
                test_line = current_line + " " + word if current_line else word
                if font.size(test_line)[0] < max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
        if current_line:
            lines.append(current_line)
            
        for i, line in enumerate(lines):
            line_surf = font.render(line, True, color)
            surface.blit(line_surf, (x, y + i * line_spacing))
        return len(lines) * line_spacing

    def update_flicker(self):
        """Efecto de parpadeo para la antorcha del caballero."""
        self.flicker_val = math.sin(pygame.time.get_ticks() * 0.06) * 0.04 + random.uniform(-0.02, 0.02)

    def get_light_intensity(self, col, row, player, maze):
        """Calcula la intensidad de luz en 2D cenital."""
        # Distancia al caballero (antorcha)
        dp = math.hypot(col - player.current_col, row - player.current_row)
        intensity_torch = max(0.0, 1.0 - (dp / self.light_radius))
        if intensity_torch > 0:
            intensity_torch += self.flicker_val * intensity_torch
            intensity_torch = max(0.0, min(1.2, intensity_torch))
        
        # Distancia al cofre (oro brillante)
        ex, ey = maze.exit_pos
        de = math.hypot(col - ex, row - ey)
        intensity_chest = max(0.0, 1.0 - (de / self.chest_light_radius)) * 0.65
        
        return max(0.06, intensity_torch + intensity_chest)

    def blend_color(self, color, intensity, tint_color=None, tint_factor=0.0):
        """Aplica intensidad y tinte cromático."""
        r = int(color[0] * intensity)
        g = int(color[1] * intensity)
        b = int(color[2] * intensity)
        
        if tint_color and tint_factor > 0:
            r = int(r * (1.0 - tint_factor) + tint_color[0] * intensity * tint_factor)
            g = int(g * (1.0 - tint_factor) + tint_color[1] * intensity * tint_factor)
            b = int(b * (1.0 - tint_factor) + tint_color[2] * intensity * tint_factor)
            
        return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

    def render(self, surface, maze, player, enemy, particle_system, story_rooms=[]):
        self.update_flicker()
        
        # Limpiar fondo
        surface.fill(COLOR_BG)
        
        # Calcular cámara 2D centrada con soporte para centrado y límites
        player_x = player.current_col * TILE_SIZE + TILE_SIZE // 2
        player_y = player.current_row * TILE_SIZE + TILE_SIZE // 2
        
        maze_pixel_width = maze.width * TILE_SIZE
        maze_pixel_height = maze.height * TILE_SIZE
        
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
        
        # Pase 1: Dibujar Suelos
        for row in range(maze.height):
            for col in range(maze.width):
                cell_type = maze.get_cell(col, row)
                if cell_type != CELL_WALL:
                    # Posición en pantalla de la celda
                    sx = col * TILE_SIZE + offset_x
                    sy = row * TILE_SIZE + offset_y
                    
                    # Viewport Culling
                    if (sx + TILE_SIZE < 0 or sx > self.width or
                        sy + TILE_SIZE < 0 or sy > self.height):
                        continue
                    
                    # Calcular luz e intensidades
                    intensity = self.get_light_intensity(col, row, player, maze)
                    
                    dist_to_player = math.hypot(col - player.current_col, row - player.current_row)
                    dist_to_exit = math.hypot(col - maze.exit_pos[0], row - maze.exit_pos[1])
                    
                    tint_color = None
                    tint_factor = 0.0
                    if dist_to_player < self.light_radius:
                        tint_color = COLOR_FLAME_ORANGE
                        tint_factor = max(0.0, 1.0 - (dist_to_player / self.light_radius)) * 0.3
                    elif dist_to_exit < self.chest_light_radius:
                        tint_color = COLOR_SHIELD_GOLD
                        tint_factor = max(0.0, 1.0 - (dist_to_exit / self.chest_light_radius)) * 0.4
                        
                    # Mapeo de material de suelo
                    floor_type = maze.floor_types.get((col, row), 'stone')
                    
                    if self.use_assets:
                        sprite = self.tile_dirt if floor_type == 'dirt' else self.tile_stone
                        self.blit_with_lighting(surface, sprite, sx, sy, intensity, tint_color, tint_factor)
                        
                        if (col, row) in story_rooms:
                            self.blit_with_lighting(surface, self.tile_rune, sx, sy, intensity, tint_color, tint_factor)
                    else:
                        if floor_type == 'dirt':
                            base_floor_c = COLOR_DIRT
                            detail_floor_c = COLOR_DIRT_DETAIL
                        else:
                            base_floor_c = COLOR_STONE_FLOOR
                            detail_floor_c = COLOR_FLOOR_GRID
                            
                        floor_color = self.blend_color(base_floor_c, intensity, tint_color, tint_factor)
                        grid_color = self.blend_color(detail_floor_c, intensity, tint_color, tint_factor)
                        
                        # Dibujar baldosa base
                        pygame.draw.rect(surface, floor_color, (sx, sy, TILE_SIZE, TILE_SIZE))
                        
                        if floor_type == 'dirt':
                            # Suelo de tierra: piedrecitas y relieve orgánico
                            random.seed(col * 31 + row * 17)
                            for _ in range(3):
                                px = sx + random.randint(3, TILE_SIZE - 6)
                                py = sy + random.randint(3, TILE_SIZE - 6)
                                size = random.choice([1, 2])
                                pygame.draw.rect(surface, grid_color, (px, py, size, size))
                            if (col + row) % 3 == 0:
                                pygame.draw.line(surface, grid_color, (sx + 5, sy + 12), (sx + 14, sy + 15), 1)
                        else:
                            # Suelo de piedra: rejilla diagonal fina
                            pygame.draw.rect(surface, grid_color, (sx, sy, TILE_SIZE, TILE_SIZE), 1)
                            pygame.draw.line(surface, grid_color, (sx, sy), (sx + TILE_SIZE, sy + TILE_SIZE), 1)
                            
                        # Si es una cámara de historia, pintamos una runa brillante en el centro
                        if (col, row) in story_rooms:
                            rune_color = self.blend_color((245, 150, 20), intensity, tint_color, tint_factor)
                            pygame.draw.polygon(surface, rune_color, [
                                (sx + TILE_SIZE // 2, sy + TILE_SIZE // 4),
                                (sx + TILE_SIZE * 3 // 4, sy + TILE_SIZE // 2),
                                (sx + TILE_SIZE // 2, sy + TILE_SIZE * 3 // 4),
                                (sx + TILE_SIZE // 4, sy + TILE_SIZE // 2)
                            ])
                            pygame.draw.polygon(surface, (255, 220, 100), [
                                (sx + TILE_SIZE // 2, sy + TILE_SIZE // 4),
                                (sx + TILE_SIZE * 3 // 4, sy + TILE_SIZE // 2),
                                (sx + TILE_SIZE // 2, sy + TILE_SIZE * 3 // 4),
                                (sx + TILE_SIZE // 4, sy + TILE_SIZE // 2)
                            ], 1)

        # Pase 2: Dibujar Muros
        for row in range(maze.height):
            for col in range(maze.width):
                cell_type = maze.get_cell(col, row)
                if cell_type == CELL_WALL:
                    sx = col * TILE_SIZE + offset_x
                    sy = row * TILE_SIZE + offset_y
                    
                    # Viewport Culling
                    if (sx + TILE_SIZE < 0 or sx > self.width or
                        sy + TILE_SIZE < 0 or sy > self.height):
                        continue
                    
                    # Intensidad lumínica
                    intensity = self.get_light_intensity(col, row, player, maze)
                    
                    dist_to_player = math.hypot(col - player.current_col, row - player.current_row)
                    dist_to_exit = math.hypot(col - maze.exit_pos[0], row - maze.exit_pos[1])
                    
                    tint_color = None
                    tint_factor = 0.0
                    if dist_to_player < self.light_radius:
                        tint_color = COLOR_FLAME_ORANGE
                        tint_factor = max(0.0, 1.0 - (dist_to_player / self.light_radius)) * 0.25
                    elif dist_to_exit < self.chest_light_radius:
                        tint_color = COLOR_SHIELD_GOLD
                        tint_factor = max(0.0, 1.0 - (dist_to_exit / self.chest_light_radius)) * 0.3
                        
                    self.draw_2d_wall(surface, sx, sy, intensity, tint_color, tint_factor)

        # Pase 3: Dibujar Cofre del Tesoro (Meta)
        ex, ey = maze.exit_pos
        sx_exit = ex * TILE_SIZE + offset_x
        sy_exit = ey * TILE_SIZE + offset_y
        exit_intensity = self.get_light_intensity(ex, ey, player, maze)
        # Determinar si el cofre está cerrado (si quedan desafíos pendientes)
        chest_locked = len(story_rooms) > 0
        self.draw_2d_chest(surface, sx_exit, sy_exit, exit_intensity, particle_system, chest_locked)

        # Pase 4: Dibujar Caballero (Jugador)
        px_screen = player.current_col * TILE_SIZE + offset_x
        py_screen = player.current_row * TILE_SIZE + offset_y
        player_intensity = self.get_light_intensity(player.current_col, player.current_row, player, maze)
        
        # Sombreado bajo el caballero
        surface.blit(self.shadow_surface, (px_screen, py_screen))
        self.draw_2d_knight(surface, px_screen + TILE_SIZE // 2, py_screen + TILE_SIZE // 2, player, player_intensity)

        # Pase 4.5: Dibujar Enemigo (Sombra Acechante)
        if enemy:
            ex_screen = enemy.current_col * TILE_SIZE + offset_x
            ey_screen = enemy.current_row * TILE_SIZE + offset_y
            enemy_intensity = self.get_light_intensity(enemy.current_col, enemy.current_row, player, maze)
            if enemy_intensity > 0.08:
                self.draw_2d_enemy(surface, ex_screen + TILE_SIZE // 2, ey_screen + TILE_SIZE // 2, enemy, enemy_intensity)

        # Pase 5: Dibujar Partículas
        particle_system.draw(surface)

    def draw_2d_wall(self, surface, sx, sy, intensity, tint_color, tint_factor):
        """Dibuja un muro de piedra elevado con relieve 3D marcado y diseño de doble ladrillo horizontal."""
        if self.use_assets:
            self.blit_with_lighting(surface, self.tile_wall, sx, sy, intensity, tint_color, tint_factor)
            return

        base_color = self.blend_color(COLOR_WALL_LEFT, intensity, tint_color, tint_factor)
        border_color = self.blend_color(COLOR_WALL_RIGHT, intensity, tint_color, tint_factor)
        highlight_color = self.blend_color(COLOR_WALL_TOP, intensity, tint_color, tint_factor)
        
        # Fondo oscuro para el bloque
        pygame.draw.rect(surface, border_color, (sx, sy, TILE_SIZE, TILE_SIZE))
        # Relleno del bloque elevado
        pygame.draw.rect(surface, base_color, (sx + 2, sy + 2, TILE_SIZE - 4, TILE_SIZE - 4))
        
        # Biselado superior/izquierdo para dar relieve 3D
        pygame.draw.line(surface, highlight_color, (sx + 3, sy + 3), (sx + TILE_SIZE - 3, sy + 3), 2)
        pygame.draw.line(surface, highlight_color, (sx + 3, sy + 3), (sx + 3, sy + TILE_SIZE - 3), 2)
        
        # Textura interna de dos ladrillos
        pygame.draw.line(surface, border_color, (sx + 2, sy + TILE_SIZE // 2), (sx + TILE_SIZE - 2, sy + TILE_SIZE // 2), 1)
        pygame.draw.line(surface, border_color, (sx + TILE_SIZE // 2, sy + 2), (sx + TILE_SIZE // 2, sy + TILE_SIZE // 2), 1)

    def draw_2d_enemy(self, surface, ex, ey, enemy, intensity):
        """Dibuja al enemigo Acechante: una sombra espectral flotante con ojos rojos brillantes."""
        if self.use_assets:
            px = ex - TILE_SIZE // 2
            py = ey - TILE_SIZE // 2 - int(enemy.bob_offset)
            sprite = self.tile_enemy
            if enemy.direction == "left":
                sprite = pygame.transform.flip(self.tile_enemy, True, False)
            self.blit_with_lighting(surface, sprite, px, py, intensity, tint_color=(100, 50, 150), tint_factor=0.35)
            return

        body_color = self.blend_color(COLOR_SHADOW_BODY, intensity)
        eyes_color = COLOR_SHADOW_EYES
        
        ey_bob = ey - int(enemy.bob_offset)
        
        # 1. Capa o bruma oscura flotante (cuerpo)
        pygame.draw.ellipse(surface, body_color, (ex - 12, ey_bob - 14, 24, 28))
        
        # Cola espectral inferior (triángulos de humo)
        tail_poly = [(ex - 10, ey_bob + 6), (ex + 10, ey_bob + 6), (ex, ey_bob + 18)]
        pygame.draw.polygon(surface, body_color, tail_poly)
        
        # 2. Ojos rojos brillantes
        if enemy.direction == "left":
            pygame.draw.circle(surface, eyes_color, (ex - 7, ey_bob - 3), 2.5)
            pygame.draw.circle(surface, eyes_color, (ex - 2, ey_bob - 3), 2.5)
        elif enemy.direction == "right":
            pygame.draw.circle(surface, eyes_color, (ex + 2, ey_bob - 3), 2.5)
            pygame.draw.circle(surface, eyes_color, (ex + 7, ey_bob - 3), 2.5)
        elif enemy.direction == "up":
            pygame.draw.circle(surface, (120, 10, 10), (ex - 4, ey_bob - 5), 1.5)
            pygame.draw.circle(surface, (120, 10, 10), (ex + 4, ey_bob - 5), 1.5)
        else: # "down" o por defecto
            pygame.draw.circle(surface, eyes_color, (ex - 4, ey_bob - 2), 3)
            pygame.draw.circle(surface, eyes_color, (ex + 4, ey_bob - 2), 3)

    def draw_2d_chest(self, surface, sx, sy, intensity, particle_system, locked=True):
        """Dibuja el cofre del tesoro visto desde arriba cenitalmente (abierto o cerrado)."""
        cx = sx + TILE_SIZE // 2
        cy = sy + TILE_SIZE // 2

        if self.use_assets:
            sprite = self.tile_chest_closed if locked else self.tile_chest_open
            self.blit_with_lighting(surface, sprite, sx, sy, intensity)
            
            if not locked:
                gold_glow = (255, 215, 0, 40)
                glow_surf = pygame.Surface((TILE_SIZE * 2, TILE_SIZE * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, gold_glow, (TILE_SIZE, TILE_SIZE), TILE_SIZE - 4)
                surface.blit(glow_surf, (sx - TILE_SIZE // 2, sy - TILE_SIZE // 2))
                
                if random.random() < 0.25:
                    particle_system.emit_gold_sparkles(cx, cy)
            return

        wood_c = self.blend_color((115, 60, 20), intensity)
        gold_c = self.blend_color((230, 185, 25), intensity)
        
        cw, ch = 26, 18
        
        if locked:
            # Cuerpo de madera
            pygame.draw.rect(surface, wood_c, (cx - cw // 2, cy - ch // 2, cw, ch))
            pygame.draw.rect(surface, (40, 20, 5), (cx - cw // 2, cy - ch // 2, cw, ch), 1)
            
            # Herrajes dorados en los costados
            pygame.draw.rect(surface, gold_c, (cx - cw // 2, cy - ch // 2, 4, ch))
            pygame.draw.rect(surface, gold_c, (cx + cw // 2 - 4, cy - ch // 2, 4, ch))
            
            # Cerradura de metal oscuro cerrada
            pygame.draw.rect(surface, (45, 45, 50), (cx - 3, cy - 3, 6, 6))
            pygame.draw.circle(surface, (15, 15, 18), (cx, cy), 1)
        else:
            # Dibujar cofre abierto y reluciente
            gold_glow = (255, 215, 0, 40)
            
            # Brillo circular dorado en el suelo
            glow_surf = pygame.Surface((TILE_SIZE * 2, TILE_SIZE * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, gold_glow, (TILE_SIZE, TILE_SIZE), TILE_SIZE - 4)
            surface.blit(glow_surf, (sx - TILE_SIZE // 2, sy - TILE_SIZE // 2))
            
            # Cuerpo de madera
            pygame.draw.rect(surface, wood_c, (cx - cw // 2, cy - ch // 2, cw, ch))
            pygame.draw.rect(surface, (40, 20, 5), (cx - cw // 2, cy - ch // 2, cw, ch), 1)
            
            # Herrajes dorados
            pygame.draw.rect(surface, gold_c, (cx - cw // 2, cy - ch // 2, 4, ch))
            pygame.draw.rect(surface, gold_c, (cx + cw // 2 - 4, cy - ch // 2, 4, ch))
            
            # Pestillo dorado central
            pygame.draw.rect(surface, gold_c, (cx - 2, cy - ch // 2 + 3, 4, 4))
            
            # Brillo de oro caliente adentro
            pygame.draw.circle(surface, (255, 240, 150), (cx, cy), 2)
            
            # Emitir partículas doradas
            if random.random() < 0.25:
                particle_system.emit_gold_sparkles(cx, cy)

    def draw_2d_knight(self, surface, kx, ky, player, intensity):
        """Dibuja al Caballero cenital: casco circular de acero, espada, escudo y penacho rojo."""
        if self.use_assets:
            px = kx - TILE_SIZE // 2
            py = ky - TILE_SIZE // 2 - int(player.bob_offset)
            sprite = self.tile_player
            if player.direction == "left":
                sprite = pygame.transform.flip(self.tile_player, True, False)
            self.blit_with_lighting(surface, sprite, px, py, intensity)
            return

        steel_c = self.blend_color(COLOR_STEEL, intensity)
        steel_d = self.blend_color(COLOR_STEEL_DARK, intensity)
        plume_c = self.blend_color(COLOR_PLUME, intensity)
        gold_c = self.blend_color(COLOR_SHIELD_GOLD, intensity)
        blue_c = self.blend_color(COLOR_SHIELD_BLUE, intensity)
        
        radius_head = 11
        by = ky - int(player.bob_offset)
        
        # --- DIBUJAR CAPA / PENACHO DE PLUMAS ---
        plume_offset = 12
        if player.direction == "up":
            plume_poly = [(kx - 3, by + 4), (kx + 3, by + 4), (kx, by + plume_offset + 2)]
        elif player.direction == "down":
            plume_poly = [(kx - 3, by - 4), (kx + 3, by - 4), (kx, by - plume_offset - 2)]
        elif player.direction == "left":
            plume_poly = [(kx + 4, by - 3), (kx + 4, by + 3), (kx + plume_offset + 2, by)]
        else: # "right"
            plume_poly = [(kx - 4, by - 3), (kx - 4, by + 3), (kx - plume_offset - 2, by)]
            
        pygame.draw.polygon(surface, plume_c, plume_poly)
        
        # --- DIBUJAR YELMO ---
        pygame.draw.circle(surface, steel_c, (kx, by), radius_head)
        pygame.draw.circle(surface, steel_d, (kx, by), radius_head, 1)
        
        # --- RANURA VISOR NEGRA ---
        visor_w, visor_h = 8, 3
        if player.direction == "up":
            pygame.draw.rect(surface, (15, 15, 20), (kx - visor_w // 2, by - radius_head + 2, visor_w, visor_h))
        elif player.direction == "down":
            pygame.draw.rect(surface, (15, 15, 20), (kx - visor_w // 2, by + radius_head - 4, visor_w, visor_h))
        elif player.direction == "left":
            pygame.draw.rect(surface, (15, 15, 20), (kx - radius_head + 2, by - visor_w // 2, visor_h, visor_w))
        else: # "right"
            pygame.draw.rect(surface, (15, 15, 20), (kx + radius_head - 4, by - visor_w // 2, visor_h, visor_w))

        # --- DIBUJAR HOMBROS Y EQUIPAMIENTO (Escudo y Espada) ---
        if player.direction in ["up", "down"]:
            # Escudo en la izquierda
            sx_shield, sy_shield = kx - 14, by
            pygame.draw.rect(surface, blue_c, (sx_shield - 3, sy_shield - 6, 6, 12))
            pygame.draw.rect(surface, gold_c, (sx_shield - 3, sy_shield - 1, 6, 2))
            pygame.draw.rect(surface, steel_d, (sx_shield - 3, sy_shield - 6, 6, 12), 1)
            
            # Espada en la derecha
            pygame.draw.circle(surface, gold_c, (kx + 14, by + 2), 2)
            blade_y_dir = -8 if player.direction == "up" else 8
            pygame.draw.line(surface, steel_c, (kx + 14, by), (kx + 14, by + blade_y_dir), 2)
        else:
            # Escudo arriba
            sx_shield, sy_shield = kx, by - 14
            pygame.draw.rect(surface, blue_c, (sx_shield - 6, sy_shield - 3, 12, 6))
            pygame.draw.rect(surface, gold_c, (sx_shield - 1, sy_shield - 3, 2, 6))
            pygame.draw.rect(surface, steel_d, (sx_shield - 6, sy_shield - 3, 12, 6), 1)
            
            # Espada abajo
            pygame.draw.circle(surface, gold_c, (kx - 2, by + 14), 2)
            blade_x_dir = -8 if player.direction == "left" else 8
            pygame.draw.line(surface, steel_c, (kx, by + 14), (kx + blade_x_dir, by + 14), 2)

    def render_story_ui(self, surface, room, chosen_option_idx, custom_text, result_text, connection_offline=False):
        """Pinta la interfaz de historia narrativa sobre la pantalla de juego."""
        # 1. Overlay oscuro semi-transparente
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((5, 5, 8, 185))
        surface.blit(overlay, (0, 0))
        
        # 2. Caja contenedora principal
        pw, ph = 800, 560
        px = (self.width - pw) // 2
        py = (self.height - ph) // 2
        
        # Panel
        panel_surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel_surf.fill((15, 12, 18, 235))
        pygame.draw.rect(panel_surf, COLOR_UI_GOLD, (0, 0, pw, ph), 2)
        
        # Borde decorativo interior
        pygame.draw.rect(panel_surf, (40, 35, 45), (4, 4, pw - 8, ph - 8), 1)
        surface.blit(panel_surf, (px, py))
        
        # 3. Encabezado de la Sala
        title = f"DESAFÍO: INTELIGENCIA {room['inteligencia_evaluada'].upper()}"
        if connection_offline:
            title += " (OFFLINE MODE)"
        title_surf = self.font_subtitle.render(title, True, COLOR_UI_GOLD)
        surface.blit(title_surf, (px + 30, py + 25))
        
        # Línea divisoria
        pygame.draw.line(surface, COLOR_UI_RED, (px + 30, py + 60), (px + pw - 30, py + 60), 2)
        
        # 4. Narrativa de la sala (Word Wrap)
        narrative_height = self.draw_wrapped_text(
            surface, 
            room["narrativa"], 
            px + 30, py + 75, 
            pw - 60, 
            self.font_ui, 
            COLOR_TEXT,
            line_spacing=24
        )
        
        # Separación dinámica según el largo del texto
        options_start_y = py + 75 + narrative_height + 25
        
        if result_text:
            # 5a. Mostrar resultado de la decisión tomada
            result_header = "RESULTADO DE TU ACCIÓN:"
            res_h_surf = self.font_subtitle.render(result_header, True, COLOR_UI_RED)
            surface.blit(res_h_surf, (px + 30, options_start_y))
            
            result_y = options_start_y + 35
            self.draw_wrapped_text(
                surface,
                result_text,
                px + 30, result_y,
                pw - 60,
                self.font_ui,
                (255, 230, 150),
                line_spacing=24
            )
            
            # Promp de continuar
            prompt_text = "PRESIONA [ ENTER ] PARA CONTINUAR EXPLORANDO..."
            if pygame.time.get_ticks() % 800 < 400:
                prompt_surf = self.font_subtitle.render(prompt_text, True, COLOR_UI_GOLD)
                surface.blit(prompt_surf, (px + pw // 2 - prompt_surf.get_width() // 2, py + ph - 55))
        else:
            # 5b. Mostrar 3 opciones + Entrada libre
            # Dibujar Opciones A, B, C
            for i, opt in enumerate(room["opciones"]):
                opt_y = options_start_y + i * 72
                is_selected = (chosen_option_idx == i)
                
                # Caja de opción
                box_color = (25, 22, 30, 150) if not is_selected else (50, 42, 20, 200)
                box_surf = pygame.Surface((pw - 60, 62), pygame.SRCALPHA)
                box_surf.fill(box_color)
                
                border_color = (60, 55, 65) if not is_selected else COLOR_UI_GOLD
                pygame.draw.rect(box_surf, border_color, (0, 0, pw - 60, 62), 1 if not is_selected else 2)
                surface.blit(box_surf, (px + 30, opt_y))
                
                # Texto de opción
                prefix = f"{chr(65+i)}. "
                full_opt_text = prefix + opt["texto"]
                
                text_color = COLOR_TEXT if not is_selected else (255, 255, 255)
                self.draw_wrapped_text(
                    surface,
                    full_opt_text,
                    px + 45, opt_y + 10,
                    pw - 90,
                    self.font_ui,
                    text_color,
                    line_spacing=20
                )
                
            # Opción D: Respuesta libre
            free_y = options_start_y + 3 * 72
            is_selected = (chosen_option_idx == 3)
            
            # Caja de texto para respuesta personalizada
            box_color = (25, 22, 30, 150) if not is_selected else (35, 45, 45, 200)
            box_surf = pygame.Surface((pw - 60, 75), pygame.SRCALPHA)
            box_surf.fill(box_color)
            border_color = (60, 55, 65) if not is_selected else (0, 240, 255) # Cian para modo escritura
            pygame.draw.rect(box_surf, border_color, (0, 0, pw - 60, 75), 1 if not is_selected else 2)
            surface.blit(box_surf, (px + 30, free_y))
            
            # Etiquetas
            free_label = "D. ESCRIBIR ACCIÓN PERSONALIZADA (Presiona ENTER para enviar):"
            label_color = COLOR_TEXT_MUTED if not is_selected else (0, 240, 255)
            label_surf = self.font_small.render(free_label, True, label_color)
            surface.blit(label_surf, (px + 45, free_y + 8))
            
            # Valor de texto escrito
            cursor = "|" if (is_selected and pygame.time.get_ticks() % 500 < 250) else ""
            display_text = custom_text + cursor
            if not custom_text and not is_selected:
                display_text = "Escribe tu propia solución aquí..."
                text_color = COLOR_TEXT_MUTED
            else:
                text_color = COLOR_TEXT if is_selected else COLOR_TEXT_MUTED
                
            self.draw_wrapped_text(
                surface,
                display_text,
                px + 45, free_y + 28,
                pw - 90,
                self.font_ui,
                text_color,
                line_spacing=20
            )
            
            # Indicación
            info_text = "Usa ARRIBA / ABAJO para seleccionar. [ ENTER ] para elegir."
            info_surf = self.font_small.render(info_text, True, COLOR_TEXT_MUTED)
            surface.blit(info_surf, (px + 30, py + ph - 25))

    def render_results(self, surface, scores, report):
        """Dibuja la pantalla final detallada de Inteligencias Múltiples y Personalidad MBTI."""
        surface.fill(COLOR_BG)
        
        # 1. Caja contenedora grande
        pw, ph = 940, 610
        px = (self.width - pw) // 2
        py = (self.height - ph) // 2
        
        panel_surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel_surf.fill((14, 11, 16, 240))
        pygame.draw.rect(panel_surf, COLOR_UI_GOLD, (0, 0, pw, ph), 2)
        surface.blit(panel_surf, (px, py))
        
        # Título General
        title_str = "REPORTE DE SIMULACIÓN COGNITIVA"
        title_surf = self.font_subtitle.render(title_str, True, COLOR_UI_GOLD)
        surface.blit(title_surf, (px + 30, py + 25))
        
        pygame.draw.line(surface, COLOR_UI_RED, (px + 30, py + 55), (px + pw - 30, py + 55), 2)
        
        # 2. COLUMNA IZQUIERDA: Gráfico de Barras de Inteligencias Múltiples
        col1_x = px + 30
        col1_y = py + 80
        col1_w = 400
        
        h_col_surf = self.font_subtitle.render("PERFIL DE INTELIGENCIAS", True, COLOR_UI_GOLD)
        surface.blit(h_col_surf, (col1_x, col1_y))
        
        # Dibujar 8 barras
        max_bar_w = 210
        for i, intel in enumerate(INTELLIGENCES):
            bar_y = col1_y + 42 + i * 52
            score = scores.get(intel, 0)
            
            # Nombre de la inteligencia
            intel_label = intel.split('-')[-1] # Simplificar nombre largo
            label_surf = self.font_small.render(intel_label, True, COLOR_TEXT)
            surface.blit(label_surf, (col1_x, bar_y))
            
            # Fondo de la barra
            pygame.draw.rect(surface, (30, 25, 35), (col1_x + 140, bar_y - 2, max_bar_w, 14))
            pygame.draw.rect(surface, (60, 55, 70), (col1_x + 140, bar_y - 2, max_bar_w, 14), 1)
            
            # Llenado de la barra proporcional (Asumimos puntuación máx sugerida de 12 para la escala)
            fill_ratio = min(1.0, score / 12.0)
            fill_w = int(max_bar_w * fill_ratio)
            
            # Color dinámico de la barra según el tipo de inteligencia
            bar_color = COLOR_FLAME_ORANGE
            if i % 3 == 0:
                bar_color = COLOR_SHIELD_BLUE
            elif i % 3 == 1:
                bar_color = COLOR_UI_GOLD
                
            if fill_w > 0:
                pygame.draw.rect(surface, bar_color, (col1_x + 141, bar_y - 1, fill_w - 2, 12))
                
            # Puntuación numérica
            score_surf = self.font_ui.render(f"{score:02d} pts", True, COLOR_UI_GOLD if fill_ratio >= 0.7 else COLOR_TEXT_MUTED)
            surface.blit(score_surf, (col1_x + 140 + max_bar_w + 12, bar_y - 4))
            
        # 3. COLUMNA DERECHA: Análisis de Personalidad MBTI (16Personalities)
        col2_x = px + 470
        col2_y = py + 80
        col2_w = 440
        
        h_col2_surf = self.font_subtitle.render("ANÁLISIS DE PERSONALIDAD", True, COLOR_UI_RED)
        surface.blit(h_col2_surf, (col2_x, col2_y))
        
        # Tipo MBTI y Título
        mbti_code = report.get("mbti", "XXXX")
        mbti_title = report.get("titulo", "El Viajero Silencioso")
        
        mbti_str = f"{mbti_code} - {mbti_title.upper()}"
        mbti_surf = self.font_mbti.render(mbti_str, True, COLOR_UI_GOLD)
        surface.blit(mbti_surf, (col2_x, col2_y + 40))
        
        # Caja de pergamino/texto para el resumen
        txt_box_y = col2_y + 80
        txt_box_h = ph - 190
        
        txt_box_surf = pygame.Surface((col2_w, txt_box_h), pygame.SRCALPHA)
        txt_box_surf.fill((22, 18, 25, 120))
        pygame.draw.rect(txt_box_surf, (60, 50, 70), (0, 0, col2_w, txt_box_h), 1)
        surface.blit(txt_box_surf, (col2_x, txt_box_y))
        
        # Resumen descriptivo de la IA
        self.draw_wrapped_text(
            surface,
            report.get("resumen", "No se pudo obtener el informe de personalidad."),
            col2_x + 15, txt_box_y + 15,
            col2_w - 30,
            self.font_ui,
            COLOR_TEXT,
            line_spacing=20
        )
        
        # 4. BOTÓN DE SALIDA (Volver al menú)
        prompt_str = "PRESIONA [ ENTER ] PARA REGRESAR AL MENÚ PRINCIPAL"
        if pygame.time.get_ticks() % 900 < 450:
            prompt_surf = self.font_ui.render(prompt_str, True, COLOR_UI_GOLD)
            surface.blit(prompt_surf, (px + pw // 2 - prompt_surf.get_width() // 2, py + ph - 38))

    def render_enemy_quiz_ui(self, surface, question, selected_idx, question_num, connection_offline=False):
        """Pinta la interfaz oscura del Enigma de las Sombras (encuentro con el enemigo)."""
        # 1. Overlay oscuro semi-transparente profundo
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((8, 5, 12, 225))
        surface.blit(overlay, (0, 0))
        
        # 2. Caja contenedora principal
        pw, ph = 740, 480
        px = (self.width - pw) // 2
        py = (self.height - ph) // 2
        
        panel_surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel_surf.fill((16, 12, 20, 245))
        # Borde morado oscuro misterioso
        pygame.draw.rect(panel_surf, (140, 30, 160), (0, 0, pw, ph), 2)
        pygame.draw.rect(panel_surf, (55, 20, 65), (4, 4, pw - 8, ph - 8), 1)
        surface.blit(panel_surf, (px, py))
        
        # Dibujar ilustración abstracta de ojos rojos del enemigo en el centro-top de la caja
        ex = px + pw // 2
        ey_eyes = py + 65
        # Bruma oscura
        pygame.draw.ellipse(surface, (25, 20, 32), (ex - 35, ey_eyes - 18, 70, 42))
        # Ojos
        pygame.draw.circle(surface, COLOR_SHADOW_EYES, (ex - 14, ey_eyes + 2), 5)
        pygame.draw.circle(surface, COLOR_SHADOW_EYES, (ex + 14, ey_eyes + 2), 5)
        # Pupilas rojas brillantes
        pygame.draw.circle(surface, (255, 255, 255), (ex - 14, ey_eyes + 2), 1.5)
        pygame.draw.circle(surface, (255, 255, 255), (ex + 14, ey_eyes + 2), 1.5)
        
        # Título
        title_text = f"ENIGMA DE LAS SOMBRAS: RETO {question_num} DE 3"
        title_surf = self.font_subtitle.render(title_text, True, COLOR_UI_GOLD)
        surface.blit(title_surf, (px + pw // 2 - title_surf.get_width() // 2, py + 120))
        
        # Subtítulo (Modo Oráculo/Offline)
        mode_str = "ORÁCULO OLLAMA ACTIVO" if not connection_offline else "MODO SIN CONEXIÓN - ACERTIJO ANCESTRAL"
        mode_surf = self.font_small.render(mode_str, True, (130, 100, 150) if connection_offline else (0, 200, 255))
        surface.blit(mode_surf, (px + pw // 2 - mode_surf.get_width() // 2, py + 152))
        
        pygame.draw.line(surface, (140, 30, 160), (px + 40, py + 175), (px + pw - 40, py + 175), 1)
        
        # Pregunta
        q_text = question.get("pregunta", "¿Qué responde el caballero ante la oscuridad?")
        self.draw_wrapped_text(
            surface,
            q_text,
            px + 50, py + 195,
            pw - 100,
            self.font_ui,
            COLOR_TEXT,
            line_spacing=22
        )
        
        # Opciones de respuesta
        options_y = py + 265
        for i, opt_text in enumerate(question.get("opciones", [])):
            is_selected = (i == selected_idx)
            
            # Caja para la opción
            opt_box_w = pw - 100
            opt_box_h = 42
            opt_box_x = px + 50
            opt_box_y = options_y + i * 52
            
            # Dibujar caja de opción
            box_color = (25, 18, 30) if not is_selected else (55, 25, 65)
            border_color = (65, 50, 80) if not is_selected else (190, 50, 220)
            
            pygame.draw.rect(surface, box_color, (opt_box_x, opt_box_y, opt_box_w, opt_box_h))
            pygame.draw.rect(surface, border_color, (opt_box_x, opt_box_y, opt_box_w, opt_box_h), 1 if not is_selected else 2)
            
            # Texto de la opción
            prefix = " > " if is_selected else "   "
            option_color = (255, 220, 255) if is_selected else COLOR_TEXT
            
            text_surf = self.font_ui.render(f"{prefix}{opt_text}", True, option_color)
            surface.blit(text_surf, (opt_box_x + 15, opt_box_y + 11))
            
        # Instrucciones de navegación
        info_text = "Navega con [ FLECHAS ] y confirma con [ ENTER ]"
        info_surf = self.font_small.render(info_text, True, COLOR_TEXT_MUTED)
        surface.blit(info_surf, (px + pw // 2 - info_surf.get_width() // 2, py + ph - 25))
