# V4.1 horror project rules

Read START_HERE.md and docs/HORROR_CONTRACT.md before work. The user authorized a
separate horror fork at D:/manim-horror-v4.1 on 11 October 2026. The original V4
workspace is preserved in D:/manim; source working-tree changes were copied.

Current film direction, 13 October 2026: OverSimplified is the primary reference
for story-led 2D illustration, complete scene worlds, expressive character acting
and focus/zoom. Follow docs/OVERSIMPLIFIED_ILLUSTRATION.md and the recorded user
decision. Illustration exports prompts only; the human user runs Flow. Every
generated character/component/prop/background needs a prompt. Alpha assets use
uniform green #00FF00 source backgrounds, then local code produces real alpha PNG.
Do not impose a rigid flat-fill recipe; shading/illustrative detail may support
the reference's storytelling. Historical Kage/3D directions do not apply to this film.

- Do only the current human-authorized step, declare task/rule/source/skill purpose,
  command or manual action, inputs/outputs and stop; report actual work, linked
  evidence, unmet checks and a declared next step (proposed, not run), then stop.
- Use local_tools/production.py and schema_version=4 with profile=horror-v4.1.
  No custom runner, provider LLM adapter, future-stage background work or auto-PASS.
- Flow supplies human-generated reusable per-object action/component/view/layer
  assets in the user's selected style. Code supplies motion/camera/environment/VFX.
  Research behavior, weight/support/contact/gaze before pose prompts. Multiple main
  characters are allowed; no shot/beat/pose quotas. Sprite sheet polish is not acting.
- Before character references or pose generation, record character descriptions,
  relationships and setting/era grounded in the script in the production packet.
  Separate facts, proposals and user decisions; ask about unresolved material
  design choices. Voice age does not determine visual age. Follow the character
  and setting brief in docs/HORROR_CONTRACT.md.
- Animated characters require reusable action/view sprite sequences; standing
  references establish identity only. Character cutouts use real transparent PNG,
  not a painted checkerboard. Props/backgrounds keep their original format unless
  compositing needs alpha. Review actual dark horror cartoon style and readable
  age relationships in the selected style; a model label or technical completion is not artwork PASS.
- Keep complete lowbudget3d + 3dviz-pro-max with relevant full references only for
  actual spatial 3D. User-selected simple 2D character design is not a placeholder.
- Use script-to-visual-director, storyboard-motion-executor, cinematic-motion-director
  and cinematic-vfx-director; remotion-horror-vfx when Remotion horror applies.
  Project bridges: ../.agents/skills/horror-asset-director and horror-audio-director.
- The user selects English or Vietnamese per video. Exactly one same-language main
  narrator, no narrator instruction; other reference voices for dialogue, stable
  character speaker map. OmniVoice only; acting brief is not arbitrary emotion payload.
- Small-SFX generated audio only; no Freesound, Kokoro or missing-sound tone fallback.
  Duration is explicitly authored per cue, not fixed 8s. Record event onset/offset,
  material/perspective/tail; preserve ambience/reverb/aftermath across cuts.
- Voice -> save -> stop/release GPU -> SFX -> save/unload/release -> renderer.
  No concurrent voice/SFX model residency or automatic CPU fallback.
- Measured final voice/take timing, 1920×1080/60fps, no time stretching, subtitles or
  decorative HUD. Silence is valid; BGM only if requested, with local reviewed asset.
- One packet owns research/claims/cast/style/assets/beat/shot/continuity; preserve
  canonical IDs and the section/film clock. New outputs go to ../outputs.
- Freeze source/reference/transcript/model/take/assets/provenance hashes and actual
  listening selections. Missing transcript/audio inspection stays UNVERIFIED.
  Technical tests/source symbols are never art, acting, VFX or listening approval.
- Representative review must be current before full production. Final release needs
  all independent current-output gates; fixtures/previews cannot release.
- Historical snapshots are references only, including earlier Kokoro/Freesound notes.
  This project's current user choices and contract have priority over those snapshots.
