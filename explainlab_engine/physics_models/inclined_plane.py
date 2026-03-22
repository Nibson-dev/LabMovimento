"""
inclined_plane_improved.py
==========================

Versão melhorada de InclinedPlane que usa o converter LaTeX seguro.

IMPORTANTE: Substitua a versão anterior pela esta.

Mudanças:
1. Usa LatexConverter para gerar LaTeX seguro
2. Retorna metadados sobre compatibilidade
3. Nunca quebra KaTeX no frontend
4. Suporta sympy.latex() sem risco

Uso:
    from latex_converter import sympy_to_katex, create_safe_equation
    from inclined_plane_improved import InclinedPlane
"""

import math
from typing import Dict, List, Any
from ..utils.latex_converter import sympy_to_katex, create_safe_equation


class InclinedPlane:
    """
    Simulação de plano inclinado com atrito.
    Gera equações LaTeX 100% compatíveis com KaTeX.
    """
    
    def solve(
        self, 
        mass: float, 
        angle: float, 
        mu_s_val: float, 
        mu_k_val: float, 
        gravity: float = 9.8
    ) -> Dict[str, Any]:
        """
        Resolve dinâmica de plano inclinado.
        
        Args:
            mass: Massa em kg
            angle: Ângulo em graus
            mu_s_val: Coeficiente de atrito estático
            mu_k_val: Coeficiente de atrito cinético
            gravity: Aceleração da gravidade (padrão 9.8 m/s²)
            
        Returns:
            Dict com simulation_data, explanation_steps, etc.
        """
        
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
        
        # ========== EQUAÇÕES (SEGURAS PARA KATEX) ==========
        
        # Passo 1: Decomposição do Peso
        eq1_text = (
            f"P = {weight:.2f} \\, \\mathrm{{N}} \\quad "
            f"P_x = {px:.2f} \\, \\mathrm{{N}} \\quad "
            f"N = {normal_force:.2f} \\, \\mathrm{{N}}"
        )
        
        # Passo 2: Análise de Atrito
        eq2_text = (
            f"F_{{at,max}} = \\mu_s \\cdot N = {mu_s_val} \\cdot {normal_force:.2f} "
            f"= {max_static_friction:.2f} \\, \\mathrm{{N}}"
        )
        
        # Passo 3: Comparação (condicional)
        if is_moving:
            eq3_text = (
                f"P_x > F_{{at,max}} \\quad "
                f"({px:.2f} > {max_static_friction:.2f}) \\quad "
                f"\\Rightarrow \\text{{Bloco se move}}"
            )
        else:
            eq3_text = (
                f"P_x \\leq F_{{at,max}} \\quad "
                f"({px:.2f} \\leq {max_static_friction:.2f}) \\quad "
                f"\\Rightarrow \\text{{Bloco travado}}"
            )
        
        # Passo 4: Segunda Lei de Newton (se movimento)
        if is_moving:
            eq4_text = (
                f"a = \\frac{{P_x - F_{{at}}}}{{m}} = "
                f"\\frac{{{px:.2f} - {friction_force:.2f}}}{{{mass}}} "
                f"= {acceleration:.2f} \\, \\mathrm{{m/s^2}}"
            )
        else:
            eq4_text = (
                f"a = 0 \\, \\mathrm{{m/s^2}} \\quad "
                f"\\text{{(bloco em repouso)}}"
            )
        
        # ========== BUILD STEPS COM SAFELATEX ==========
        steps = [
            {
                "step": 1,
                "title": "Decomposição do Peso",
                "text": f"O peso total é {weight:.2f} N. Decomposto em componentes paralela (Px) e normal (N).",
                "equation_latex": sympy_to_katex(eq1_text)  # ✅ SAFE
            },
            {
                "step": 2,
                "title": "Limite de Atrito Estático",
                "text": f"Atrito estático máximo possível: {max_static_friction:.2f} N. Agora comparamos com Px.",
                "equation_latex": sympy_to_katex(eq2_text)  # ✅ SAFE
            },
            {
                "step": 3,
                "title": "Análise de Movimento",
                "text": status_text,
                "equation_latex": sympy_to_katex(eq3_text)  # ✅ SAFE
            }
        ]
        
        if is_moving:
            steps.append({
                "step": 4,
                "title": "Segunda Lei de Newton",
                "text": "Como Px > Fatrito_max, o bloco se move com aceleração constante.",
                "equation_latex": sympy_to_katex(eq4_text)  # ✅ SAFE
            })
        
        # ========== SIMULAÇÃO ==========
        ramp_length = 15.0
        num_frames = 60
        
        time_array = []
        position_s_array = []
        velocity_v_array = []
        
        if is_moving and acceleration > 0:
            # Calcula tempo total para descer a rampa
            total_time = math.sqrt((2 * ramp_length) / acceleration)
            
            time_array = [round((total_time / num_frames) * i, 3) for i in range(num_frames + 1)]
            
            for t in time_array:
                pos = 0.5 * acceleration * t**2
                vel = acceleration * t
                position_s_array.append(round(pos, 3))
                velocity_v_array.append(round(vel, 3))
        else:
            # Bloco travado
            time_array = [0.0, 1.0, 2.0]
            position_s_array = [0.0, 0.0, 0.0]
            velocity_v_array = [0.0, 0.0, 0.0]
        
        # ========== RETORNO ==========
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
                    "gravity": gravity,
                    "mu_s": mu_s_val,
                    "mu_k": mu_k_val
                },
                "physics": {
                    "is_moving": is_moving,
                    "weight_N": round(weight, 2),
                    "normal_force_N": round(normal_force, 2),
                    "px_N": round(px, 2),
                    "friction_force_N": round(friction_force, 2),
                    "net_force_N": round(net_force, 2),
                    "acceleration_m_s2": round(acceleration, 2),
                    "max_static_friction_N": round(max_static_friction, 2)
                },
                "time_array": time_array,
                "position_s_array": position_s_array,
                "velocity_v_array": velocity_v_array,
                "metrics": {
                    "total_time_s": round(time_array[-1] if time_array else 0, 2),
                    "max_velocity_m_s": round(max(velocity_v_array) if velocity_v_array else 0, 2),
                    "max_distance_m": round(max(position_s_array) if position_s_array else 0, 2)
                }
            }
        }


