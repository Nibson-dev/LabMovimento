"""
vertical_motion_3d.py - Animação 3D de lançamento vertical
"""

import pygame
import math
from animations.geometry_3d import Sphere, Ground, Arrow, Vector3, project_3d_to_2d
from router import ModelRouter


class VerticalMotionSimulator:
    """Simulador 3D de lançamento vertical"""
    
    def __init__(self, y0=0, v0=15, g=9.8):
        self.y0 = y0
        self.v0 = v0
        self.g = g
        
        params = {"y0": y0, "v0": v0, "g": g, "t_final": 5.0}
        self.solution = ModelRouter.route("vertical_motion", params)
        
        sim_data = self.solution.get("simulation_data", {})
        self.time_array = sim_data.get("time_array", [0, 1, 2, 3, 4, 5])
        self.position_array = sim_data.get("position_y_array", [0, 5, 8, 9, 8, 5])
        self.velocity_array = sim_data.get("velocity_array", [15, 10, 5, 0, -5, -10])
        
        self.current_index = 0
        self.is_playing = True
        self.speed = 1.0
        
        self.sphere = Sphere(Vector3(0, self.position_array[0], 0), 0.3, color=(255, 100, 100))
        self.ground = Ground(size=8, color=(100, 200, 100))
        
        self.max_height = max(self.position_array) if self.position_array else 15
        self.trajectory = []
    
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
        
        if idx_floor < len(self.position_array) and idx_ceil < len(self.position_array):
            y_current = (self.position_array[idx_floor] * (1 - alpha) + 
                        self.position_array[idx_ceil] * alpha)
            
            v_current = (self.velocity_array[idx_floor] * (1 - alpha) + 
                        self.velocity_array[idx_ceil] * alpha)
            
            self.sphere.update(Vector3(0, y_current, 0))
            
            if len(self.trajectory) == 0 or \
               abs(self.trajectory[-1].y - y_current) > 0.3:
                self.trajectory.append(Vector3(0, y_current, 0))
            
            if len(self.trajectory) > 30:
                self.trajectory.pop(0)
    
    def draw(self, surface, screen_width=1200, screen_height=800):
        """Desenha a simulação"""
        surface.fill((20, 20, 40))
        
        self._draw_grid(surface, screen_width, screen_height)
        self.ground.draw(surface, scale=30, screen_width=screen_width, screen_height=screen_height)
        self._draw_trajectory(surface, screen_width, screen_height)
        self.sphere.draw(surface, scale=30, screen_width=screen_width, screen_height=screen_height)
        
        if len(self.velocity_array) > 0:
            idx_floor = int(self.current_index)
            if 0 <= idx_floor < len(self.velocity_array):
                v_current = self.velocity_array[idx_floor]
                velocity_arrow = Arrow(self.sphere.center, Vector3(0, v_current * 0.3, 0), 
                                     length=3, color=(0, 255, 0))
                velocity_arrow.draw(surface, scale=30, screen_width=screen_width, screen_height=screen_height)
        
        self._draw_hud(surface, screen_width, screen_height)
    
    def _draw_grid(self, surface, screen_width, screen_height):
        """Desenha uma grade de referência"""
        gray = (50, 50, 50)
        for i in range(-5, 6):
            p1 = project_3d_to_2d(Vector3(i, 0, -5), screen_width, screen_height, 30)
            p2 = project_3d_to_2d(Vector3(i, 0, 5), screen_width, screen_height, 30)
            pygame.draw.line(surface, gray, p1, p2, 1)
            
            p1 = project_3d_to_2d(Vector3(-5, 0, i), screen_width, screen_height, 30)
            p2 = project_3d_to_2d(Vector3(5, 0, i), screen_width, screen_height, 30)
            pygame.draw.line(surface, gray, p1, p2, 1)
    
    def _draw_trajectory(self, surface, screen_width, screen_height):
        """Desenha a trajetória como linhas"""
        if len(self.trajectory) < 2:
            return
        
        points_2d = [project_3d_to_2d(p, screen_width, screen_height, 30) for p in self.trajectory]
        
        for i in range(len(points_2d) - 1):
            pygame.draw.line(surface, (200, 100, 255), points_2d[i], points_2d[i+1], 2)
    
    def _draw_hud(self, surface, screen_width, screen_height):
        """Desenha informações na tela"""
        font = pygame.font.Font(None, 24)
        
        idx_floor = int(self.current_index)
        if 0 <= idx_floor < len(self.time_array):
            t = self.time_array[idx_floor]
            y = self.position_array[idx_floor] if idx_floor < len(self.position_array) else 0
            v = self.velocity_array[idx_floor] if idx_floor < len(self.velocity_array) else 0
            
            texts = [
                f"Tempo: {t:.2f}s",
                f"Altura: {y:.2f}m",
                f"Velocidade: {v:.2f}m/s",
                f"Altura Máxima: {self.max_height:.2f}m",
                f"Condições: y0={self.y0}m, v0={self.v0}m/s, g={self.g}m/s²",
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
                y_offset += 25
    
    def toggle_play(self):
        """Pausa/resume"""
        self.is_playing = not self.is_playing
    
    def reset(self):
        """Reseta a simulação"""
        self.current_index = 0
        self.trajectory = []
    
    def increase_speed(self):
        """Aumenta a velocidade de playback"""
        self.speed = min(self.speed + 0.5, 5.0)
    
    def decrease_speed(self):
        """Diminui a velocidade de playback"""
        self.speed = max(self.speed - 0.5, 0.1)
    
    def get_explanation_steps(self):
        """Retorna os passos da solução"""
        return self.solution.get("explanation_steps", [])