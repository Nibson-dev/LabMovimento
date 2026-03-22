"""
latex_converter.py
==================

Módulo profissional para converter LaTeX gerado por SymPy
para formato compatível com KaTeX (frontend).

Soluciona:
- Comandos SymPy incompat. com KaTeX (\tfrac, \tmspace, etc)
- Unicode corrompido
- Espaçamento problemático
- Caracteres de controle

Uso:
    from latex_converter import sympy_to_katex, validate_latex
    
    # Converter SymPy LaTeX
    latex_str = str(sympy.latex(expr))
    safe_latex = sympy_to_katex(latex_str)
    
    # Ou validar string manual
    equation = r"P_x = 10 \\, \\mathrm{N}"
    if validate_latex(equation):
        # Seguro usar
"""

import re
from typing import Optional, Tuple
from enum import Enum


class LatexCompatibility(Enum):
    """Níveis de compatibilidade KaTeX"""
    FULL = "full"          # Renderiza perfeitamente
    PARTIAL = "partial"    # Renderiza mas pode ter diferenças
    DEGRADED = "degraded"  # Renderiza com fallback
    INCOMPATIBLE = "incompatible"  # Não renderiza


class LatexConverter:
    """
    Conversor profissional de LaTeX SymPy → KaTeX
    
    Whitelist de comandos KaTeX suportados:
    https://katex.org/docs/supported.html
    """
    
    # Comandos SymPy que NÃO funcionam em KaTeX
    INCOMPATIBLE_COMMANDS = {
        # Espaçamento (SymPy gera \tmspace{...})
        r'\tmspace': '',
        r'\mkern': '',
        r'\kern': '',
        r'\hspace': '',
        
        # Frações alternativas (converter para \frac padrão)
        r'\tfrac': r'\frac',      # text fraction → normal
        r'\dfrac': r'\frac',      # display fraction → normal
        r'\cfrac': r'\frac',      # continued fraction (aprox.)
        
        # Estilo de fonte (KaTeX é limitado)
        r'\mathrm{': r'\mathrm{',   # OK
        r'\mathbf{': r'\mathbf{',   # OK
        r'\mathit{': r'\mathit{',   # OK
        r'\mathbb{': r'\mathbb{',   # OK (blackboard bold)
        r'\text{': r'\text{',       # OK
        
        # Estilos que não fazem diferença em KaTeX
        r'\displaystyle': '',
        r'\textstyle': '',
        r'\scriptstyle': '',
        r'\scriptscriptstyle': '',
    }
    
    # Caracteres perigosos
    CONTROL_CHARS_PATTERN = re.compile(r'[\x00-\x1F\x7F]')
    
    # Unicode combinado corrompido (e.g., \t̲m̲space)
    COMBINING_MARKS_PATTERN = re.compile(r'([a-zA-Z])\u0300-\u0336', re.UNICODE)
    
    # Múltiplos espaços
    MULTIPLE_SPACES_PATTERN = re.compile(r'\s{2,}')
    
    @staticmethod
    def sanitize(latex: str) -> str:
        """
        Sanitizar LaTeX removendo/convertendo comandos incompatíveis.
        
        Args:
            latex: String LaTeX raw do SymPy
            
        Returns:
            String LaTeX sanitizada, segura para KaTeX
            
        Example:
            >>> latex = r"\\tfrac{1}{2} \\quad test"
            >>> LatexConverter.sanitize(latex)
            '\\\\frac{1}{2}  test'
        """
        if not latex or not isinstance(latex, str):
            return ''
        
        clean = latex
        
        # 1️⃣ Remove Unicode combinado corrompido
        clean = LatexConverter._remove_corrupted_unicode(clean)
        
        # 2️⃣ Substitui comandos incompatíveis
        clean = LatexConverter._replace_incompatible_commands(clean)
        
        # 3️⃣ Limpa espaçamento
        clean = LatexConverter._normalize_spacing(clean)
        
        # 4️⃣ Remove caracteres de controle
        clean = LatexConverter.CONTROL_CHARS_PATTERN.sub('', clean)
        
        # 5️⃣ Valida resultado
        if not LatexConverter.validate(clean)[0]:
            # Se ainda há problemas, tenta recuperar
            clean = LatexConverter._recover_broken_latex(clean)
        
        return clean.strip()
    
    @staticmethod
    def _remove_corrupted_unicode(latex: str) -> str:
        """Remove marcas diacríticas combinadas que corrompem LaTeX"""
        # Remove combining marks (U+0300 até U+0036F)
        clean = re.sub(r'[\u0300-\u036F]', '', latex)
        return clean
    
    @staticmethod
    def _replace_incompatible_commands(latex: str) -> str:
        """Substitui comandos SymPy por equivalentes KaTeX"""
        clean = latex
        
        for sympy_cmd, katex_cmd in LatexConverter.INCOMPATIBLE_COMMANDS.items():
            # Padrão com boundary word
            pattern = re.escape(sympy_cmd)
            clean = re.sub(pattern, katex_cmd, clean)
        
        return clean
    
    @staticmethod
    def _normalize_spacing(latex: str) -> str:
        """Normaliza espaçamento problemático"""
        clean = latex
        
        # Remove múltiplos espaços
        clean = LatexConverter.MULTIPLE_SPACES_PATTERN.sub(' ', clean)
        
        # Normaliza espaçamento ao redor de \left e \right
        clean = re.sub(r'\s*\\left\s*', '\\left', clean)
        clean = re.sub(r'\s*\\right\s*', '\\right', clean)
        
        # Remove espaços ao redor de operadores
        clean = re.sub(r'\s*\\\,\s*', '\\,', clean)
        clean = re.sub(r'\s*\\\;\s*', '\\;', clean)
        
        return clean
    
    @staticmethod
    def _recover_broken_latex(latex: str) -> str:
        """
        Tenta recuperar LaTeX quebrado aplicando heurísticas.
        Útil para dados muito corrompidos.
        """
        # Escape de braces desequilibrados
        open_braces = latex.count('{')
        close_braces = latex.count('}')
        
        if open_braces > close_braces:
            latex += '}' * (open_braces - close_braces)
        elif close_braces > open_braces:
            # Trunca ou tenta remover
            latex = latex[:latex.rfind('}')]
        
        # Remove sequências inválidas
        latex = re.sub(r'\\{2,}', '\\', latex)  # \\\\ → \\
        latex = re.sub(r'\$\$', '', latex)  # Remove $$ aninhados
        
        return latex
    
    @staticmethod
    def validate(latex: str) -> Tuple[bool, LatexCompatibility, Optional[str]]:
        """
        Valida se LaTeX é compatível com KaTeX.
        
        Returns:
            Tuple[is_valid: bool, compatibility: LatexCompatibility, issue: str|None]
            
        Example:
            >>> is_ok, compat, msg = LatexConverter.validate(r"\\frac{1}{2}")
            >>> is_ok
            True
        """
        if not latex:
            return False, LatexCompatibility.INCOMPATIBLE, "Empty LaTeX"
        
        issues = []
        
        # Verifica braces
        if latex.count('{') != latex.count('}'):
            issues.append("Braces desequilibrados")
            return False, LatexCompatibility.INCOMPATIBLE, issues[0]
        
        # Verifica $ (só deve ser escape de texto, não comandos)
        if '$$' in latex:
            issues.append("$$ aninhado detectado")
        
        # Verifica comandos desconhecidos (heurística)
        unknown_commands = re.findall(r'\\[a-zA-Z]+', latex)
        known_commands = {
            'frac', 'sqrt', 'sin', 'cos', 'tan', 'log', 'ln', 'exp',
            'mathrm', 'mathbf', 'mathit', 'mathbb', 'text',
            'left', 'right', 'Big', 'big',
            'sum', 'prod', 'int', 'quad', 'cdot', 'times',
            'alpha', 'beta', 'gamma', 'delta', 'pi', 'theta',
            'partial', 'nabla', 'infty', 'approx', 'pm', 'mp',
            'le', 'ge', 'll', 'gg', 'sim', 'simeq',
            'times', 'div', 'equiv', 'neq',
            'in', 'notin', 'subset', 'supset',
            'vdots', 'ldots', 'cdots', 'ddots',
            'vec', 'hat', 'bar', 'dot', 'ddot', 'tilde',
            'overline', 'underline', 'overbrace', 'underbrace'
        }
        
        problematic = []
        for cmd in unknown_commands:
            cmd_name = cmd.replace('\\', '')
            if cmd_name not in known_commands and len(cmd_name) > 2:
                problematic.append(cmd)
        
        if problematic:
            return False, LatexCompatibility.PARTIAL, f"Unknown: {problematic[:3]}"
        
        # Se passou em tudo
        compatibility = (
            LatexCompatibility.FULL 
            if not issues 
            else LatexCompatibility.PARTIAL
        )
        
        return True, compatibility, None
    
    @staticmethod
    def sympy_to_katex(sympy_latex: str) -> str:
        """
        Converter LaTeX direto de sympy.latex(expr).
        
        Args:
            sympy_latex: Output de sympy.latex(expression)
            
        Returns:
            String LaTeX compatível com KaTeX
            
        Example:
            >>> import sympy as sp
            >>> x = sp.Symbol('x')
            >>> expr = x**2 + 2*x + 1
            >>> latex = sp.latex(expr)
            >>> katex_safe = LatexConverter.sympy_to_katex(latex)
        """
        return LatexConverter.sanitize(sympy_latex)
    
    @staticmethod
    def create_safe_equation(
        latex: str, 
        fallback: str = "⚗️ Equação complexa"
    ) -> dict:
        """
        Cria dicionário seguro para API com latex + metadados.
        
        Útil para retornar na API junto com a equação.
        
        Returns:
            {
                "latex": string sanitizada,
                "compatibility": "full" | "partial" | "degraded",
                "is_valid": bool,
                "fallback": texto se renderização falhar,
                "original_length": len original (debug)
            }
        """
        clean = LatexConverter.sanitize(latex)
        is_valid, compat, issue = LatexConverter.validate(clean)
        
        return {
            "latex": clean,
            "compatibility": compat.value,
            "is_valid": is_valid,
            "fallback": fallback,
            "original_length": len(latex),
            "sanitized_length": len(clean),
            "issue": issue
        }


