# Reproducible reference video study

Use real media and inspect images. Transcripts, player metadata, sparse scrub
previews and synthetic images do not establish a one-image-per-second study.
The [current three-video request](research/oversimplified_study_request.json)
is **blocked**, with 0/540 images sampled/inspected. It is not a completed study.

The research commands share `local_tools/production.py`; they do not start
models, generate a film, submit Flow prompts or supply artwork approval. FFmpeg,
ffprobe and Pillow are required. Generated reference caches belong in ignored
`outputs/`; do not commit third-party clips or frame collections to the public repo.

## Sample a supplied local video

For a full original file:

```bash
python local_tools/production.py reference-sample french.mp4 \
  --source-url 'https://www.youtube.com/watch?v=8qRZcXIODNU' \
  --start 0 --seconds 180 --output ../outputs/reference-study/french
```

For an already cut clip beginning at original source 17:00:

```bash
python local_tools/production.py reference-sample pig-17m-20m.mp4 \
  --source-url 'https://www.youtube.com/watch?v=QLq6GEiHqR8' \
  --source-offset 1020 --seconds 180 --output ../outputs/reference-study/pig
```

`--start` is local file time; `--source-offset` is the original source time at
local file zero. The URL/offset are declared provenance, not identity proved by
the file hash. Choose the actual source file, verify its title/content and record
edits. The sampler never silently downloads, overwrites evidence, creates filler
frames or substitutes thumbnails when a video is missing/unreadable/too short.

Output: 180 JPEGs, nine timestamped contact sheets, `manifest.json` and an empty
`annotations.json`. Manifest records source/frame/sheet hashes, decoded stream
size/frame rate, sampling arguments and tool versions. The sampled timestamps
are a nominal one-second grid using FFmpeg fps round=up (source frame at/before each point), not exact source PTS.
Clips with variable rate, unusual edit/start timestamps or important fast cuts
need an extra precise source-frame check. Similar/still frames can be valid holds.

## Inspect and annotate

View every contact sheet and enlarge ambiguous full-size frames. Record the
actual inspected indices and reviewer. Add `sample_groups` only after inspection:

```json
{
  "id": "observed_view_01",
  "first_index": 0,
  "last_index": 5,
  "scene_id": "observed_location_a",
  "composition": "Describe the observed arrangement and focal subject.",
  "background_information": "Which fixed details add context/evidence?",
  "cast_and_props": "Individuals/groups, visible expressions, meaningful props; note uncertainty.",
  "camera": "Observed framing/crop change or hold; do not invent a lens.",
  "next_visual_link": "Describe what visible state/action links to the next sampled view."
}
```

These are sampled view groups, not guaranteed exact shots: a cut lies between
neighboring sample times, and brief intermediate shots may be entirely absent.
Do not count a face/pose replacement as a cut without a framing/context change.
Scene geography and shot framing are separate. Distinguish observed arrangement,
interpretation and proposed horror adaptation. Keep unknown details explicit.
Audio is NOT_PERFORMED by this tool; do not infer SFX/dialogue/music from stills.

Run:

```bash
python local_tools/production.py reference-check ../outputs/reference-study/french
```

The checker verifies hashes, dimensions, one-second grid and manifest-bound,
non-overlapping annotation coverage. Empty/partial notes stay INCOMPLETE. Full
declared coverage is REVIEW_RECORDED_NOT_INDEPENDENTLY_VERIFIED, never automatic
analysis/art/fear PASS. It does not verify that someone actually looked or
listened. Never fill inspected_indices from an extraction script.

## Synthesis after real inspection

Use source timecodes/examples to compare internal staging, background reuse,
principal/supporting/extra treatment, attention changes and links between views.
Report differences between the three windows. Separate sample-specific findings
from recommendations; do not turn nine minutes into whole-channel averages or
an official storyboard formula. Keep original Kage artwork/horror performance.
Update active examples/contracts only when the evidence supports a change.
