# Current-session V4.1 horror authoring

Read HORROR_CONTRACT.md for the additive current artwork/cast/SFX fields.
No old provider reference below overrides it.


USER OVERRIDE (10 October 2026): Follow START_HERE.md's stepwise sequence.
Do only the current authorized step, report actual rule/skill application and
artifacts/unmet requirements, then stop. Earlier autonomous production guidance
is superseded. No self-authored easier acceptance or automatic PASS/continuation.
Both the current-step announcement and next-step proposal name the task,
rule/source, skills/references and concrete purposes, command/manual action,
input/output and stopping point. A next-step proposal is not executed; repeat
the announcement before acting on the human's next instruction. Use explicit
not-applicable reasons rather than inventing a skill or command.

The assistant in this conversation researches, directs, writes source and reviews
the rendered work. `prompts/v4.py` is the active authoring guidance. The original
stage1–stage5 API pipeline remains a legacy path; it does not automatically become
a semantic director. No CLI LLM adapter or external planning provider is required.

Start at `START_HERE.md`; use `local_tools/production.py` for new V4 work.
One `production_packet` lives in the plan: brief(audience/question/takeaway/
visual_thesis), research.sources(id/title/url/finding/visual_decision),
research.claims(id/text/kind/visual_treatment; factual claims need source_ids),
representative(shot_id/reason/acceptance), consulted_resources(skill/file/sha256/
applied_to/decision). Consulted resource hashes establish traceability, not
comprehension. Record actual full skill reading and relevant references, especially
the complete lowbudget3d + 3dviz-pro-max base for 3D. Frozen copies keep the
original resource_name; a renamed SKILL.md is not a substitute for a base reference.
Use `context --shot ID` for one focused execution card plus adjacent handoffs;
do not inject all historical guides/full neighboring cards into every shot prompt.

## Meaning before widgets

Choose a visual thesis: what can the image explain that narration alone cannot?
Each semantic beat changes understanding/expectation/world state: ID, purpose,
before, after, narration_anchor.segment_id, visual_evidence, completion, depends_on.
No beat/shot/animation count quotas. One shot may show multiple beats, and a beat
may cross shots. Dependencies complete before their dependent reveal.

Sections contain the complete narration and `narration_segments`: stable ID, text,
optional pause_after and delivery. These are recording passages, **not** a one-to-one
semantic beat requirement. Prepare speech first. Measured segment intervals are
honest coarse anchors; this workflow does not manufacture word-level alignment.
Split a recording passage or supply a separately verified finer authoring process
when a word-specific action is needed. OmniVoice acting direction is separate from supported null/whisper payload and needs audition.

## Three phases and one clock

1. `draft`: research, script, visual_system, beats, object briefs and shot cards.
2. `timed`: runner has frozen OmniVoice multi-speaker WAVs, SHA256, script hash, voice, speed, exact
   padded frame count and measured recording anchors. Author shot intervals now.
3. `authored`: complete source, execution mapping and contiguous shot intervals
   covering exactly the measured section. Render uses that WAV again; no second
   synthesis, time stretching, forced runtime, automatic filler or join padding.

Prepare removes provisional beat slots and records only anchor_interval. Multiple
semantic beats may share one recording passage; the director allocates their
actual intervals later. The WAV, script, anchor text/intervals, voice, speed and
frame clock must match the frozen measurement receipt. Ordinary measured joins
of >=1 second require an explicit story justification, not automatic padding.

All frames are section-absolute and end-exclusive at 60 fps. Browser local frame
plus `productionContract.absolute_start_frame` gives the section frame. Manim
receives the same JSON through `CODE2VIDEO_SHOT_CONTRACT`; `src/v4_runtime.py`
provides deterministic state/envelope helpers. The execution manifest also records
film-absolute offsets. Persistent `state_tracks` apply across shots, not per-shot
reset. Numeric tracks interpolate; discrete tracks switch at completion. A track
needs ID, object_id, property, from/to, start/end_frame and cause. This is an authored
state model, not a physical solver.
`filmFrame`/`film_frame` expose the film clock to authored sources. When the same
object ID occurs in another section, its initial_state must equal the previous
section's final state; use a different ID for a different object. Continuing
events declare carry_across_shots=true and later shots reference their event_ids.
The renderer receives the active event with its original envelope, not a restarted
copy at each cut. Each renderer still authors the appropriate visual realization.

