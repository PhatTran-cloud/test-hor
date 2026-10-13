# Ensembles, character design and restrained horror performance

Current user direction, 13 October 2026: upgrade the complete repo for scenes
with any number of principal/supporting characters and anonymous extras. Record
who appears, what the crowd does, and the faces/poses Illustration must supply.
Keep storyboard light. Kage remains the artwork target; OverSimplified informs
economical ensemble staging and readable character hierarchy. Original horror
characters and acting are the production goal. Default humor is none.

## Design once, note presence per shot

Use production_packet.character_direction, contract_revision=1,
tone=restrained_horror, humor=none. Its characters and crowd_groups are reusable
definitions. These are visual definitions, separate from cast.characters, which
maps dialogue characters to selected voice speakers. A silent character does not
need a voice. Do not derive visible ages from voice labels.

Each individual instance in section.objects has character_id. An anonymous
group instance has crowd_group_id. All generated parts of one person belong to
that person's canonical object_id; do not count each eye, hand or body asset as
another person. Any number of principal characters is valid. Principal is a
design responsibility, not a requirement to dominate attention in every shot.

shot.cast has one short entry per present individual or anonymous group:

| Note | Individual | Anonymous group |
|---|---|---|
| object_id / attention_role | Canonical instance; primary, secondary, ambient or suppressed | Canonical group; usually ambient, explicit collective focus when meaningful |
| state_ids | Ordered intended performance sequence; a deliberate hold uses one state | Shared group states |
| blocking | Position, facing and relation needed by this shot | Shared staging; distinguish a crop from people actually leaving |
| gaze_target | Object ID, camera/down/away/eyes_closed, or offscreen:SOURCE | Shared behavior in the group state |
| view_id | Needed for generated 2D state/view coverage at Illustration | Needed for a 2D group cutout |
| count | One individual instance | Exact people represented by this shot's group variant |

Zero-character shots need no cast rows. Entries must cover every visible actor
exactly once, including extras. The exports provide scene_cast_inventory with
people per shot; do not sum counts across shots to claim unique population.
Do not make every crowd member a protagonist or animate every background person.
When a state changes the intended gaze, a compact gaze_targets mapping binds
state ID to target; do not leave the face recipe and gaze note contradictory.

An anonymous group is valid only when members share staging/behavior and no
member independently matters. Give a speaking extra, distinct action, individual
reaction or individual close-up its own character_id and object_id. Collective
fear/movement can remain a group with an explicit collective focal intent.
Wide group plates are separate alpha assets, not people baked into the room
background. A native 3D group remains native geometry with named members/parts.

## Character design and expressions at Illustration

Every used character has identity and importance=principal|supporting|extra,
plus a design: silhouette, proportions, costume, identity_anchors and
detail_strategy. Principal characters also require face_features. Record
visible ages, relationships, appearance, era and decision status in the existing
character_setting_brief; unresolved choices stay explicit before image generation.

Principal design must sustain recognition and close viewing: distinctive head/
hair/body silhouette, stable facial construction, controllable eyes/brows/mouth,
costume and a few useful identity anchors. Increase readable, story-relevant
detail; adding ornament everywhere is not the goal. Supporting characters still
need readable identity/acting. Anonymous extras use simpler distant silhouettes;
an extra promoted to close view receives the appropriate design and states.

Each used character state defines id, emotion, intent, expression.eyes,
expression.brows, expression.mouth and pose. These describe original drawn
appearance and body support, not just an emotion label. Common useful states
include ordinary ease, listening, doubt, recognition, held fear and aftermath.
Use only those the story needs; no expression/pose quota or Cartesian grid.

Horror changes the performance: gaze fixes before the head follows, breath holds,
mouth closes or parts slightly, shoulders/hand support tighten, a reaction settles
into persistent fear. Scale intensity to the event. Default excludes meme faces,
comic rubber deformation, gag falls, laughter, punchline resets and playful
motion at the scare. A strong scream can still be story-justified; restraint does
not mean every face stays neutral. Clues and faces remain legible in dark artwork.

2D pose frames declare performance_state_ids. Reusable body parts can support
several states; faces/poses must actually support the named appearances. Every
required state must exist in the cast-required view for each requested component.
Whole poses and separate face/part assets are both valid. Only frame-relevant
states go into a copyable image prompt, so a later reveal is not injected into
earlier expression requests. Keep internal lore separate from drawable identity.

Crowd definitions have identity, grouping_reason and shared states with appearance
and behavior. Each crowd pose/variant has performance_state_ids and member_count.
Different counts/crops require matching variants; six people cannot silently be
represented by the same two-person bitmap. When count/behavior is truly dynamic,
use individually registered people or a native authored group instead of faking
independent acting inside a rigid plate.

Native character/group variants carry the same performance_state_ids (and group
member_count). Preserve the complete lowbudget3d + 3dviz-pro-max fabrication,
articulation, surfaces, anchors and closest-use inspections. Morphs/rigged face
controls execute states; a raster replacement is not native fabrication.

asset-brief outputs character_design_sha256. At real asset registration, bind
the artwork to that hash and perform the existing current asset_digest visual
review. Changed identity/expression, approved visible ages/setting or art direction
invalidates the character hash; changed drawn state/view/count variants or files
invalidate the asset review. A valid excerpt can reuse a reviewed superset.
Exporting the expected hash does not bind, fabricate or approve artwork.
generation_blockers records unresolved design choices before human-run Flow.
Explicit unresolved character/group choices also block authored production.

## Motion, VFX and actual review

At phase=authored, shot.performance_tracks covers every cast instance with ordered
section-absolute keys {frame, state_id}, starting at shot.start_frame. Optional
gaze_target changes are explicit. The keys execute the shot's intended state
sequence. Existing per-object behaviors, camera intent, contacts, source bindings
and measured 60fps timeline still apply.

Every generated 2D actor component needs its actual sprite binding and pose_track:
{frame, pose_id, performance_state_id}. Keys match the performance track and a
registered pose in the required view. Explicit pose tracks are one-shot control,
independent of list order/hold durations. They reconstruct correctly on seeks.
Native rigs consume performance tracks through actual authored variant/face controls.
No character or crowd reset simply because a new shot function begins.
If the same instance enters in a different state, entry_change_reason records
the story/event/off-screen cause rather than silently resetting its expression.

Python performance_at and browser performanceAt return control intent. sprite_state/
spriteState selects the actual registered replacement. Runtime cast_states must
come from evaluated mounted poses/rigs and group population, alongside existing
camera/object/event observations. State labels are not pixel proof of emotion.

Review actual principal/supporting recognition, eye/brow/mouth/body readability,
gaze/support/contact, view swaps, crowd count/readability, focal hierarchy and
horror tone. Review templates include character, performance, crowd and horror_tone
targets; these remain UNVERIFIED until actual media is inspected. VFX reacts to
events and respects those performances; it does not replace facial acting.

## Reference evidence and trial

The official OverSimplified recruitment page distinguishes animation, asset
creation and research/writing: https://www.oversimplified.tv/create (checked
13 October 2026). It does not publish a mandatory main-character detail formula.
The hierarchy/face/crowd rules above implement the user's observation and our
original horror adaptation; they are not claimed as the channel's internal rig.

examples/horror-ensemble-draft.json is a proposed contract trial, not a selected
film/cast. Three shots represent 9, 4 and 1 people: two principal individuals,
one supporting individual, and anonymous group variants with 6 or 2 people when
visible. Cropping explains the reduction. Designs/visible ages remain proposals;
no voice, artwork, animation, listening or fear quality is approved by the trial.
