# Current illustration pipeline: Kage artwork, separate 2D/3D fabrication

Read [Shared scene staging](HORROR_SCENE_STAGING.md) for one master plate, named shot views and story-bearing static details. These flow into the copyable background request and downstream motion/context/review. Staging is a project proposal; [reference sampling](research/2026-10-13_oversimplified_sampling_status.md) remains blocked.

Ensemble and facial/body performance use [HORROR_CHARACTERS.md](HORROR_CHARACTERS.md):
one reusable character/group registry, compact cast presence per shot, checked
state/view/count coverage and current character design hash. Principal characters
carry deliberate face/costume/silhouette detail; anonymous extras are grouped
only while sharing behavior. Kage governs artwork; original economical staging
is adapted to restrained horror with no default comedy.

Current default: **horror_light** authoring, per
[HORROR_LIGHT_WORKFLOW.md](HORROR_LIGHT_WORKFLOW.md). Keep short scene cards and
move asset detail to Illustration and temporal detail to Motion/VFX. The full
semantic/metaphor/seven-role fields below describe the retained full mode; they
are not mandatory for new light horror plans. Artwork and production evidence
requirements still apply to both modes.

User direction, 13 October 2026: upgrade this repository; illustration exports
asset drawing prompts; target artwork is https://github.com/MengTo/kage; fabricate
native 3D with lowbudget3d, generate 2D assets from prompts, complete each shot's
components, then hand off to motion and VFX. This overrides older assertions that
Kage/native 3D cannot apply to the current film. Existing cast, character ages,
era, audio choices and evidence are not re-selected by this workflow upgrade.

## Ownership

- Storyboard owns meaning, metaphor, geography, object/instance IDs, information,
  attention, camera intent, causal relationships and continuity.
- Illustration owns separate editable assets, parts, materials/textures, anchors,
  variants and necessary camera views. It does not precompose the whole moving shot.
- 2D exports human-run Flow prompts. Alpha sources use #00FF00 and local keying;
  opaque clean plates preserve their intended format. No automatic Flow submission.
- Native 3D exports lowbudget3d fabrication requests. Keep the **complete**
  3dviz-pro-max base plus lowbudget3d and its illustration bridge. Verify that full
  package and relevant resources before fabricating. A missing base remains
  UNVERIFIED/blocked; never substitute a summary, flat image or cheap primitive.
- Motion mounts reviewed assets by IDs/anchors into the existing Remotion/Three.js
  assembly, owns acting/camera/secondary behavior and derives state from absolute
  section time. VFX expands causal source/transport/interaction/light/residue
  events inside that assembly. Neither changes the storyboard's meaning.

## Artwork reference

Primary sources inspected: Kage README and PROMPT.md, retrieved 13 October 2026.
They describe live procedural 3D combined with generated imagery and foreground
cutouts. Adopt original crafted subjects, readable layered depth, coherent
materials/light, restrained atmospheric support and deliberate handoffs. This is
reference research, not inspection of this film's generated images or final pixels.

Develop the film's own palette/shape/typography/transition system from its meaning.
Do not force Kyoto, Japanese headings, five chapters, web navigation or scroll
interaction into the film. Use measured 1080p60 timing. Kage's code/art are not
vendored; this pipeline generates/fabricates original assets.

## Additive fields, same schema 4

New authoring uses `horror.artwork_style=kage_illustrated_hybrid`,
`horror.artwork_provider=hybrid`, `horror.visual_reference.primary=kage` and the
recorded USER_SELECTED visual_style_decision. Use `horror.illustrator` with
mode=prompt_export_only, generation_operator=human user, the chosen 2D model,
chroma_key_color=#00FF00 and three_d_skill=lowbudget3d.

Set `production_packet.illustration_direction.contract_revision=1` and
`target_artwork=kage`. Older frozen plans remain readable under their old contract;
they do not acquire the new completeness checks or artwork approval by relabeling.

Required new direction:

