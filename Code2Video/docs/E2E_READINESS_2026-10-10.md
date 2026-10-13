# V3 end-to-end readiness — 2026-10-10

Scope: inspect v3 and prepare one new topic. The user chose a new topic;
the topic name, angle, and requested length have not been supplied yet.
No new production film was authored or rendered during this preflight.

New topic outputs are written to `D:/manim/outputs/<topic>/` by the shared
resolver in `src/output_paths.py`.

## Verified on this machine

- Repository: `D:/manim/Code2Video`, branch `main`, HEAD `b71c5c3`.
- Read active `AGENTS.md`, v3 production contract, v2 visual contract,
  editorial policy, runner, renderer adapters, narration code and v3 tests.
- Existing local modifications in `AGENTS.md`,
  `REPO30_PRODUCTION_CONTRACT.md` and `prompts/stage2.py` were preserved.
- Six v3 contract/audio tests: PASS.
- Fixture browser `npm run check` / TypeScript compilation: PASS.
- Fixture `render_local.py --validate-only`: PASS.
- Python 3.12.0 / ManimCE 0.19.0 import: PASS.
- FFmpeg, ffprobe, Node v24.18.0, npm 11.17.0, latex and dvisvgm available.
- Local Kokoro container running, voices endpoint reachable, `am_michael`
  available; real speech preparation: PASS.
- Fixture browser dependencies present with its pinned lockfile.
- Existing tracked diff whitespace check: PASS.

Fresh `--prepare-only` source/audio snapshot:

`D:/manim/Code2Video/src/CASES/LOCAL_ASSISTANT_9e178428/0-V3_mixed_renderer_integration_check`

Measured fixture speech: 284 frames / 4.733333 seconds, natural speed 1.0,
no time stretch. This verifies preparation, not a fresh full-render run.
Earlier mixed-renderer export evidence remains in
`outputs/v3_verification/report.json` and `docs/V3_VALIDATION.md`.

## Production path

1. Receive the topic; research claims with primary sources and record limits.
2. Write a topic brief and complete English narration in this conversation.
3. Plan causal beats and reveal timing; choose section/shot/step counts from
   content complexity. Route each visual task to Manim, Remotion or Three.js.
4. Author local sources and a `schema_version: 3` plan. Carry visual,
   scientific, editorial, motion/VFX and selected audio contracts.
5. Validate inputs, then run `--prepare-only` to freeze sources/assets and
   measure Kokoro narration. Set authored shot frame totals to measured speech.
6. Render with `local_tools/render_local.py`; repair sources in this chat.
7. Verify final 1920x1080 / 60fps output, frame totals, audio and full decode.
   Review stills and motion, factual fidelity, VFX attachment and listening
   separately. Report PASS/FAIL/PARTIAL/UNVERIFIED with evidence.

Commands from the repository root, once the topic plan exists:

```powershell
.venv/Scripts/python.exe local_tools/render_local.py <topic-dir>/plan.json --validate-only
.venv/Scripts/python.exe local_tools/render_local.py <topic-dir>/plan.json --prepare-only
# Update shot durations and authored motion using speech_timing.json first.
.venv/Scripts/python.exe local_tools/render_local.py <topic-dir>/plan.json
```

## Timing and scope limits

- The checked-in fixture plan contains 360 shot frames, but its narration
  measures 284. Do not run it unchanged with TTS: the renderer correctly rejects
  unequal totals. `local_tools/v3_smoke/verify.py` measures speech and adjusts
  the final shot for the full integration check.
- `--validate-only` checks contracts and source entry locations. It does not
  validate dependency completeness, visual quality, cue asset availability,
  or equality with speech that has not yet been measured.
- English male `am_michael`, 1080p60, natural speech timing, no music and no
  burned subtitles remain the active defaults. V3 adaptive SFX is selective;
  empty cues are valid. Selected assets require provenance and listening.
- Three.js production needs the complete lowbudget3d + 3dviz-pro-max workflow.
  The spatial fixture is an integration example, not a fidelity benchmark.
- Current adapters do not implement cross-section J/L audio overlaps or
  automatic browser source generation. No LLM API/CLI adapter is needed.

Readiness: local runner, preparation, and one complete authored topic PASS.
The completed topic is `D:/manim/outputs/stardust_to_human`; its final render,
measured storyboard, English narration, frozen CC0 audio assets, mix manifest,
contact sheet, and QA report are stored there. Visual and listening review remain
explicitly marked for human review in `qa/final_report.json`.
