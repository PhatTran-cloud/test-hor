# Conditional visual reference: Kage

User instruction, 10 October 2026: use [MengTo/kage](https://github.com/MengTo/kage)
as a visual reference for image-rich storytelling. Exclude it for formula-focused
mathematics with Manim occupying **80% or more of visual duration**. Measure frame
allocation, not shot count. Drafts use the brief estimate; authored plans recompute.

Primary sources inspected: [README](https://github.com/MengTo/kage/blob/main/README.md)
and [PROMPT](https://github.com/MengTo/kage/blob/main/PROMPT.md). Kage is a live
Three.js environment layered with generated scene plates and transparent foreground
art, with a continuous scroll-driven camera and section-specific fade/blur handoffs.

Design inference for our videos:

- Compose an environment with meaningful depth and recognizable crafted subjects.
- Use authored plates/cutouts and live 3D where each has a visual purpose.
- Keep continuity in world/camera/light through the next shot; adapt scroll motion
  to measured narration and an absolute frame clock, never browser scroll state.
- Let lighting separate focus: warm/cool relationships, restrained bloom, depth
  haze and occlusion when the actual subject calls for them.
- Give foreground/background a narrative function, restrained parallax and clean
  negative space. Avoid crowding labels or merely increasing particle counts.
- Develop an original subject-specific visual system; do not force Kyoto, night,
  Japanese typography, vermilion moons or horror styling onto every story.

The website's oversized headings, technical labels, chapter rail, navigation and
custom cursor are web UI. They do not override the user's no-subtitle/no-decorative-
HUD rule. Its five chapters and slow page interaction are not pacing/count quotas.
Kage supplements art research; it does not replace full lowbudget3d + 3dviz-pro-max.

Its README explicitly grants no reuse/redistribution license for original code or
artwork. This integration records a reference and design principles; it does not
copy its source/assets or vendor its Three.js r149 runtime.
