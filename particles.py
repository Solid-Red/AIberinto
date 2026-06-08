import pygame
import random
import math

class Particle:
    def __init__(self, x, y, vx, vy, color, size, decay, gravity=0.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.initial_size = size
        self.size = size
        self.life = 1.0  # Va de 1.0 (nacimiento) a 0.0 (muerte)
        self.decay = decay  # Cuánto disminuye la vida por frame
        self.gravity = gravity

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= self.decay
        self.size = max(0, self.initial_size * self.life)
        return self.life > 0

    def draw(self, surface):
        if self.size <= 0:
            return
        
        # Para partículas de fuego/brillo, multiplicamos color por vida útil
        alpha_color = [max(0, min(255, int(c * self.life))) for c in self.color]
        
        try:
            # Dibujar núcleo
            pygame.draw.circle(surface, alpha_color, (int(self.x), int(self.y)), int(self.size))
            if self.size > 2 and self.color != (80, 78, 82): # No brilla para el humo
                # Centro brillante caliente (blanco/amarillo claro)
                pygame.draw.circle(surface, (255, 255, 200), (int(self.x), int(self.y)), int(self.size * 0.4))
        except (TypeError, ValueError):
            pass

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit_torch(self, x, y):
        """Emite chispas de fuego y humo provenientes de la antorcha del caballero."""
        # 1. Partícula de Fuego (Naranja, Amarillo, Rojo)
        color = random.choice([
            (245, 120, 10),  # Naranja
            (255, 210, 40),  # Amarillo
            (210, 40, 10)    # Rojo fuego
        ])
        vx = random.uniform(-0.4, 0.4)
        vy = random.uniform(-1.0, -0.4)  # Sube
        size = random.uniform(3, 5)
        decay = random.uniform(0.04, 0.08)
        self.particles.append(Particle(x, y, vx, vy, color, size, decay, gravity=-0.01))
        
        # 2. Partícula de Humo (Ocasional, gris/oscuro)
        if random.random() < 0.25:
            smoke_color = (80, 78, 82)
            svx = random.uniform(-0.2, 0.2)
            svy = random.uniform(-0.8, -0.3)
            ssize = random.uniform(4, 7)
            sdecay = random.uniform(0.02, 0.04)
            self.particles.append(Particle(x, y - 2, svx, svy, smoke_color, ssize, sdecay, gravity=-0.015))

    def emit_gold_sparkles(self, x, y):
        """Emite destellos dorados que suben desde el cofre del tesoro."""
        offset_x = random.uniform(-15, 15)
        offset_y = random.uniform(-8, 8)
        vx = random.uniform(-0.3, 0.3)
        vy = random.uniform(-0.8, -0.2)
        color = (240, 190, 20)  # Oro brillante
        size = random.uniform(2.5, 4.5)
        decay = random.uniform(0.02, 0.04)
        self.particles.append(Particle(x + offset_x, y + offset_y, vx, vy, color, size, decay, gravity=-0.01))

    def emit_burst(self, x, y, color, count=40):
        """Emite una explosión circular de chispas (ej. al abrir el cofre)."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1.2, 3.5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            size = random.uniform(4, 8)
            decay = random.uniform(0.015, 0.03)
            self.particles.append(Particle(x, y, vx, vy, color, size, decay, gravity=0.03))

    def update(self):
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

    def clear(self):
        self.particles.clear()
