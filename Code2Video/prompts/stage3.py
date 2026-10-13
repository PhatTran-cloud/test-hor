"""Legacy scaffold authoring. Fixed headers/lecture text are not V4 instructions."""
import os


def get_prompt3_code(regenerate_note, section, base_class):
    if getattr(section, "renderer", "manim") != "manim" or getattr(section, "shots", []):
        raise ValueError("The Manim code prompt only accepts a Manim section; author browser/mixed shots directly")
    is_3d = getattr(section, "scene_type", "2d") == "3d"
    scaffold = "Teaching3DScene" if is_3d else "TeachingScene"
    setup_method = "setup_3d_layout" if is_3d else "setup_layout"
    return f"""
You are an expert Manim animator using Manim Community Edition v0.19.0. 
Please generate a high-quality Manim class based on the following teaching script.
{regenerate_note}

1. Basic Requirements:
- Use the provided base class without modification. Scene type: {getattr(section, "scene_type", "2d")}.
- For scene_type "3d", inherit from Teaching3DScene and call setup_3d_layout(...); for "2d", inherit from TeachingScene and call setup_layout(...).
- Each lecture line must have a matching color with its corresponding animation elements.
- Apply ONLY color changes to lecture lines - no scaling, translation, or Transform animations.

2. Visual Anchor System (MANDATORY for 2D):
- Use 6x6 grid system (A1-F6) for precise positioning.
- Pay attention to the positioning of elements to avoid occlusions (e.g., labels and formulas).
- All labels must be positioned within 1 grid unit of their corresponding objects
- Grid layout (right side only):
```
lecture |  A1  A2  A3  A4  A5  A6
        |  B1  B2  B3  B4  B5  B6
        |  C1  C2  C3  C4  C5  C6
        |  D1  D2  D3  D4  D5  D6
        |  E1  E2  E3  E4  E5  E6
        |  F1  F2  F3  F4  F5  F6
```

3. POSITIONING METHODS:
- Point example: self.place_at_grid(obj, 'B2', scale_factor=0.8)
- Area example: self.place_in_area(obj, 'A1', 'C3', scale_factor=0.7)
- In 2D, NEVER use .to_edge(), .move_to(), or manual positioning.
- In 3D scenes, use self.place_3d(obj, (x, y, z), scale_factor=...) and set_camera_orientation or move_camera deliberately. Fixed text must remain in frame.

4. TEACHING CONTENT:
- Title: {section.title}
- Lecture Lines: {section.lecture_lines}
- Animation Description: {'; '.join(section.animations)}
- Visual thesis: {getattr(section, 'visual_thesis', '')}
- Visual metaphor: {getattr(section, 'visual_metaphor', '')}
- Foreground: {getattr(section, 'foreground', [])}
- Midground: {getattr(section, 'midground', [])}
- Background: {getattr(section, 'background', [])}
- Primary object: {getattr(section, 'primary_object', {})}
- Secondary objects: {getattr(section, 'secondary_objects', [])}
- Object relationships: {getattr(section, 'object_relationships', [])}
- Camera plan: {getattr(section, 'camera_plan', [])}
- Transition in: {getattr(section, 'transition_in', '')}
- Transition out: {getattr(section, 'transition_out', '')}
- Sound cues (the audio pipeline will realize these): {getattr(section, 'sfx_cues', [])}
- VFX event ledger: {getattr(section, 'vfx_events', [])}
- Scientific/data contract: {getattr(section, 'scientific_contract', {})}
- Editorial/shot purpose: {getattr(section, 'editorial', {})}

5. STRUCTURE FOR CODE:
Use the following comment format to indicate which block corresponds to which line:
```python
# === Animation for Lecture Line 1 ===
```

6. EXAMPLE STRUCTURE:
```python
from manim import *

{base_class}

class {section.id.title().replace('_', '')}Scene({scaffold}):
    def construct(self):
        self.{setup_method}({section.title!r}, {section.lecture_lines!r})
        
        # rest of animation code
        # === Animation for Lecture Line 1 ===
        ...

        # === Animation for Lecture Line 2 ===
        ...
```

7. MANDATORY CONSTRAINTS:
- Colors: Use light, distinguishable hexadecimal colors.
- Scaling: Maintain appropriate font sizes and object scales for readability.
- Consistency: Do not apply any animation to the lecture lines except for color changes; The lecture lines and title's size and position must remain unchanged.
- Assets: If provided, MUST use the elements in the Animation Description formatted as [Asset: XXX/XXX.png] (abstract path).
- 3D integrity: distinguish schematic illustration from a numerical simulation; do not claim orbital, geographic, or physical accuracy unless the code updates the stated equations/state.
- Simplicity: avoid external dependencies except for filenames in Animation Description. Use ThreeDScene primitives, Surface, ParametricFunction, ThreeDAxes, Sphere, and camera motion when appropriate.
- Representation: use primitives for deliberate scientific diagrams. Recognizable astronauts, animals, equipment, and landmarks require suitable authored assets or a faithful representation; a collection of generic primitives is not evidence of likeness.
- Creative direction: build a foreground/midground/background hierarchy. Give secondary objects purposeful behavior and causal relationships; do not merely duplicate the nouns in the narration.
- Scene continuity: begin from the transition_in state and end in a visual state that can motivate transition_out. Use camera movement to reveal relationships, not as decoration.
- Composition: reserve clear zones for title, labels, and narration overlays. Never allow labels, formulas, or objects to collide; fade or reposition supporting elements when focus changes.
- Scientific contracts: state units, coordinate frame, scale exaggerations, data source, and the authoritative state/equations where relevant. A smooth shader or plausible-looking animation does not certify a scientific claim.
- Motion: assign each object a purpose (active, reactive, static, optical, or camera-induced). Move the camera to reveal a spatial relationship; maintain coherent motion and attached geometry.
- Layering: create explicit background, midground, and foreground groups; use add_visual_layers(...) when helpful and keep the active layer visually dominant.
- Validation: design views that expose the important geometry and mechanism. Inspect geometry, domain fidelity, readability, motion, and current-output evidence independently; render success alone is not visual approval.
- VFX: realize only planned events with a causal source, staged onset/peak/decay, object attachment, depth/occlusion and residue. Do not add blanket glow, camera shake or particle spam. Inspect before/peak/after and a motion segment; disabling VFX must leave a coherent teaching scene.
- Output: no burned subtitles, debug HUD or archive codes. Labels are brief and attached to the concept they clarify. Keep narration joins below one second. Do not generate audio in scene code: the shared mixer owns SFX/narration.
"""


def get_regenerate_note(attempt, MAX_REGENERATE_TRIES):
    return f"""    
**IMPORTANT NOTE:** This is attempt {attempt}/{MAX_REGENERATE_TRIES} to generate working code.
The previous attempts failed to run correctly. Please:
1. Use only basic, well-tested Manim functions
2. Avoid complex animations that might cause errors
3. Use simple, reliable Manim patterns
"""
