# V4.1 Horror

Dedicated workspace at `D:/manim-horror-v4.1`, requested 11 October 2026.
Start with [Code2Video/START_HERE.md](Code2Video/START_HERE.md).

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
