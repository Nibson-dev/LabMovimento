import sympy as sp
from .base_model import BaseModel

class HorizontalMRUV(BaseModel):
    def solve(self, s0, v0, a):
        t = sp.Symbol('t')
        
        eq_pos_latex = f"S(t) = {s0} + {v0}t + {0.5*a}t^2"
        eq_vel_latex = f"v(t) = {v0} + {a}t"
        
        stop_time = 0.0
        will_stop = False
        
        if (v0 > 0 and a < 0) or (v0 < 0 and a > 0):
            will_stop = True
            stop_time = -v0 / a
            stop_pos = s0 + v0 * stop_time + 0.5 * a * stop_time**2
            status = "Movimento Retardado (Freando) ate parar, depois Acelerado (Invertido)."
        elif a == 0:
             status = "Movimento Retilineo Uniforme (MRU - Aceleracao nula)."
             stop_pos = None
        else:
            status = "Movimento Acelerado (Ganhando velocidade no mesmo sentido)."
            stop_pos = None

        steps = [
            {
                "step": 1, "title": "Funções Horárias do MRUV",
                "text": f"O movimento é definido pela posição inicial S0={s0}m, velocidade inicial v0={v0}m/s e aceleração constante a={a}m/s^2. {status}",
                "equation_latex": rf"S(t) = S_0 + v_0 t + \frac{{at^2}}{{2}} \Rightarrow {eq_pos_latex}"
            },
             {
                "step": 2, "title": "Função da Velocidade",
                "text": "A velocidade varia linearmente com o tempo devido à aceleração constante.",
                "equation_latex": rf"v(t) = v_0 + at \Rightarrow {eq_vel_latex}"
            }
        ]
        
        if will_stop:
             steps.append({
                "step": 3, "title": "Ponto de Inversão (Velocidade Nula)",
                "text": f"O objeto para momentaneamente (v=0) no instante t = {stop_time:.2f}s antes de inverter o sentido do movimento.",
                "equation_latex": rf"v(t) = 0 \Rightarrow {v0} + {a}t = 0 \Rightarrow t = {stop_time:.2f} \text{{ s}}. \quad S({stop_time:.2f}) = {stop_pos:.2f} \text{{ m}}"
            })

        sim_duration = max(10.0, stop_time * 1.5) if will_stop else 10.0
        num_frames = 60
        time_array = [round((sim_duration / num_frames) * i, 3) for i in range(num_frames + 1)]
        
        position_s_array = []
        velocity_v_array = []
        acceleration_a_array = [] 

        for t_val in time_array:
            pos = s0 + v0 * t_val + 0.5 * a * t_val**2
            vel = v0 + a * t_val
            position_s_array.append(round(pos, 3))
            velocity_v_array.append(round(vel, 3))
            acceleration_a_array.append(a)

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
                "velocity_v_array": velocity_v_array,
                "acceleration_a_array": acceleration_a_array
            }
        }