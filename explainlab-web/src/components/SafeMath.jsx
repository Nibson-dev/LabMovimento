import React from 'react';
import { BlockMath, InlineMath } from 'react-katex';
import 'katex/dist/katex.min.css';

// Escudo de Erros Simples e Eficiente
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, errorMsg: '' };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, errorMsg: error.message };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '12px', background: 'rgba(255,0,0,0.1)', border: '1px solid #ff4444', borderRadius: '8px', color: '#ffaaaa', fontFamily: 'monospace', fontSize: '12px' }}>
          <strong>⚠️ Erro de Sintaxe:</strong><br/>
          <code>{this.props.equation}</code><br/><br/>
          <span style={{ color: '#ff5555' }}>{this.state.errorMsg}</span>
        </div>
      );
    }
    return this.props.children;
  }
}

// O Componente Principal Limpo
export default function SafeMath({ equation, inline = false }) {
  if (!equation) return null;
  const Component = inline ? InlineMath : BlockMath;
  
  return (
    <ErrorBoundary equation={equation}>
      <Component math={equation} />
    </ErrorBoundary>
  );
}

export function InlineSafeMath({ equation }) {
  return <SafeMath equation={equation} inline={true} />;
}

export function DisplaySafeMath({ equation }) {
  return <SafeMath equation={equation} inline={false} />;
}