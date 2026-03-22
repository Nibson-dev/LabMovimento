"""
latex_converter.py
==================

Módulo profissional para converter LaTeX gerado por SymPy
para formato compatível com KaTeX (frontend).
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
        r'\tmspace': '',
        r'\mkern': '',
        r'\kern': '',
        r'\hspace': '',
        r'\tfrac': r'\frac',      
        r'\dfrac': r'\frac',      
        r'\cfrac': r'\frac',      
        r'\mathrm{': r'\mathrm{',   
        r'\mathbf{': r'\mathbf{',   
        r'\mathit{': r'\mathit{',   
        r'\mathbb{': r'\mathbb{',   
        r'\text{': r'\text{',       
        r'\displaystyle': '',
        r'\textstyle': '',
        r'\scriptstyle': '',
        r'\scriptscriptstyle': '',
    }
    
    CONTROL_CHARS_PATTERN = re.compile(r'[\x00-\x1F\x7F]')
    COMBINING_MARKS_PATTERN = re.compile(r'([a-zA-Z])\u0300-\u0336', re.UNICODE)
    MULTIPLE_SPACES_PATTERN = re.compile(r'\s{2,}')
    
    @staticmethod
    def sanitize(latex: str) -> str:
        if not latex or not isinstance(latex, str):
            return ''
        
        clean = latex
        clean = LatexConverter._remove_corrupted_unicode(clean)
        clean = LatexConverter._replace_incompatible_commands(clean)
        clean = LatexConverter._normalize_spacing(clean)
        clean = LatexConverter.CONTROL_CHARS_PATTERN.sub('', clean)
        
        if not LatexConverter.validate(clean)[0]:
            clean = LatexConverter._recover_broken_latex(clean)
        
        return clean.strip()
    
    @staticmethod
    def _remove_corrupted_unicode(latex: str) -> str:
        clean = re.sub(r'[\u0300-\u036F]', '', latex)
        return clean
    
    @staticmethod
    def _replace_incompatible_commands(latex: str) -> str:
        """Substitui comandos SymPy por equivalentes KaTeX usando replace seguro"""
        clean = latex
        
        for sympy_cmd, katex_cmd in LatexConverter.INCOMPATIBLE_COMMANDS.items():
            # AQUI ESTÁ A CORREÇÃO: Usar .replace() evita o "bad escape \m" do Python 3.14!
            clean = clean.replace(sympy_cmd, katex_cmd)
        
        return clean
    
    @staticmethod
    def _normalize_spacing(latex: str) -> str:
        clean = latex
        clean = LatexConverter.MULTIPLE_SPACES_PATTERN.sub(' ', clean)
        clean = re.sub(r'\s*\\left\s*', '\\left', clean)
        clean = re.sub(r'\s*\\right\s*', '\\right', clean)
        clean = clean.replace(r'\,', r'\,').replace(r'\;', r'\;')
        return clean
    
    @staticmethod
    def _recover_broken_latex(latex: str) -> str:
        open_braces = latex.count('{')
        close_braces = latex.count('}')
        
        if open_braces > close_braces:
            latex += '}' * (open_braces - close_braces)
        elif close_braces > open_braces:
            latex = latex[:latex.rfind('}')]
        
        latex = latex.replace(r'\\\\', r'\\')
        latex = latex.replace('$$', '')
        return latex
    
    @staticmethod
    def validate(latex: str) -> Tuple[bool, LatexCompatibility, Optional[str]]:
        if not latex:
            return False, LatexCompatibility.INCOMPATIBLE, "Empty LaTeX"
        
        issues = []
        if latex.count('{') != latex.count('}'):
            issues.append("Braces desequilibrados")
            return False, LatexCompatibility.INCOMPATIBLE, issues[0]
        
        if '$$' in latex:
            issues.append("$$ aninhado detectado")
            
        unknown_commands = re.findall(r'\\[a-zA-Z]+', latex)
        known_commands = {
            'frac', 'sqrt', 'sin', 'cos', 'tan', 'log', 'ln', 'exp',
            'mathrm', 'mathbf', 'mathit', 'mathbb', 'text',
            'left', 'right', 'Big', 'big',
            'sum', 'prod', 'int', 'quad', 'cdot', 'times',
            'alpha', 'beta', 'gamma', 'delta', 'pi', 'theta', 'mu',
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
        
        compatibility = LatexCompatibility.FULL if not issues else LatexCompatibility.PARTIAL
        return True, compatibility, None

    @staticmethod
    def sympy_to_katex(sympy_latex: str) -> str:
        return LatexConverter.sanitize(sympy_latex)

def sympy_to_katex(sympy_latex: str) -> str:
    return LatexConverter.sanitize(sympy_latex)

def validate_latex(latex: str) -> bool:
    is_valid, _, _ = LatexConverter.validate(latex)
    return is_valid