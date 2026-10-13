/** Absolute-section-frame sprite state for Remotion, Canvas or Three.js planes.
 * Not a rig/physics engine. Use the declared authored solver for complex contacts.
 */
export function validatePoseTrack(view, binding) {
  const keys=binding.pose_track;
  if (keys===undefined || keys===null) return;
  if (!Array.isArray(keys) || !keys.length || binding.loop)
    throw new Error('Explicit pose_track needs nonempty one-shot absolute-frame keys, not a loop');
  let previous=-1;
  for (const key of keys) {
    if (!Number.isInteger(key.frame) || key.frame<=previous || key.frame<binding.start_frame || key.frame>=binding.end_frame)
      throw new Error('Pose keys must be ordered absolute frames inside sprite playback');
    const pose=view.frames.find(p=>p.id===key.pose_id);
    if (!pose) throw new Error('Pose track references an unavailable view/pose');
    if (key.performance_state_id!==undefined && key.performance_state_id!==null && !(pose.performance_state_ids ?? []).includes(key.performance_state_id))
      throw new Error('Pose does not support the selected performance state');
    previous=key.frame;
  }
  if (keys[0].frame!==binding.start_frame) throw new Error('Pose track must establish the entry pose at playback start');
}

export function spriteState(asset, binding, frame) {
  if (!Number.isFinite(frame)) throw new Error('Frame must be finite');
  if (binding.contact_solver?.implementation) throw new Error('Use the authored contact solver');
  const view = asset.views.find(v => v.id === binding.view_id);
  if (!view?.frames.length) throw new Error('Missing registered sprite view');
  validatePoseTrack(view,binding);
  const total = view.frames.reduce((n,p) => n + p.hold_frames, 0);
  const elapsed = Math.max(0, frame - binding.start_frame);
  let t = binding.loop ? elapsed % total : Math.min(elapsed,total-1);
  let pose = view.frames.at(-1);
  for (const p of view.frames) {
    if (t < p.hold_frames) { pose=p; break; }
    t-=p.hold_frames;
  }
  let selectedKey=null;
  if (binding.pose_track?.length) {
    selectedKey=binding.pose_track[0];
    for (const key of binding.pose_track) {
      if (key.frame>frame) break;
      selectedKey=key;
    }
    pose=view.frames.find(p=>p.id===selectedKey.pose_id);
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
  const result={pose_id:pose.id,file:pose.file ?? null,root_position:root,
    image_position:root.map((x,j)=>x-pose.root_anchor[j]*scale),scale,contact,view_id:view.id,
    visible:frame>=binding.start_frame && frame<binding.end_frame};
  if (selectedKey?.performance_state_id!==undefined && selectedKey?.performance_state_id!==null)
    result.performance_state_id=selectedKey.performance_state_id;
  if ('member_count' in pose) result.member_count=pose.member_count;
  return result;
}
