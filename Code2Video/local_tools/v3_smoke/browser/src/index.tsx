import React from 'react';
import {AbsoluteFill, Composition, registerRoot, useCurrentFrame, useVideoConfig} from 'remotion';
import {ThreeCanvas} from '@remotion/three';

type Event = {id: string; start: number; peak: number; end: number};
type Props = {durationInFrames: number; vfxEvents: Event[]; disableVfx?: boolean};

// Technical fixture, not a finished film or a planetary simulation. All state
// derives from frame; revisiting a frame never depends on prior playback.
const Diagram: React.FC<Props> = ({vfxEvents, disableVfx}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const x = 560 + Math.min(1, frame / fps) * 760;
  const event = vfxEvents.find((e) => e.id === 'arrival');
  const age = event ? frame / fps - event.start : -1;
  const visible = !disableVfx && event && age >= 0 && frame / fps <= event.end;
  return <AbsoluteFill style={{backgroundColor: '#05070D'}}>
    <svg width={1920} height={1080} viewBox="0 0 1920 1080">
      <path d="M560 540 L1320 540" stroke="#456878" strokeWidth={4}/>
      <circle cx={560} cy={540} r={90} fill="#102938" stroke="#9BBCCD" strokeWidth={3}/>
      <circle cx={1320} cy={540} r={90} fill="#102938" stroke="#9BBCCD" strokeWidth={3}/>
      <circle cx={x} cy={540} r={16} fill="#64D9E8"/>
      {visible && <circle cx={1320} cy={540} r={25 + age * 150}
        fill="none" stroke="#64D9E8" strokeWidth={3} opacity={Math.max(0, 1 - age / (event.end - event.start))}/>}
    </svg>
  </AbsoluteFill>;
};

const Spatial: React.FC<Props> = () => {
  const frame = useCurrentFrame();
  const {width, height, durationInFrames} = useVideoConfig();
  const a = .15 + (frame / durationInFrames) * 1.6;
  return <AbsoluteFill style={{backgroundColor: '#05070D'}}>
    <ThreeCanvas width={width} height={height} camera={{position: [0, 1.8, 6], fov: 42}}
      gl={{antialias: true}}>
      <ambientLight intensity={.45}/>
      <directionalLight position={[3, 5, 4]} intensity={2}/>
      <group rotation={[.3, -.4, 0]}>
        <mesh><sphereGeometry args={[1.25, 64, 48]}/><meshStandardMaterial color="#143F56" roughness={.7}/></mesh>
        <mesh rotation={[Math.PI / 2, 0, 0]}><torusGeometry args={[1.27, .012, 8, 128]}/><meshBasicMaterial color="#64D9E8"/></mesh>
        <mesh position={[1.29 * Math.cos(a), 0, 1.29 * Math.sin(a)]}>
          <sphereGeometry args={[.055, 20, 16]}/><meshStandardMaterial color="#FFAD72" roughness={.4}/>
        </mesh>
      </group>
    </ThreeCanvas>
  </AbsoluteFill>;
};

const defaults: Props = {durationInFrames: 120, vfxEvents: []};
const Root = () => <>
  <Composition id="V3Diagram" component={Diagram} durationInFrames={120} fps={60} width={1920} height={1080}
    defaultProps={defaults} calculateMetadata={({props}) => ({durationInFrames: props.durationInFrames})}/>
  <Composition id="V3Spatial" component={Spatial} durationInFrames={120} fps={60} width={1920} height={1080}
    defaultProps={defaults} calculateMetadata={({props}) => ({durationInFrames: props.durationInFrames})}/>
</>;
registerRoot(Root);
