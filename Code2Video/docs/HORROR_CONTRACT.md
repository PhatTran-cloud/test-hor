# V4.1 horror contract on schema 4

This is the current additive contract. Historical source snapshots in `references`
describe earlier decisions and do not override this document or the user's choices.

## Current user-selected illustration direction

On 13 October 2026 the user selected OverSimplified as the primary reference for
storytelling, staging, complete worlds and expressive cutout animation, adapted
to horror. AI supplies art; Remotion supplies motion/compositing. Read
`OVERSIMPLIFIED_ILLUSTRATION.md` for the maintained illustration fields, prompt
coverage, component/pose decisions, scene geography and green-screen workflow.
The user accepts illustration construction that serves this thinking; do not
impose a rigid all-solid-fill/geometric recipe. Illustrated shadows, gradients
and drawn detail are permitted when they support clarity/depth.

`artwork_style=2d_flat_geometric_vector` remains the compatible machine style ID,
not a ban on those illustration techniques. Record a USER_SELECTED
visual_style_decision with selected_style, primary_reference=oversimplified,
authorization {reviewer: human user, request: actual instruction}. Historical
Kage/3D directives are superseded for this film. Old rejected art is not reusable
approval; preserve frozen evidence. Generated vector-looking raster is not SVG.

## Plan and art

Keep schema_version=4, profile=horror-v4.1, explicit language_id en|vi and existing
draft/timed/authored phases. content_profile.genre=horror. `horror` contains:

- artwork_style, artwork_provider=flow; current visual_reference.primary=oversimplified.
- illustrator: mode=prompt_export_only, generation_operator=human user,
  model=Nano Banana 2.1, chroma_key_color=#00FF00.
- voice_provider=omnivoice, sfx_provider=stable_audio_3_small_sfx.
- style_bible: canonical_prompt, proportions, materials, lighting, depth, identity_rules.
- assets: reusable generated character component/action/view sequences, props and layers.

Illustration only exports prompts. Every generated item, including background and
props, requires explicit prompts. The human runs Flow; no automatic submission.
Code composes and animates individual parts/poses, camera, environment/VFX and
sound. Keep backgrounds coherent and empty of moving characters; do not flatten
interacting items into them. Multiple main characters/semantic beats are allowed;
counts come from story, not quotas. True spatial 3D keeps its full skill route only
when actually used. Historical plans may retain Kage for reproducibility; it is
not required for current OverSimplified direction.

## Character and setting brief before artwork

Before generating canonical references or action poses, put a reviewable brief in
the same `production_packet`. This is required direction and review documentation;
it does not introduce new schema fields or claim automatic validator enforcement.
Use canonical character/object IDs and link the existing script, research and
style bible instead of maintaining a competing packet.

- Characters: story role, family/other relationships, visible age or age band,
  face/body/silhouette, costume and relevant materials, distinguishing features,
  and any transformation states needed by the story. Link script quotations or
  source IDs. Keep script facts, inferences, proposals and user decisions distinct.
- Setting: location, era or permitted time range, architecture/interiors,
  technology, clothing, ritual/everyday props and relevant lighting conditions.
  These decisions must agree with the story and with one another across assets.
- Uncertainty: identify missing or conflicting details and their design impact.
  Ask the user before choosing details that materially affect identity, visible
  age, relationships, era, costume, architecture or props. A village, funeral or
  wooden house alone does not establish a decade. Do not fabricate an exact age
  or year when it can remain unspecified. Preserve prior user decisions without
  asking again; an assistant proposal is not approval.

Visual ages and family relationships must read correctly in the images. A
voice-library age label is not a visual casting decision. Script anchors and
approved choices override model defaults or generic stereotypes. Resolve material
questions before submitting affected references/poses; do not generate first and
silently choose the answer from the output.

Translate the current approved style into effective prompts and record model
and prompt provenance. Compare actual outputs to the current brief, not old 3D
reference wording. A model name or successful job does not establish style PASS.

## Animation sprites and image formats

Characters intended to animate use `kind: sprite_sequence`: reusable isolated
action poses and the camera views required by the storyboard. Derive pose phases
from intention, anticipation, contact, action and aftermath; no fixed pose quota.
Maintain identity, costume, scale and registration across frames/views. A neutral
standing portrait or front/side/back identity sheet is a reference, not a complete
production animation asset. Flow supplies images; authored code supplies motion.
Do not replace acting with rigid cutout rocking or generate AI video instead.