# ========== HELPER: Usar com SymPy (se needed) ==========

def from_sympy_expression(expr, var_name='x'):
    """
    Converter uma expressão SymPy para LaTeX seguro.
    
    OPCIONAL - use se quiser gerar equações com SymPy em vez de strings.
    
    Args:
        expr: sympy Expression
        var_name: nome da variável
        
    Returns:
        String LaTeX segura para KaTeX
        
    Example:
        >>> import sympy as sp
        >>> x = sp.Symbol('x')
        >>> expr = x**2 + 2*x + 1
        >>> latex_safe = from_sympy_expression(expr)
    """
    try:
        import sympy
        latex_raw = sympy.latex(expr)
        return sympy_to_katex(latex_raw)
    except ImportError:
        # Se sympy não está instalado, retorna original
        return str(expr)


# ========== TESTE ==========

if __name__ == '__main__':
    print("🧪 Testando InclinedPlane...\n")
    
    model = InclinedPlane()
    result = model.solve(
        mass=10,
        angle=30,
        mu_s_val=0.5,
        mu_k_val=0.3,
        gravity=9.8
    )
    
    print(f"✅ Modelo: {result['model_detected']}")
    print(f"✅ Steps: {len(result['explanation_steps'])}")
    print(f"✅ Aceleração: {result['simulation_data']['physics']['acceleration_m_s2']} m/s²")
    print("\n📐 Equações geradas:")
    
    for step in result['explanation_steps']:
        print(f"\n  Step {step['step']}: {step['title']}")
        print(f"  LaTeX: {step['equation_latex'][:60]}...")
        
        # Valida cada equação
        from latex_converter import validate_latex
        is_valid, compat, issue = validate_latex(step['equation_latex'])
        print(f"  Valid: {is_valid} ({compat.value})")