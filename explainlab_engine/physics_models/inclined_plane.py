import math
from typing import Dict, Any

class InclinedPlane:
    """Simulação de plano inclinado com atrito. LaTeX elegante e nativo."""
    
    def solve(self, mass: float, angle: float, mu_s_val: float, mu_k_val: float, gravity: float = 9.8) -> Dict[str, Any]:
        
        angle_rad = math.radians(angle)
        
        # ========== FÍSICA ==========
        weight = mass * gravity
        normal_force = weight * math.cos(angle_rad)
        px = weight * math.sin(angle_rad)
        
        max_static_friction = mu_s_val * normal_force
        is_moving = px > max_static_friction
        
        if is_moving:
            friction_force = mu_k_val * normal_force
            net_force = px - friction_force
            acceleration = net_force / mass
            status_text = "A componente Px supera o atrito estático máximo. O bloco desce acelerando."
        else:
            friction_force = px
            net_force = 0.0
            acceleration = 0.0
            status_text = "A componente Px não supera o atrito estático. O bloco permanece em repouso."
        
        # ========== EQUAÇÕES (PADRÃO OURO LATEX) ==========
        eq1_text = rf"P = {weight:.2f} \, \mathrm{{N}} \quad P_x = {px:.2f} \, \mathrm{{N}} \quad N = {normal_force:.2f} \, \mathrm{{N}}"
        
        eq2_text = rf"F_{{at,max}} = \mu_s \cdot N = {mu_s_val} \cdot {normal_force:.2f} = {max_static_friction:.2f} \, \mathrm{{N}}"
        
        if is_moving:
            eq3_text = rf"P_x > F_{{at,max}} \quad \Rightarrow \quad {px:.2f} > {max_static_friction:.2f}"
            eq4_text = rf"a = \frac{{P_x - F_{{at}}}}{{m}} = \frac{{{px:.2f} - {friction_force:.2f}}}{{{mass}}} = {acceleration:.2f} \, \mathrm{{m/s^2}}"
        else:
            eq3_text = rf"P_x \leq F_{{at,max}} \quad \Rightarrow \quad {px:.2f} \leq {max_static_friction:.2f}"
            eq4_text = rf"a = 0 \, \mathrm{{m/s^2}}"
        
        # ========== BUILD STEPS ==========
        steps = [
            {"step": 1, "title": "Decomposição do Peso", "text": f"O peso total é {weight:.2f} N. Decomposto em componentes paralela (Px) e normal (N).", "equation_latex": eq1_text},
            {"step": 2, "title": "Limite de Atrito Estático", "text": f"Atrito estático máximo possível: {max_static_friction:.2f} N. Agora comparamos com Px.", "equation_latex": eq2_text},
            {"step": 3, "title": "Análise de Movimento", "text": status_text, "equation_latex": eq3_text}
        ]
        
        if is_moving:
            steps.append({"step": 4, "title": "Segunda Lei de Newton", "text": "Como a força de descida supera o atrito, o bloco acelera.", "equation_latex": eq4_text})
        
        # ========== SIMULAÇÃO ==========
        ramp_length = 15.0
        num_frames = 60
        time_array, position_s_array, velocity_v_array = [], [], []
        
        if is_moving and acceleration > 0:
            total_time = math.sqrt((2 * ramp_length) / acceleration)
            time_array = [round((total_time / num_frames) * i, 3) for i in range(num_frames + 1)]
            for t in time_array:
                position_s_array.append(round(0.5 * acceleration * t**2, 3))
                velocity_v_array.append(round(acceleration * t, 3))
        else:
            time_array, position_s_array, velocity_v_array = [0.0, 1.0, 2.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]
        
        return {
            "model_detected": "Plano Inclinado",
            "explanation_steps": steps,
            "simulation_data": {
                "type": "inclined_plane", "ramp_length_m": ramp_length, "angle_degrees": angle, "gravity_m_s2": gravity,
                "parameters": {"mass": mass, "gravity": gravity, "mu_s": mu_s_val, "mu_k": mu_k_val},
                "physics": {"is_moving": is_moving, "weight_N": round(weight, 2), "normal_force_N": round(normal_force, 2), "px_N": round(px, 2), "friction_force_N": round(friction_force, 2), "net_force_N": round(net_force, 2), "acceleration_m_s2": round(acceleration, 2), "max_static_friction_N": round(max_static_friction, 2)},
                "time_array": time_array, "position_s_array": position_s_array, "velocity_v_array": velocity_v_array
            }
        }