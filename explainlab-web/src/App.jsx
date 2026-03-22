import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Canvas } from '@react-three/fiber';
import { BlockMath } from 'react-katex';
import * as THREE from 'three';
import toast, { Toaster } from 'react-hot-toast';
import { THEME } from './theme';
import Scene3D from './components/Scene3D';

const VectorLegend = ({ show, activeModel, hasFriction }) => {
  if (!show) return null;
  return (
    <div className="vector-legend" style={{ position: 'absolute', bottom: '24px', right: '24px', padding: '16px', backgroundColor: 'rgba(5, 5, 5, 0.85)', backdropFilter: 'blur(24px)', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)', zIndex: 90, boxSizing: 'border-box', pointerEvents: 'none', fontFamily: 'Inter, sans-serif', boxShadow: '0 10px 30px rgba(0,0,0,0.5)' }}>
      <h3 style={{ fontSize: '10px', color: '#666', textTransform: 'uppercase', margin: '0 0 12px 0', letterSpacing: '2px', fontWeight: '800' }}>Vetores Ativos</h3>
      <table style={{ borderCollapse: 'collapse', width: '100%', fontSize: '11px', color: '#FFF' }}>
        <tbody>
          {activeModel === 'inclined_plane' && (
            <>
              <tr><td><div style={{ width: '8px', height: '8px', background: THEME.weight, borderRadius: '50%', marginRight: '10px' }}></div></td><td style={{fontWeight:'600'}}>P</td><td style={{color:'#888'}}>Peso</td></tr>
              <tr><td><div style={{ width: '8px', height: '8px', background: THEME.normal, borderRadius: '50%', marginRight: '10px' }}></div></td><td style={{fontWeight:'600'}}>N</td><td style={{color:'#888'}}>Normal</td></tr>
              <tr><td><div style={{ width: '8px', height: '8px', background: THEME.descida, borderRadius: '50%', marginRight: '10px' }}></div></td><td style={{fontWeight:'600'}}>Px</td><td style={{color:'#888'}}>Descida</td></tr>
              {hasFriction && <tr><td><div style={{ width: '8px', height: '8px', background: THEME.atrito, borderRadius: '50%', marginRight: '10px' }}></div></td><td style={{fontWeight:'600'}}>Fat</td><td style={{color:'#888'}}>Atrito</td></tr>}
            </>
          )}
          {(activeModel === 'vertical_motion' || activeModel === 'projectile_motion') && (
             <tr><td><div style={{ width: '8px', height: '8px', background: THEME.weight, borderRadius: '50%', marginRight: '10px' }}></div></td><td style={{fontWeight:'600'}}>g</td><td style={{color:'#888'}}>Gravidade</td></tr>
          )}
          {(activeModel === 'vertical_motion' || activeModel === 'horizontal_mruv' || activeModel === 'projectile_motion') && (
             <tr><td><div style={{ width: '8px', height: '8px', background: THEME.velocidade, borderRadius: '50%', marginRight: '10px' }}></div></td><td style={{fontWeight:'600'}}>v</td><td style={{color:'#888'}}>Velocidade Total</td></tr>
          )}
           {activeModel === 'projectile_motion' && (
            <>
              <tr><td><div style={{ width: '8px', height: '8px', background: THEME.vx, borderRadius: '50%', marginRight: '10px' }}></div></td><td style={{fontWeight:'600'}}>vx</td><td style={{color:'#888'}}>Vel. Horizontal (MRU)</td></tr>
              <tr><td><div style={{ width: '8px', height: '8px', background: THEME.vy, borderRadius: '50%', marginRight: '10px' }}></div></td><td style={{fontWeight:'600'}}>vy</td><td style={{color:'#888'}}>Vel. Vertical (MRUV)</td></tr>
            </>
          )}
          {activeModel === 'horizontal_mruv' && (
             <tr><td><div style={{ width: '8px', height: '8px', background: THEME.aceleracao, borderRadius: '50%', marginRight: '10px' }}></div></td><td style={{fontWeight:'600'}}>a</td><td style={{color:'#888'}}>Aceleração</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default function App() {
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
  
  // EFEITO PARA FORÇAR CARREGAMENTO DO KATEX NO DEPLOY
  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth <= 768);
    window.addEventListener('resize', handleResize);
    
    // Injeção dinâmica do CSS do KaTeX
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css';
    document.head.appendChild(link);
    
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const [data, setData] = useState(null); 
  const [ghostData, setGhostData] = useState(null); 
  const [useGhost, setUseGhost] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeModel, setActiveModel] = useState('inclined_plane'); 
  const [leftHudOpen, setLeftHudOpen] = useState(!isMobile);
  const [rightHudOpen, setRightHudOpen] = useState(!isMobile);
  const [gravity, setGravity] = useState(9.8);
  const [y0, setY0] = useState(0); const [v0, setV0] = useState(20); 
  const [s0, setS0] = useState(0); const [a, setA] = useState(-2); 
  const [mass, setMass] = useState(10); const [angle, setAngle] = useState(30); 
  const [muStatic, setMuStatic] = useState(0.5); const [muKinetic, setMuKinetic] = useState(0.3); 
  const [playbackSpeed, setPlaybackSpeed] = useState(1); 
  const [manualProgress, setManualProgress] = useState(0); 
  const [showVectors, setShowVectors] = useState(true);
  const [viewMode, setViewMode] = useState('3D'); 

  const clearSimulation = () => {
    setData(null);
    if (!useGhost) setGhostData(null);
  };

  const takeScreenshot = () => {
    const canvas = document.querySelector('canvas');
    if (!canvas) return;
    const link = document.createElement('a');
    link.download = `explainlab-${activeModel}.png`;
    link.href = canvas.toDataURL('image/png');
    link.click();
    toast.success('Screenshot salva com sucesso!', { icon: '📸' });
  };

  const fetchSimulation = async () => {
    if (gravity <= 0) return toast.error('A gravidade deve ser maior que zero!');
    if (mass <= 0 && activeModel === 'inclined_plane') return toast.error('A massa deve ser maior que zero!');
    if (angle < 0 || angle > 89) return toast.error('O ângulo deve estar entre 0º e 89º!');

    if (useGhost && data) { setGhostData(data.simulation_data); } 
    else if (!useGhost) { setGhostData(null); }

    setLoading(true);
    let params = { gravity: parseFloat(gravity) };
    if (activeModel === 'vertical_motion') params = { ...params, y0: parseFloat(y0), v0: parseFloat(v0) };
    else if (activeModel === 'inclined_plane') params = { ...params, mass: parseFloat(mass), angle: parseFloat(angle), mu_s_val: parseFloat(muStatic), mu_k_val: parseFloat(muKinetic) };
    else if (activeModel === 'projectile_motion') params = { ...params, v0: parseFloat(v0), angle_deg: parseFloat(angle) };
    else if (activeModel === 'horizontal_mruv') params = { s0: parseFloat(s0), v0: parseFloat(v0), a: parseFloat(a) };

    try {
      const response = await axios.post('https://labengine.onrender.com/api/simulate', { model_type: activeModel, parameters: params });
      setData(response.data);
      setPlaybackSpeed(1);
      if (!isMobile) setRightHudOpen(true); 
      if (isMobile) setLeftHudOpen(false); 
      toast.success('Física computada!', { icon: '🚀' });
    } catch (e) { 
      console.error("Erro:", e); 
      toast.error('Erro no servidor!');
    } 
    setLoading(false);
  };

  const inputStyle = { width: '100%', padding: '10px', background: '#0a0a0a', border: '1px solid #222', color: '#FFF', borderRadius: '8px', marginTop: '6px' };
  const labelStyle = { fontSize: '10px', color: '#888', fontWeight: '700', letterSpacing: '1px' };
  const closeBtnStyle = { background: 'transparent', border: 'none', color: '#888', cursor: 'pointer', fontSize: '16px', padding: '4px' };

  const renderInputs = () => {
      switch(activeModel) {
          case 'vertical_motion': return (<><div style={{gridColumn:'span 2'}}><label style={labelStyle}>GRAVIDADE (m/s²)</label><input type="number" value={gravity} onChange={e=>setGravity(e.target.value)} style={inputStyle}/></div><div><label style={labelStyle}>ALTURA INICIAL y0 (m)</label><input type="number" value={y0} onChange={e=>setY0(e.target.value)} style={inputStyle}/></div><div><label style={{...labelStyle, color: THEME.velocidade}}>VELOCIDADE v0 (m/s)</label><input type="number" value={v0} onChange={e=>setV0(e.target.value)} style={inputStyle}/></div></>);
          case 'inclined_plane': return (<><div style={{gridColumn:'span 2'}}><label style={labelStyle}>GRAVIDADE (m/s²)</label><input type="number" value={gravity} onChange={e=>setGravity(e.target.value)} style={inputStyle}/></div><div><label style={labelStyle}>MASSA (kg)</label><input type="number" value={mass} onChange={e=>setMass(e.target.value)} style={inputStyle}/></div><div><label style={labelStyle}>ÂNGULO (º)</label><input type="number" value={angle} onChange={e=>setAngle(e.target.value)} style={inputStyle}/></div><div><label style={{...labelStyle, color: THEME.accent}}>ATRITO ESTÁTICO</label><input type="number" step="0.1" value={muStatic} onChange={e=>setMuStatic(e.target.value)} style={inputStyle}/></div><div><label style={{...labelStyle, color: THEME.atrito}}>ATRITO CINÉTICO</label><input type="number" step="0.1" value={muKinetic} onChange={e=>setMuKinetic(e.target.value)} style={inputStyle}/></div></>);
          case 'projectile_motion': return (<><div style={{gridColumn:'span 2'}}><label style={labelStyle}>GRAVIDADE (m/s²)</label><input type="number" value={gravity} onChange={e=>setGravity(e.target.value)} style={inputStyle}/></div><div><label style={{...labelStyle, color: THEME.velocidade}}>VELOCIDADE v0 (m/s)</label><input type="number" value={v0} onChange={e=>setV0(e.target.value)} style={inputStyle}/></div><div><label style={labelStyle}>ÂNGULO DE LANÇAMENTO (º)</label><input type="number" value={angle} onChange={e=>setAngle(e.target.value)} style={inputStyle}/></div></>);
          case 'horizontal_mruv': return (<><div><label style={labelStyle}>POSIÇÃO INICIAL S0 (m)</label><input type="number" value={s0} onChange={e=>setS0(e.target.value)} style={inputStyle}/></div><div><label style={{...labelStyle, color: THEME.velocidade}}>VELOCIDADE v0 (m/s)</label><input type="number" value={v0} onChange={e=>setV0(e.target.value)} style={inputStyle}/></div><div style={{gridColumn:'span 2'}}><label style={{...labelStyle, color: THEME.aceleracao}}>ACELERAÇÃO a (m/s²)</label><input type="number" value={a} onChange={e=>setA(e.target.value)} style={inputStyle}/></div></>);
          default: return null;
      }
  }

  const renderMetrics = () => {
      if (!data) return null;
      const metrics = data.simulation_data.metrics || {};
      const phys = data.simulation_data.physics || {};
      const styleItem = { display: 'flex', justifyContent: 'space-between', background: 'rgba(255,255,255,0.03)', padding: '8px', borderRadius: '6px' };
      const styleVal = { color: '#FFF', fontWeight: 'bold' };

      switch(activeModel) {
          case 'inclined_plane': return (<><div style={{...styleItem, background: phys.is_moving ? THEME.velocidade : THEME.atrito, color:'#000'}}>STATUS: {phys.is_moving ? "DESCENDO" : "TRAVADO"}</div><div style={styleItem}><span>Aceleração:</span><span style={styleVal}>{phys.acceleration_m_s2} m/s²</span></div></>);
          case 'vertical_motion': return (<><div style={styleItem}><span>Ápice (H_max):</span><span style={{...styleVal, color:THEME.descida}}>{data.simulation_data.max_height_m}m</span></div><div style={styleItem}><span>Tempo Total:</span><span style={styleVal}>{data.simulation_data.flight_time_s}s</span></div></>);
          case 'projectile_motion': return (<><div style={styleItem}><span>Alcance (R):</span><span style={{...styleVal, color:THEME.accent}}>{metrics.range_m}m</span></div><div style={styleItem}><span>Ápice (H_max):</span><span style={{...styleVal, color:THEME.descida}}>{metrics.h_max_m}m</span></div><div style={styleItem}><span>Tempo de Voo:</span><span style={styleVal}>{metrics.flight_time_s}s</span></div><div style={styleItem}><span style={{color:THEME.vx}}>v0x:</span><span style={styleVal}>{metrics.v0x_m_s}m/s</span></div><div style={styleItem}><span style={{color:THEME.vy}}>v0y:</span><span style={styleVal}>{metrics.v0y_m_s}m/s</span></div></>);
          case 'horizontal_mruv': return (<><div style={styleItem}><span>Vai Parar?</span><span style={{...styleVal, color: metrics.will_stop ? THEME.aceleracao : THEME.velocidade}}>{metrics.will_stop ? "SIM" : "NÃO"}</span></div>{metrics.will_stop && <div style={styleItem}><span>Inversão:</span><span style={styleVal}>{metrics.stop_pos_m}m</span></div>}</>);
          default: return null;
      }
  }

  return (
    <>
      <Toaster position="top-center" reverseOrder={false} />
      <style>{`
        body, html, #root { margin: 0; padding: 0; width: 100vw; height: 100vh; overflow: hidden; background: #000; font-family: 'Inter', sans-serif; } 
        * { box-sizing: border-box; } 
        
        /* CORREÇÃO DO KATEX (FÓRMULAS) */
        .katex-display { margin: 12px 0; overflow-x: auto; color: #00e5ff !important; }
        .katex { color: white !important; font-size: 1.1em !important; }
        .katex .base { margin: 4px 0; }

        .hud-panel {
          position: absolute;
          background-color: rgba(5, 5, 5, 0.75);
          backdrop-filter: blur(24px);
          -webkit-backdrop-filter: blur(24px);
          border-radius: 16px;
          border: 1px solid rgba(255, 255, 255, 0.08);
          box-shadow: 0 20px 50px rgba(0,0,0,0.8);
          box-sizing: border-box;
          transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.4s ease;
          z-index: 100;
        }
        
        .hud-left { top: 24px; left: 24px; width: 360px; padding: 28px; display: flex; flex-direction: column; gap: 20px; max-height: 90vh; overflow-y: auto; transform: ${leftHudOpen ? 'translateX(0)' : 'translateX(-120%)'}; opacity: ${leftHudOpen ? 1 : 0}; pointer-events: ${leftHudOpen ? 'auto' : 'none'}; }
        .hud-right { top: 24px; right: 24px; bottom: 24px; width: 420px; padding: 28px; display: flex; flex-direction: column; overflow-y: auto; transform: ${rightHudOpen ? 'translateX(0)' : 'translateX(120%)'}; opacity: ${rightHudOpen ? 1 : 0}; pointer-events: ${rightHudOpen ? 'auto' : 'none'}; }
        
        .float-btn { position: absolute; top: 24px; z-index: 101; background: rgba(10,10,10,0.8); backdrop-filter: blur(10px); border: 1px solid #333; color: ${THEME.accent}; padding: 10px 16px; border-radius: 8px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 15px rgba(0,0,0,0.5); transition: all 0.2s ease; }
        .top-buttons { position: absolute; top: 24px; left: 50%; transform: translateX(-50%); display: flex; gap: 10px; z-index: 100; }
        .energy-hud { position: absolute; bottom: 24px; left: 50%; transform: translateX(-50%); display: flex; gap: 24px; background: rgba(5,5,5,0.85); padding: 16px 24px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); z-index: 90; backdrop-filter: blur(24px); }
        .bar-container { width: 12px; height: 60px; background: #222; border-radius: 6px; display: flex; align-items: flex-end; overflow: hidden; }
        .bar-fill { width: 100%; transition: height 0.05s linear; }
        .energy-col { display: flex; flex-direction: column; align-items: center; gap: 8px; }

        @media (max-width: 768px) {
          .hud-left, .hud-right { width: calc(100vw - 32px); left: 16px; right: 16px; top: 70px; max-height: calc(100vh - 160px); }
          .top-buttons { top: 10px; width: 100%; justify-content: center; transform: none; left: 0; padding: 0 10px; box-sizing: border-box; }
          .float-btn { top: auto; bottom: 24px; font-size: 12px; padding: 8px 12px; }
          .float-btn.left { left: 16px; }
          .float-btn.right { right: 16px; }
          .energy-hud { bottom: 80px; transform: translateX(-50%) scale(0.8); }
        }
      `}</style>
      
      <div style={{ position: 'fixed', inset: 0, color: '#EDEDED' }}>
        <Canvas shadows gl={{ antialias: true, toneMapping: THREE.ReinhardToneMapping, preserveDrawingBuffer: true }} camera={{ position: [0, 10, 40], fov: 45 }} dpr={[1, 1.5]}>
          <Scene3D 
            simData={data ? data.simulation_data : null} 
            playbackSpeed={playbackSpeed} 
            showVectors={showVectors} 
            ghostData={ghostData} 
            activeModel={activeModel}
            s0={s0} setS0={setS0}
            angle={angle} setAngle={setAngle}
            clearSimulation={clearSimulation}
            viewMode={viewMode}
            manualProgress={manualProgress}
          />
        </Canvas>

        <div className="top-buttons">
           <button onClick={() => setViewMode(prev => prev === '3D' ? '2D' : '3D')} style={{ background: 'rgba(10,10,10,0.8)', border: `1px solid ${THEME.accent}`, color: THEME.accent, borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold', backdropFilter: 'blur(10px)' }}>
             {viewMode === '3D' ? '🎥 3D' : '📐 2D'}
           </button>
           <button onClick={takeScreenshot} style={{ background: 'rgba(10,10,10,0.8)', border: '1px solid #444', color: '#FFF', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold', backdropFilter: 'blur(10px)' }}>
             📸 Foto
           </button>
        </div>

        {!leftHudOpen && (
          <button className="float-btn left" onClick={() => { setLeftHudOpen(true); if(isMobile) setRightHudOpen(false); }}>
            ⚙️ Controles
          </button>
        )}
        
        <div className="hud-panel hud-left">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ width: '16px', height: '16px', borderRadius: '50%', background: `linear-gradient(135deg, ${THEME.accent}, ${THEME.descida})`, boxShadow: `0 0 15px ${THEME.accent}` }}></div>
              <h1 style={{ fontSize: '18px', margin: 0, color: '#FFF', fontWeight: '800' }}>ExplainLab Pro</h1>
            </div>
            <button onClick={() => setLeftHudOpen(false)} style={closeBtnStyle}>✕</button>
          </div>
          
          <select value={activeModel} onChange={e => {setActiveModel(e.target.value); clearSimulation();}} style={{ width: '100%', padding: '12px', background: 'rgba(0,0,0,0.5)', color: '#FFF', border: '1px solid #333', borderRadius: '8px', outline: 'none' }}>
            <option value="inclined_plane">📐 Rampa com Atrito</option>
            <option value="projectile_motion">🏹 Lançamento Oblíquo</option>
            <option value="horizontal_mruv">🚗 MRUV Horizontal</option>
            <option value="vertical_motion">🪂 Lançamento Vertical</option>
          </select>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>{renderInputs()}</div>

          <button onClick={fetchSimulation} disabled={loading} style={{ width: '100%', padding: '14px', background: `linear-gradient(90deg, ${THEME.accent}, ${THEME.normal})`, color: '#000', borderRadius: '8px', fontWeight: '800', border: 'none', cursor: 'pointer' }}>
            {loading ? "CALCULANDO..." : "SIMULAR FÍSICA"}
          </button>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', background:'rgba(255,255,255,0.03)', padding:'12px', borderRadius:'8px' }}>
             <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <button onClick={() => setPlaybackSpeed(prev => prev === 0 ? 1 : 0)} style={{ padding: '6px 10px', background: playbackSpeed === 0 ? THEME.atrito : '#222', color: '#FFF', border: 'none', borderRadius: '6px' }}>
                  {playbackSpeed === 0 ? '▶' : '❚❚'}
                </button>
                <span style={{ fontSize: '10px', color: '#888' }}>{playbackSpeed === 0 ? "Manual" : "Auto"}</span>
             </div>
             <input type="range" min="0" max="1" step="0.01" value={playbackSpeed === 0 ? manualProgress : 1} onChange={e => { setPlaybackSpeed(0); setManualProgress(parseFloat(e.target.value)); }} style={{ width: '100%', accentColor: THEME.accent }} />
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}><input type="checkbox" checked={showVectors} onChange={e => setShowVectors(e.target.checked)} /><label style={{ fontSize: '12px', color: '#CCC' }}>Vetores 3D</label></div>

          {data && (
            <div style={{ marginTop: '10px', paddingTop: '20px', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
              <div style={{ fontSize: '12px', color: '#DDD', display: 'flex', flexDirection: 'column', gap: '6px' }}>{renderMetrics()}</div>
            </div>
          )}
        </div>

        {data && (
          <div className="energy-hud">
             <div className="energy-col">
               <div className="bar-container"><div id="bar-ec" className="bar-fill" style={{background: THEME.velocidade, height: '0%'}}></div></div>
               <span style={{fontSize: '9px', fontWeight: 'bold', color: THEME.velocidade}}>Ec</span>
             </div>
             <div className="energy-col">
               <div className="bar-container"><div id="bar-ep" className="bar-fill" style={{background: THEME.accent, height: '0%'}}></div></div>
               <span style={{fontSize: '9px', fontWeight: 'bold', color: THEME.accent}}>Ep</span>
             </div>
             {activeModel === 'inclined_plane' && (
               <div className="energy-col">
                 <div className="bar-container"><div id="bar-et" className="bar-fill" style={{background: THEME.atrito, height: '0%'}}></div></div>
                 <span style={{fontSize: '9px', fontWeight: 'bold', color: THEME.atrito}}>Calor</span>
               </div>
             )}
          </div>
        )}

        {data && !rightHudOpen && (
          <button className="float-btn right" onClick={() => { setRightHudOpen(true); if(isMobile) setLeftHudOpen(false); }}>
            ∑ Fórmulas
          </button>
        )}

        {data && (
          <div className="hud-panel hud-right">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
              <h2 style={{ fontSize: '14px', color: '#888', textTransform: 'uppercase', margin: 0 }}>Engenharia Reversa</h2>
              <button onClick={() => setRightHudOpen(false)} style={closeBtnStyle}>✕</button>
            </div>
            <div style={{ flex: 1 }}>
              {data.explanation_steps.map(step => (
                <div key={step.step} style={{ marginBottom: '28px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
                    <div style={{ width: '24px', height: '24px', borderRadius: '50%', background: 'rgba(0,229,255,0.1)', color: THEME.accent, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', fontWeight: 'bold' }}>{step.step}</div>
                    <h4 style={{ fontSize: '14px', color: '#FFF', margin: 0 }}>{step.title}</h4>
                  </div>
                  <p style={{ fontSize: '13px', color: '#AAA', margin: '0 0 14px 34px' }}>{step.text}</p>
                  <div style={{ marginLeft: '34px', background: '#050505', padding: '16px', borderRadius: '10px', border: '1px solid #222' }}>
                   <BlockMath 
  math={
    (step.equation_latex || "")
      .replace(/\\t/g, "")   // remove \t
      .replace(/\\n/g, "")   // remove \n
      .replace(/\\r/g, "")   // remove \r
  } 
  renderError={(error) => (
    <div style={{ color: '#ff4444', background: '#330000', padding: '10px', borderRadius: '8px', border: '1px solid red', marginTop: '10px' }}>
      <strong style={{fontSize: '14px'}}>🚨 O MOTIVO DO ERRO:</strong><br/>
      <span style={{fontSize: '12px', fontFamily: 'monospace'}}>{error.message}</span>
    </div>
  )} 
/>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        <VectorLegend show={showVectors} activeModel={activeModel} hasFriction={muStatic > 0 || muKinetic > 0} />
      </div>
    </>
  );
}