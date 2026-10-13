# Repo illustration update — 13 October 2026

Implemented the user's current instruction: illustration follows OverSimplified's
storytelling thinking for horror; it exports prompts and the human runs Flow.
The construction is flexible: simple expressive characters, coherent complete
scene worlds and functional props, with drawn shading/detail where useful.

## Concrete changes

- AGENTS, START_HERE, README, HORROR_CONTRACT and V4_AUTHORING_GUIDE now route the
  current film to [the maintained illustration direction](../OVERSIMPLIFIED_ILLUSTRATION.md).
  The project horror-asset-director skill and workflow reference agree with it.
- horror_contract and v4_contract select the current OverSimplified reference
  without requiring Kage. Historical plans remain readable; new direction needs
  recorded human selection and prompt-only illustrator configuration.
- prompts/v4.py and production.py context bring the selected reference and
  current character/setting/style/world direction into authoring context.
- horror_illustration.py checks per-visible-object ownership and generated asset
  coverage, including props/backgrounds; scene IDs reuse declared world layouts.
  Missing assets/worlds/views/poses stop export rather than silently skip objects.
- horror_assets.py exports JSON and copyable Markdown, grouping five prompts per
  batch. Each generated part/action/view/prop/background has its own prompt and
  hash. Alpha items request #00FF00; opaque backgrounds request coherent empty
  environment clean plates. Historical Flow-agent/3D metadata is excluded from
  effective character/setting prompt context.
- production.py flow-submit and direct flow_assets.submit fail before any network
  activity. Manual illustration needs no extension or backend connection.
- production.py chroma-key invokes horror_chroma.py: local RGBA PNG, matte mask
  and hashed receipt, preserving originals. It checks thresholds and refuses source
  overwrite, existing targets, absent green or an entirely removed subject.
- File validation respects explicit requires_alpha on props/layers and rejects
  opaque, non-PNG or entirely empty cutouts where alpha is required.
- Canonical production_packet.json records current reference, manual generation,
  green-key treatment and Remotion/2D shot direction. Previous decisions are kept
  in history and a before-update snapshot. Changed skill hashes were refreshed
  with the actual new direction decision, not silently bypassed.

## Validation

8 illustration tests, 21 horror regressions and 35 V4 tests succeeded: **64 total**.
These verify coverage/manual ownership, current reference/context routing, actual
matte pixels and source preservation, opaque-format exceptions, deterministic
sprite/timing behavior and unchanged independent audio/review gates.

The updated project skill passed quick_validate. The canonical packet passed
production.py check as **draft; renderable=false; quality=UNVERIFIED**. Chroma-key
CLI help was checked. No live model, Flow request, generated film image or render
was executed by these checks. Audio provider transports are fixtures in unit tests.

## What this does not prove

Actual art consistency, scene richness and edge quality require returned images.
Green on a subject cannot be recovered by chroma key; thresholds and despill need
inspection on light/dark backgrounds. The helper is not guaranteed segmentation.
Five exported prompts do not establish Flow's concurrent processing capability.

Film-specific world layouts, generated/procedural/existing ownership and part/pose
asset requests remain pending. This repo edit does not invent or export completed
film prompts. Parts use the existing sprite_sequence schema; exporting them is
not a new multi-joint rig implementation. Remotion articulation/contact solvers
and actual animation must be authored and reviewed in the motion step.

Applied skills: horror-asset-director for compositable art/prompt/alpha direction;
skill-creator for the focused skill update and structural validation. Earlier
reference observations remain in the OverSimplified research report; no internal
software/rig/FPS or sound-listening claims were added.

Proposed next step, not run: use script-to-visual-director for scene/shot geography,
cinematic-motion-director for action/contact needs and horror-asset-director for
part/pose/prop/background requests, against the existing first-minute script,
approved ages/era and measured word timing. Follow OVERSIMPLIFIED_ILLUSTRATION.md;
author the scoped packet, then run production.py asset-brief to produce JSON and
Markdown prompts for human-run Flow. Stop at prompts and any material uncertainty.
