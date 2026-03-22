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

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth <= 768);
    window.addEventListener('resize', handleResize);
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
    toast.success('📸 Screenshot salva!');
  };

  const fetchSimulation = async () => {
    if (gravity <= 0) return toast.error('Confira os valores!');
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
      toast.success('🚀 Física computada!');
    } catch (e) { 
      toast.error('Erro no servidor!');
    } 
    setLoading(false);
  };

  const hudStyle = { backgroundColor: 'rgba(5, 5, 5, 0.75)', backdropFilter: 'blur(24px)', borderRadius: '16px', border: '1px solid rgba(255, 255, 255, 0.08)', boxSizing: 'border-box', transition: 'all 0.4s ease' };
  const inputStyle = { width: '100%', padding: '10px', background: '#0a0a0a', border: '1px solid #222', color: '#FFF', borderRadius: '8px', marginTop: '6px' };
  const labelStyle = { fontSize: '10px', color: '#888', fontWeight: '700', letterSpacing: '1px' };

  return (
    <>
      <Toaster position="top-center" />
      <style>{`
        /* --- RESET E IMPORT KA-TEX --- */
        @import url('https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css');

        body, html, #root { margin: 0; padding: 0; width: 100vw; height: 100vh; overflow: hidden; background: #000; font-family: 'Inter', sans-serif; } 
        * { box-sizing: border-box; } 

        /* --- FORÇA BRUTA FORMULAS --- */
        .katex-display { margin: 15px 0 !important; display: block !important; width: 100% !important; text-align: center !important; }
        .katex { font-size: 1.2em !important; color: white !important; line-height: 1.2 !important; text-rendering: auto !important; }
        .katex .base { display: inline-block !important; margin-right: 0.1em !important; }
        .katex .mord { color: #00e5ff !important; }
        
        .hud-panel { position: absolute; z-index: 100; overflow-y: auto; }
        .hud-left { top: 24px; left: 24px; width: 360px; padding: 28px; transform: ${leftHudOpen ? 'translateX(0)' : 'translateX(-120%)'}; opacity: ${leftHudOpen ? 1 : 0}; }
        .hud-right { top: 24px; right: 24px; bottom: 24px; width: 420px; padding: 28px; transform: ${rightHudOpen ? 'translateX(0)' : 'translateX(120%)'}; opacity: ${rightHudOpen ? 1 : 0}; }
        
        .top-buttons { position: absolute; top: 24px; left: 50%; transform: translateX(-50%); display: flex; gap: 10px; z-index: 100; }
        .energy-hud { position: absolute; bottom: 24px; left: 50%; transform: translateX(-50%); display: flex; gap: 24px; background: rgba(5,5,5,0.85); padding: 16px 24px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); z-index: 90; backdrop-filter: blur(24px); }
        .bar-container { width: 12px; height: 60px; background: #222; border-radius: 6px; display: flex; align-items: flex-end; overflow: hidden; }
        .bar-fill { width: 100%; transition: height 0.05s linear; }

        @media (max-width: 768px) {
          .hud-left, .hud-right { width: calc(100vw - 32px); left: 16px; right: 16px; top: 70px; max-height: calc(100vh - 160px); }
          .top-buttons { top: 10px; width: 100%; justify-content: center; transform: none; left: 0; padding: 0 10px; box-sizing: border-box; }
          .energy-hud { bottom: 80px; transform: translateX(-50%) scale(0.8); }
        }
      `}</style>
      
      <div style={{ position: 'fixed', inset: 0, color: '#EDEDED' }}>
        <Canvas shadows gl={{ preserveDrawingBuffer: true }} camera={{ position: [0, 10, 40], fov: 45 }}>
          <Scene3D simData={data?.simulation_data} playbackSpeed={playbackSpeed} showVectors={showVectors} ghostData={ghostData} activeModel={activeModel} s0={s0} setS0={setS0} angle={angle} setAngle={setAngle} clearSimulation={clearSimulation} viewMode={viewMode} manualProgress={manualProgress} />
        </Canvas>

        <div className="top-buttons">
           <button onClick={() => setViewMode(v => v === '3D' ? '2D' : '3D')} style={{ background: '#000', border: '1px solid #00e5ff', color: '#00e5ff', padding: '8px 16px', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' }}>{viewMode === '3D' ? '🎥 3D' : '📐 2D'}</button>
           <button onClick={takeScreenshot} style={{ background: '#000', border: '1px solid #444', color: '#FFF', padding: '8px 16px', borderRadius: '8px', cursor: 'pointer' }}>📸 Foto</button>
        </div>

        <div className="hud-panel hud-left" style={hudStyle}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
            <h1 style={{ fontSize: '18px', margin: 0, color: '#FFF' }}>ExplainLab Pro</h1>
            <button onClick={() => setLeftHudOpen(false)} style={{ background: 'none', border: 'none', color: '#888', cursor: 'pointer' }}>✕</button>
          </div>
          
          <select value={activeModel} onChange={e => {setActiveModel(e.target.value); clearSimulation();}} style={{ width: '100%', padding: '12px', background: '#000', color: '#FFF', border: '1px solid #333', borderRadius: '8px' }}>
            <option value="inclined_plane">📐 Rampa com Atrito</option>
            <option value="projectile_motion">🏹 Lançamento Oblíquo</option>
            <option value="horizontal_mruv">🚗 MRUV Horizontal</option>
            <option value="vertical_motion">🪂 Lançamento Vertical</option>
          </select>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginTop: '12px' }}>{renderInputs()}</div>

          <button onClick={fetchSimulation} disabled={loading} style={{ width: '100%', padding: '14px', background: 'linear-gradient(90deg, #00e5ff, #00ff88)', color: '#000', borderRadius: '8px', fontWeight: '800', border: 'none', cursor: 'pointer', marginTop: '20px' }}>{loading ? "CALCULANDO..." : "SIMULAR"}</button>

          <div style={{ marginTop: '15px' }}>
             <button onClick={() => setPlaybackSpeed(s => s === 0 ? 1 : 0)} style={{ width: '40px', background: '#222', border: 'none', color: '#fff', borderRadius: '4px', cursor: 'pointer' }}>{playbackSpeed === 0 ? '▶' : 'II'}</button>
             <input type="range" min="0" max="1" step="0.01" value={playbackSpeed === 0 ? manualProgress : 1} onChange={e => { setPlaybackSpeed(0); setManualProgress(parseFloat(e.target.value)); }} style={{ width: 'calc(100% - 50px)', marginLeft: '10px', accentColor: '#00e5ff' }} />
          </div>
        </div>

        {data && (
          <div className="hud-panel hud-right" style={hudStyle}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
              <h2 style={{ fontSize: '14px', color: '#888', margin: 0 }}>ENGENHARIA REVERSA</h2>
              <button onClick={() => setRightHudOpen(false)} style={{ background: 'none', border: 'none', color: '#888', cursor: 'pointer' }}>✕</button>
            </div>
            {data.explanation_steps.map(step => (
              <div key={step.step} style={{ marginBottom: '24px' }}>
                <h4 style={{ color: '#00e5ff', fontSize: '14px', margin: '0 0 5px 0' }}>{step.step}. {step.title}</h4>
                <p style={{ fontSize: '13px', color: '#AAA', margin: '0 0 12px 0' }}>{step.text}</p>
                <div style={{ background: '#000', padding: '15px', borderRadius: '10px', border: '1px solid #222' }}>
                    <BlockMath math={step.equation_latex} />
                </div>
              </div>
            ))}
          </div>
        )}

        {data && (
          <div className="energy-hud">
             <div className="energy-col">
               <div className="bar-container"><div id="bar-ec" className="bar-fill" style={{background: THEME.velocidade, height: '0%'}}></div></div>
               <span style={{fontSize: '9px', color: THEME.velocidade}}>Ec</span>
             </div>
             <div className="energy-col">
               <div className="bar-container"><div id="bar-ep" className="bar-fill" style={{background: '#00e5ff', height: '0%'}}></div></div>
               <span style={{fontSize: '9px', color: '#00e5ff'}}>Ep</span>
             </div>
          </div>
        )}

        {!leftHudOpen && <button onClick={() => setLeftHudOpen(true)} style={{ position: 'absolute', bottom: '24px', left: '24px', background: '#000', color: '#00e5ff', border: '1px solid #00e5ff', padding: '12px', borderRadius: '8px', zIndex: 101 }}>⚙️</button>}
      </div>
    </>
  );
}