## Artwork and shot cards

Record `content_profile.kind` as storytelling_rich, formula_math or mixed, plus
planned_manim_share while drafting if relevant. Current horror films with the
user-selected OverSimplified reference follow `OVERSIMPLIFIED_ILLUSTRATION.md`:
shared scene worlds, readable action/face/props, human-run prompts for all generated
items, uniform-green sources for alpha assets and local keying. Historical/other
rich storytelling consults
`docs/KAGE_VISUAL_REFERENCE.md`. Pure formula mathematics with Manim >=80% of
authored visual frames excludes Kage; the validator recomputes this policy from
actual duration, so changing shot counts cannot evade it.

Objects: stable identity, hero/support/environment role, initial_state and craft
brief with silhouette, construction, material, references and fidelity_limits.
Reference research must change concrete silhouette/material/behavior decisions.
Choose SVG/Canvas/illustration/media/procedural/imported assets intentionally.
Complete a representative difficult shot at 1080p60 before multiplying its style.
Do not default organisms to stick figures or complex heroes to spheres to avoid
the brief. User-selected simple cutout bodies/thin articulated limbs are a valid
design when they communicate identity, acting and contact; they still need review.

Shots: beat_ids, renderer/reason, visual_thesis, object_ids, attention, camera
purpose/implementation, pattern, events, handoff and execution bindings. Add
foreground/midground/background or secondary activity only when useful.
Execution maps every visible object ID to a source symbol, motion_mode, behavior
and layout.bounds `[x,y,width,height]` in delivery pixels, overlap_policy and
review_frames. Source symbol checks establish traceability, **not** proof that a
symbol draws the right thing. Review actual silhouette, occlusion, text bounds,
motion and sampled frames. Environment overlap can be intentional; labels need
readable reserved space. Plan bounds are not measured runtime bounds.
The browser helper `useV4LayoutAudit` measures tagged rendered SVG/HTML bounds at
requested samples and rejects unintended overlap among objects marked `avoid`.
`intentional` overlap needs a reason. This does not cover untagged text or replace
motion/occlusion review; author equivalent projected-bounds checks for 3D/Manim.

Runtime samples carry the renderer's contract hash, actual object IDs, reading
pattern and delivery-space bounds. Missing requested samples fail rendering.
Shot first/last frames and relevant event lead/peak/aftermath are added to samples;
this is a sampling floor, not a beat count or all-frame layout guarantee. The
browser audit waits for visible layout using delayRender; metadata-only evaluation
must not emit production observations. Manim sources use record_execution after
evaluating mobjects at each requested absolute frame; specialized 3D sources need
real projected bounds. Never manufacture bounds from the planned rectangle.

## Patterns are reading structures

- timeline: ordered milestones and time relation; implement the axis/world change.
- comparison: entities, variable and fair_conditions; make the comparison visible.
- before_after: same identity/condition, changed_property, visible connection.
- cause_effect: cause/result, transport, delayed response and visible consequence.
- flow/cycle/network/hub_spoke: meaningful connections/direction/feedback/hub.
- scale: reference and scale_relation; preserve orientation and explain changes.
- map: geographic data_sources, projection and legend. A textured globe alone
  does not implement a geographic explanation; numerical data needs provenance.
- evidence: sources and inference; never present generated art as observation.
- custom: reading_logic; no forced preset library.

