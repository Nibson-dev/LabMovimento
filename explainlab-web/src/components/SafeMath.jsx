import React, { useState, useEffect } from 'react';
import { BlockMath, InlineMath } from 'react-katex';
import 'katex/dist/katex.min.css';

// ============================================
// 🛡️ A CLASSE FOI MOVIDA PARA O TOPO! 
// Evita o erro "Cannot access 'r' before initialization" na Vercel
// ============================================
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
 * SafeMath - Componente robusto para renderização de equações LaTeX
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
    const clean = sanitizeLatex(equation);
    setSanitized(clean);
    setRenderMode('katex'); 
  }, [equation]);

  const handleKaTexError = (error) => {
    if (debug) console.warn('❌ KaTeX error:', error.message, 'Equation:', sanitized);
    if (onError) onError({ type: 'katex', error, equation: sanitized });
    setRenderMode('mathml');
  };

  // 1️⃣ RENDERIZAÇÃO KATEX
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

  // 2️⃣ RENDERIZAÇÃO MATHML
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

  // 3️⃣ FALLBACK FINAL
  return renderFallback(sanitized, fallback, inline);
}

// ============================================
// FUNÇÕES AUXILIARES (Podem ficar em baixo pois são içadas pelo JS)
// ============================================

function sanitizeLatex(latex) {
  if (!latex || typeof latex !== 'string') return '';
  let clean = latex;

  clean = clean.replace(/([a-z])\u0332(?=[a-z])/g, '$1'); 
  clean = clean.replace(/([a-z])\u0308(?=[a-z])/g, '$1'); 

  const incompatibleCommands = {
    '\\tmspace': ' ', '\\mkern': '', '\\kern': '', '\\hspace': '',
    '\\quad ': ' ', '\\qquad ': ' ', '\\tfrac': '\\frac',
    '\\dfrac': '\\frac', '\\cfrac': '\\frac', '\\mathrm': '\\mathrm',
    '\\mathbf': '\\mathbf', '\\mathit': '\\mathit', '\\text': '\\text',
    '\\displaystyle': '', '\\textstyle': '', '\\scriptstyle': ''
  };

  Object.entries(incompatibleCommands).forEach(([search, replace]) => {
    const regex = new RegExp(search.replace(/\\/g, '\\\\'), 'g');
    clean = clean.replace(regex, replace);
  });

  clean = clean.replace(/\s+/g, ' ');
  clean = clean.replace(/[\x00-\x1F\x7F]/g, '');
  clean = clean.replace(/\s*\\left\s*/g, '\\left');
  clean = clean.replace(/\s*\\right\s*/g, '\\right');

  return clean.trim();
}

function MathMLRenderer({ latex, inline, onError }) {
  const [mathml, setMathml] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const convert = async () => {
      try {
        if (window.MathJax && window.MathJax.typesetPromise) {
          const container = document.createElement('div');
          container.innerHTML = `\\(${latex}\\)`;
          await window.MathJax.typesetPromise([container]);
          setMathml(container.innerHTML);
        } else {
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
      <div style={{ padding: '8px 12px', background: 'rgba(255,255,255,0.03)', borderRadius: '6px', fontSize: '12px', color: '#666' }}>
        ⟳ Renderizando...
      </div>
    );
  }
  if (mathml) {
    return <div dangerouslySetInnerHTML={{ __html: mathml }} style={{ padding: inline ? '0 2px' : '8px', opacity: 0.85 }} />;
  }
  return null; 
}

function renderFallback(equation, mode, inline) {
  const styles = {
    container: { margin: inline ? '0 2px' : '12px 0', padding: inline ? '2px 6px' : '12px 16px', borderRadius: '8px', fontSize: inline ? '0.9em' : '1.1em', fontFamily: 'monospace' },
    text: { container: { background: 'rgba(255,255,255,0.03)', color: '#aaa', border: '1px solid rgba(255,255,255,0.08)' }, content: { whiteSpace: 'pre-wrap', wordBreak: 'break-word' } },
    placeholder: { container: { background: 'linear-gradient(90deg, rgba(0,229,255,0.05), rgba(0,229,255,0.02))', color: '#666', border: '1px dashed rgba(0,229,255,0.2)', textAlign: 'center' }, icon: { marginRight: '8px' } },
    hidden: { container: { display: 'none' } }
  };

  if (mode === 'hidden') return <div style={styles.hidden.container} />;
  if (mode === 'text') {
    return (
      <div style={{...styles.container, ...styles.text.container}}>
        <code style={styles.text.content}>{equation}</code>
      </div>
    );
  }
  return (
    <div style={{...styles.container, ...styles.placeholder.container}}>
      <span style={styles.placeholder.icon}>⚗️</span> Equação complexa
    </div>
  );
}

export function InlineSafeMath({ equation, debug = false }) {
  return <SafeMath equation={equation} inline={true} fallback="text" debug={debug} />;
}

export function DisplaySafeMath({ equation, debug = false }) {
  return <SafeMath equation={equation} inline={false} fallback="placeholder" debug={debug} />;
}