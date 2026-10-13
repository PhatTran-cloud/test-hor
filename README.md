# V4.1 Horror

[Shared scene staging](Code2Video/docs/HORROR_SCENE_STAGING.md) preserves one room/plate across named shot views, background evidence and motivated story links. It feeds illustration, motion and actual review without inflating shot cards. [Reference sampling](Code2Video/docs/REFERENCE_VIDEO_STUDY.md) exports/checks real 1 Hz frames; [the current video study](Code2Video/docs/research/2026-10-13_oversimplified_sampling_status.md) is blocked with 0/540 frames.

Dedicated workspace at `D:/manim-horror-v4.1`, requested 11 October 2026.
Start with [Code2Video/START_HERE.md](Code2Video/START_HERE.md).

New horror work defaults to [Horror light](Code2Video/docs/HORROR_LIGHT_WORKFLOW.md):
short storyboard cards, separate illustration assets, then explicit motion/VFX
assembly tasks. See the [small washer trial](Code2Video/examples/horror-light-washer-draft.json).

[Characters and crowds](Code2Video/docs/HORROR_CHARACTERS.md) records any number
of principal/supporting/extra actors and anonymous groups, with original readable
designs and restrained horror expressions. The same cast/state/view/count contract
feeds illustration prompts, Python/browser motion and actual review. The
[ensemble trial](Code2Video/examples/horror-ensemble-draft.json) represents 9, 4
and 1 people across tighter shots; this is an unapproved production proposal.

Current illustration target is [Kage](https://github.com/MengTo/kage): export
separate 2D asset prompts and native lowbudget3d fabrication briefs, validate
complete-shot meaning/components, then hand reviewed assets to motion/VFX.
See [the pipeline contract](Code2Video/docs/KAGE_ILLUSTRATION_PIPELINE.md) and
[request-only example](Code2Video/examples/kage-request-benchmark.json).

The fork retains V4's schema 4, semantic beats, canonical objects/events,
continuity, renderer adapters, measured timing and independent review gates.
Horror specializes artwork, sprite assets, cast, OmniVoice, generated Small-SFX
and serialized GPU ownership. Output lives in this folder's `outputs`.

The 24 voice references and three pinned official SFX model graphs were copied
locally. Voice transcripts/listening/clone auditions remain unverified. Installed
Python environments were copied; use their `python.exe -m ...` commands rather
than old generated console launchers. System Python, FFmpeg, Node/npm, NVIDIA
driver and the existing OmniVoice Docker container remain host dependencies.

## Read-only inventory

From `Code2Video`:

```powershell
.venv/Scripts/python.exe local_tools/production.py doctor --check-weights
```

No model is started by this command. No production art/audio approval is implied.
See `outputs/upgrade/UPGRADE_REPORT.md` for implementation and verification.

## GitHub source snapshot

This repository contains the workflow source, project skills, documentation,
tests, dependency manifests and tracked reference assets. The existing gitignore
keeps generated `outputs/`, model weights, the voice library, Python environments,
Node dependencies and local secrets on the workstation. A clone is therefore a
source checkout, not a complete backup of rendered films or installed runtimes.

The checked-in `config.json` describes the original Windows host. Adjust its paths
for another machine and provision the local models, voice references and runtimes
before running production. Start with `Code2Video/START_HERE.md`.