# ============================================
# API Simplificada (use isso no seu backend)
# ============================================

def sympy_to_katex(sympy_latex: str) -> str:
    """
    Função simples para usar no seu backend.
    
    from latex_converter import sympy_to_katex
    safe_latex = sympy_to_katex(str(sympy.latex(expr)))
    """
    return LatexConverter.sanitize(sympy_latex)


def validate_latex(latex: str) -> bool:
    """Testa se LaTeX é válido para KaTeX"""
    is_valid, _, _ = LatexConverter.validate(latex)
    return is_valid


def create_safe_equation(
    latex: str, 
    fallback: str = "Equação complexa"
) -> dict:
    """Cria equação segura com metadados para API"""
    return LatexConverter.create_safe_equation(latex, fallback)


# ============================================
# TESTS (execute com: python -m pytest)
# ============================================

if __name__ == '__main__':
    # Teste casos problemáticos
    test_cases = [
        # (input, expected_substring, description)
        (r'\tfrac{1}{2}', r'\frac{1}{2}', "tfrac → frac"),
        (r'P_x = 10 \tmspace  test', 'P_x = 10   test', "tmspace removed"),
        (r'test{{}', 'test{}', "double brace"),
        (r'\displaystyle \frac{a}{b}', r'\frac{a}{b}', "displaystyle removed"),
    ]
    
    print("🧪 Testando LatexConverter...\n")
    
    for input_latex, expected, desc in test_cases:
        result = LatexConverter.sanitize(input_latex)
        is_valid, compat, _ = LatexConverter.validate(result)
        
        status = "✅" if expected in result else "❌"
        print(f"{status} {desc}")
        print(f"   Input:    {input_latex}")
        print(f"   Output:   {result}")
        print(f"   Valid:    {is_valid} ({compat.value})")
        print()
    
    # Teste sympy_to_katex
    print("=" * 50)
    print("Teste direto da função API:\n")
    
    test_eq = r"\tfrac{x^2}{2} \quad \text{metros}"
    safe = sympy_to_katex(test_eq)
    valid = validate_latex(safe)
    
    print(f"Original: {test_eq}")
    print(f"Seguro:   {safe}")
    print(f"Válido:   {valid}")