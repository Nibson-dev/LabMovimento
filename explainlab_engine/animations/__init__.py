"""
animations - Módulo de simulações 3D com Pygame
"""

from .vertical_motion_3d import VerticalMotionSimulator
from .mruv_3d import MRUVSimulator
from .inclined_plane_3d import InclinedPlaneSimulator

__all__ = [
    'VerticalMotionSimulator',
    'MRUVSimulator',
    'InclinedPlaneSimulator'
]