# Code2Video V4.1 Horror

[Shared scene staging](docs/HORROR_SCENE_STAGING.md) preserves one world/plate across shot views, fixed clues, offscreen cast and typed story links. [Reference sampling](docs/REFERENCE_VIDEO_STUDY.md) uses reference-sample/reference-check for real local video, hashes and annotation coverage. Current three-video analysis is blocked (0/540 images), not an empirical finding.

Read [START_HERE.md](START_HERE.md). This is the dedicated horror fork, not the
historical provider pipeline. See [Horror contract](docs/HORROR_CONTRACT.md).

Default to [Horror light](docs/HORROR_LIGHT_WORKFLOW.md): short scene cards with
purpose/action/assets/camera/sound/handoff. `production.py asset-brief` exports
illustration requests; `production.py motion-brief` exports assembly tasks.
Full asset registration, motion/VFX execution and real-media review stay required.

See [Characters and crowds](docs/HORROR_CHARACTERS.md): reusable original principal/
supporting/extra designs, required eyes/brows/mouth/body states, explicit cast and
anonymous count per shot. Illustration checks required state/view/count coverage;
Python/browser motion uses absolute-frame pose selection. Default tone is
restrained horror with no humor. [Ensemble trial](examples/horror-ensemble-draft.json)
demonstrates 9, 4 and 1 people represented by tighter framing.

Illustration exports prompts for every generated character part/pose, prop and
background. The human user runs Flow; automated submission is disabled. Current
art direction targets [Kage](docs/KAGE_ILLUSTRATION_PIPELINE.md), with separate
2D artwork prompts and native lowbudget3d fabrication briefs. Light shots record
purpose, visible cast/components, focal action/camera and scene relationship;
metaphor/layer expansion is optional and execution detail belongs to Motion/VFX.
Alpha assets use a
uniform green source and `production.py chroma-key` produces alpha PNG, mask and
receipt, preserving originals. Code assembles movement, camera and VFX. OmniVoice
provides one main narrator and character dialogue in the user's selected English
or Vietnamese. Small-SFX generates event-specific audio with explicit durations.
There is no active Kokoro/Freesound route. GPU audio stages run sequentially.

Keep schema 4, semantic beat/shot many-to-many mapping, researched behavior,
the full 3D skill route only for actual spatial 3D, measured speech, 1080p60 and independent quality review.
Use `.venv/Scripts/python.exe local_tools/production.py --help` for explicit stages.
No command authorizes its following stage. Output: ../outputs. Configure host
providers in ../config.json. The imported voices still need transcripts/audition.
