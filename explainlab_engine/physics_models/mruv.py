from typing import Dict, Any
import numpy as np
from .base_model import BasePhysicsModel

class MRUV(BasePhysicsModel):
    def __init__(self, parameters: Dict[str, Any]):
        super().__init__(parameters)
        self.model_name = "MRUV"
        self.s0 = parameters.get('s0', 0.0)
        self.v0 = parameters.get('v0', 0.0)
        self.a = parameters.get('a', 1.0)
        self.t_final = parameters.get('t_final', 5.0)

    def solve(self) -> Dict[str, Any]:
        # EQUAÇÕES BLINDADAS
        self._add_step(
            step_number=1,
            title="Equação Horária",
            text="Movimento com aceleração constante.",
            equation_latex=f"s(t) = s0 + v0~t + (at²) / 2"
        )

        s_final_val = self.s0 + self.v0 * self.t_final + 0.5 * self.a * self.t_final**2
        
        self._add_step(
            step_number=2,
            title="Substituição",
            text=f"Para t = {self.t_final}s",
            equation_latex=f"s({self.t_final}) = {s_final_val:.2f}~m"
        )

        # Dados numéricos com Numpy (Preservando lógica)
        time_array = np.linspace(0, self.t_final, 50)
        pos_array = self.s0 + self.v0 * time_array + 0.5 * self.a * time_array**2
        
        self.simulation_data = {
            "time_array": time_array.tolist(),
            "position_array": pos_array.tolist()
        }
        return self._build_output(self.model_name)