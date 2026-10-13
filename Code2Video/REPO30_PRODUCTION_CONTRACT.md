> Historical versioned contract. New production starts at START_HERE.md.

# Code2Video 3.0 production contract

V3 adds executable renderer routing and an editorial/effects contract to the v2
visual system. The assistant in this chat researches, authors and reviews the
sources. No Codex CLI/API substitute for this conversation is introduced.

## Routing from the research

Use the visual task, not the channel category, as the decision boundary.

| Visual task | Primary route | Why / limit |
|---|---|---|
| Equations, proofs, geometry, causal scientific diagrams | `manim` | Mathematical object identity and transformations; 3D is useful for schematic spatial reasoning |
| Maps, timeline, footage, UI, comparative panels, typography | `remotion` | Browser media/layout tools; maps still require real data, projection and label rules |
| Material-rich worlds, recognizable objects, spatial cameras, atmospheric 3D | `threejs` | Complete lowbudget3d + 3dviz-pro-max authoring and validation; scientific solver/data are separate responsibilities |
| Mixed educational/storytelling sequence | Per-shot routing | One narration clock, visual system, continuity and final audio mix |

Remotion's 3D integration is compared with the **lowbudget3d workflow**, not
with Manim's geometric 3D. `@remotion/three` hosts deterministic frame export
of a Three.js scene; it does not guarantee art fidelity or substitute for the
complete 3dviz-pro-max resources, lighting/materials/asset workflow and QA.
Existing 3D projects retain their authoritative scene, camera and renderer;
port only the time/export boundary deliberately. GPU simulations need an
absolute-frame solver/cache, not preview-history-dependent updates.

Research: `docs/research/youtube_niche_renderer_matrix.csv` and the full report
beside it. Its 48 broad families / 240 examples are a practical taxonomy, not
an exhaustive census or measured quality benchmark of every YouTube niche.
The earlier El Niño Remotion trial remains isolated and was 2D/SVG, not a 3D benchmark.

## Executable plans

`schema_version: 3` fixes 1920x1080 / 60fps, defaults to narration pacing,
preserved native scene duration and adaptive SFX. Legacy plans default to Manim
and voice-only. V2 visual fields remain applicable.

Storyboard section, shot and animation-step counts follow causal structure,
explanatory complexity and information gain. There is no ordinary/key-section
quota or cap on detailed sections. Use enough steps to explain the mechanism,
merge redundant actions and split overloaded ones. Labels and animation steps
are independent, not a mandatory one-to-one mapping. Timing still follows
measured narration; count freedom is not a reason to pad or overcrowd a scene.

Every section may use a single `renderer` or contain `shots` with their own
renderer, safe `id`, `duration_frames`, source and contract. Shot frames total
must equal measured section speech frames. The runner renders each shot,
normalizes mixed encoding, concatenates the shots, then attaches one continuous
section narration. It never stretches the shot timeline to hide a duration error.

Manim shots have `source` and `scene_name`. Browser shots have:

```json
{
  "renderer": "remotion",
  "scene_type": "2d",
  "render_spec": {
    "project_dir": "browser",
    "entry_point": "src/index.tsx",
    "composition_id": "MyComposition",
    "time_model": "absolute_frame",
    "props": {}
  }
}
```

The adapter supplies `durationInFrames`, `speechTiming`, `vfxEvents`, width,
height and fps. Authored compositions must consume these values using
`calculateMetadata` and frame-driven state. No `useFrame`, wall clock, CSS
animation, unseeded randomness or second master loop. The adapter checks actual
output size/fps/duration; it does not certify source determinism by declaration.

Three.js additionally declares `scene_type: 3d` and `three_contract` containing
workflow `lowbudget3d+3dviz-pro-max`, representation, coordinate_frame, units,
scale_exaggerations and asset_provenance. The contract is a production gate,
not proof that a primitive fixture achieves high fidelity.

`scientific_contract` names schematic vs numerical_simulation. Simulations need
equations, authoritative state and sources. Editorial evidence needs sources.
Read [the editorial policy](docs/BROLL_EDITORIAL_POLICY.md) before shot planning.

## Motion and VFX

Apply cinematic-motion-director for choreography/continuity and
cinematic-vfx-director for effects. Remotion horror additionally uses
remotion-horror-vfx. Their installed complete resources remain authoritative;
this repo stores their interface and does not copy a reduced skill replacement.

