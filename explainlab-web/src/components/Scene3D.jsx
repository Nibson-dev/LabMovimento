import React, { useState, useRef, useEffect, useMemo } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Stars, Line, Text, MeshReflectorMaterial, Float, Environment, Trail } from '@react-three/drei';
import { EffectComposer, Bloom } from '@react-three/postprocessing';
import * as THREE from 'three';
import { THEME } from '../theme';

const ReflectiveGround = () => (
  <group position={[0, -0.01, 0]}>
    <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
      <planeGeometry args={[300, 300]} />
      <MeshReflectorMaterial blur={[100, 50]} resolution={512} mixBlur={0.5} mixStrength={10} roughness={1} depthScale={1} minDepthThreshold={0.4} maxDepthThreshold={1.4} color="#0f0f0f" metalness={0.6} mirror={1} />
    </mesh>
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, 0]}><planeGeometry args={[300, 300]} /><meshBasicMaterial color={THEME.chaoGrid} wireframe transparent opacity={0.08} /></mesh>
    {/* NOVIDADE: Grid Milimetrado */}
    <gridHelper args={[300, 60, THEME.accent, '#222222']} position={[0, 0.02, 0]} />
  </group>
);

const AngleArc = ({ b, angleDegrees }) => {
  const rad = (angleDegrees * Math.PI) / 180; const radius = Math.max(1.5, Math.min(3, b / 3));
  const thetaStart = Math.PI / 2 - rad; const labelX = -Math.cos(rad / 2) * (radius + 0.6); const labelY = Math.sin(rad / 2) * (radius + 0.6);
  return (
    <group position={[b/2, 0, 0]}>
      <mesh><ringGeometry args={[radius, radius + 0.05, 32, 1, thetaStart, rad]} /><meshBasicMaterial color={THEME.accent} side={THREE.DoubleSide} transparent opacity={0.8} toneMapped={false} /></mesh>
      <Text position={[labelX, labelY, 0]} fontSize={0.6} color={THEME.accent} outlineWidth={0.04} outlineColor="#000">θ</Text>
    </group>
  );
};

const VibrantInclinedPlane = ({ rampLength, angleDegrees, h, b }) => {
  const depth = 3;
  const geometry = useMemo(() => {
    const geo = new THREE.BufferGeometry();
    const vertices = new Float32Array([-b/2, 0, depth/2, b/2, 0, depth/2, b/2, 0, -depth/2, -b/2, 0, -depth/2, -b/2, h, depth/2, -b/2, h, -depth/2]);
    geo.setIndex([ 0,1,4,  3,5,2,  0,4,5, 0,5,3,  1,2,5, 1,5,4,  0,3,2, 0,2,1 ]);
    geo.setAttribute('position', new THREE.BufferAttribute(vertices, 3)); geo.computeVertexNormals(); return geo;
  }, [b, h, depth]);
  return (
    <group>
      <mesh geometry={geometry} castShadow receiveShadow><meshStandardMaterial color="#0a0a0a" transparent opacity={0.9} roughness={0.1} metalness={0.5} /></mesh>
      <Line points={[[-b/2, 0, 0], [b/2, 0, 0], [-b/2, h, 0], [-b/2, 0, 0]]} color={THEME.accent} lineWidth={1.5} toneMapped={false} />
      <AngleArc b={b} angleDegrees={angleDegrees} />
    </group>
  );
};

