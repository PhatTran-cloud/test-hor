> Historical versioned contract. New production starts at START_HERE.md.

# Code2Video 2.0 Visual Contract

Every generated section is a small visual system, not a literal illustration of the narration.

## Required Section Data

- `visual_thesis`: the image-based claim of the scene
- `visual_metaphor`: the visual language that carries the claim
- `foreground`, `midground`, `background`: depth layers with informative behavior
- `primary_object`: the object carrying the teaching point
- `secondary_objects`: supporting objects with a role and visible behavior
- `object_relationships`: causal or spatial relationships that must be visible
- `camera_plan`: why the camera moves and what it reveals
- `transition_in`, `transition_out`: continuity between neighboring sections
- `sfx_cues`: optional timed sound events linked to visible actions

Older storyboards remain valid. The agent supplies conservative defaults for missing fields while existing projects are upgraded.

## Composition Rules

Foreground objects may frame or occlude the view only when that occlusion carries meaning. The midground owns the primary action. The background supplies scale, context, atmosphere, or hidden information. Labels and formulas have reserved zones and must never compete with the active object.

## Audio Rules

Default audio is narration-only, with no music or SFX. Scenes follow measured natural speech; do not slow narration or pad scenes to reach an arbitrary runtime. Keep exterior silence at scene joins below one second. Do not burn subtitles into the picture.

SFX require explicit opt-in. When enabled, cue types include `reveal`, `transition`, `camera`, `impact`, and `step`. The optional mix is deterministic, ducked beneath narration, and recorded in a provenance manifest.

`src/freesound.py` provides optional search and preview caching, using `FREESOUND_API_KEY` from the ignored root `.env`. It records each selected sound's creator, source URL, license, and file hash. It is an asset preparation tool; the current mixer still uses procedural cues and does not automatically select or mix Freesound search results.

## Backup

The pre-2.0 state is preserved in Git as branch `backup/code2video-v1-20261009` and tag `code2video-v1-20261009`.
