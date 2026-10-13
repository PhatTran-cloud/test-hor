# Horror light: small storyboard, complete illustration and motion

Read [Shared scene staging](HORROR_SCENE_STAGING.md): one world definition supplies named camera views and static background evidence; the handoff records a typed story link. New template selects staging_revision=1. This adds no per-second or layer quota. Reference research must use [actual samples](REFERENCE_VIDEO_STUDY.md); the current three-video request is blocked, not a completed channel analysis.

Current user direction, 13 October 2026: simplify this horror project. The
rainforest experiment belongs to an explainer reference, not the default horror
benchmark. Keep Kage as the artwork target, separate asset illustration, and the
existing motion/VFX skills. No art quality, identity, timing or evidence gate is
waived by making storyboard authoring shorter.

## The three jobs

| Stage | Author now | Output |
|---|---|---|
| Storyboard | Scene purpose/new information, visible IDs, main action, focal/camera purpose, sound intent and next scene | Short cards in the same schema 4 plan |
| Illustration | Identity, separate drawable parts, necessary states/views, registration/anchors; native model construction when selected | Copyable 2D prompts or full lowbudget3d requests; then actual reviewed assets |
| Motion / VFX | Mount assets, actor mechanics, secondary response, camera implementation, event transport/contact/light/aftermath, continuity | Existing assembly/source and a real preview for review |

Storyboard does not enumerate every particle or fabricate geometry. Static
backgrounds and intentional holds are valid. Choose additional layers, metaphors,
camera moves, poses and VFX only when they clarify the story. No fixed shot count.
Kage governs artwork; clear cause/reaction/payoff governs this horror storytelling.

Read [HORROR_CHARACTERS.md](HORROR_CHARACTERS.md) for ensemble design and acting.
Visible-ID notes include a compact shot.cast list: people present, state sequence,
gaze/view/blocking and anonymous group count. Character designs and facial/body
recipes live once in character_direction, not repeatedly on storyboard cards.
Principal/supporting/extra is design importance; per-shot attention can change.
Multiple principal characters are valid. Default performance is restrained horror,
humor=none. Separate an extra when it speaks, acts independently or needs its own
close-up. Exported scene inventories retain fewer/more people per shot.

## Short authoring contract

Keep schema_version=4, profile=horror-v4.1 and illustration contract_revision=1.
Set production_packet.illustration_direction.authoring_mode=horror_light.
The updated horror-profile-template.json selects this for new authoring.

Keep the inherited beat before/after, narration anchor and visual evidence;
write short actual descriptions. A shot uses the inherited IDs, visual_thesis,
object_ids, attention, camera.purpose and handoff, plus:

- action: one readable main action or an intentional hold;
- sound_intent: sources and intended quiet; a brief, not generated audio;
- handoff.to_shot_id: actual next shot, or null at the end;
- handoff.reason/carry_state: why it follows and what must persist.

No mandatory beat.direction/metaphor, visual_system.bindings, per-object semantic
layers, seven component-role accounting or repeated attention reasons. These
full-detail fields remain available when useful and unchanged for old mode=full
plans. Scene worlds retain layout, perspective, lighting and crop_safety; asset
briefs retain story/cast/setting facts. Artwork choices and unresolved visible
ages/era remain with the user.

Illustration.method must be explicit before export: generated, existing or
procedural. For generated objects in light mode, declare route=2d|3d and asset_ids.
Coverage still checks every visible object and every generated asset. A native
3D route cannot become a raster replacement.

## Illustration

```bash
python local_tools/production.py asset-brief PLAN --output ../outputs/illustration/prompts.json
```

2D: separate alpha characters/parts/props and opaque background plates. Export
only the states/views that motion actually needs; transforms of a rigid prop do
not automatically need a pose series. Human-run Flow uses the selected existing
model. Alpha sources use #00FF00 and local chroma-key cleanup; measured anchors,
edges, crop and identity must be checked on returned images. No automatic Flow.

Light exports put shared visual/world context once in JSON and use asset-specific
context in each copyable prompt. Their shot inventory stays small. The asset
registry and motion detail are exported separately below.

3D: only when actual spatial construction is selected. Keep the complete
lowbudget3d + 3dviz-pro-max + illustration bridge, parts/pivots/anchors/variants,
surface/texture plan, closest-camera inspection and real source/resource hashes.
That detail is Illustration's work, not a tax on every storyboard card. The full
base must be available at fabrication; unavailable remains blocked/unverified.

Review real artwork before assembling animation. Prompts are requests, not art.

## Motion and VFX

```bash
python local_tools/production.py motion-brief PLAN --output ../outputs/motion/brief.json
```

JSON includes shared asset registry, visual system, scene worlds and object
states per section; Markdown gives the readable task summary. One assembly
task per shot: instance IDs, asset routes, focus/camera, main action, sound,
handoff, active events and transitive upstream causes. Missing assets/current
reviews or measured voice timing are reported. Export never executes animation.

Use storyboard-motion-executor for ID/meaning/attention preservation,
cinematic-motion-director for trajectories, pivots/contact/secondary motion,
camera and transitions, and cinematic-vfx-director for effects caused by an event.
Keep one Remotion/Three.js/Manim assembly and the measured section-absolute 60fps
clock. Stillness is authored; no global idle sine loops or arbitrary resets.

At phase=authored, all objects still require full behaviors
(mode/motivation/trigger/response/secondary_response/settle/exit_state), camera
information_intent and the inherited execution/source/sample bindings. Those
details are added by Motion in the same packet. Existing sprite/model bindings,
alpha/native-resource registration, measured audio and current review checks
remain required. No empty motion ledger can render under light mode.

VFX follows source -> transport/interaction -> object/world/light response ->
aftermath. If a shot has no VFX event, do not invent fog/glow/shake to fill a box.
Audio stays OmniVoice and Small-SFX with serialized GPU stages. Review actual
encoded motion, focus, contacts, seeks, transitions and sound; exporting or
validating a light plan never supplies an artistic PASS.

## Small trial

examples/horror-light-washer-draft.json uses three proposed shots in one room:
establish the unplugged lead, inspect the hatch reacting to an internal knock,
then show the same disconnected supply while the clue persists. Four reusable
2D assets, four image prompts, one restrained event proposal. No human visual
casting, era changes, narrator selection or media production is implied.

The old forest draft remains a historical explainer/hybrid contract experiment.
Do not use it as the default horror template or scale it into an approved film.
