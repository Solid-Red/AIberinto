import random
from config import CELL_FLOOR, CELL_WALL, CELL_START, CELL_EXIT

class Maze:
    def __init__(self, width=9, height=9):
        # Asegurar que el tamaño sea impar para el algoritmo de tallado
        self.width = width if width % 2 != 0 else width + 1
        self.height = height if height % 2 != 0 else height + 1
        self.grid = []
        self.start_pos = (1, 1)
        self.exit_pos = (self.width - 2, self.height - 2)
        self.generate()
        self.generate_floor_types()

    def generate(self):
        # 1. Inicializar toda la cuadrícula con muros (1)
        self.grid = [[CELL_WALL for _ in range(self.width)] for _ in range(self.height)]
        
        # 2. Algoritmo DFS (Depth-First Search) con Backtracking
        stack = []
        start_x, start_y = 1, 1
        self.grid[start_y][start_x] = CELL_FLOOR
        stack.append((start_x, start_y))
        
        visited_count = 1
        # Número total de celdas "habitación" (coordenadas impares)
        total_rooms = ((self.width - 1) // 2) * ((self.height - 1) // 2)

        while stack:
            cx, cy = stack[-1]
            
            # Buscar vecinos no visitados a distancia 2
            neighbors = []
            directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
            
            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy
                if 0 < nx < self.width - 1 and 0 < ny < self.height - 1:
                    if self.grid[ny][nx] == CELL_WALL:
                        neighbors.append((nx, ny, dx // 2, dy // 2))
            
            if neighbors:
                # Elegir un vecino aleatorio
                nx, ny, dx, dy = random.choice(neighbors)
                
                # Derribar el muro entre el actual y el vecino
                self.grid[cy + dy][cx + dx] = CELL_FLOOR
                # Marcar el vecino como camino
                self.grid[ny][nx] = CELL_FLOOR
                
                stack.append((nx, ny))
            else:
                # Retroceder si no hay vecinos
                stack.pop()
                
        # 3. Establecer posiciones de inicio y salida
        self.start_pos = (1, 1)
        self.grid[self.start_pos[1]][self.start_pos[0]] = CELL_START
        
        self.exit_pos = (self.width - 2, self.height - 2)
        self.grid[self.exit_pos[1]][self.exit_pos[0]] = CELL_EXIT

    def is_walkable(self, col, row):
        """Devuelve True si la celda es transitable (suelo, inicio o salida)."""
        if 0 <= col < self.width and 0 <= row < self.height:
            return self.grid[row][col] != CELL_WALL
        return False

    def get_cell(self, col, row):
        """Obtiene el tipo de celda en una coordenada determinada."""
        if 0 <= col < self.width and 0 <= row < self.height:
            return self.grid[row][col]
        return CELL_WALL

    def generate_floor_types(self):
        """Genera zonas orgánicas de tierra y piedra en base a centros aleatorios."""
        self.floor_types = {}
        # Elegir centros de zonas de tierra (en proporción al tamaño)
        num_dirt_centers = max(2, (self.width * self.height) // 40)
        dirt_centers = []
        for _ in range(num_dirt_centers):
            rx = random.randint(1, self.width - 2)
            ry = random.randint(1, self.height - 2)
            dirt_centers.append((rx, ry))
            
        for r in range(self.height):
            for c in range(self.width):
                if self.grid[r][c] != CELL_WALL:
                    is_dirt = False
                    for dc_x, dc_y in dirt_centers:
                        # Distancia Manhattan
                        dist = abs(c - dc_x) + abs(r - dc_y)
                        if dist <= 2.2:  # Radio del cúmulo de tierra
                            is_dirt = True
                            break
                    self.floor_types[(c, r)] = 'dirt' if is_dirt else 'stone'
