"""
3d_objects.py - Classes para renderizar objetos 3D simples com Pygame
"""

import pygame
import math
import numpy as np


class Vector3:
    """Representa um ponto 3D"""
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def copy(self):
        return Vector3(self.x, self.y, self.z)


def project_3d_to_2d(point_3d, screen_width, screen_height, scale=30):
    """
    Projeta ponto 3D em 2D usando projeção isométrica
    """
    iso_x = (point_3d.x - point_3d.z) * scale
    iso_y = (point_3d.y - (point_3d.x + point_3d.z) * 0.5) * scale
    
    screen_x = screen_width // 2 + iso_x
    screen_y = screen_height // 2 + iso_y
    
    return (screen_x, screen_y)


class Sphere:
    """Esfera 3D"""
    def __init__(self, center, radius, color=(255, 100, 100)):
        self.center = center
        self.radius = radius
        self.color = color
    
    def update(self, new_center):
        self.center = new_center
    
    def draw(self, surface, scale=30, screen_width=1200, screen_height=800):
        pos_2d = project_3d_to_2d(self.center, screen_width, screen_height, scale)
        radius_2d = max(int(self.radius * scale * 0.7), 5)
        pygame.draw.circle(surface, self.color, pos_2d, radius_2d)
        
        highlight_pos = (pos_2d[0] - radius_2d // 3, pos_2d[1] - radius_2d // 3)
        pygame.draw.circle(surface, (255, 255, 255), highlight_pos, radius_2d // 3, 1)


class Cube:
    """Cubo 3D"""
    def __init__(self, center, size, color=(100, 150, 255)):
        self.center = center
        self.size = size
        self.color = color
    
    def get_vertices(self):
        """Retorna os 8 vértices do cubo"""
        s = self.size / 2
        return [
            self.center + Vector3(-s, -s, -s),
            self.center + Vector3(s, -s, -s),
            self.center + Vector3(s, s, -s),
            self.center + Vector3(-s, s, -s),
            self.center + Vector3(-s, -s, s),
            self.center + Vector3(s, -s, s),
            self.center + Vector3(s, s, s),
            self.center + Vector3(-s, s, s),
        ]
    
    def update(self, new_center):
        self.center = new_center
    
    def draw(self, surface, scale=30, screen_width=1200, screen_height=800):
        vertices = self.get_vertices()
        vertices_2d = [project_3d_to_2d(v, screen_width, screen_height, scale) for v in vertices]
        
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]
        
        for edge in edges:
            pygame.draw.line(surface, self.color, vertices_2d[edge[0]], vertices_2d[edge[1]], 2)
        
        face_points = [vertices_2d[0], vertices_2d[1], vertices_2d[2], vertices_2d[3]]
        pygame.draw.polygon(surface, self.color, face_points, 1)


class Ground:
    """Plano 3D (chão)"""
    def __init__(self, size=10, color=(100, 200, 100)):
        self.size = size
        self.color = color
    
    def draw(self, surface, scale=30, screen_width=1200, screen_height=800):
        corners = [
            Vector3(-self.size, 0, -self.size),
            Vector3(self.size, 0, -self.size),
            Vector3(self.size, 0, self.size),
            Vector3(-self.size, 0, self.size),
        ]
        
        corners_2d = [project_3d_to_2d(c, screen_width, screen_height, scale) for c in corners]
        pygame.draw.polygon(surface, self.color, corners_2d, 2)


class InclinedPlane:
    """Plano inclinado 3D"""
    def __init__(self, length=8, angle_deg=30, width=2, color=(150, 100, 50)):
        self.length = length
        self.angle_rad = math.radians(angle_deg)
        self.width = width
        self.color = color
    
    def get_plane_vertices(self):
        """Retorna os 4 vértices do plano inclinado"""
        start_x = -self.length / 2
        start_z = 0
        start_y = 0
        
        end_x = self.length / 2
        end_z = 0
        end_y = self.length * math.sin(self.angle_rad)
        
        w = self.width / 2
        
        return [
            Vector3(start_x, start_y, start_z - w),
            Vector3(end_x, end_y, end_z - w),
            Vector3(end_x, end_y, end_z + w),
            Vector3(start_x, start_y, start_z + w),
        ]
    
    def draw(self, surface, scale=30, screen_width=1200, screen_height=800):
        vertices = self.get_plane_vertices()
        vertices_2d = [project_3d_to_2d(v, screen_width, screen_height, scale) for v in vertices]
        
        pygame.draw.polygon(surface, self.color, vertices_2d, 2)
        pygame.draw.line(surface, self.color, vertices_2d[0], vertices_2d[1], 3)


class Arrow:
    """Seta para representar velocidade/aceleração"""
    def __init__(self, start, direction, length=2, color=(255, 0, 0)):
        self.start = start
        self.direction = direction.copy() if hasattr(direction, 'copy') else direction
        self.length = length
        self.color = color
    
    def draw(self, surface, scale=30, screen_width=1200, screen_height=800):
        mag = math.sqrt(self.direction.x**2 + self.direction.y**2 + self.direction.z**2)
        if mag < 0.001:
            return
        
        dir_normalized = Vector3(
            self.direction.x / mag,
            self.direction.y / mag,
            self.direction.z / mag
        )
        
        end = self.start + dir_normalized * self.length
        
        start_2d = project_3d_to_2d(self.start, screen_width, screen_height, scale)
        end_2d = project_3d_to_2d(end, screen_width, screen_height, scale)
        
        pygame.draw.line(surface, self.color, start_2d, end_2d, 3)
        
        arrow_size = 10
        dx = end_2d[0] - start_2d[0]
        dy = end_2d[1] - start_2d[1]
        
        if dx != 0 or dy != 0:
            angle = math.atan2(dy, dx)
            point1 = (end_2d[0] - arrow_size * math.cos(angle - math.pi/6),
                     end_2d[1] - arrow_size * math.sin(angle - math.pi/6))
            point2 = (end_2d[0] - arrow_size * math.cos(angle + math.pi/6),
                     end_2d[1] - arrow_size * math.sin(angle + math.pi/6))
            pygame.draw.polygon(surface, self.color, [end_2d, point1, point2])