import sympy as sp
from .base_model import BaseModel
import math

class InclinedPlane(BaseModel):
    # NOVIDADE: Adicionamos o gravity=9.8 aqui na porta de entrada!
    def solve(self, mass, angle, mu_s_val, mu_k_val, gravity=9.8):
        
        angle_rad = math.radians(angle)
        
        # 1. Decomposição de Forças (usando a gravidade customizada!)
        weight = mass * gravity
        normal_force = weight * math.cos(angle_rad)
        px = weight * math.sin(angle_rad)
        
        max_static_friction = mu_s_val * normal_force
        
        # 2. Verificação de Movimento
        is_moving = px > max_static_friction
        
        if is_moving:
            friction_force = mu_k_val * normal_force
            net_force = px - friction_force
            acceleration = net_force / mass
            status_text = "A componente Px é maior que o atrito estático máximo. O bloco desce acelerando."
        else:
            friction_force = px # Atrito iguala a força que tenta mover
            net_force = 0.0
            acceleration = 0.0
            status_text = "A componente Px não supera o atrito estático. O bloco permanece em repouso."

        # 3. Engenharia Reversa (LaTeX)
        steps = [
            {
                "step": 1, "title": "Decomposição do Peso",
                "text": f"O peso (P = mg = {weight:.2f}N) é decomposto nos eixos paralelo (Px) e perpendicular (Py/Normal) à rampa.",
                "equation_latex": f"P_x = P \\sin(\\theta) = {px:.2f}\\text{{ N}} \\quad | \\quad N = P \\cos(\\theta) = {normal_force:.2f}\\text{{ N}}"
            },
            {
                "step": 2, "title": "Análise do Atrito",
                "text": f"Atrito Estático Máximo: {max_static_friction:.2f}N. {status_text}",
                "equation_latex": f"F_{{at}} = \\mu N = {friction_force:.2f}\\text{{ N}}"
            }
        ]
        
        if is_moving:
            steps.append({
                "step": 3, "title": "Segunda Lei de Newton",
                "text": "Calculamos a força resultante e a aceleração do bloco.",
                "equation_latex": f"F_R = P_x - F_{{at}} = m \\cdot a \\Rightarrow {net_force:.2f} = {mass} \\cdot a \\Rightarrow a = {acceleration:.2f}\\text{{ m/s}}^2"
            })

        # 4. Arrays de Animação (Rampa padrão de 15 metros)
        ramp_length = 15.0
        num_frames = 60
        
        time_array = []
        position_s_array = []
        velocity_v_array = []
        
        if is_moving and acceleration > 0:
            # Descobrindo quanto tempo leva pra chegar no fim da rampa
            total_time = math.sqrt((2 * ramp_length) / acceleration)
            time_array = [round((total_time / num_frames) * i, 3) for i in range(num_frames + 1)]
            
            for t in time_array:
                pos = 0.5 * acceleration * t**2
                vel = acceleration * t
                position_s_array.append(round(pos, 3))
                velocity_v_array.append(round(vel, 3))
        else:
            # Se não se mover, fica parado o tempo todo
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