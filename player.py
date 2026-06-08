import pygame
import math
from config import PLAYER_SPEED, PLAYER_BOB_SPEED, PLAYER_BOB_HEIGHT

class Player:
    def __init__(self, col, row):
        # Posición lógica en la cuadrícula (destino)
        self.col = col
        self.row = row
        
        # Posición física interpolada (para dibujo suave)
        self.current_col = float(col)
        self.current_row = float(row)
        
        # Animación de respiración/flotación
        self.bob_time = 0.0
        self.bob_offset = 0.0
        
        # Dirección actual del jugador (para orientación de dibujo cenital)
        self.direction = "down"

    def move(self, d_col, d_row, maze):
        """Intenta mover al jugador en la cuadrícula en base a un diferencial."""
        # Solo permite iniciar otro movimiento si ya casi ha llegado al destino anterior
        if self.is_moving():
            return False
            
        target_col = self.col + d_col
        target_row = self.row + d_row
        
        if maze.is_walkable(target_col, target_row):
            self.col = target_col
            self.row = target_row
            
            # Guardar dirección cardinal clásica
            if d_col > 0:
                self.direction = "right"
            elif d_col < 0:
                self.direction = "left"
            elif d_row > 0:
                self.direction = "down"
            elif d_row < 0:
                self.direction = "up"
                
            return True
        return False

    def is_moving(self):
        """Devuelve True si el jugador se está desplazando entre celdas."""
        return (abs(self.col - self.current_col) > 0.01 or 
                abs(self.row - self.current_row) > 0.01)

    def update(self):
        # Interpolación lineal (Lerp) para movimiento fluido
        self.current_col += (self.col - self.current_col) * PLAYER_SPEED
        self.current_row += (self.row - self.current_row) * PLAYER_SPEED
        
        # Snap al destino si está muy cerca
        if abs(self.col - self.current_col) < 0.01:
            self.current_col = float(self.col)
        if abs(self.row - self.current_row) < 0.01:
            self.current_row = float(self.row)
            
        # Animación de respiración/flotación cenital
        self.bob_time += PLAYER_BOB_SPEED
        self.bob_offset = math.sin(self.bob_time) * PLAYER_BOB_HEIGHT

    def reset(self, col, row):
        """Reinicia la posición del jugador al iniciar un nuevo nivel."""
        self.col = col
        self.row = row
        self.current_col = float(col)
        self.current_row = float(row)
        self.bob_time = 0.0
        self.bob_offset = 0.0
        self.direction = "down"