Each pattern has entities and an implementation symbol pointing to actual source.
The browser runtime supplies timeline/comparison/network/scale layout helpers;
they are construction aids, not an automatic art engine. Map data, specialized
science and novel patterns still need authored implementation and review.

## Renderer and craft routing

Manim: proofs, geometry, mechanisms, exact transformations. Remotion: 2D art,
maps/data/media and compositing. Three.js: spatial worlds/materials/terrain,
objects/cameras with depth. Remotion may host its export. Three.js routes must
retain complete **lowbudget3d + 3dviz-pro-max**, including base references, assets,
materials, lighting and validation; a workflow string does not establish fidelity.
Read the relevant skill and full base before 3D authoring. Preserve scientific
representation/units/scale/provenance and distinguish illustration from simulation.

## V4.1: behavior-led 2.5D sprite animation

This addition applies to generated 2D sprites in a layered 2.5D scene. It is
authoring guidance, not a new schema or renderer. The horror fork adds explicit asset/cast/SFX validation described in HORROR_CONTRACT.md.
Keep schema_version=4 and `local_tools/production.py`. Spatial 3D work continues
through the complete lowbudget3d + 3dviz-pro-max route above.

**Behavior research precedes pose prompts.** Use script-to-visual-director to
identify the character's intention, emotional state, attention/gaze, story trigger
and the visible change the beat must communicate. Study relevant action footage,
pose/anatomy references or material/puppet construction. Record source, inspected
time/frame or page, observed mechanics and the concrete design decision in the
existing production_packet research and object craft brief. Separate observed
behavior from an authored supernatural/stylized departure; a style-only reference
or README GIF does not establish how an action works or how it was animated.

Use cinematic-motion-director's object-motion-physics and scene-motion-orchestration
references to analyze support, center of mass, weight transfer, force, gesture
arcs, contact/release, gaze timing, attached props and delayed cloth/hair response.
Describe preparation, action, reaction/follow-through and terminal state where
the behavior calls for them. Motivated stillness is valid; generic idle loops,
whole-image rocking or camera parallax cannot stand in for required acting.

Before artwork, specify the action's key poses and necessary intermediate states,
view/facing, silhouette, body proportions, prop ownership, foot/hand contact and
entry/exit state. Choose pose count and holds from action/readability, not a fixed
sprite quota. Timing is provisional until it is allocated against measured audio;
never invent word alignment. Do not require skeletal rigging for pose playback.
When deformation or another view is needed, request those assets explicitly.

Flow supplies generated artwork and poses, replacing the drawing backend. In the
current horror illustration route, export prompts only and let the human run Flow;
include props/backgrounds as well as character components and replacement poses.
Use visual-ip-illustrations's selected identity/style/composition/QA references
when that visual route is requested; it does not supply a sprite animator.
Generate reusable character poses, props and separable scene layers rather than
a flattened finished shot. Preserve original outputs and reference identity across
poses; identify required alpha/background separation, crop safety and occluded
parts. Do not accept identity/proportion drift or missing action states merely
because individual images look polished. Artwork remains its own review step.

During the separately authorized motion step, storyboard-motion-executor preserves
canonical asset/instance/pose IDs, beat timing, contacts, attention and continuity.
Register each pose's dimensions/crop, scale, root/ground anchor and relevant grip
sockets; record ordered frames, holds, playback cadence, loop or one-shot behavior
and final state in the existing craft/execution descriptions and authored source.
Keep world/root travel separate from frame-local pose changes so planted feet and
held props do not slide or detach. Sprite cadence may be lower than 60fps, but
encoded output remains 1920x1080 at 60fps. Select frames from absolute section time;
non-sequential seeking must reproduce the same pose and persistent state.
FG/MG/BG depth, occlusion and parallax must agree with the authored camera.

Review the pose contact sheet for identity/silhouette and the actual encoded clip
for acting, weight, contacts, frame registration/flicker, reveal timing, secondary
response, boundary/terminal state and seek behavior. Distinguish intentional holds
or stylization from defects. Still images cannot prove temporal quality; format
checks cannot approve acting. Report missing assets or failed motion explicitly,
then stop under START_HERE's human-directed steps. Do not auto-PASS or full-render.

