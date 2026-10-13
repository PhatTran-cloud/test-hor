import {useLayoutEffect} from 'react';
import {cancelRender, continueRender, delayRender} from 'remotion';

type State = Record<string, number | string | boolean>;
export type V4Event = {id: string; kind: string; start_frame: number; peak_frame: number; end_frame: number};
export type V4Contract = {
  schema_version: 4; fps: 60; absolute_start_frame: number; duration_frames: number;
  contract_sha256: string;
  film_start_frame: number;
  objects: {id: string; initial_state: State}[];
  state_tracks: {object_id: string; property: string; from: number | string | boolean;
    to: number | string | boolean; start_frame: number; end_frame: number}[];
  shot: {id: string; start_frame: number; end_frame: number; pattern: {kind:string}; object_ids: string[]; events?: V4Event[];
    execution: {review_frames: number[]; objects: Record<string, {layout: {overlap_policy: string}}>}};
};

export const progress = (f: number, a: number, b: number) => Math.max(0, Math.min(1, (f-a)/Math.max(1, b-a)));
export const absoluteFrame = (c: V4Contract, local: number) => c.absolute_start_frame + local;
export const filmFrame = (c: V4Contract, local: number) => c.film_start_frame + local;
export function stateAt(c: V4Contract, id: string, frame: number): State {
  const object = c.objects.find(o => o.id === id);
  if (!object) throw new Error(`Unknown object ${id}`);
  const state = {...object.initial_state};
  for (const t of [...(c.state_tracks || [])].sort((a,b) => a.start_frame-b.start_frame)) {
    if (t.object_id !== id || frame < t.start_frame) continue;
    const p = progress(frame, t.start_frame, t.end_frame);
    state[t.property] = typeof t.from === 'number' && typeof t.to === 'number'
      ? t.from + (t.to-t.from)*p : p < 1 ? t.from : t.to;
  }
  return state;
}
export function envelope(e: V4Event | undefined, frame: number) {
  if (!e || frame < e.start_frame || frame >= e.end_frame) return 0;
  return frame <= e.peak_frame ? progress(frame, e.start_frame, e.peak_frame)
    : 1-progress(frame, e.peak_frame, e.end_frame);
}

// Construction primitives implement reading structures, not a generic art preset.
export const comparisonColumns = (ids: string[], left=360, right=1560) => ids.map((id,i) =>
  ({id, x: left + i*(right-left)/Math.max(1,ids.length-1)}));
export const timelinePositions = (milestones: {id: string; time: number}[], left=220, right=1700) => {
  const times = milestones.map(m => m.time), a=Math.min(...times), b=Math.max(...times);
  return milestones.map(m => ({...m, x: left+(right-left)*progress(m.time,a,b)}));
};
export const networkEdges = (points: Record<string,{x:number;y:number}>, connections: [string,string][]) =>
  connections.map(([a,b]) => ({a: points[a], b: points[b]}));
export const scaleView = (x:number,y:number,scale:number) => `translate(960 540) scale(${scale}) translate(${-x} ${-y})`;

/** Sample rendered SVG/HTML bounds at requested QA frames. Never label this art QA. */
export function useV4LayoutAudit(c: V4Contract, frame: number) {
  useLayoutEffect(() => {
    if ('metadata_only' in c && c.metadata_only) return;
    if (!c.shot.execution.review_frames.includes(frame)) return;
    const handle=delayRender(`V4 execution audit ${c.shot.id}/${frame}`);
    let pending=true, raf=0;
    const started=performance.now();
    const finish=()=>{if(pending){pending=false;continueRender(handle);}};
    const audit=()=>{
    // Remotion may mount a hidden composition while resolving the actual tree.
    // Observe the visible delivery tree after layout, including its first frame.
    const stage = Array.from(document.querySelectorAll('[data-v4-stage]')).find(n=>{
      const r=n.getBoundingClientRect();return r.width>0 && r.height>0;
    });
    if (!stage) {
      if(performance.now()-started>5000){cancelRender(new Error('V4 has no visible delivery stage'));finish();return;}
      raf=requestAnimationFrame(audit);return;
    }
    try {
    const root = stage.getBoundingClientRect();
    const sx=1920/root.width, sy=1080/root.height;
    const nodes = c.shot.object_ids.map(id => {
      const node = stage.querySelector(`[data-v4-object="${id}"]`);
      if (!node) throw new Error(`Missing rendered object ${id}`);
      const r=node.getBoundingClientRect();
      const bounds={x:(r.x-root.x)*sx,y:(r.y-root.y)*sy,w:r.width*sx,h:r.height*sy};
      const policy=c.shot.execution.objects[id].layout.overlap_policy;
      if (policy==='avoid' && (bounds.x < -2 || bounds.y < -2 || bounds.x+bounds.w > 1922 || bounds.y+bounds.h > 1082))
        throw new Error(`Rendered bounds leave frame: ${id} ${JSON.stringify({bounds,root:{width:root.width,height:root.height}})}`);
      return {id, ...bounds, policy};
    });
    for (let i=0;i<nodes.length;i++) for (let j=i+1;j<nodes.length;j++) {
      const a=nodes[i], b=nodes[j];
      if (a.policy!=='avoid' || b.policy!=='avoid') continue;
      const overlap=Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x)>2 && Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y)>2;
      if (overlap) throw new Error(`Unintended overlap ${a.id}/${b.id}`);
    }
    console.info('V4_EXECUTION_SAMPLE ' + JSON.stringify({shot:c.shot.id,frame,
      contract_sha256:c.contract_sha256, object_ids:nodes.map(n=>n.id), pattern_kind:c.shot.pattern.kind,
      bounds:Object.fromEntries(nodes.map(n=>[n.id,[n.x,n.y,n.w,n.h]]))}));
    finish();
    } catch(error) {cancelRender(error instanceof Error?error:new Error(String(error)));finish();}
    };
    audit();
    return ()=>{cancelAnimationFrame(raf);finish();};
  }, [c,frame]);
}
