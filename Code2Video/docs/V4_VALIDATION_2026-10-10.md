# V4 implementation and validation — 10 October 2026

This records the initial V4 implementation. The current workflow's strengthened
entrypoint, representative gate, runtime/evidence checks and later verification
are in [V4_HARDENING_2026-10-10.md](V4_HARDENING_2026-10-10.md).

Active source: `D:/manim/Code2Video`. Prior edits, legacy plans and production
outputs were preserved. No v5 source/project/server was changed.

## Backup

`D:/manim/backups/Code2Video-v3-20261010-123059` contains working-tree.zip,
history.bundle, uncommitted.patch and manifest.json with per-file hashes.
The archive includes tracked and nonignored working-tree changes. Ignored .env,
dependencies and production media remain at their original paths.

## Implemented

| Area | Executable mechanism |
|---|---|
| Dynamic semantic beats | before/after/evidence/completion/dependencies; many-to-many shot coverage; no count quota |
| Real narration clock | draft -> Kokoro measured segments -> timed -> authored; script/audio hashes, am_michael, natural speed, no stretching |
| Visual direction | new current-session prompts; craft briefs, attention/camera/pattern/source bindings; conditional Kage art research |
| Pattern/B-roll | semantic reading structures, implementation bindings, executed shot mappings and output samples; browser construction helpers |
| Persistent world | section-absolute state tracks, film offsets, shared object state carry across sections, explicitly continuing events |
| Renderer transport | per-shot contracts via Remotion props / Manim environment JSON; full lowbudget3d + 3dviz-pro-max ownership for authored 3D |
| Transitions | handoff reason/state/source binding; implement inside allocated shot frames; no extra assembler padding |
| Motion/VFX | object modes, event cause/action/reaction/aftermath, VFX transport/interaction/lighting; original event envelope through cuts |
| Sound | selected/listened hash-bound assets, event-derived time/source, Freesound provenance, ducking/pan/fades; optional requested continuous BGM |
| Layout | delivery-space planned bounds plus sampled browser SVG/HTML actual bounds/overlap audit; full occlusion review separate |
| QA | frozen source and output hashes, execution ledger, frame samples; independent gates and release check that rejects stale artifacts |

Kage is a reference only: no code/artwork import, website UI or pacing quota.
Formula-focused math excludes it at >=80% **authored Manim visual duration**.
Sources: [README](https://github.com/MengTo/kage/blob/main/README.md),
[build prompt](https://github.com/MengTo/kage/blob/main/PROMPT.md).

## Tests and actual exports

- `python -m unittest discover -s tests -v`: **20 tests PASS**, including the
  existing output-path and V3/audio regressions.
- V4 browser `npm run check`: TypeScript PASS.
- `git diff --check`: PASS.
- Real Kokoro endpoint: measured 313 frames / 5.216667 s, two recording passages.
  Authored render reused exactly the same WAV SHA256.
- Voiced Remotion/SVG export:
  `D:/manim/outputs/V4_measured_narration_integration/runs/V4_7d9b5a23/final.mp4`.
  ffprobe: 1920x1080, r_frame_rate=60/1, avg_frame_rate=60/1, nb_frames=313.
- Silent technical construction export:
  `D:/manim/outputs/V4_rainforest_construction_study/runs/V4_36479c71/final.mp4`.
  Three authored shots, 540 frames: cause/response, comparison, macro B-roll.
  Requested frame samples inspected; visible response persists into comparison.
- Real Manim adapter export:
  `D:/manim/outputs/v4_adapter_clock_check/manim_clock.mp4`, 60 frames / 1 s.
  Captured source log confirms section frame 180 and carried point.x=3.

## Practical limits and truthful status

This is an implemented production/authoring framework, not a general compiler
that turns any JSON into beautiful art. Each project still needs researched
sources/artwork, authored pattern/camera/event implementation and inspection.
Symbol presence establishes traceability only. The illustrative leaf study is
not a botanical simulation, full science film or 3D fidelity benchmark.

Recording-segment anchors are measured coarse timing. No unverified ASR/word
timestamps are invented. Split passages or verify finer alignment for word hits.
Browser layout auditing covers tagged SVG/HTML at requested samples; projection,
3D occlusion, all-frame readability and temporal rhythm need project-specific QA.
Authored transitions are not automatically synthesized by the assembler.

The voice export deliberately has zero SFX. Mixer/regression and event-binding
tests pass, but no new production SFX/BGM selection/listening approval was claimed.
Both sequence quality reports remain REVIEW_REQUIRED; the comparison sample has
a documented PARTIAL layout review. Other visual/scientific/motion/VFX/editorial/
listening gates remain UNVERIFIED. Full lowbudget3d asset quality must be proven
on the actual project's 3D output; retaining its workflow string is insufficient.

Pinned browser dependencies are available through the original installed project
node_modules junction; source snapshots are frozen. Dependency runtime itself is
not vendored into each run. Install from the lockfile for a fresh checkout.