Character cutouts, and other layers that require transparency for compositing,
must have actual transparent alpha in PNG/RGBA. Retain provider originals and
inspect alpha, edges, full crop and hidden regions. A painted checkerboard or
conversion of RGB JPEG to PNG does not create transparency. Props/environments
that do not need transparency retain their original image format; PNG is not
mandatory for every asset. Register measured dimensions/anchors after generation;
request-only provisional registration must not pass as measured production data.

## Behavior â†’ pose/view â†’ asset

Each asset: `id`, `object_id`, `provider: flow`, `kind: sprite_sequence|prop|layer`,
`identity`, `action`, `views`. Action: intent, mechanics, packet research source_ids,
entry_state, exit_state and contact_requirements (empty when justified).
Research the action, support/weight/gaze/forces and environmental response before
pose prompts; document inspected pages/frames and observed versus supernatural
or stylized departures. Preserve identity, proportion, costume/props and lighting.

Each view has `id`, `camera_region`, ordered `frames`. Each frame has id,
description, width/height, root_anchor/ground_anchor `[x,y]` in image pixels,
sockets map, and positive integer hold_frames on the delivery 60fps clock.
After generation add file/sha256; source alpha, crop safety and hidden parts must
be reviewed. One-shot holds the final pose; loop is explicit, not automatic.
No fixed frame count or forced skeletal rig. Sprite cadence may differ from 60fps.

Before authored motion each asset has `review` with status PASS, reviewer, notes
and `asset_digest` computed by `horror_contract.asset_digest`. This binds actual
files/registration; the digest is not an artistic judgment. Record real observations.

Shots declare `sprite_bindings`: object_id/asset_id/view_id, loop, start_frame,
end_frame, root_track and contact_windows. Camera lists supported_sprite_views.
Root keys use absolute section frame and scene-pixel position; pose anchors remain
image-local. Contact windows use socket, start/end_frame, world_position.
The built-in adapter pins one controlling socket through root correction; multiple
simultaneous constraints or bending use an authored rig/solver and its own review,
not this simple adapter. Do not downgrade required acting to rigid cutout rocking.

`horror_sprites.sprite_state` is deterministic and seek-safe. Equivalent browser
implementation is in `runtime/horror-sprites.mjs`. It supplies placement/pose state,
not anatomy or a physical simulator. Camera rotation does not create an unseen
backside or relight painted highlights; obtain the needed view or route true 3D.

The runtime shot contract carries relevant `horror_assets` plus sprite bindings.
Canonical IDs, attention, reveal, contacts, event phases and state carry across cuts.
World forces must agree across rain, hair, cloth, foliage, fog and surface reactions.
All visible objects get a justified temporal state; world-static is allowed.

## Cast and utterances

`cast.library` points to the reference manifest; `cast.narrator` is exactly one
main speaker ID. `cast.characters` maps any number of canonical character IDs to
dialogue speaker IDs. The user chooses language/cast per film, never a default.

For schema compatibility `section.narration` is the complete spoken text, including
dialogue in order. `narration_segments` are utterances with id/text/role and
optional pause_after. Narrator role uses the main cast voice, no instruct or acting
prompt. Dialogue has character_id and acting_direction `{intention, mood}`.
Provider `instruct` is null or whisper only. Creative fear/anger/grief remains in
direction; it is not a supported arbitrary instruction. If appropriate, a dialogue
segment can choose delivery_reference_id from a reviewed same-speaker reference.

References must match the selected language/role, retain correct hashes, have a
REVIEWED transcript and hash-bound listening review. New imports remain unreviewed.
For an explicitly authorized dialogue cast audition, `production.py voice-design`
uses the runtime design endpoint's supported gender/age/pitch/whisper controls.
It saves actual WAVs, API metadata, request hashes and GPU lifecycle receipts;
it does not select/register references, verify transcripts or approve listening.
This is separate from cloning: its null/whisper instruction contract is unchanged.
Do not cut a sample at an arbitrary time or claim it is clone-ready because it is
mono/24k or inside the suggested 3â€“10s range. Do not fabricate transcript/mood.

`voice_settings` optionally controls steps/guidance/denoise/preprocess/postprocess.
The adapter does not set duration to fill a scene. It preserves decoded take PCM,
including quiet speech; joins/padding are explicit, measured, never stretched.
Preparation stores actual take/receipt hashes, cast/reference/transcript/settings
identity, utterance intervals, final frame-padded WAV and measurement receipt.
The demo API exposes no seed or checkpoint revision; record that uncertainty and
freeze the chosen take. Timings are measured utterance anchors, not word alignment.
Word-level ASR is always required for visual/voice alignment in this film; use
measured word anchors rather than guessed slots. Word timestamps do not establish
phonemes/visemes; detailed mouth alignment needs a separately verified process.

