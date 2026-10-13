# Casting, acting and acoustic direction

Choose language and one same-language main from voice_library. Dialogue characters
can span shots and use multiple speakers; map each character consistently. Review
reference language, transcript, speaker isolation and timbre before cloning. Main
uses canonical reference and null instruction. Dialogue keeps intention/mood separate
from clone instruct; fear does not always mean whisper or shouting.

User direction recorded 2026-10-11: for dialogue needing another age/timbre,
use OmniVoice's supported Voice Design attributes and audition the actual audio.
Approximate age/timbre is acceptable for the selected grandmother/child samples.
Run `production.py voice-design` and freeze the selected WAV as a stable reference;
do not redesign independently for every line. Narrator stays canonical with null
instruction. Gender/age/pitch/whisper controls do not establish arbitrary emotional
acting or waive transcript, word-level ASR or listening review.

The runtime clone endpoint is /_clone_fn with text, lang, ref_aud, ref_text,
instruct, ns, gs, dn, sp, du, pp, po. The adapter checks metadata before inference.
Do not assume working-copy source equals the running container. Style in reference
can win against instruction. Use appropriate auditioned same-speaker delivery
reference, text/prosody and take selection when direct emotion control is absent.

Measure the selected final WAV after processing; preserve quiet audio and natural
pauses, avoid forced duration/time stretching. Freeze reference/transcript/settings,
take and receipts. SRT/segment time is not verified word/phoneme alignment. Plan
mouth states only when needed and with sufficient timing evidence.

SFX prompt describes acoustic source/action/material, force/cadence, space/distance,
texture, decay and unwanted voice/music. Specify generation seconds/seed explicitly,
separately from usable duration/asset offset. One generated asset per event or
ambience, not a full-shot soundtrack. CUDA worker uses official pinned exports;
short generation can need longer audition material/cropping, never an unexplained 8s.

Choose transient onset by audition, place it against event start/peak/end plus
authored offset. Anticipation/offscreen/J/L sound bridges are explicit editorial
choices. Weight, material and space decide sound; ambience, foley, creature and
accents have hierarchy. Silence is an active choice. Tail and room tone carry
across cuts rather than restarting. Protect whisper intelligibility using measured
speech activity, then listen to actual final mix at normal playback.

Use production.py prepare only for the voice step; it unloads OmniVoice when done.
Use production.py sfx only for the next specifically instructed stage; the worker
exits and VRAM release is observed. A stuck lock/release failure is a stop condition,
not permission to force concurrent models or switch CPU. No full film during audition.

Review current reference/take/cue hashes and the actual final encoded mix separately.
Meters/no clipping/accepted whisper syntax do not prove emotion, natural decay,
spatial continuity, exact hit count or voice clarity. Record UNVERIFIED when unheard.
