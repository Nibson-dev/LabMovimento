import sympy as sp
from .base_model import BaseModel
import math

class VerticalMotion(BaseModel):
    def solve(self, y0, v0, gravity=9.8):
        t = sp.Symbol('t')
        
        # 1. Equações
        eq_pos = y0 + v0 * t - 0.5 * gravity * t**2
        
        # 2. Tempo de Voo (Bhaskara)
        a = -0.5 * gravity
        b = v0
        c = y0
        delta = b**2 - 4 * a * c
        
        if delta < 0:
            flight_time = 0.0
        else:
            t1 = (-b + math.sqrt(delta)) / (2 * a)
            t2 = (-b - math.sqrt(delta)) / (2 * a)
            flight_time = max(t1, t2)
            
        # 3. Ápice
        if v0 > 0:
            t_up = v0 / gravity
            max_h = y0 + (v0**2) / (2 * gravity)
        else:
            t_up = 0.0
            max_h = y0
            
        # 4. Passos para o Frontend
        steps = [
            {
                "step": 1, "title": "Equação da Trajetória",
                "text": "O movimento é um MRUV sob ação exclusiva da gravidade.",
                "equation_latex": f"y(t) = y_0 + v_0 t - \\frac{{g t^2}}{{2}} = {y0} + {v0}t - {0.5*gravity}t^2"
            },
            {
                "step": 2, "title": "Equação da Velocidade",
                "text": "A velocidade é a derivada da posição. Ela inverte o sentido no topo.",
                "equation_latex": f"v(t) = v_0 - gt = {v0} - {gravity}t"
            },
            {
                "step": 3, "title": "Análise de Ápice (H_max)",
                "text": "O projétil atinge a altura máxima quando v(t) = 0.",
                "equation_latex": f"t_{{subida}} = {t_up:.2f}\\text{{ s}} \\quad \\Rightarrow \\quad H_{{max}} = {max_h:.2f}\\text{{ m}}"
            }
        ]
        
        # 5. Arrays de Animação
        num_frames = 40
        if flight_time <= 0:
            time_array = [0, 1, 2]
            position_y_array = [y0, y0, y0]
            velocity_v_array = [0, 0, 0]
        else:
            time_array = [round((flight_time / num_frames) * i, 3) for i in range(num_frames + 1)]
            position_y_array = [max(0.0, round(y0 + v0 * t_val - 0.5 * gravity * t_val**2, 3)) for t_val in time_array]
            velocity_v_array = [round(v0 - gravity * t_val, 3) for t_val in time_array]

        return {
            "model_detected": "Lançamento Vertical",
            "explanation_steps": steps,
            "simulation_data": {
                "type": "vertical_motion",
                "max_height_m": round(max_h, 2),
                "flight_time_s": round(flight_time, 2),
                "time_up_s": round(t_up, 2),
                "gravity_m_s2": gravity,
                "time_array": time_array,
                "position_y_array": position_y_array,
                "velocity_v_array": velocity_v_array
            }
        }