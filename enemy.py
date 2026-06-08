import pygame
import math
from config import PLAYER_SPEED

class Enemy:
    def __init__(self, col, row):
        # Posición lógica en la cuadrícula
        self.col = col
        self.row = row
        
        # Posición física interpolada para renderizado fluido
        self.current_col = float(col)
        self.current_row = float(row)
        
        # Animación oscilante (flotación en el aire)
        self.bob_time = 0.0
        self.bob_offset = 0.0
        self.bob_speed = 0.06
        self.bob_height = 4.0
        
        # Orientación ("up", "down", "left", "right")
        self.direction = "down"

    def move_towards(self, player_col, player_row, maze):
        """Calcula el siguiente paso usando BFS y mueve al enemigo una celda."""
        if self.col == player_col and self.row == player_row:
            return
            
        next_step = self.find_next_step((self.col, self.row), (player_col, player_row), maze)
        if next_step != (self.col, self.row):
            d_col = next_step[0] - self.col
            d_row = next_step[1] - self.row
            
            self.col = next_step[0]
            self.row = next_step[1]
            
            # Guardar la dirección para la orientación
            if d_col > 0:
                self.direction = "right"
            elif d_col < 0:
                self.direction = "left"
            elif d_row > 0:
                self.direction = "down"
            elif d_row < 0:
                self.direction = "up"

    def find_next_step(self, start, target, maze):
        """Búsqueda BFS de camino corto en cuadrícula transitable."""
        if start == target:
            return start
            
        queue = [[start]]
        visited = {start}
        
        while queue:
            path = queue.pop(0)
            curr = path[-1]
            
            if curr == target:
                return path[1] if len(path) > 1 else start
                
            cx, cy = curr
            # 4 direcciones cardinales
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = cx + dx, cy + dy
                if (nx, ny) not in visited and maze.is_walkable(nx, ny):
                    visited.add((nx, ny))
                    queue.append(path + [(nx, ny)])
                    
        return start

    def update(self):
        """Actualiza suavemente la interpolación física y la flotación."""
        # Lerp
        self.current_col += (self.col - self.current_col) * PLAYER_SPEED
        self.current_row += (self.row - self.current_row) * PLAYER_SPEED
        
        if abs(self.col - self.current_col) < 0.01:
            self.current_col = float(self.col)
        if abs(self.row - self.current_row) < 0.01:
            self.current_row = float(self.row)
            
        # Animación de flotación sinusoidal (espectro)
        self.bob_time += self.bob_speed
        self.bob_offset = math.sin(self.bob_time) * self.bob_height

    def reset(self, col, row):
        """Coloca al enemigo en una nueva celda y limpia estados."""
        self.col = col
        self.row = row
        self.current_col = float(col)
        self.current_row = float(row)
        self.bob_time = 0.0
        self.bob_offset = 0.0
        self.direction = "down"
