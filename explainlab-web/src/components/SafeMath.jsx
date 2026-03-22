import React, { useState, useEffect } from 'react';
import { BlockMath, InlineMath } from 'react-katex';
import 'katex/dist/katex.min.css';

/**
 * SafeMath - Componente robusto para renderização de equações LaTeX
 * 
 * Estratégia de fallback:
 * 1. Tenta KaTeX (renderização mais bonita)
 * 2. Se falhar, tenta MathML (compatibilidade)
 * 3. Se falhar, mostra texto puro com placeholder elegante
 * 4. NUNCA mostra erro ao usuário final
 * 
 * Props:
 * - equation: string LaTeX a renderizar
 * - inline: boolean (padrão: false)
 * - fallback: 'text' | 'placeholder' | 'hidden' (padrão: 'placeholder')
 * - debug: boolean - mostra erros no console (padrão: false)
 * - onError: callback quando há erro
 */
export default function SafeMath({ 
  equation, 
  inline = false, 
  fallback = 'placeholder',
  debug = false,
  onError = null 
}) {
  const [renderMode, setRenderMode] = useState('katex'); // 'katex' | 'mathml' | 'text' | 'fallback'
  const [sanitized, setSanitized] = useState(equation);

  useEffect(() => {
    // Sanitiza e prepara a equação
    const clean = sanitizeLatex(equation);
    setSanitized(clean);
    setRenderMode('katex'); // Reset para tentar novamente
  }, [equation]);

  const handleKaTexError = (error) => {
    if (debug) console.warn('❌ KaTeX error:', error.message, 'Equation:', sanitized);
    if (onError) onError({ type: 'katex', error, equation: sanitized });
    setRenderMode('mathml');
  };

  // ============================================
  // 1️⃣ RENDERIZAÇÃO KATEX (Primária)
  // ============================================
  if (renderMode === 'katex') {
    const Component = inline ? InlineMath : BlockMath;
    return (
      <ErrorBoundary 
        onError={handleKaTexError}
        fallback={
          <div onClick={() => setRenderMode('mathml')}>
            {renderFallback(sanitized, fallback, inline)}
          </div>
        }
      >
        <Component math={sanitized} />
      </ErrorBoundary>
    );
  }

  // ============================================
  // 2️⃣ RENDERIZAÇÃO MATHML (Fallback)
  // ============================================
  if (renderMode === 'mathml') {
    return (
      <div style={{ margin: inline ? '0 2px' : '12px 0' }}>
        <MathMLRenderer 
          latex={sanitized}
          inline={inline}
          onError={(error) => {
            if (debug) console.warn('❌ MathML error:', error);
            if (onError) onError({ type: 'mathml', error, equation: sanitized });
            setRenderMode('text');
          }}
        />
      </div>
    );
  }

  // ============================================
  // 3️⃣ FALLBACK FINAL (Texto + Placeholder)
  // ============================================
  return renderFallback(sanitized, fallback, inline);
}

/**
 * SANITIZAR LaTeX - Remove comandos incompatíveis com KaTeX
 * 
 * Problemas resolvidos:
 * - Unicode corrompido (\t̲m̲space → \tmspace)
 * - Comandos SymPy incompat. (\tfrac → \frac, \tmspace removed)
 * - Espaços duplos, caracteres inválidos
 */
function sanitizeLatex(latex) {
  if (!latex || typeof latex !== 'string') return '';

  let clean = latex;

  // ✅ Remove Unicode combinado corrompido (e.g., \t̲m̲space)
  clean = clean.replace(/([a-z])\u0332(?=[a-z])/g, '$1'); // Remove underline combinado
  clean = clean.replace(/([a-z])\u0308(?=[a-z])/g, '$1'); // Remove diaeresis combinado

  // ✅ Substitui comandos SymPy incompatíveis
  const incompatibleCommands = {
    // Espaçamento (KaTeX usa \, \: \; ou espaço normal)
    '\\tmspace': ' ',
    '\\mkern': '',
    '\\kern': '',
    '\\hspace': '',
    '\\quad ': ' ',
    '\\qquad ': ' ',

    // Frações (SymPy às vezes usa \tfrac - texto fraction)
    '\\tfrac': '\\frac',
    '\\dfrac': '\\frac',
    '\\cfrac': '\\frac',

    // Estilos (KaTeX suporta limitado)
    '\\mathrm': '\\mathrm', // OK
    '\\mathbf': '\\mathbf', // OK
    '\\mathit': '\\mathit', // OK
    '\\text': '\\text', // OK
    '\\displaystyle': '', // Remove - não é necessário
    '\\textstyle': '',
    '\\scriptstyle': '',
  };

  Object.entries(incompatibleCommands).forEach(([search, replace]) => {
    const regex = new RegExp(search.replace(/\\/g, '\\\\'), 'g');
    clean = clean.replace(regex, replace);
  });

  // ✅ Remove múltiplos espaços
  clean = clean.replace(/\s+/g, ' ');

  // ✅ Remove caracteres de controle perigosos
  clean = clean.replace(/[\x00-\x1F\x7F]/g, '');

  // ✅ Normaliza espaçamento ao redor de \left e \right
  clean = clean.replace(/\s*\\left\s*/g, '\\left');
  clean = clean.replace(/\s*\\right\s*/g, '\\right');

  return clean.trim();
}

