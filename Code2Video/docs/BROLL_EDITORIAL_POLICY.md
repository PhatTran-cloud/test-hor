# B-roll principles adapted to Code2Video v3

Assessment of the user-provided **B-ROLL MASTERCLASS** (68 parts, received 2026-10-10).
The document is a useful editorial reference, not a renderer specification or
empirical proof of retention. This distilled policy is the active repo reference;
the long document does not need to be inserted into every code prompt.

## What it adds

For a faceless explainer, the primary diagram, map or 3D world is often the main
visual story. Supporting shots may be footage, archive, graphic, macro detail,
reaction, environmental context or a change of viewpoint within the same scene.
Do not force an A-roll/B-roll ratio or require stock footage.

Plan narration first, measure speech, then map **story beat → viewer need →
visual claim → sequence → reveal time → renderer → sound**. Sections change when
the causal idea changes; shots change when scale, evidence, viewpoint or revealed
information changes. A sentence boundary alone is not a reason to cut.

Every authored shot can carry `editorial`:

| Field | Decision |
|---|---|
| `function` | explanation, context, evidence, action, detail, emotion, reveal, transition |
| `information_gain` | What becomes clearer/new in this shot? |
| `viewer_question` | What does the viewer need/want to know next? |
| `payoff` | What resolves the action/question? |
| `shot_size` | wide, medium, close, detail, POV, insert; chosen for the idea |
| `timing_relation` | before, sync or after the relevant narration beat |
| `evidence_type` | evidence, reconstruction, illustration or metaphor |
| `sources` | Data/footage/document origin; mandatory for evidence |
| `continuity` | Screen direction, subject/shape, motion phase, color/light or sound carried across the cut |

Use action → detail → result or setup → build → payoff where appropriate.
Wide → medium → close → detail is coverage guidance, not a compulsory recipe.
Use callbacks and visual motifs only when their meaning progresses. Hold a
diagram during a difficult explanation; complexity in the narration usually
calls for less competing visual detail, motion and sound.

## Restrictions and review

- No arbitrary cut every 3 seconds, numerical B-roll density quota, or guaranteed retention claim.
- No sound on every cut/label. Prefer source-matched foley/ambience and rare accents; silence is a choice.
- Do not let an emotional metaphor distort a scientific causal claim.
- Generated imagery, reconstructions and unrelated stock are not historical/scientific evidence.
- Verify location/date/identity/projection; match palette, direction and scale across renderer handoffs.
- A visual hold differs from dead narration gaps. Preserve the project's short scene joins.
- J/L cuts need a global audio timeline. Current section mixer supports sound across
  shots inside one section, but does not implement cross-section J/L-cut overlap.

Review without narration for visual causality, then with narration for clarity,
timing and cognitive load. Apply the removal test: if deleting a shot changes
no understanding, emotion or progression, omit it. Review VFX disabled and SFX
muted as well; decoration must not carry a missing explanation.

Example for El Niño: ocean-wide context → wind weakens → close cross-section of
the thermocline response → map of region-specific consequences. Manim can own
the mechanism, Remotion the map/data evidence, and lowbudget3d a justified
spatial shot. The sequence teaches cause before consequence rather than cycling
through generic ocean clips.