`vfx_events` record id, cause, source/anchor, trigger, representation,
start/peak/end, interaction, residue, lighting_response and transition_handoff.
Implement cause → source → transport → world interaction → decay/residue →
optical response → handoff. Distinguish atmospheric support from a hero event.
Default to one main action and restrained atmosphere; add a second effect only
with a causal reason. Avoid generic glow, lens overlays, repeated flashes and shake.

The render host passes the ledger; scene code realizes the effect. No universal
particle overlay is injected automatically. Review before/peak/after, a motion
segment, depth/attachment and the scene with effects disabled. Technical success
and visual/scientific/VFX acceptance remain separate gates.

## SFX research and mix

Adaptive means selective, motivated sound, including intentionally empty cues.
Foley corresponds to visible material/action; ambience establishes persistent
environment; accents mark rare reveals; transitions preserve an existing energy.
Do not sound every arrow, label, camera move or cut. Space scenes must not imply
literal propagation of sound in vacuum; stylized accents should be understood as score/design.

Each cue records trigger, purpose, role, section-relative time, duration,
gain_db, fades, pan, optional asset_offset/loop, and a selected sound_id or local
file. `gain_db` is relative to active narration RMS: initial event/foley -18dB,
ambience -24dB, refined by listening. These are project starting values, not
universal psychoacoustic targets. More than one prominent simultaneous cue
requires a clarity reason. Sustained recordings can be looped with crossfades.

Research candidates with Freesound, listen for event/material/distance/tone,
then select explicitly. No first-result auto-pick and no synthetic fallback for
a missing recording. Freeze locally with creator, source, license and SHA-256.
Default commercial asset policy allows CC0 / CC-BY; CC-BY attribution remains
in the SFX ledger. API Token supports previews; original downloads need OAuth2.
The API key stays in the ignored root `.env` and never enters props/reports.

The mixer preserves stereo, trims using asset_offset, fades edges, ducks effects
from the speech envelope and caps sample peaks. It writes a per-mix ledger with
master attenuation and pending listening/true-peak status. It does not claim
broadcast loudness normalization. No music or burned subtitles are added.
Cross-shot sound is possible inside a section; cross-section J/L cuts remain
outside this mixer and are not silently claimed as implemented.
Legacy v1/v2 provider plans may retain their old procedural cues through an
explicit compatibility flag; schema v3 rejects unresolved cues before render.

## Authoring and execution

New topic projects and generated artifacts live in the workspace sibling
`outputs` directory: `D:/manim/outputs` beside `Code2Video` on this host. The shared
resolver is `src/output_paths.py`; `CODE2VIDEO_OUTPUT_ROOT` and the local
runner's `--output-root` support explicit overrides. Each topic contains its
authored project and fresh run snapshots. Existing historical outputs are retained.

```powershell
# Validate contracts/source locations without network/render:
.venv/Scripts/python.exe local_tools/render_local.py path/to/plan.json --validate-only
# Freeze sources/SFX and measure Kokoro narration to author exact shot frames:
.venv/Scripts/python.exe local_tools/render_local.py path/to/plan.json --prepare-only
# Research candidates (does not select/download first result):
.venv/Scripts/python.exe local_tools/prepare_sfx.py path/to/plan.json --search-only --output outputs/sfx_candidates.json
# Render after selecting assets and authoring durations:
.venv/Scripts/python.exe local_tools/render_local.py path/to/plan.json
```

Browser project dependencies must be installed with `npm ci`. Each run snapshots
project sources/assets and uses the original dependency tree via a directory
link. Full dependency versions are frozen by that project's lockfile. A manifest
records the authored contracts; per-shot QA records technical output separately
from pending visual/scientific/VFX checks. Legacy provider code generation is
still Manim-specific; browser/mixed sources are authored locally and never sent
through its Python repair loop.

`local_tools/v3_smoke` is a small integration fixture, not a production film or
evidence of high-fidelity planetary rendering. It tests three renderer routes,
one source-attached informational VFX pulse and mixed-shot export. Its voice-only
override keeps the visual test independent; selected Freesound/mixer checks are separate.

## Sources and backup

- [Remotion Three integration](https://www.remotion.dev/docs/three)
- [Deterministic rendering](https://www.remotion.dev/docs/flickering)
- [Freesound API resources](https://freesound.org/docs/api/resources_apiv2.html)
- [Freesound previews/authentication](https://freesound.org/docs/api/overview.html)
- User-provided B-roll masterclass, distilled in the editorial policy.

Pre-v3 commit `301bda7` is preserved at branch
`backup/code2video-v2-20261010` and tag `code2video-v2-20261010`.

Integration evidence and practical limits: [V3_VALIDATION.md](docs/V3_VALIDATION.md).
