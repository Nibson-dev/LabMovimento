"""
inclined_plane_3d.py - Animação 3D de plano inclinado
"""

import pygame
import math
from animations.geometry_3d import Cube, InclinedPlane, Arrow, Vector3, project_3d_to_2d
from router import ModelRouter


class InclinedPlaneSimulator:
    """Simulador 3D de plano inclinado"""
    
    def __init__(self, m=5, theta=30, g=9.8, mu=0):
        self.m = m
        self.theta = theta
        self.theta_rad = math.radians(theta)
        self.g = g
        self.mu = mu
        
        params = {"m": m, "theta": theta, "g": g}
        self.solution = ModelRouter.route("inclined_plane", params)
        
        self.P = m * g
        self.Px = self.P * math.sin(self.theta_rad)
        self.Py = self.P * math.cos(self.theta_rad)
        self.N = self.Py
        
        self.f_atrito = mu * self.N if mu > 0 else 0
        self.a = (self.Px - self.f_atrito) / m if m > 0 else 0
        
        self.plano_length = 8
        t_final = 5.0
        
        self.time_array = [i * 0.1 for i in range(int(t_final * 10))]
        self.distance_array = [0.5 * self.a * t**2 for t in self.time_array]
        self.distance_array = [min(d, self.plano_length) for d in self.distance_array]
        self.velocity_array = [self.a * t for t in self.time_array]
        
        self.current_index = 0
        self.is_playing = True
        self.speed = 1.0
        
        self.inclined_plane = InclinedPlane(length=self.plano_length, angle_deg=theta, 
                                           width=2, color=(150, 100, 50))
        
        start_pos = self._get_block_position(0)
        self.block = Cube(start_pos, 0.5, color=(100, 150, 255))
        
        self.trajectory = []
    
    def _get_block_position(self, distance):
        """Calcula a posição 3D do bloco dado a distância ao longo do plano"""
        ratio = distance / self.plano_length
        
        x = -self.plano_length / 2 + distance
        y = distance * math.sin(self.theta_rad)
        z = 0
        
        return Vector3(x, y, z)
    
    def update(self, dt):
        """Atualiza a simulação"""
        if not self.is_playing or len(self.time_array) < 2:
            return
        
        self.current_index += dt * self.speed * 5
        
        if self.current_index >= len(self.time_array) - 1:
            self.current_index = 0
            self.trajectory = []
        
        idx_floor = int(self.current_index)
        idx_ceil = min(idx_floor + 1, len(self.time_array) - 1)
        alpha = self.current_index - idx_floor
        
        if idx_floor < len(self.distance_array) and idx_ceil < len(self.distance_array):
            d_current = (self.distance_array[idx_floor] * (1 - alpha) + 
                        self.distance_array[idx_ceil] * alpha)
            
            block_pos = self._get_block_position(d_current)
            self.block.update(block_pos)
            
            if len(self.trajectory) == 0 or \
               abs(self.trajectory[-1].x - block_pos.x) > 0.1:
                self.trajectory.append(Vector3(block_pos.x, block_pos.y, block_pos.z))
            
            if len(self.trajectory) > 40:
                self.trajectory.pop(0)
    
    def draw(self, surface, screen_width=1200, screen_height=800):
        """Desenha a simulação"""
        surface.fill((20, 20, 40))
        
        self._draw_grid(surface, screen_width, screen_height)
        self.inclined_plane.draw(surface, scale=30, screen_width=screen_width, 
                                screen_height=screen_height)
        self._draw_trajectory(surface, screen_width, screen_height)
        self.block.draw(surface, scale=30, screen_width=screen_width, screen_height=screen_height)
        self._draw_forces(surface, screen_width, screen_height)
        self._draw_hud(surface, screen_width, screen_height)
    
    def _draw_grid(self, surface, screen_width, screen_height):
        """Grade de referência"""
        gray = (50, 50, 50)
        for i in range(-10, 11, 2):
            p1 = project_3d_to_2d(Vector3(i, 0, -5), screen_width, screen_height, 30)
            p2 = project_3d_to_2d(Vector3(i, 0, 5), screen_width, screen_height, 30)
            pygame.draw.line(surface, gray, p1, p2, 1)
    
    def _draw_trajectory(self, surface, screen_width, screen_height):
        """Traço do movimento"""
        if len(self.trajectory) < 2:
            return
        
        points_2d = [project_3d_to_2d(p, screen_width, screen_height, 30) for p in self.trajectory]
        
        for i in range(len(points_2d) - 1):
            pygame.draw.line(surface, (200, 100, 255), points_2d[i], points_2d[i+1], 2)
    
    def _draw_forces(self, surface, screen_width, screen_height):
        """Desenha os vetores de força"""
        block_center = self.block.center
        
        peso_arrow = Arrow(block_center, Vector3(0, -self.m * 0.5, 0), length=3, color=(255, 0, 0))
        peso_arrow.draw(surface, scale=30, screen_width=screen_width, screen_height=screen_height)
        
        normal_x = -math.sin(self.theta_rad)
        normal_y = math.cos(self.theta_rad)
        normal_arrow = Arrow(block_center, Vector3(normal_x * 2, normal_y * 2, 0), 
                           length=2, color=(0, 0, 255))
        normal_arrow.draw(surface, scale=30, screen_width=screen_width, screen_height=screen_height)
    
    def _draw_hud(self, surface, screen_width, screen_height):
        """Informações na tela"""
        font = pygame.font.Font(None, 24)
        
        idx_floor = int(self.current_index)
        if 0 <= idx_floor < len(self.time_array):
            t = self.time_array[idx_floor]
            d = self.distance_array[idx_floor] if idx_floor < len(self.distance_array) else 0
            v = self.velocity_array[idx_floor] if idx_floor < len(self.velocity_array) else 0
            
            texts = [
                f"Tempo: {t:.2f}s",
                f"Distância ao longo do plano: {d:.2f}m",
                f"Velocidade: {v:.2f}m/s",
                "",
                f"PARÂMETROS:",
                f"Massa: {self.m:.2f}kg",
                f"Ângulo: {self.theta:.1f}°",
                f"Gravidade: {self.g:.2f}m/s²",
                f"Coef. Atrito: {self.mu:.2f}",
                "",
                f"FORÇAS:",
                f"Peso: {self.P:.2f}N",
                f"Px (paralela): {self.Px:.2f}N",
                f"Py (perpendicular): {self.Py:.2f}N",
                f"Normal: {self.N:.2f}N",
                f"Atrito: {self.f_atrito:.2f}N",
                f"Aceleração: {self.a:.2f}m/s²",
                "",
                "CONTROLES:",
                "[SPACE] Play/Pause",
                "[R] Reset",
                "[+] Aumentar velocidade",
                "[-] Diminuir velocidade",
                "[Q] Sair"
            ]
            
            y_offset = 20
            for text in texts:
                text_surface = font.render(text, True, (255, 255, 255))
                surface.blit(text_surface, (20, y_offset))
                y_offset += 22
    
    def toggle_play(self):
        self.is_playing = not self.is_playing
    
    def reset(self):
        self.current_index = 0
        self.trajectory = []
    
    def increase_speed(self):
        self.speed = min(self.speed + 0.5, 5.0)
    
    def decrease_speed(self):
        self.speed = max(self.speed - 0.5, 0.1)
    
    def get_explanation_steps(self):
        return self.solution.get("explanation_steps", [])