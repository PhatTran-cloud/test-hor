# Illustration direction: OverSimplified storytelling for horror

Current staging and research status: [HORROR_SCENE_STAGING.md](HORROR_SCENE_STAGING.md) applies to new Kage/horror light plans; [the three-video sampling request](research/2026-10-13_oversimplified_sampling_status.md) has 0/540 frames. The earlier text below is not a completed frame-level study.

Current ensemble/performance contract is [HORROR_CHARACTERS.md](HORROR_CHARACTERS.md).
Kage remains the current artwork target; OverSimplified is an explicitly recorded
staging/character-hierarchy reference. Use original restrained horror performances,
humor=none, and the shared registry/cast/state/count checks. The earlier primary
artwork direction below remains only for frozen-plan reproduction.

Historical primary-artwork direction (superseded by KAGE_ILLUSTRATION_PIPELINE.md): AI supplies artwork; the human user runs
Flow; Remotion composes and animates. Illustration exports prompts only. Use the
[inspected reference research](research/2026-10-13_oversimplified_horror_direction.md)
for observed examples and its explicit uncertainties. OverSimplified is the primary
reference; older Kage/3D/trial directions are historical for this film.

## Outcome, not a rigid drawing recipe

Illustration should communicate the story as clearly as the reference: simple,
recognizable characters; expressive eyes/brows/mouth/poses; a designed environment;
functional props; shot framing that directs attention. The user accepts any art
construction that serves this thinking. Do not force solid fills everywhere, a
uniform face preset, a pose count, a prop quota or a software/rig presumed to be
OverSimplified's. Drawn shadows, gradients and illustrative texture are allowed
when they support depth and readability. Generated vector-looking raster is
still raster, not editable SVG.

Horror comes from script-specific anticipation, withheld information, reveal and
aftermath. Do not turn every person into a corpse, darken everything into illegible
silhouettes or use one frightened idle loop for all dialogue. Keep Viễn's approved
22–25 appearance distinct from mother 48–52 and grandmother 75–80. Their village
home is in contemporary Vietnam, with an old house, not a historical period.

## A scene world supports its shots

Record `production_packet.illustration_direction.scene_worlds`: each world has
`id`, `layout`, `perspective`, `lighting`, `required_props`, `crop_safety`. Each
shot declares the shared `scene_id`. Record entrances/exits, interacting objects,
ground plane, human scale, view and light direction. Layout may be described in
words initially; it must become measured positions before motion execution.

The grandmother's room needs the courtyard doorway, side window, overhead beam
and two adjacent beds in a coherent layout. Mother must be able to reach Viễn
from her bed. Add useful lived-in detail without inventing new plot facts or
changing approved era/identity. Label proposed details. Other shots reuse that
world; request another clean plate/view only when the camera really exposes it.
Design opaque backgrounds without characters. Separate doors, furniture, foreground
occluders and other interacting objects when their movement/occlusion requires it.
Do not bake a moving character or held prop into the background.

Simplified inserts/empty space are valid when they serve a specific beat. They
are not a reason to leave a lived-in room or forest unconstructed. Weather includes
the place and surfaces it affects; animated rain/fog belongs to code, not every
character cutout. The rainforest example remains a separate benchmark, not a new
location in Viễn's script.

Camera defaults to a held frame, attention/focus and zoom in/out. Define the focal
target, reason, visible art region and crop margin. Focus does not mandate blur.
Camera movement cannot substitute for character acting.

## Art for the action

For each beat record trigger, intention, gaze target, face state, body pose,
gesture, contact/grip, listener reaction and exit state. Design parts or replacement
action/view poses that can express those states. Holds are valid when intentional.
Plain standing portraits establish identity; they do not complete an animation set.

Use separate head/torso/expression/limb/hand/foot assets as needed; thin vector limbs
may be drawn by code with an explicit procedural-art reason. Ask for hidden joint
overlap, a common face coordinate space and full crop. Plan neck/shoulder/hip pivots,
front/back order, grip points and support. Replace a view/pose when a simple rig
cannot represent the action. A whole person rocking as a rigid PNG is not acting.

