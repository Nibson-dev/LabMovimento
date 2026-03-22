import math
from .base_model import BaseModel

class ProjectileMotion(BaseModel):
    def solve(self, v0, angle_deg, gravity=9.8):
        angle_rad = math.radians(angle_deg)
        v0x = v0 * math.cos(angle_rad)
        v0y = v0 * math.sin(angle_rad)
        
        t_up = v0y / gravity
        h_max = (v0y**2) / (2 * gravity)
        t_flight = 2 * t_up
        range_x = v0x * t_flight
        
        # EQUAÇÕES BLINDADAS (Unicode para vetores)
        steps = [
            {
                "step": 1, "title": "Decomposição da Velocidade",
                "text": f"Velocidade de {v0} m/s decomposta nos eixos X e Y.",
                "equation_latex": f"v0x = v0~cos(θ) = {v0x:.2f}~m/s   |   v0y = v0~sin(θ) = {v0y:.2f}~m/s"
            },
            {
                "step": 2, "title": "Análise Vertical (Eixo Y)",
                "text": f"Altura máxima atingida em {t_up:.2f}s.",
                "equation_latex": f"H_max = (v0y²) / 2g = {h_max:.2f}~m"
            },
            {
                "step": 3, "title": "Análise Horizontal (Eixo X)",
                "text": f"Alcance total baseado no tempo de voo ({t_flight:.2f}s).",
                "equation_latex": f"R = v0x * t_voo = {v0x:.2f} * {t_flight:.2f} = {range_x:.2f}~m"
            }
        ]
        
        # Geração de dados
        num_frames = 60
        sim_duration = t_flight * 1.1 if t_flight > 0 else 1.0
        time_array = [round((sim_duration / num_frames) * i, 3) for i in range(num_frames + 1)]
        
        pos_x = [round(v0x * t, 3) for t in time_array]
        pos_y = [round(max(0.0, v0y * t - 0.5 * gravity * t**2), 3) for t in time_array]

        return {
            "model_detected": "Lançamento Oblíquo",
            "explanation_steps": steps,
            "simulation_data": {
                "type": "projectile_motion",
                "metrics": {
                    "h_max_m": round(h_max, 2),
                    "range_m": round(range_x, 2),
                    "flight_time_s": round(t_flight, 2),
                    "v0x_m_s": round(v0x, 2),
                    "v0y_m_s": round(v0y, 2)
                },
                "time_array": time_array,
                "position_x_array": pos_x,
                "position_y_array": pos_y
            }
        }