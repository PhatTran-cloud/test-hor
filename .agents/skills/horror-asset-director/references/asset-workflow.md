# Behavior-led artwork and pose review

## Preflight before image requests

Follow the character and setting brief in Code2Video/docs/HORROR_CONTRACT.md.
Read the actual script and current packet; for every affected character record
canonical ID, relationships, visible age/age band, face/body/silhouette, costume,
distinguishing features and required story states. Record setting/era and check
architecture, technology, clothes and props together. Link supporting script
text/research; label inference, proposal, user decision and unresolved questions.
Ask the user about missing/conflicting details that affect design before submitting
affected images. Do not choose an era from generic village imagery or visual age
from a voice-library label. Preserve existing approved choices.

Translate the current selected style into shape, proportion, face, material and
lighting instructions. For OverSimplified follow Code2Video/docs/OVERSIMPLIFIED_ILLUSTRATION.md:
simple expressive characters, complete worlds and purposeful props/acting, not
a fixed drawing recipe. Illustrated shading/detail is allowed when useful. Record
effective prompts and actual model evidence; a label or completed job is not approval.

Plan characters as animation sprites: object x action x required camera view,
with phases justified by the story mechanics. Standing identity references are
not the final animation set. Keep face/body/costume and scale consistent, leave
crop room for the action, and plan root/ground/grip registration. No pose quota.
Request images, not AI video; code owns animation and camera/VFX.

Character cutouts require real transparent alpha PNG. Props/backgrounds retain
their original format unless compositing needs alpha. Preserve originals and
verify actual alpha/edges/crop after generation; checkerboard artwork or RGB-to-PNG
conversion is not background removal. Measure returned dimensions and anchors.

## Behavior, generation and review

For direction, inspect action/anatomy/material footage or references. In the packet
record source/page/time, observed mechanics and the decision, separately from fictional
departures. Explain intention/gaze, support/center of mass, contacts/grips, anticipation,
action, follow-through and terminal state; justify intentional stillness.

Use the packet's current primary reference. OverSimplified uses the inspected
research and illustration direction; Kage is historical for this film. The cinematic-video-prompt-skill
snapshot in Code2Video/references offers camera/light/material/style/pose vocabulary;
read relevant references, not its AI-video provider limits as global video rules.

For artwork, derive object × action × required view from the camera/reveal. Pose
intermediates follow mechanics/readability; a front/side/back standing sheet is only
identity reference. Lock canonical face/body/costume/prop identity and style bible.
Export Flow prompts for isolated full-crop parts/poses, props and layers, plus
complete empty background clean plates. Each shot belongs to one shared scene
world: preserve layout/perspective/light/crop across shots. Do not bake dynamic rain,
fog, blur, interactive shadows or final camera composition into each pose.

Use production.py asset-brief to export requests without calling Flow. The human
user runs Flow; no automatic browser/Flowkit generation. Declare illustration.method
for every visible object; every generated character component, prop and background
needs explicit assets/prompts. Export groups of five are not a claim of concurrency.
Alpha-required items use uniform solid #00FF00, without green subject color, spill,
shadow, texture or checkerboard. Opaque backgrounds keep their drawn world. Run
production.py chroma-key only in the authorized cleanup step; preserve source,
mask and receipt, inspect actual alpha and register measured root/ground/grip
points, dimensions, scale and holds. Components retain their own hashes/registration;
their parent/joint relationships belong to the authored rig, not the simple sampler.
Mask cleanup is not automatically successful; inspect edges and hidden regions.

For motion, emit asset/instance/action/view bindings, root tracks, contact windows,
view limits and persistent state. The provided sampler only solves pose timing and
simple root contact, not deformation or multiple joint constraints. Use an authored
rig/solver where mechanics require it. Camera must not reveal nonexistent sides.

Review identity/silhouette/material/light/registration in sheets, then acting/weight/
foot sliding/grip/view pops/cloth response in a clip. When it fails, identify the
missing pose/view/registration or rig; do not claim polish alone meets the requirement.