Before authored rendering annotate each utterance's listening_review with PASS,
reviewer, notes on identity/acting/intelligibility and asset_sha256=take_sha256.
Annotations may change; underlying take/configuration/measurement must not.
Actual final mix listening is still mandatory for release.

## SFX duration, generation and mix

No Freesound or Kokoro route exists in active horror production. Each cue has:

- id, event_id, source_object, trigger, purpose, role, selection_reason.
- Explicit positive `duration` (seconds of selected audible content including tail).
- `sync_phase: start|peak|end` and integer offset_frames. Negative offsets need
  timing_reason and cannot put onset before the section begins.
- `generation: {prompt, seconds, seed}`; optimized backend currently steps=8/cfg=1.
  Generation length is explicit and must cover asset_offset+duration unless a
  consciously chosen ambience loop is used. No default 8s, no forced full-shot track.
- `perspective: {space, distance, occlusion, reason}` and any authored gain/pan,
  fades, pan_keyframes/gain_keyframes (cue-local seconds), lowpass_hz or frozen IR.

Actual WAV duration is verified; model semantic content/onset/count are not assumed.
Audition/select asset offset or another take. Short generation below the consumer
Lâ‰¥256 region runs but has a documented quality caveat; listening decides suitability.
Public official optimized graphs are pinned/hashed. CUDA kernels are profiled;
host sampling and some graph ops remain CPU. No CPU inference fallback.

`production.py sfx` takes a timed plan, generates separate cues, leaves reviews
UNVERIFIED and returns sfx_plan.json. Record actual listening_review status/reviewer/
notes/current asset hash before authored render. Keep model source, revision,
sampler/tokenizer/request hashes and generated provenance; never label it recording.

Derive cue onset from the event's selected phase. Long tail across sections requires
carry_across_sections=true and must fit the measured film clock. Mix once over the
whole film so ambience/reverb/tails do not restart at each cut. Silence is valid;
music only after explicit request with local provenance/license and listening review.

Ducking uses measured speech activity, including whisper. Optional gain/pan
automation, lowpass and frozen impulse response implement authored acoustic changes;
metadata alone does not prove audible perspective. A room IR must have sufficient
explicit cue/tail allocation; meter/peak control does not prove listening/loudness.

## GPU and QA

Commands are distinct stages. Voice/SFX share a lock and never coexist in model
residency. Stop OmniVoice first, record idle VRAM; voice starts the configured
container then stops it in finally. Small-SFX uses its separate process/runtime;
that process exits, then lifecycle observes VRAM release. Release failure stops the
stage; no silent next-stage launch. Rendering rejects a live voice stage/container.
Host/container/driver availability is checked, not guessed from login status.

The representative workflow and V4 technical/art/motion/VFX/editorial/layout/
scientific/listening gates remain. Technical fixtures cannot release. Identity/
acting/contact/reveal/seek/endpoints and final audio need current observed clips or
listened audio, not source symbols or model meters. Follow the user's stepwise mode.

## Explicit opening candidate excerpts

An explicitly requested opening test clip may declare `preview_scope` with kind
`candidate_excerpt`, section ID, integer start_frame=0/end_frame on the original
measured clock, original source_audio_sha256, and the recorded human request.
Only `production.py preview` accepts this scope. Speech, take/configuration hashes
and the complete measurement receipt remain unchanged; authored shots cover the
requested excerpt. If the user explicitly retains defective test audio, record
`voice_review_deferred` with status USER_RETAINS_TEST_AUDIO_WITH_KNOWN_DEFECTS,
the current WAV hash, that request and the limitations. Actual listening statuses
remain unchanged. This exception applies only to this candidate preview.

The manifest is candidate_excerpt and stays REVIEW_REQUIRED. It cannot replace
the representative review, run as production or release, even after reviews.
Artwork registration, source/runtime evidence and other checks still apply.

## Manual Flow illustration and historical diagnostics

Current illustration uses `production.py asset-brief` only: JSON and copyable
Markdown prompts with full generated-object coverage. The human runs Flow.
`flow-submit` and the direct `flow_assets.submit` function are disabled before any
network activity. Extension/backend health is not a prerequisite for prompt export.
`flow-status` and legacy batch-payload helpers are retained for read-only historical
inspection and compatibility, not permission to generate. Their old project/scene/
UUID bindings do not control the new manual illustration route.

Alpha-required sources use uniform #00FF00 and local `production.py chroma-key`.
Preserve source, mask and receipt; register actual alpha PNG dimensions/anchors,
then review edges, age/identity, state and scene correctness on actual images.
Opaque assets retain their original format. See OVERSIMPLIFIED_ILLUSTRATION.md.
