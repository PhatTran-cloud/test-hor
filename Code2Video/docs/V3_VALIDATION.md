# V3 integration verification — 2026-10-10

Verified on the local Windows project, Python 3.12 / ManimCE 0.19.0 and the
fixture's pinned Remotion 4.0.534 browser dependencies.

- Six contract/audio tests passed: legacy defaults, mixed routes, invalid clocks,
  3D/scientific/evidence gates, deterministic stereo/ducking/peak-safe mix,
  license policy and explicit v2 procedural compatibility.
- TypeScript `tsc --noEmit`, Python compilation and `git diff --check` passed.
- Existing six-section El Niño plan passed local input validation with voice-only defaults.
- Real Freesound CC0 candidate search succeeded using the ignored environment key.
- Selected asset 669468, **Low Click 1**, CJspellsfish, CC0, preview cached with SHA-256
  and source metadata. Selection was by metadata/event intent; listening is unverified.
- Full local render exported Manim, Remotion SVG/VFX, and ThreeCanvas spatial shots,
  then mixed one selected SFX under Kokoro `am_michael`, preserving stereo.
- Measured speech: 284 frames. Final output: 284 frames / 4.733333 seconds,
  1920x1080, both frame-rate fields `60/1`. Full FFmpeg decode succeeded.
- Contact sheet showed marker movement, source-attached pulse and sphere/path/marker;
  no blank renderer handoff. This supports fixture visibility, not a cinematic or
  domain-fidelity approval.

Latest evidence on this machine: `outputs/v3_verification/report.json`,
`outputs/v3_verification/contact.jpg`, render log and the referenced source snapshot.
These generated outputs are ignored by Git. Reproduce with
`local_tools/v3_smoke/verify.py`.

Status: **technical integration PASS**. Production artistic/scientific/VFX acceptance,
audio listening and true-peak mastering remain **UNVERIFIED** for this technical fixture.
No finished El Niño or other pilot was regenerated. Cross-section J/L sound bridges,
automatic browser source generation and arbitrary legacy Three.js project conversion
are not implemented by these adapters.
