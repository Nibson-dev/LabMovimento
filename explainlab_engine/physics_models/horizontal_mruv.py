import sympy as sp
from .base_model import BaseModel

class HorizontalMRUV(BaseModel):
    def solve(self, s0, v0, a):
        # Lógica de status
        stop_time = 0.0
        will_stop = False
        
        if (v0 > 0 and a < 0) or (v0 < 0 and a > 0):
            will_stop = True
            stop_time = -v0 / a
            stop_pos = s0 + v0 * stop_time + 0.5 * a * stop_time**2
            status = "Movimento Retardado (Freando)."
        elif a == 0:
             status = "Movimento Retilíneo Uniforme (MRU)."
             stop_pos = None
        else:
            status = "Movimento Acelerado."
            stop_pos = None

        # EQUAÇÕES BLINDADAS (Sem barras invertidas complexas)
        eq_pos_latex = f"S(t) = {s0} + {v0}t + {0.5*a:.2f}t²"
        eq_vel_latex = f"v(t) = {v0} + {a}t"

        steps = [
            {
                "step": 1, "title": "Funções Horárias do MRUV",
                "text": f"O movimento tem S0={s0}m, v0={v0}m/s e a={a}m/s². {status}",
                "equation_latex": f"S(t) = S0 + v0~t + (at²) / 2   =>   {eq_pos_latex}"
            },
            {
                "step": 2, "title": "Função da Velocidade",
                "text": "A velocidade varia linearmente com o tempo.",
                "equation_latex": f"v(t) = v0 + at   =>   {eq_vel_latex}"
            }
        ]
        
        if will_stop:
             steps.append({
                "step": 3, "title": "Ponto de Inversão",
                "text": f"O objeto para em t = {stop_time:.2f}s.",
                "equation_latex": f"v(t) = 0   =>   {v0} + {a}t = 0   =>   t = {stop_time:.2f}~s,   S = {stop_pos:.2f}~m"
            })

        # Geração de dados (Mantendo seu código original)
        sim_duration = max(10.0, stop_time * 1.5) if will_stop else 10.0
        num_frames = 60
        time_array = [round((sim_duration / num_frames) * i, 3) for i in range(num_frames + 1)]
        position_s_array = [round(s0 + v0 * t + 0.5 * a * t**2, 3) for t in time_array]
        velocity_v_array = [round(v0 + a * t, 3) for t in time_array]

        return {
            "model_detected": "MRUV Horizontal",
            "explanation_steps": steps,
            "simulation_data": {
                "type": "horizontal_mruv",
                "parameters": { "s0": s0, "v0": v0, "a": a },
                "metrics": {
                    "will_stop": will_stop,
                    "stop_time_s": round(stop_time, 2) if will_stop else None,
                    "stop_pos_m": round(stop_pos, 2) if stop_pos is not None else None
                },
                "time_array": time_array,
                "position_s_array": position_s_array,
                "velocity_v_array": velocity_v_array
            }
        }