## Motion, VFX, handoff, B-roll (all routes)

Apply script-to-visual-director, storyboard-motion-executor,
cinematic-motion-director and cinematic-vfx-director for relevant work. Object
motion modes: active, reactive, passive, optical, camera_induced. Stillness is valid;
sine motion everywhere is not direction. Events use stable IDs, source/targets,
cause, action, reaction, aftermath, implementation, start/peak/end_frame. VFX should
change the appropriate world/light/optics and leave the required consequence.

Handoff: cut/match/follow/scale/authored_bridge/fade, reason, carry_state and
implementation for anything except a cut. Author the handoff inside the outgoing/
incoming shot allocation. The assembler cuts contiguous clips without adding
dead air or overlapping narration. It does not manufacture cinematic transitions.

B-roll is an executed shot, not a stock requirement. Its card records function,
relation_to_main, construction, anchor and return_handoff. Illustration/macro/
3D insert may be B-roll. Use no minimum quantity or quota. Preserve evidence type.

## Event-driven sound

Sound defaults to adaptive, but an empty cue list is a valid deliberate decision.
Pick the audible physical/editorial consequence rather than keyword-matched effects.
Each cue binds event_id/source_object; its relative_time is derived from the same
event start plus offset_frames. It needs trigger, purpose, role, selection_reason,
file and listening_review(status, reviewer, notes, asset_sha256). Listen/select
before declaring PASS; an asset existing is not listening proof. Freeze generated model/source/request/take hashes through the Small-SFX resolver.
No Freesound route or key exists in this fork.
Existing mixer provides speech ducking, gain, pan and fades. Inspect voice clarity,
cue salience/timing, harshness and joins by ear. Silence can be preferable to a bad
cue. No synthesized generic tone as a missing-recording fallback. BGM is optional:
set music_requested=true only from the user's brief, and provide music.file, purpose,
selection_reason and a hash-bound listening_review. The runner freezes the asset
and mixes it across the complete film with speech ducking; it does not restart at
scene joins. Gain/fades/asset_offset/loop use the existing mixer fields. Never
silently loop an unsuitable track or label a meter reading as a listening review.

## QA and delivery

Renderer probes establish format/frame count, not quality. Execution manifest
records shot/beat/event/B-roll mapping, exact output hashes and requested frame
evidence. Source snapshot includes plan/source hashes. Independent visual,
scientific, motion, VFX, editorial, layout and listening gates begin UNVERIFIED.
Review notes must cite current hashed clips/images/measurements. `v4_review.py`
rejects changed sources/audio/plan/output and prevents technical fixtures from
becoming production releases. A FAIL/PARTIAL/unreviewed gate requires repair/review.
No generic assertion that art is beautiful, scientific or cinematic based on JSON.

Before a full production, `preview` renders the packet's representative shot at
1080p60 and trims the same measured narration to its exact allocation. Preview
does not include the film-wide music bed. Inspect and review visual/layout/motion/
editorial, then set representative.review.run_dir. A changed source/timing/style/
acceptance fingerprint invalidates that representative review. Report the actual
review findings and stop; the user now explicitly requires each step to be shown
before continuation. Never create acceptance that substitutes for their requirements.

Fill the generated review_template: named reviewer, current hashes, typed hashed
frame/clip/audio/measurement evidence, and expected/observed observations covering
every required target. Artwork/layout needs rendered images/clips. Temporal motion,
VFX and editorial need clips, not stills/JSON. Listening needs method=listened on
the complete current final.mp4 with audio; meters or a selected SFX file are
insufficient. Required science claims, VFX events and final audio cannot be waived.
Representative/technical fixtures cannot pass production release. An old review
format must be replaced with current evidence, never auto-promoted.
