import React from 'react';
import {AbsoluteFill,Composition,registerRoot,useCurrentFrame} from 'remotion';
import {absoluteFrame,comparisonColumns,envelope,progress,scaleView,stateAt,useV4LayoutAudit,V4Contract} from './v4-runtime';

type Props={durationInFrames:number; productionContract:V4Contract};
const veins=[-60,-30,0,30,60];
const Leaf=({id,x,y,glow=0,small=false}:{id:string;x:number;y:number;glow?:number;small?:boolean}) =>
  <g data-v4-object={id} transform={`translate(${x} ${y}) scale(${small?.72:1})`}>
    <path d="M0 165 C-215 65 -165 -100 0 -220 C165 -100 215 65 0 165Z"
      fill={`hsl(${147-glow*20} ${36+glow*25}% ${22+glow*18}%)`} stroke="#7aa584" strokeWidth={2}/>
    <path d="M0 165 Q-13 0 0 -207" fill="none" stroke="#b7ca8e" strokeWidth={4}/>
    {veins.map(v=><g key={v} opacity={.55+glow*.4} stroke="#a8c194" strokeWidth={2} fill="none">
      <path d={`M0 ${v+65} Q-65 ${v+25} ${-105+Math.abs(v)*.6} ${v-35}`}/>
      <path d={`M0 ${v+65} Q65 ${v+25} ${105-Math.abs(v)*.6} ${v-35}`}/>
    </g>)}
  </g>;
const Canopy=({frame}:{frame:number}) => <g>
  <rect width={1920} height={1080} fill="url(#air)"/>
  {[240,550,940,1270,1720].map((x,i)=><g key={x} opacity={.17+i*.014}>
    <path d={`M${x} 1100 Q${x-60} 600 ${x+40} -100`} stroke="#5d8d83" strokeWidth={80+i*13} fill="none"/>
    <path d={`M${x} 650 l-190 -240 M${x} 450 l200 -260`} stroke="#5d8d83" strokeWidth={19} fill="none"/>
  </g>)}
  {[0,1,2,3].map((i)=><path key={i} d={`M-90 ${830+i*60} Q${850+i*100} ${580+i*75} 2060 ${780+i*60}`}
    fill="none" stroke="#a3c8a9" strokeWidth={40} opacity={.022+progress(frame,0,180)*.005}/>) }
</g>;
// Illustrative signal metaphor, not a biochemical or growth-rate simulation.
const RainforestStudy:React.FC<Props>=({productionContract:c})=>{
  const local=useCurrentFrame(), frame=absoluteFrame(c,local);
  useV4LayoutAudit(c,frame);
  const lit=Number(stateAt(c,'lit_leaf',frame).response), shot=c.shot.id;
  const arrival=c.shot.events?.find(e=>e.id==='signal_arrival');
  const ring=envelope(arrival,frame);
  const comparison=comparisonColumns(['lit_leaf','shade_leaf'],640,1280);
  const signalTravel=progress(frame,c.shot.start_frame+18,arrival?.start_frame??110);
  const handoff=shot==='macro_insert'?progress(frame,c.shot.end_frame-60,c.shot.end_frame):0;
  const macro=shot==='macro_insert'?1+progress(frame,c.shot.start_frame,c.shot.end_frame-60)*1.8:1;
  const cameraTransform=shot==='macro_insert'?scaleView(640,560,macro):'translate(0 0)';
  return <AbsoluteFill style={{background:'#061b1f'}} data-v4-stage>
    <svg width={1920} height={1080} viewBox="0 0 1920 1080">
      <defs>
        <linearGradient id="air" x2=".7" y2="1"><stop stopColor="#071c26"/><stop offset="1" stopColor="#184539"/></linearGradient>
        <radialGradient id="warm"><stop stopColor="#e7cf87" stopOpacity=".13"/><stop offset="1" stopColor="#e7cf87" stopOpacity="0"/></radialGradient>
      </defs>
      <Canopy frame={frame}/>
      <ellipse cx={520} cy={250} rx={800} ry={610} fill="url(#warm)"/>
      <g transform={cameraTransform}>
        <path d="M600 1080 Q730 820 640 560 M1290 1080 Q1220 820 1280 560" stroke="#38694e" strokeWidth={18} fill="none"/>
        <Leaf id="lit_leaf" x={640} y={560} glow={lit}/>
        {shot!=='macro_insert' && <Leaf id="shade_leaf" x={1280} y={560}/>} 
        {shot==='canopy_cause' && <g data-v4-object="signal" opacity={1-progress(frame,(arrival?.start_frame??110)+2,(arrival?.peak_frame??126)+14)}>
          <path d="M340 130 L640 400" stroke="#e8c978" strokeWidth={3} opacity={.24}/>
          <circle cx={340+300*signalTravel} cy={130+270*signalTravel} r={12} fill="#f6d989"/>
          <circle cx={340+300*signalTravel} cy={130+270*signalTravel} r={26} fill="#f6d989" opacity={.09}/>
        </g>}
        {shot==='canopy_cause' && <g data-v4-object="leaf_response" opacity={ring}>
          <circle cx={640} cy={400} r={35+progress(frame,arrival?.start_frame??110,arrival?.end_frame??176)*65} stroke="#e8d48f" strokeWidth={2} fill="none"/>
        </g>}
        {shot==='comparison_hold' && <g data-v4-object="comparison_axis">
          <path d="M640 820 H1280" stroke="#8eb29e" strokeWidth={2}/>
          {comparison.map(p=><path key={p.id} d={`M${p.x} 805 v30`} stroke="#8eb29e" strokeWidth={2}/>)}
          <text x={640} y={890} fill="#e3d9ad" fontFamily="Georgia" fontSize={30} textAnchor="middle">signal received</text>
          <text x={1280} y={890} fill="#b8cbbd" fontFamily="Georgia" fontSize={30} textAnchor="middle">no signal</text>
        </g>}
        {shot==='macro_insert' && <g data-v4-object="vein_insert" opacity={.6} stroke="#ecd894" fill="none" strokeWidth={2}>
          {veins.map((v,i)=><circle key={v} cx={-105+Math.abs(v)*.6+640} cy={v-35+560}
            r={4+progress(frame,c.shot.start_frame+15+i*5,c.shot.end_frame-25)*5}/>)}
        </g>}
      </g>
      {/* Authored optical handoff: same leaf remains the source of the macro cut. */}
      <rect width={1920} height={1080} fill="#071c26" opacity={handoff*.65}/>
      <path d="M0 930 C110 735 200 920 370 820 C330 990 190 1060 0 1100Z" fill="#0b2929"/>
      <path d="M1920 0 C1760 150 1780 300 1560 330 C1600 100 1770 40 1920 0Z" fill="#0c2829"/>
    </svg>
  </AbsoluteFill>;
};
const defaults={durationInFrames:180,productionContract:{} as V4Contract};
const Root=()=> <Composition id="V4RainforestStudy" component={RainforestStudy} durationInFrames={180}
  fps={60} width={1920} height={1080} defaultProps={defaults}
  calculateMetadata={({props})=>({durationInFrames:props.durationInFrames})}/>;
registerRoot(Root);
