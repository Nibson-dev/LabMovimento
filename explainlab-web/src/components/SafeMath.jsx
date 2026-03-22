import React from 'react';
import { BlockMath, InlineMath } from 'react-katex';
import 'katex/dist/katex.min.css';

export default function SafeMath({ equation, inline = false }) {
  if (!equation) return null;

  // 🛡️ O FILTRO ANTI-SYMPY: Limpa as bizarrices que o backend manda
  let cleanEq = equation;
  
  // 1. Destrói o \tmspace maldito e transforma em espaço normal
  cleanEq = cleanEq.replace(/\\tmspace\s*\+3mu\s*\.1667em/g, ' ');
  cleanEq = cleanEq.replace(/\\tmspace/g, ' ');
  
  // 2. Destrói o \mathrm (que o KaTeX às vezes chora pra ler)
  cleanEq = cleanEq.replace(/\\mathrm\{([^}]+)\}/g, '$1');
  cleanEq = cleanEq.replace(/\\mathrm/g, '');
  
  // 3. Troca vírgulas e formatações estranhas por espaços puros
  cleanEq = cleanEq.replace(/\\,/g, ' ');
  cleanEq = cleanEq.replace(/~/g, ' ');

  const Component = inline ? InlineMath : BlockMath;

  return (
    <div style={{ padding: '8px 0', overflowX: 'auto' }}>
      <Component 
        math={cleanEq} 
        renderError={(error) => {
          // Se o KaTeX ainda assim falhar, ele mostra o texto limpo sem quebrar a tela!
          console.warn("KaTeX falhou, mostrando texto puro:", error.message);
          return <span style={{ color: '#00e5ff', fontFamily: 'monospace' }}>{cleanEq}</span>;
        }} 
      />
    </div>
  );
}

export function InlineSafeMath({ equation }) {
  return <SafeMath equation={equation} inline={true} />;
}

export function DisplaySafeMath({ equation }) {
  return <SafeMath equation={equation} inline={false} />;
}