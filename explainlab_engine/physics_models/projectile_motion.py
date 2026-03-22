import sympy as sp
from .base_model import BaseModel
import math
from explainlab_engine.utils.latex_converter import sympy_to_katex, create_safe_equation

class ProjectileMotion(BaseModel):
    def solve(self, v0, angle_deg, gravity=9.8):
        t = sp.Symbol('t')
        angle_rad = math.radians(angle_deg)
        
        v0x = v0 * math.cos(angle_rad)
        v0y = v0 * math.sin(angle_rad)
        
        t_up = v0y / gravity
        h_max = (v0y**2) / (2 * gravity)
        t_flight = 2 * t_up
        range_x = v0x * t_flight
        
        steps = [
            {
                "step": 1, "title": "Decomposição da Velocidade Inicial",
                "text": f"O vetor v0 ({v0} m/s) é dividido nos eixos X (MRU) e Y (MRUV).",
                "equation_latex": rf"v_{{0x}} = v_0 \cos(\theta) = {v0x:.2f} \text{{ m/s}} \quad | \quad v_{{0y}} = v_0 \sin(\theta) = {v0y:.2f} \text{{ m/s}}"
            },
            {
                "step": 2, "title": "Análise Vertical (Eixo Y)",
                "text": f"A gravidade desacelera o objeto até o ápice (v_y=0) e depois o acelera para baixo. Altura máxima atingida em {t_up:.2f}s.",
                "equation_latex": rf"H_{{max}} = \frac{{v_{{0y}}^2}}{{2g}} = {h_max:.2f} \text{{ m}}"
            },
            {
                "step": 3, "title": "Análise Horizontal (Eixo X)",
                "text": f"Sem resistência do ar, a velocidade horizontal v_x permanece constante. O alcance total depende do tempo de voo ({t_flight:.2f}s).",
                "equation_latex": rf"R = v_{{0x}} \cdot t_{{voo}} = {v0x:.2f} \cdot {t_flight:.2f} = {range_x:.2f} \text{{ m}}"
            }
        ]
        
        num_frames = 60
        sim_duration = t_flight * 1.1 if t_flight > 0 else 1.0
        time_array = [round((sim_duration / num_frames) * i, 3) for i in range(num_frames + 1)]
        
        position_x_array = []
        position_y_array = []
        velocity_vx_array = []
        velocity_vy_array = []

        for t_val in time_array:
            pos_x = v0x * t_val
            vel_x = v0x
            pos_y = max(0.0, v0y * t_val - 0.5 * gravity * t_val**2)
            vel_y = v0y - gravity * t_val

            position_x_array.append(round(pos_x, 3))
            position_y_array.append(round(pos_y, 3))
            velocity_vx_array.append(round(vel_x, 3))
            velocity_vy_array.append(round(vel_y, 3))

        return {
            "model_detected": "Lançamento Oblíquo",
            "explanation_steps": steps,
            "simulation_data": {
                "type": "projectile_motion",
                "v0_m_s": v0,
                "angle_deg": angle_deg,
                "gravity_m_s2": gravity,
                "metrics": {
                    "h_max_m": round(h_max, 2),
                    "range_m": round(range_x, 2),
                    "flight_time_s": round(t_flight, 2),
                    "v0x_m_s": round(v0x, 2),
                    "v0y_m_s": round(v0y, 2)
                },
                "time_array": time_array,
                "position_x_array": position_x_array,
                "position_y_array": position_y_array,
                "velocity_vx_array": velocity_vx_array,
                "velocity_vy_array": velocity_vy_array
            }
        }