Use the existing `sprite_sequence` schema for each generated character component
or replacement sequence, with its own `id` and the character's `object_id`.
`illustration_role` identifies `character_part` or `character_pose`. Many assets
can belong to the same canonical character. Existing pose sampling only changes
images/root position and pins one controlling socket. It does not supply a
multi-joint rig: author and review that solver in Remotion during the separately
authorized motion step. Do not claim a rig or animation is implemented by exporting
part prompts.

Remotion state must derive from absolute frame; register actual anchors and
contact/view limits, preserve ownership and state across cuts, then inspect grip,
support, face changes and non-sequential seeks. Word-level ASR is always the
timing basis; it does not establish phonemes/visemes. Open/closed mouth animation
must be described as such unless a phoneme process has actually been verified.

## Every generated item has a prompt

Every visible object, including props and backgrounds, declares:

```json
{"illustration": {"method": "generated", "asset_ids": ["vien_head"]}}
```

Alternatively use `method: procedural|existing` with a concrete `reason`; existing
art still needs current file/provenance/review checks before rendering. This
declaration is not a waiver of art quality. Generated objects require all listed
assets in `horror.assets`, whose `views[].frames[]` each export a prompt. Missing
assets, missing coverage or empty view/pose lists fail export rather than silently
skip an object. Counts come from actions and views, not five-asset quotas.

Add to each generated asset:

```json
{"scene_ids": ["grandmother_room"], "illustration_role": "character_part", "requires_alpha": true}
```

Roles: `character_part|character_pose|prop|background|environment_layer`. Character
parts/poses need alpha. Props/environment layers declare alpha only when needed.
An opaque background can use kind `layer`, role `background`, requires_alpha=false.
Its prompt asks for a complete coherent empty clean plate, not an isolated object
on green. Any asset requiring alpha asks for uniform solid #00FF00 instead.

`horror.visual_reference.primary=oversimplified`; the user-selected
`production_packet.visual_style_decision` records `primary_reference=oversimplified`.
`horror.illustrator` contains `mode=prompt_export_only`,
`generation_operator=human user`, `model=Nano Banana 2.1`,
`chroma_key_color=#00FF00`. These values reflect the current user's choices.

Run only when the illustration step is authorized, from Code2Video:

```powershell
.venv/Scripts/python.exe local_tools/production.py asset-brief timed_plan.json --output ../outputs/illustration/prompts.json
```

This writes JSON plus a sibling Markdown file with copyable prompts, IDs, style,
story/world context, action/view/state and alpha treatment. Groups of five preserve
the user's batching preference; they do not prove five concurrent Flow jobs. No
Flow connection, login, extension or model load is needed. The human runs the
prompts and returns provider originals. `flow-submit` is disabled, including direct
Python submission; no illustration agent/browser auto-generation.

## Green-screen originals → reviewed alpha PNG

Prompt uniform #00FF00, also in gaps between limbs; no green subject color, green
spill, cast ground shadow, backdrop gradient, checkerboard or text. Code removes
green locally, preserving provider originals. Opaque images retain original format.

```powershell
.venv/Scripts/python.exe local_tools/production.py chroma-key ../outputs/illustration/vien-source.jpg --output ../outputs/illustration/vien.png
```

The command writes real RGBA PNG, `.mask.png` and `.chroma.json` with source/output/
mask hashes, measured dimensions, thresholds and UNVERIFIED edge review. It refuses
source overwrite, existing output names, invalid thresholds, missing green or an
entirely removed subject. Defaults are RGB-distance thresholds inner=30, outer=100;
tune `--inner`/`--outer` after inspecting actual edges; `--no-despill` disables edge
green suppression. Uniform key colors on the subject cannot be recovered; fix the
prompt/source when necessary. This is a matte helper, not guaranteed segmentation.

Inspect hair, thin limbs, finger gaps, overlap/crop and halos on light/dark
backgrounds. Register measured dimensions/root/ground/grip anchors after return.
Retain originals/masks/receipts and actual provider/model/prompt evidence. Technical
completion, alpha existence or prompt hashes do not confer artwork PASS. Image
review and animated clip review remain separate, current-output gates.