// NOVIDADE: Câmera Inteligente agora respeita o Modo 2D/3D
const CameraManager = ({ simData, viewMode }) => {
  const { camera, controls } = useThree();
  useEffect(() => {
    if (viewMode === '2D') {
       // Trava a câmera perfeitamente de lado (Ortogonal Falsa)
       camera.position.set(0, 15, 60);
       if (controls) {
         controls.target.set(0, 5, 0);
         controls.minAzimuthAngle = 0; controls.maxAzimuthAngle = 0;
         controls.minPolarAngle = Math.PI / 2; controls.maxPolarAngle = Math.PI / 2;
       }
       return;
    } else {
       // Destrava para o 3D Livre
       if (controls) {
         controls.minAzimuthAngle = -Infinity; controls.maxAzimuthAngle = Infinity;
         controls.minPolarAngle = 0; controls.maxPolarAngle = Math.PI / 2;
       }
    }

    if (!simData) return;
    const type = simData.type;
    if (type === 'projectile_motion') {
      const r = simData.metrics.range_m; const h = simData.metrics.h_max_m; const maxD = Math.max(r, h);
      camera.position.set(r / 2, h / 2 + maxD * 0.3, maxD * 0.8 + 15);
      if (controls) controls.target.set(r / 2, h / 3, 0);
    } else if (type === 'horizontal_mruv') {
      const s0 = simData.parameters?.s0 || 0; const stop = simData.metrics.stop_pos_m || s0 + 20;
      const center = (s0 + stop) / 2; const dist = Math.abs(stop - s0);
      camera.position.set(center, 8, dist * 0.8 + 20);
      if (controls) controls.target.set(center, 0, 0);
    } else {
      camera.position.set(0, 10, 40); if (controls) controls.target.set(0, 5, 0);
    }
  }, [simData, camera, controls, viewMode]);
  return null;
};

const DynamicVectors = ({ position, angleDegrees, show, type, physics, currentVel, currentVx, currentVy, gravity, simData }) => {
  if (!show) return null;
  const textStyle = { fontSize: 0.3, color: "#FFF", outlineWidth: 0.04, outlineColor: "#000", anchorX: "center", anchorY: "middle" };
  const gLen = 2.0;

  if (type === 'vertical_motion') {
    const velMag = Math.abs(currentVel) * 0.18; const velDir = currentVel >= 0 ? new THREE.Vector3(0, 1, 0) : new THREE.Vector3(0, -1, 0);
    return (
      <group position={position}>
        <primitive object={new THREE.ArrowHelper(new THREE.Vector3(0,-1,0), new THREE.Vector3(0.6, 0, 0), gLen, THEME.weight, 0.4, 0.2)} /><Text position={[1.4, -1, 0]} {...textStyle}>g</Text>
        {velMag > 0.1 && (<><primitive object={new THREE.ArrowHelper(velDir, new THREE.Vector3(-0.6, 0, 0), velMag, THEME.velocidade, 0.4, 0.2)} /><Text position={[-1.4, currentVel >= 0 ? velMag/2 : -velMag/2, 0]} {...textStyle}>v</Text></>)}
      </group>
    );
  }

  if (type === 'projectile_motion') {
    const vTotal = new THREE.Vector3(currentVx, currentVy, 0); const vTotalMag = vTotal.length() * 0.15; vTotal.normalize();
    const vxMag = Math.abs(currentVx) * 0.15; const vyMag = Math.abs(currentVy) * 0.15;
    const vyDir = currentVy >= 0 ? new THREE.Vector3(0, 1, 0) : new THREE.Vector3(0, -1, 0);
    return (
      <group position={position}>
        <primitive object={new THREE.ArrowHelper(new THREE.Vector3(0,-1,0), new THREE.Vector3(0, 0, 0), gLen, THEME.weight, 0.4, 0.2)} /><Text position={[0, -gLen-0.3, 0]} {...textStyle}>g</Text>
        {vTotalMag > 0.1 && <primitive object={new THREE.ArrowHelper(vTotal, new THREE.Vector3(0, 0, 0), vTotalMag, THEME.velocidade, 0.4, 0.2)} />}
        {vxMag > 0.1 && <primitive object={new THREE.ArrowHelper(new THREE.Vector3(1,0,0), new THREE.Vector3(0, 0, 0), vxMag, THEME.vx, 0.3, 0.15)} />}
        {vyMag > 0.1 && <primitive object={new THREE.ArrowHelper(vyDir, new THREE.Vector3(0, 0, 0), vyMag, THEME.vy, 0.3, 0.15)} />}
      </group>
    );
  }

  if (type === 'horizontal_mruv') {
      const vMag = Math.abs(currentVel) * 0.2; const vDir = currentVel >= 0 ? new THREE.Vector3(1, 0, 0) : new THREE.Vector3(-1, 0, 0);
      const aVal = simData?.parameters?.a || 0; 
      const aMag = Math.abs(aVal) * 0.5; const aDir = aVal >= 0 ? new THREE.Vector3(1, 0, 0) : new THREE.Vector3(-1, 0, 0);
      return (
          <group position={position}>
              {vMag > 0.1 && <primitive object={new THREE.ArrowHelper(vDir, new THREE.Vector3(0, 1.0, 0), vMag, THEME.velocidade, 0.4, 0.2)} />}
              {aMag > 0.1 && <primitive object={new THREE.ArrowHelper(aDir, new THREE.Vector3(0, 1.4, 0), aMag, THEME.aceleracao, 0.4, 0.2)} />}
              <Text position={[0, 2.0, 0]} {...textStyle}>{currentVel.toFixed(1)} m/s</Text>
          </group>
      )
  }

  if (type === 'inclined_plane' && physics) {
    const rad = (angleDegrees * Math.PI) / 180; const baseScale = 4.0 / (physics.weight_N || 1);
    const lenP = Math.max(0.5, physics.weight_N * baseScale); const lenN = Math.max(0.5, physics.normal_force_N * baseScale);
    const lenPx = Math.max(0.5, physics.px_N * baseScale); const lenFat = Math.max(0.5, physics.friction_force_N * baseScale);
    return (
      <group position={position}>
        <primitive object={new THREE.ArrowHelper(new THREE.Vector3(0,-1,0), new THREE.Vector3(0,0,0), lenP, THEME.weight, 0.4, 0.2)} />
        <primitive object={new THREE.ArrowHelper(new THREE.Vector3(Math.sin(rad), Math.cos(rad), 0), new THREE.Vector3(0,0,0), lenN, THEME.normal, 0.4, 0.2)} />
        <primitive object={new THREE.ArrowHelper(new THREE.Vector3(Math.cos(rad), -Math.sin(rad), 0), new THREE.Vector3(0,0,0), lenPx, THEME.descida, 0.4, 0.2)} />
        {physics.friction_force_N > 0 && (<primitive object={new THREE.ArrowHelper(new THREE.Vector3(-Math.cos(rad), Math.sin(rad), 0), new THREE.Vector3(0,0,0), lenFat, THEME.atrito, 0.4, 0.2)} />)}
      </group>
    );
  }
  return null;
};

