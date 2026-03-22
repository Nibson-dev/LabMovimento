import math
from .base_model import BaseModel

class VerticalMotion(BaseModel):
    def solve(self, y0, v0, gravity=9.8):
        # Lógica de Báscara (Mantendo seu código original)
        a_quad = -0.5 * gravity
        delta = v0**2 - 4 * a_quad * y0
        flight_time = (-v0 - math.sqrt(delta)) / (2 * a_quad) if delta >= 0 else 0.0
            
        t_up = max(0.0, v0 / gravity) if v0 > 0 else 0.0
        max_h = y0 + (v0**2 / (2 * gravity)) if v0 > 0 else y0
            
        # EQUAÇÕES BLINDADAS
        steps = [
            {
                "step": 1, "title": "Equação da Trajetória",
                "text": "Movimento vertical sob ação da gravidade.",
                "equation_latex": f"y(t) = y0 + v0~t - (g~t²) / 2 = {y0} + {v0}t - {0.5*gravity}t²"
            },
            {
                "step": 2, "title": "Equação da Velocidade",
                "text": "A velocidade diminui até o topo (v=0).",
                "equation_latex": f"v(t) = v0 - gt = {v0} - {gravity}t"
            },
            {
                "step": 3, "title": "Cálculo do Ápice",
                "text": f"Altura máxima em t = {t_up:.2f}s.",
                "equation_latex": f"t_subida = {t_up:.2f}~s   =>   H_max = {max_h:.2f}~m"
            }
        ]
        
        num_frames = 40
        time_array = [round((flight_time / num_frames) * i, 3) for i in range(num_frames + 1)]
        pos_y = [round(max(0.0, y0 + v0 * t - 0.5 * gravity * t**2), 3) for t in time_array]

        return {
            "model_detected": "Lançamento Vertical",
            "explanation_steps": steps,
            "simulation_data": {
                "type": "vertical_motion",
                "max_height_m": round(max_h, 2),
                "flight_time_s": round(flight_time, 2),
                "time_array": time_array,
                "position_y_array": pos_y
            }
        }