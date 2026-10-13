---
name: horror-audio-director
description: Direct OmniVoice narration and character acting plus event-timed generated Small-SFX for V4.1 horror, preserving cast, measured timing and serialized GPU stages.
---

# Horror Audio Director

Read [voice and sound workflow](references/voice-and-sound.md) and the workspace
[Horror contract](../../../Code2Video/docs/HORROR_CONTRACT.md) for API/data details.
Use script-to-visual-director for intention/reveal/cast and cinematic-motion-director
for contact/material/causal acoustic behavior. This bridge does not replace them.

The user chooses English or Vietnamese per film; exactly one main narrator, no narrator
instruction. Other references serve dialogue. Preserve character speaker identity.
OmniVoice is the voice provider; Small-SFX is the SFX provider. No Kokoro/Freesound.

Mood is creative direction, separate from valid provider instruction. Null/whisper
is supported by the audited cloning adapter; arbitrary fear/anger/grief is not.
Do not alter a parser whitelist and claim learned acting. Audition same-speaker
delivery references and actual takes. Never invent a transcript or listening PASS.

Design cue onset, audible duration and decay/perspective at storyboard time. There
is no fixed 8s duration or required sound per beat. Voice and sound stages are
explicit commands with GPU release between them, not permission to chain stages.
