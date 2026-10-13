# V4 workflow hardening — 10 October 2026

Active repository: D:/manim/Code2Video. No complete new topic film was requested
or generated. Existing V1–V3 production outputs and the v5 reference were retained.
Before these changes, 177 nonignored source/document files were archived with
hashes at D:/manim/backups/Code2Video-v4-before-hardening-20261010-132219.
Ignored secrets, dependencies and production media stay at their original paths.

## Findings and repairs

| Failure path | Current behavior |
|---|---|
| Multiple conflicting production instructions | START_HERE -> topic packet -> current-stage guidance; production.py is the V4 entrypoint; legacy contracts/prompts are explicitly historical |
| Repeated full-film context competing with one shot | context --shot includes the selected card, its objects/beats/state/anchors and neighboring handoffs; skill routing follows the selected shot |
| No auditable research-to-art link | packet records brief, sources/factual claims, visual decisions, representative acceptance and concrete consulted skill resources; full lowbudget3d/base references remain required for 3D |
| Recording passages mistaken for semantic beat slots | prepare records real anchors and removes provisional beat intervals; multiple beats may share one passage and get authored timing later |
| Edited timing still presented as measured | audio/script/voice/speed/frame count/anchors must match the frozen Kokoro measurement receipt |
| Entire film rendered before checking its art | representative preview + actual visual/layout/motion/editorial review is required before production; source/style/timing changes invalidate it |
| A comment containing a symbol counted as implementation | source binding uses Python AST / TypeScript lexical names excluding comments and strings, followed by runtime observations |
| Planned bounds mistaken for rendered layout | renderer emits contract-bound actual/projected bounds at required frames; missing samples, unintentional overlap and out-of-frame avoid objects fail |
| First-frame audit ran on a hidden Remotion tree | metadata is separate; the browser audit waits for a visible delivery tree with delayRender and validates first/last frames as well as event samples |
| Manim horizontal lines had empty measured height | actual stroke padding is included in the rendered footprint; observed samples retain the absolute section clock |
| Frozen support code still pointed at originals | support modules are copied, rebased and collision-checked; browser sources and consulted resources are frozen with hashes |
| Any JSON/image used to approve all quality gates | typed evidence and observations must cover actual targets; artwork needs frames/clips, temporal gates need clips, listening needs the complete current final mix actually listened to |
| Old/stale/cropped test output declared released | release checks hashes, full frame count and independent current reviews; representative previews and technical fixtures cannot be released |

No beat, shot, object, animation or SFX density quota was added. Support objects,
background, B-roll, pattern, camera, transitions and VFX must have subject-specific
purpose. Pure formula math with >=80% Manim visual duration still excludes Kage.
Always 1920x1080/60fps; Kokoro English am_michael; no subtitles/decorative HUD;
natural measured speech, short ordinary joins, optional requested BGM and selective
event-driven real SFX. The existing mixer/Freesound resolver remains the audio path.

## Verification

- 37 regression tests pass, including old output/V3/audio tests and shared anchors,
  changed receipt, false source bindings, representative fingerprints, static
  objects, justified macro crops, cross-section handoff context, runtime contract/
  sample/overlap checks and scoped review/release failures.
- Browser TypeScript check passes. git diff --check passes.
- Real Kokoro prepare measured 322 frames with one recording passage anchoring
  two semantic beats; no automatic per-beat timing was fabricated:
  D:/manim/outputs/V4_hardened_coanchor_narration_check/runs/V4_7e9c7f76/timed_plan.json.
- Representative browser export successfully reuses and trims that same WAV:
  D:/manim/outputs/V4_hardened_measured_representative_check/runs/V4_1816bcfe/final.mp4.
  ffprobe: 1920x1080, 60/1, 100 frames, 1.666667s, audio stream present.
  All four requested absolute-frame samples (130,150,220,229) were observed.
- Full silent construction fixture using the hardened first-frame/event sampler:
  D:/manim/outputs/V4_rainforest_construction_study/runs/V4_ff7c7ab8/final.mp4.
  Three shots, cause/response -> comparison -> authored macro B-roll, 540 frames.
- Real Manim export at D:/manim/outputs/v4_adapter_clock_check/manim_clock.mp4:
  1080p60, 60 frames, section frame 180 and carried point.x=3, three actual mobject
  samples at 180/210/239. This is an adapter proof, not an art-quality judgment.
- A full production attempt with no representative review was correctly rejected
  before rendering. Fixtures/previews remain REVIEW_REQUIRED or fixture-only.

## Limits

The framework enforces sequencing, coverage, provenance and evidence freshness.
It cannot prove that a skill was understood, every pixel is tagged, a metaphor is
creative or a reviewer listened honestly. Sampled 2D bounds do not prove all-frame
3D occlusion. Three.js must implement genuine projection and be reviewed with its
complete craft workflow; no new 3D fidelity benchmark was produced in this audit.
Recording intervals are coarse measured passages, not ASR word alignment.

The leaf study is a deliberately simple graphic metaphor for adapter testing,
not the visual target for future science/storytelling. Audio transport/mixer tests
do not approve SFX/music taste. No new SFX/BGM listening PASS, scientific PASS or
cinematic production-quality PASS was fabricated. Every real topic still needs
researched artwork, a difficult representative shot and current clip/audio review.

Early V4 candidates are retained. To resume one, supply its real topic packet and
prepare a new receipt if the old audio has no measurement receipt; fill current
typed review evidence. No automatic migration promotes old quality assertions.