const GhostTrajectory = ({ ghostData }) => {
  if (!ghostData) return null;
  const points = [];
  const times = ghostData.time_array;
  for (let i = 0; i < times.length; i++) {
    let x=0, y=0, z=0;
    if (ghostData.type === 'projectile_motion') { x = ghostData.position_x_array[i]; y = ghostData.position_y_array[i]; }
    if (ghostData.type === 'vertical_motion') { y = ghostData.position_y_array[i]; }
    if (ghostData.type === 'horizontal_mruv') { x = ghostData.position_s_array[i]; }
    if (ghostData.type === 'inclined_plane') {
        const rad = (ghostData.angle_degrees * Math.PI)/180; const rLen = ghostData.ramp_length_m;
        const h = Math.sin(rad)*rLen; const b = Math.cos(rad)*rLen; const s = ghostData.position_s_array[i];
        x = -(b/2) + Math.cos(rad)*s; y = h - Math.sin(rad)*s;
    }
    const yOffset = ghostData.type === 'horizontal_mruv' ? 0.25 : 0.51;
    points.push(new THREE.Vector3(x, y + yOffset, z));
  }
  return (
    <group>
      <Line points={points} color="#888888" lineWidth={3} dashed dashSize={0.5} gapSize={0.2} opacity={0.6} transparent />
      <Text position={points[points.length-1].clone().add(new THREE.Vector3(0, 1, 0))} fontSize={0.4} color="#888">Anterior</Text>
    </group>
  );
};

