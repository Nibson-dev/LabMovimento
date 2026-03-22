import sympy as sp 
from .base_model import BaseModel
import math

class InclinedPlane(BaseModel):
    def solve(self, mass, angle, mu_s_val, mu_k_val, gravity=9.8):
        
        angle_rad = math.radians(angle)
        
        weight = mass * gravity
        normal_force = weight * math.cos(angle_rad)
        px = weight * math.sin(angle_rad)
        
        max_static_friction = mu_s_val * normal_force
        
        is_moving = px > max_static_friction
        
        if is_moving:
            friction_force = mu_k_val * normal_force
            net_force = px - friction_force
            acceleration = net_force / mass
            status_text = "A componente Px e maior que o atrito estatico maximo. O bloco desce acelerando."
        else:
            friction_force = px 
            net_force = 0.0
            acceleration = 0.0
            status_text = "A componente Px nao supera o atrito estatico. O bloco permanece em repouso."

        # ✅ EQUAÇÕES 100% SEGURAS
        eq1 = "P_x = P \\cdot \\sin(\\theta) = {:.2f}\\,\\mathrm{{N}} \\quad N = P \\cdot \\cos(\\theta) = {:.2f}\\,\\mathrm{{N}}".format(px, normal_force)
        
        eq2 = "F_{{at}} = mu \\cdot N = {:.2f}\\,\\mathrm{{N}}".format(friction_force)
        
        eq3 = "F_R = P_x - F_{{at}} = m \\cdot a \\Rightarrow a = {:.2f}\\,\\mathrm{{m/s^2}}".format(acceleration)

        steps = [
            {
                "step": 1,
                "title": "Decomposicao do Peso",
                "text": "O peso (P = mg) e decomposto nos eixos paralelo (Px) e perpendicular (Normal) a rampa.",
                "equation_latex": eq1
            },
            {
                "step": 2,
                "title": "Analise do Atrito",
                "text": f"Atrito estatico maximo: {max_static_friction:.2f}N. {status_text}",
                "equation_latex": eq2
            }
        ]
        
        if is_moving:
            steps.append({
                "step": 3,
                "title": "Segunda Lei de Newton",
                "text": "Calculamos a forca resultante e a aceleracao do bloco.",
                "equation_latex": eq3
            })

        ramp_length = 15.0
        num_frames = 60
        
        time_array = []
        position_s_array = []
        velocity_v_array = []
        
        if is_moving and acceleration > 0:
            total_time = math.sqrt((2 * ramp_length) / acceleration)
            time_array = [round((total_time / num_frames) * i, 3) for i in range(num_frames + 1)]
            
            for t in time_array:
                pos = 0.5 * acceleration * t**2
                vel = acceleration * t
                position_s_array.append(round(pos, 3))
                velocity_v_array.append(round(vel, 3))
        else:
            time_array = [0.0, 1.0, 2.0]
            position_s_array = [0.0, 0.0, 0.0]
            velocity_v_array = [0.0, 0.0, 0.0]

        return {
            "model_detected": "Plano Inclinado",
            "explanation_steps": steps,
            "simulation_data": {
                "type": "inclined_plane",
                "ramp_length_m": ramp_length,
                "angle_degrees": angle,
                "gravity_m_s2": gravity,
                "parameters": {
                    "mass": mass,
                    "gravity": gravity
                },
                "physics": {
                    "is_moving": is_moving,
                    "weight_N": round(weight, 2),
                    "normal_force_N": round(normal_force, 2),
                    "px_N": round(px, 2),
                    "friction_force_N": round(friction_force, 2),
                    "net_force_N": round(net_force, 2),
                    "acceleration_m_s2": round(acceleration, 2)
                },
                "time_array": time_array,
                "position_s_array": position_s_array,
                "velocity_v_array": velocity_v_array
            }
        }