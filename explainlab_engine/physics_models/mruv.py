from typing import Dict, Any
import sympy as sp
import numpy as np
from .base_model import BasePhysicsModel
from explainlab_engine.utils.latex_converter import sympy_to_katex, create_safe_equation

class MRUV(BasePhysicsModel):
    def __init__(self, parameters: Dict[str, Any]):
        super().__init__(parameters)
        self.model_name = "MRUV"
        self.s0 = parameters.get('s0', 0.0)
        self.v0 = parameters.get('v0', 0.0)
        self.a = parameters.get('a', 1.0)
        self.t_final = parameters.get('t_final', 5.0)
        self.t = sp.Symbol('t', real=True, positive=True)

    def validate_parameters(self) -> bool:
        if self.t_final <= 0:
            self.errors.append("Tempo final deve ser positivo")
            return False
        return True

    def solve(self) -> Dict[str, Any]:
        if not self.validate_parameters():
            return {
                "model_detected": self.model_name,
                "errors": self.errors,
                "explanation_steps": [],
                "simulation_data": {}
            }
        
        self._add_step(
            step_number=1,
            title="Identificação do Modelo",
            text="Movimento com aceleração constante.",
            equation_latex=rf"s(t) = s_0 + v_0 t + \frac{{1}}{{2}}at^2"
        )

        s_general = self.s0 + self.v0 * self.t + sp.Rational(1, 2) * self.a * self.t**2
        s_general_latex = sp.latex(s_general)
        
        self._add_step(
            step_number=2,
            title="Substituição de Valores",
            text=f"Substituindo s0 = {self.s0}, v0 = {self.v0}, a = {self.a}",
            equation_latex=s_general_latex
        )

        v_t = sp.diff(s_general, self.t)
        v_t_latex = sp.latex(v_t)
        
        self._add_step(
            step_number=3,
            title="Equação Horária da Velocidade",
            text="Derivando a posição",
            equation_latex=v_t_latex
        )

        self._generate_simulation_data(s_general, v_t)
        return self._build_output(self.model_name)

    def _generate_simulation_data(self, s_general, v_t) -> None:
        t_final = self.t_final
        time_array = np.linspace(0, t_final, 50)
        s_func = sp.lambdify(self.t, s_general, 'numpy')
        v_func = sp.lambdify(self.t, v_t, 'numpy')
        position_array = s_func(time_array)
        velocity_array = v_func(time_array)
        self.simulation_data = {
            "time_array": time_array.tolist(),
            "position_array": position_array.tolist(),
            "velocity_array": velocity_array.tolist()
        }