export default function Scene3D({ simData, playbackSpeed, showVectors, ghostData, activeModel, s0, setS0, angle, setAngle, clearSimulation, viewMode, manualProgress }) {
  const objectRef = useRef(); const pointLightRef = useRef(); 
  const [currentPos, setCurrentPos] = useState(new THREE.Vector3(0, 0, 0));
  const [currentVel, setCurrentVel] = useState(0); const [currentVx, setCurrentVx] = useState(0); const [currentVy, setCurrentVy] = useState(0);
  const simTime = useRef(0);
  
  const [dragType, setDragType] = useState(null);

  const type = simData?.type || activeModel;
  const isInclined = type === 'inclined_plane'; const isVertical = type === 'vertical_motion';
  const isProjectile = type === 'projectile_motion'; const isMRUV = type === 'horizontal_mruv';

  useEffect(() => {
    if (!simData && objectRef.current) {
       if (isMRUV) objectRef.current.position.set(s0, 0.25, 0);
       else if (isProjectile || isVertical) objectRef.current.position.set(0, 0.51, 0);
       else if (isInclined) {
          const rLen = 15; const rad = (angle * Math.PI) / 180;
          const h = Math.sin(rad) * rLen; const b = Math.cos(rad) * rLen;
          objectRef.current.position.set(-(b/2), h + 0.51, 0);
          objectRef.current.rotation.z = -rad;
       }
    }
  }, [simData, isMRUV, isProjectile, isVertical, isInclined, s0, angle]);

  // Reseta o tempo se a simulação mudar, ou se der play de novo
  useEffect(() => { if(playbackSpeed > 0) simTime.current = 0; }, [simData]);

  useFrame((state, delta) => {
    if (!simData || !simData.time_array || !objectRef.current) return;
    
    const times = simData.time_array; const maxTime = times[times.length - 1];
    
    // NOVIDADE: Scrubber (Controle de Tempo Manual)
    if (playbackSpeed === 0 && manualProgress !== undefined) {
       simTime.current = maxTime * manualProgress;
    } else {
       simTime.current += delta * playbackSpeed;
       if (simTime.current > maxTime + 1.5) { simTime.current = 0; } 
    }

    const t = Math.min(simTime.current, maxTime);
    let posX = 0, posY = 0; let vel = 0, vx = 0, vy = 0;
    let dataArrayS, dataArrayX, dataArrayY;

    if (isInclined) dataArrayS = simData.position_s_array;
    else if (isVertical) dataArrayY = simData.position_y_array;
    else if (isProjectile) { dataArrayX = simData.position_x_array; dataArrayY = simData.position_y_array; }
    else if (isMRUV) dataArrayS = simData.position_s_array;

    const interpolate = (arr, i, prog) => arr[i] + (arr[i+1] - arr[i]) * prog;

    for (let i = 0; i < times.length - 1; i++) {
      if (t >= times[i] && t <= times[i + 1]) {
        const progress = (t - times[i]) / (times[i + 1] - times[i]);
        if (isInclined || isMRUV) posX = interpolate(dataArrayS, i, progress);
        if (isVertical) posY = interpolate(dataArrayY, i, progress);
        if (isProjectile) { posX = interpolate(dataArrayX, i, progress); posY = interpolate(dataArrayY, i, progress); }

        if (simData.velocity_v_array) vel = interpolate(simData.velocity_v_array, i, progress);
        if (simData.velocity_vx_array) vx = interpolate(simData.velocity_vx_array, i, progress);
        if (simData.velocity_vy_array) vy = interpolate(simData.velocity_vy_array, i, progress);
        break;
      }
    }

    const yOffset = isMRUV ? 0.25 : 0.51; 
    if (isVertical) objectRef.current.position.set(0, posY + yOffset, 0);
    else if (isMRUV) objectRef.current.position.set(posX, yOffset, 0);
    else if (isProjectile) objectRef.current.position.set(posX, posY + yOffset, 0);
    else if (isInclined) {
      const rLen = simData.ramp_length_m; const rad = (simData.angle_degrees * Math.PI) / 180;
      const h = Math.sin(rad) * rLen; const b = Math.cos(rad) * rLen;
      objectRef.current.position.set(-(b/2) + Math.cos(rad) * posX, h - Math.sin(rad) * posX + yOffset, 0);
      objectRef.current.rotation.z = -rad;
    }
    
    const m = simData.parameters?.mass || 10; 
    const g = simData.gravity_m_s2 || simData.parameters?.gravity || 9.8;
    let currentH = 0;
    if (isVertical || isProjectile) currentH = posY;
    if (isInclined) currentH = Math.max(0, (Math.sin(simData.angle_degrees * Math.PI / 180) * simData.ramp_length_m) - (Math.sin(simData.angle_degrees * Math.PI / 180) * posX));
    
    const v2 = isProjectile ? ((vx * vx) + (vy * vy)) : (vel * vel);
    const ec = 0.5 * m * v2;
    const ep = m * g * currentH;
    let termica = 0;
    if (isInclined && simData.physics?.friction_force_N) { termica = simData.physics.friction_force_N * posX; } 
    const energiaTotal = (ec + ep + termica) || 1; 

    const ecBar = document.getElementById('bar-ec');
    const epBar = document.getElementById('bar-ep');
    const etBar = document.getElementById('bar-et');
    if (ecBar) ecBar.style.height = `${(ec / energiaTotal) * 100}%`;
    if (epBar) epBar.style.height = `${(ep / energiaTotal) * 100}%`;
    if (etBar) etBar.style.height = `${(termica / energiaTotal) * 100}%`;

    setCurrentPos(objectRef.current.position.clone()); setCurrentVel(vel); setCurrentVx(vx); setCurrentVy(vy);
    if (pointLightRef.current) pointLightRef.current.position.copy(objectRef.current.position);
  });

  const h_max = simData?.max_height_m || simData?.metrics?.h_max_m || 0;
  const range_x = simData?.metrics?.range_m || 0;
  const stop_pos = simData?.metrics?.stop_pos_m;
  const s0_pos = simData?.parameters?.s0;

  return (
    <>
      <CameraManager simData={simData} viewMode={viewMode} />
      <Environment preset="night" />
      <color attach="background" args={['#020202']} /> <fog attach="fog" args={['#020202', 20, 150]} />
      <Stars radius={100} count={1500} factor={3} fade />
      <ambientLight intensity={0.2} />
      <directionalLight position={[10, 30, 20]} intensity={1.5} castShadow shadow-mapSize={[2048, 2048]} />
      <pointLight ref={pointLightRef} color={THEME.accent} intensity={2} distance={20} decay={2} castShadow />
      
      <ReflectiveGround />
      <GhostTrajectory ghostData={ghostData} />

      {/* PLANO INVISÍVEL DE RAYCAST */}
      <mesh
        visible={false}
        position={[0, 0, 0]}
        onPointerMove={(e) => {
          if (!dragType) return;
          if (dragType === 's0') {
             setS0(Math.round(e.point.x)); 
          } else if (dragType === 'angle') {
             let deg = Math.round(Math.atan2(e.point.y, e.point.x) * (180 / Math.PI));
             deg = Math.max(0, Math.min(89, deg)); // Trava entre 0 e 89 graus
             setAngle(deg);
          }
        }}
        onPointerUp={() => { setDragType(null); document.body.style.cursor = 'auto'; }}
      >
        <planeGeometry args={[1000, 1000]} />
      </mesh>

      {isMRUV && (
        <group position={[0, 0.02, 0]}>
          <Line points={[[-100, 0, 1], [100, 0, 1]]} color="#333" lineWidth={2} dashed />
          <Line points={[[-100, 0, -1], [100, 0, -1]]} color="#333" lineWidth={2} dashed />
          {!simData && (
            <group position={[s0, 0, 0]}>
              <mesh position={[0, 0.5, 0]} onPointerOver={(e) => { e.stopPropagation(); document.body.style.cursor = 'ew-resize'; }} onPointerOut={() => { if(!dragType) document.body.style.cursor = 'auto'; }} onPointerDown={(e) => { e.stopPropagation(); setDragType('s0'); clearSimulation(); document.body.style.cursor = 'grabbing'; }}>
                <boxGeometry args={[3, 2, 2]} />
                <meshBasicMaterial visible={false} />
              </mesh>
              <Line points={[[0, 0, 1.5], [0, 0, -1.5]]} color="#00ff00" lineWidth={3} />
              <Text position={[0, -0.5, 2]} rotation={[-Math.PI/2, 0, 0]} fontSize={0.8} color="#00ff00">Arraste-me: S0={s0}</Text>
            </group>
          )}
        </group>
      )}

      {/* NOVO: DRAG-AND-DROP DA RAMPA (CONSERTADO!) */}
      {!simData && (isProjectile || isInclined) && (
        <group position={[0, 0, 0]}>
          <mesh position={[0,0,0]} onPointerOver={(e) => { e.stopPropagation(); document.body.style.cursor = 'ns-resize'; }} onPointerOut={() => { if(!dragType) document.body.style.cursor = 'auto'; }} onPointerDown={(e) => { e.stopPropagation(); setDragType('angle'); clearSimulation(); document.body.style.cursor = 'grabbing'; }}>
             <ringGeometry args={[1.5, 5.0, 32, 1, 0, Math.PI / 2]} />
             <meshBasicMaterial visible={false} />
          </mesh>
        </group>
      )}

      {isInclined && <VibrantInclinedPlane rampLength={simData?.ramp_length_m || 15} angleDegrees={simData?.angle_degrees || angle} h={Math.sin(((simData?.angle_degrees || angle) * Math.PI)/180) * (simData?.ramp_length_m || 15)} b={Math.cos(((simData?.angle_degrees || angle) * Math.PI)/180) * (simData?.ramp_length_m || 15)} />}

      {(isVertical || isProjectile) && h_max > 0.1 && (
        <group position={[isProjectile ? range_x/2 : 0, h_max, 0]}>
           <Line points={[[0,0,0], [0, -h_max, 0]]} color={THEME.accent} dashed />
           <Text position={[0, 0.5, 0]} fontSize={0.8} color={THEME.descida}>H_max: {h_max}m</Text>
        </group>
      )}
      
      {isProjectile && range_x > 0.1 && (
         <group position={[range_x, 0.1, 0]}>
            <Text position={[0, 0.5, 0]} fontSize={0.8} color={THEME.accent}>Alcance: {range_x}m</Text>
            <mesh rotation={[-Math.PI/2,0,0]}><ringGeometry args={[0.5, 0.8, 32]} /><meshBasicMaterial color={THEME.accent} /></mesh>
         </group>
      )}
      
      {isMRUV && stop_pos !== undefined && stop_pos !== null && (
         <group position={[stop_pos, 0.1, 0]}>
            <Line points={[[0, 0, 1.5], [0, 0, -1.5]]} color={THEME.aceleracao} lineWidth={3} />
            <Text position={[0, 0.5, 0]} fontSize={0.8} color={THEME.aceleracao}>Inversão: {stop_pos}m</Text>
         </group>
      )}

      <DynamicVectors position={currentPos} angleDegrees={simData?.angle_degrees || angle} show={showVectors} type={type} physics={simData?.physics} currentVel={currentVel} currentVx={currentVx} currentVy={currentVy} gravity={simData?.gravity_m_s2} simData={simData} />

      <Trail width={isMRUV ? 1.0 : 0.3} color={isMRUV ? THEME.aceleracao : THEME.accent} length={isMRUV ? 50 : 80} decay={1} local={false}>
        <Float speed={isInclined ? 0 : 2} rotationIntensity={isInclined ? 0 : (isMRUV ? 0 : 0.2)} floatIntensity={isInclined ? 0 : (isMRUV ? 0 : 0.1)}>
          <mesh ref={objectRef} castShadow>
            {isMRUV ? <boxGeometry args={[2, 0.5, 1]} /> : (isInclined ? <boxGeometry args={[1, 1, 1]} /> : <sphereGeometry args={[0.5, 64, 64]} />)}
            <meshPhysicalMaterial color="#fff" emissive="#ffffff" emissiveIntensity={0.8} metalness={1} roughness={0} toneMapped={false} />
          </mesh>
        </Float>
      </Trail>

      <EffectComposer disableNormalPass><Bloom luminanceThreshold={0.5} luminanceSmoothing={0.9} height={300} intensity={1.5} /></EffectComposer>
      
      <OrbitControls makeDefault enableDamping dampingFactor={0.05} enabled={!dragType && viewMode === '3D'} />
    </>
  );
}