| Owner | Fields |
|---|---|
| visual_system | Existing palette/typography/shape_language plus bindings.color_roles, shape_roles, typography_roles, transition_rules |
| scene_world | layout, perspective, lighting, crop_safety; semantic_layers with object_id, depth, information and function |
| beat.direction | idea, visual_proposition, metaphor(source/target/mapping/limits), adds_information, object_ids, knowledge(before/after/withheld), payoff |
| shot.components | items(object_id/roles/route), required_roles and omissions with reasons |
| shot.attention_plan | Every visible object: object_id, primary/secondary/ambient/suppressed priority and reason |
| shot.behaviors | Every visible object: mode, motivation, trigger, response, secondary_response, settle, exit_state object |
| shot.camera.information_intent | known_before, hidden_before, reveals, target_object, reason_for_move_or_hold |
| shot.handoff.semantic_link | to_shot_id, causal/semantic/spatial/sound/end kind, relation, invariants; optional trigger_event_id |
| generated asset.design_semantics | role, meaning, recognition_traits, parts_or_layers, anchors, variants, closest_camera_use |

Component roles: subject, support, foreground, midground, background, atmosphere,
interactive_prop. Required roles must be represented by actual canonical objects;
unneeded roles need explicit reasons. This accounts for a complete shot without
forcing every macro/empty-frame insert to have an arbitrary prop or cast quota.
All object IDs must match; an unnamed noun in a prompt is not coverage.

Routes: `2d|3d|procedural|existing`. The latter two retain concrete reasons and
actual source/file review requirements. A 3D component cannot bind a 2D image as
its production replacement. Holds use passive behavior with intentional_hold;
other behavior triggers bind a known event phase, world/source, or this camera.
Secondary activity supports information and never becomes a global sine loop.

When one event causes another, declare `event.cause_event_ids`. The optional list
must contain unique known event IDs and form an acyclic graph. Scoped handoff
includes the full upstream cause chain, its owners and objects; these dependencies
remain separate from events currently active in the selected shot.

## 2D assets

Keep provider=flow, kinds sprite_sequence/prop/layer and reusable action/view
requests. Animated characters use actual alpha PNG, parts or replacement poses;
neutral portraits are identity references. Prompt every generated component,
prop and background. Backgrounds are clean but meaningful: leave interacting,
occluding or moving parts independently addressable. Dynamic fog/rain/blur,
interactive shadows, camera and final shot composition belong downstream.

## Native 3D assets

Use provider=lowbudget3d, kind=model_3d, requires_alpha=false, explicit scene_ids
and an appropriate illustration_role (character_model/prop/background/environment_layer).
Keep identity, action research, entry/exit/contact and design_semantics.

`model_spec` declares representation=glb|threejs_module; metre dimensions; named
parts with pivots, material regions and optional parent IDs; anchors, variants,
surface_regions, texture_plan, articulation and closest_camera_use. `views`
request id/camera_region/inspection_purpose, including closest use. Do not pretend
sprite frames establish 3D geometry. Organic/body/attachment fabrication follows
the relevant full lowbudget3d specialist, not primitive placeholders.

After fabrication register model_spec.file/sha256, bundled resources with hashes,
and inspection_evidence(view_id/file/sha256) for every requested view. Retain an
asset review bound by asset_digest. Authored shots need model_bindings with the
canonical object_id/asset_id/instance_symbol and a real spatial Three.js assembly.
Geometry/resources/inspection files are frozen with the run; technical container
or hash validity never confers domain or artwork PASS.

## Export and next-stage handoff

Use the existing entrypoint:

```powershell
.venv/Scripts/python.exe local_tools/production.py asset-brief timed_plan.json --output ../outputs/illustration/prompts.json
```

JSON and sibling Markdown contain 2D tasks/batches, three_d_tasks,
complete-shot inventory and motion_vfx_handoff. The export validates coverage
and emits requests, not images or models. 3D requests explicitly name the full
base and overlay; their base availability is unverified until fabrication.

Register and review returned assets before motion/VFX. Keep one production packet,
one clock and one assembly. Execution context and renderer contract use the same
scoped direction resolver, including prerequisite beats and carried events.
Representative fingerprint includes its relevant world/asset/direction payload;
upstream changes invalidate the affected review.

## Review

Check actual artwork for identity, complete views/parts, readable materials/depth,
alpha/crop/anchors and closest-camera use. Check the encoded clip for meaningful
background/secondary activity, attention, camera information gain, cause/reaction,
reveal and transition invariants. Technical validity and exported prompt count
remain separate from these judgments. Use the existing independent gates and
START_HERE step boundaries; exporting requests does not start motion/VFX/render.