/**
 * MATHML Renderer - Tenta converter LaTeX para MathML
 * Usa https://www.mathjax.org/ como fallback
 */
function MathMLRenderer({ latex, inline, onError }) {
  const [mathml, setMathml] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Tenta converter usando MathJax (se disponível)
    const convert = async () => {
      try {
        // Se MathJax está carregado globalmente
        if (window.MathJax && window.MathJax.typesetPromise) {
          const container = document.createElement('div');
          container.innerHTML = `\\(${latex}\\)`;
          await window.MathJax.typesetPromise([container]);
          setMathml(container.innerHTML);
        } else {
          // Fallback: renderiza como <code> elegante
          throw new Error('MathJax not available');
        }
      } catch (error) {
        onError(error);
        setMathml(null);
      } finally {
        setLoading(false);
      }
    };

    convert();
  }, [latex, onError]);

  if (loading) {
    return (
      <div style={{
        padding: '8px 12px',
        background: 'rgba(255,255,255,0.03)',
        borderRadius: '6px',
        fontSize: '12px',
        color: '#666'
      }}>
        ⟳ Renderizando...
      </div>
    );
  }

  if (mathml) {
    return (
      <div 
        dangerouslySetInnerHTML={{ __html: mathml }}
        style={{
          padding: inline ? '0 2px' : '8px',
          opacity: 0.85
        }}
      />
    );
  }

  return null; // Fallback já lidou
}

/**
 * Error Boundary - Captura erros do KaTeX com elegância
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error) {
    this.props.onError?.(error);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || <div>Erro ao renderizar</div>;
    }
    return this.props.children;
  }
}

/**
 * Renderizar Fallback - Modo degradado elegante
 */
function renderFallback(equation, mode, inline) {
  const styles = {
    container: {
      margin: inline ? '0 2px' : '12px 0',
      padding: inline ? '2px 6px' : '12px 16px',
      borderRadius: '8px',
      fontSize: inline ? '0.9em' : '1.1em',
      fontFamily: 'monospace',
    },
    text: {
      container: {
        ...styles.container,
        background: 'rgba(255,255,255,0.03)',
        color: '#aaa',
        border: '1px solid rgba(255,255,255,0.08)',
      },
      content: {
        whiteSpace: 'pre-wrap',
        wordBreak: 'break-word',
      }
    },
    placeholder: {
      container: {
        ...styles.container,
        background: 'linear-gradient(90deg, rgba(0,229,255,0.05), rgba(0,229,255,0.02))',
        color: '#666',
        border: '1px dashed rgba(0,229,255,0.2)',
        textAlign: 'center',
      },
      icon: {
        marginRight: '8px',
      }
    },
    hidden: {
      container: { display: 'none' }
    }
  };

  if (mode === 'hidden') {
    return <div style={styles.hidden.container} />;
  }

  if (mode === 'text') {
    return (
      <div style={styles.text.container}>
        <code style={styles.text.content}>{equation}</code>
      </div>
    );
  }

  // placeholder (padrão)
  return (
    <div style={styles.placeholder.container}>
      <span style={styles.placeholder.icon}>⚗️</span>
      Equação complexa
    </div>
  );
}

/**
 * COMPONENTE AUXILIAR: InlineSafeMath
 * Para uso rápido em textos inline
 */
export function InlineSafeMath({ equation, debug = false }) {
  return (
    <SafeMath 
      equation={equation} 
      inline={true} 
      fallback="text"
      debug={debug}
    />
  );
}

/**
 * COMPONENTE AUXILIAR: DisplaySafeMath
 * Para blocos de equações destacadas
 */
export function DisplaySafeMath({ equation, debug = false }) {
  return (
    <SafeMath 
      equation={equation} 
      inline={false} 
      fallback="placeholder"
      debug={debug}
    />
  );
}
