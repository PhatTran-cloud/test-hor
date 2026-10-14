# V4.1 Horror

Story-led 2D horror with shared scene worlds, reusable Flow artwork, Remotion
acting/compositing, OmniVoice and generated Small-SFX. Keep schema 4 and the
single [production entrypoint](Code2Video/START_HERE.md), measured timing and
independent art/audio review. The human runs Flow; prompts are exported locally.

**Latest film: [Ngày 47](Code2Video/projects/day47/README.md).** The user's
14 October request selects Edge TTS, JavaScript drawings, Remotion and
Hyperframes for this voiced storyboard. It has 16 shots, a measured 92.5s clock,
and a scoped `storyboard-js` entrypoint; its narration/art choices override the
older Flow/OmniVoice defaults for this film only. No GPU models are required.

## Clone and start

```bash
git clone --depth 1 https://github.com/PhatTran-cloud/test-hor.git
cd test-hor/Code2Video
python local_tools/production.py --help
```

For reference sampling only, install Pillow and put FFmpeg/FFprobe on PATH:

```bash
python -m pip install Pillow
python local_tools/production.py reference-study examples/reference-windows.json --output ../outputs/reference-study
```

Supply the three actual local videos named in the manifest first. Each 180s
window produces 180 real images, source PTS/hashes, sheets and blank annotations.
See [sampling guide](Code2Video/docs/REFERENCE_STUDY.md) and
[scene/shot grammar](Code2Video/docs/SCENE_SHOT_GRAMMAR.md).
**The 540 OverSimplified reference frames are still unverified:** this session
retrieved captions/metadata but media delivery failed. Read the
[evidence report](Code2Video/docs/research/2026-10-14_reference_study.md).

## Production and checks

Full production needs the host tools/models/voice library in `config.json`.
Adjust the original Windows paths for your machine and provision the runtimes;
a source clone does not include weights, voices, outputs or installed environments.
From `Code2Video`, install `requirements.txt` for the full workflow. GPU/provider
setup and each human-authorized production stage remain in `START_HERE.md`.
Outputs live in `outputs/` at the repo root; reference videos are local inputs.

Run the regression suite from the repo root with the workflow Python environment:

```bash
python -m unittest discover -s Code2Video/tests -q
```

Current source, tests, necessary V4 fixture and pinned Small-SFX vendor files are
retained. Old academic/demo media, unrelated pilot projects, provider-stage
scripts and duplicate historical guides were removed; details and recovery links
are in the [cleanup report](Code2Video/docs/research/2026-10-14_repo_cleanup.md).
