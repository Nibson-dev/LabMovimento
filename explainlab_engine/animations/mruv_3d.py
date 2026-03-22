"""
mruv_3d.py - Animação 3D de MRUV
"""

import pygame
import math
from animations.geometry_3d import Cube, Ground, Arrow, Vector3, project_3d_to_2d
from router import ModelRouter


class MRUVSimulator:
    """Simulador 3D de MRUV"""
    
    def __init__(self, s0=0, v0=0, a=2, t_final=10):
        self.s0 = s0
        self.v0 = v0
        self.a = a
        self.t_final = t_final
        
        params = {"s0": s0, "v0": v0, "a": a, "t_final": t_final}
        self.solution = ModelRouter.route("mruv", params)
        
        sim_data = self.solution.get("simulation_data", {})
        self.time_array = sim_data.get("time_array", [i for i in range(int(t_final)+1)])
        self.position_array = sim_data.get("position_array", 
                                          [s0 + v0*t + 0.5*a*t**2 for t in self.time_array])
        self.velocity_array = sim_data.get("velocity_array", 
                                          [v0 + a*t for t in self.time_array])
        
        self.current_index = 0
        self.is_playing = True
        self.speed = 1.0
        
        self.car = Cube(Vector3(self.position_array[0] - 5, 0.5, 0), 0.8, color=(255, 100, 100))
        self.ground = Ground(size=20, color=(100, 200, 100))
        
        self.trajectory = []
        self.max_position = max(self.position_array) if self.position_array else 50
    
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
            s_current = (self.position_array[idx_floor] * (1 - alpha) + 
                        self.position_array[idx_ceil] * alpha)
            
            v_current = (self.velocity_array[idx_floor] * (1 - alpha) + 
                        self.velocity_array[idx_ceil] * alpha)
            
            self.car.update(Vector3(s_current - 5, 0.5, 0))
            
            if len(self.trajectory) == 0 or \
               abs(self.trajectory[-1].x - s_current) > 0.2:
                self.trajectory.append(Vector3(s_current - 5, 0.5, 0))
            
            if len(self.trajectory) > 50:
                self.trajectory.pop(0)
    
    def draw(self, surface, screen_width=1200, screen_height=800):
        """Desenha a simulação"""
        surface.fill((20, 20, 40))
        
        self._draw_grid(surface, screen_width, screen_height)
        self.ground.draw(surface, scale=30, screen_width=screen_width, screen_height=screen_height)
        self._draw_trajectory(surface, screen_width, screen_height)
        self.car.draw(surface, scale=30, screen_width=screen_width, screen_height=screen_height)
        
        idx_floor = int(self.current_index)
        if 0 <= idx_floor < len(self.velocity_array):
            v_current = self.velocity_array[idx_floor]
            velocity_arrow = Arrow(self.car.center, Vector3(v_current * 0.15, 0, 0),
                                 length=3, color=(0, 255, 0))
            velocity_arrow.draw(surface, scale=30, screen_width=screen_width, screen_height=screen_height)
        
        self._draw_hud(surface, screen_width, screen_height)
    
    def _draw_grid(self, surface, screen_width, screen_height):
        """Grade de referência"""
        gray = (50, 50, 50)
        for i in range(-10, 11, 2):
            p1 = project_3d_to_2d(Vector3(i, 0, -5), screen_width, screen_height, 30)
            p2 = project_3d_to_2d(Vector3(i, 0, 5), screen_width, screen_height, 30)
            pygame.draw.line(surface, gray, p1, p2, 1)
    
    def _draw_trajectory(self, surface, screen_width, screen_height):
        """Trajetória como linhas"""
        if len(self.trajectory) < 2:
            return
        
        points_2d = [project_3d_to_2d(p, screen_width, screen_height, 30) for p in self.trajectory]
        
        for i in range(len(points_2d) - 1):
            pygame.draw.line(surface, (200, 100, 255), points_2d[i], points_2d[i+1], 2)
    
    def _draw_hud(self, surface, screen_width, screen_height):
        """Informações na tela"""
        font = pygame.font.Font(None, 24)
        
        idx_floor = int(self.current_index)
        if 0 <= idx_floor < len(self.time_array):
            t = self.time_array[idx_floor]
            s = self.position_array[idx_floor] if idx_floor < len(self.position_array) else 0
            v = self.velocity_array[idx_floor] if idx_floor < len(self.velocity_array) else 0
            
            texts = [
                f"Tempo: {t:.2f}s",
                f"Posição: {s:.2f}m",
                f"Velocidade: {v:.2f}m/s",
                f"Aceleração: {self.a:.2f}m/s²",
                f"Condições: s0={self.s0}m, v0={self.v0}m/s, a={self.a}m/s²",
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