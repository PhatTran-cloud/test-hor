/** Absolute-section-frame sprite state for Remotion, Canvas or Three.js planes.
 * Not a rig/physics engine. Use the declared authored solver for complex contacts.
 */
export function spriteState(asset, binding, frame) {
  if (!Number.isFinite(frame)) throw new Error('Frame must be finite');
  if (binding.contact_solver?.implementation) throw new Error('Use the authored contact solver');
  const view = asset.views.find(v => v.id === binding.view_id);
  if (!view?.frames.length) throw new Error('Missing registered sprite view');
  const total = view.frames.reduce((n,p) => n + p.hold_frames, 0);
  const elapsed = Math.max(0, frame - binding.start_frame);
  let t = binding.loop ? elapsed % total : Math.min(elapsed,total-1);
  let pose = view.frames.at(-1);
  for (const p of view.frames) {
    if (t < p.hold_frames) { pose=p; break; }
    t-=p.hold_frames;
  }
  const keys=binding.root_track;
  let root=[...keys.at(-1).position];
  if (frame<=keys[0].frame) root=[...keys[0].position];
  else for (let i=1;i<keys.length;i++) {
    const a=keys[i-1],b=keys[i];
    if (frame<=b.frame) {
      const f=(frame-a.frame)/(b.frame-a.frame);
      root=a.position.map((x,j)=>x+(b.position[j]-x)*f); break;
    }
  }
  const scale=binding.scale ?? 1;
  if (!(Number.isFinite(scale)&&scale>0)) throw new Error('Invalid sprite scale');
  let contact=null;
  for (const w of binding.contact_windows) if (frame>=w.start_frame && frame<w.end_frame) {
    const socket=w.socket==='ground' ? pose.ground_anchor : pose.sockets[w.socket];
    if (!socket) throw new Error('Missing contact socket');
    root=w.world_position.map((x,j)=>x-(socket[j]-pose.root_anchor[j])*scale);
    contact=w.socket; break;
  }
  return {pose_id:pose.id,file:pose.file ?? null,root_position:root,
    image_position:root.map((x,j)=>x-pose.root_anchor[j]*scale),scale,contact,view_id:view.id,
    visible:frame>=binding.start_frame && frame<binding.end_frame};
}
