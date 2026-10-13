# Code2Video V4.1 Horror

Read [START_HERE.md](START_HERE.md). This is the dedicated horror fork, not the
historical provider pipeline. See [Horror contract](docs/HORROR_CONTRACT.md).

Illustration exports prompts for every generated character part/pose, prop and
background. The human user runs Flow; automated submission is disabled. Current
art direction follows [OverSimplified storytelling](docs/OVERSIMPLIFIED_ILLUSTRATION.md)
for horror, with AI artwork and Remotion acting/compositing. Alpha assets use a
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
