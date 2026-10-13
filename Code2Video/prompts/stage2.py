"""Legacy storyboard prompt (V1–V3). New production uses prompts/v4.py."""
import json


def get_prompt2_storyboard(outline, reference_image_path):

    base_prompt = f""" 
    You are a professional explainer director converting researched outlines into renderer-neutral Code2Video v3 storyboards.

    ## Task
    Convert the following teaching outline into a detailed step-by-step storyboard script:

    {outline}
    """

    # Add reference image guidance
    if reference_image_path:
        base_prompt += f"""

    ## Reference Image Available
    A reference image has been provided to assist with designing the animations for this concept.

    ### How to Use the Reference Image:
    - Examine the visual elements, diagrams, layouts, and representations shown in the image
    - Use the image to inspire and guide your animation design, especially for the KEY SECTIONS
    - Focus on recreating the visual concepts using Manim objects (shapes, text, mathematical expressions)
    - Pay attention to how information is organized spatially in the image
    - If the image shows mathematical diagrams, design animations that build similar visualizations step by step
    - Use the image to identify which sections should have more detailed/complex animations
    - DO NOT reference the image directly in animations - instead recreate the concepts with Manim code
    
    ### Priority:
    - Give extra attention to sections that can benefit most from the visual concepts shown in the reference image
    """

    base_prompt += """
    ## Storyboard Requirements
    
    ### Content Structure
    - Choose section, shot, and animation-step counts dynamically from the causal structure, explanatory complexity, and information gain. There is no fixed count or quota for ordinary or key sections, and no cap on how many sections may need detailed treatment.
    - Use as many meaningful animation steps as needed to make the reasoning clear. Simple ideas may need fewer steps; complex ideas may need more. Merge redundant steps and split overloaded steps; never add actions merely to fill a quota or omit a necessary causal step to fit one.
    - Choose lecture_lines independently from animation steps. A label may support several actions, and an action need not introduce a new label; do not force a one-to-one mapping.
    - Must keep each lecture line brief [NO MORE THAN 10 WORDS FOR ONE LINE].
    - Divide sections by causal ideas and shots by reveals, changes of scale, perspective or evidence. Do not mechanically split every sentence into a scene.
    - Animation steps express cause and effect rather than illustrating isolated nouns.
    - Add a natural English narration paragraph for each section, suitable for Kokoro voice am_michael. Narration explains the mechanism; lecture_lines remain short on-screen labels.
    - Every section MUST include a visual_thesis, visual_metaphor, foreground, midground, background, primary_object, secondary_objects, object_relationships, camera_plan, transition_in, transition_out, and sfx_cues.
    - Secondary objects are purposeful supporting agents, not decoration: each must have a visible behavior and a relationship to the primary object.
    - Background elements must carry information through restrained motion, texture, atmosphere, or scale cues. Do not fill the frame with unrelated detail.
    - The camera must have a job: reveal scale, follow a causal action, reframe attention, or hand off to the next section.
    - V3 sound design is adaptive: selective SFX, not continuous noise. Each cue needs trigger, purpose, role, relative_time, duration, gain_db, and a query or selected sound_id/local file. Default gain is -18 dB relative to narration RMS, ambience -24 dB; duck beneath speech and fade edges. Never invent Freesound IDs or asset paths; unresolved queries must be researched, listened to and frozen before rendering. Empty cues are valid.
    - Each significant VFX event needs id, cause, source, trigger, representation, start/peak/end seconds, interaction, residue, lighting_response and transition_handoff. Build cause -> emission/transport -> world interaction -> decay/residue. Optical effects need a source; particles, shake, glow and fog are not generic decoration.
    - Choose renderer per shot: manim for mathematical/geometric reasoning, remotion for media/maps/typography, threejs for lowbudget3d scene fidelity. Explain renderer_reason. Remotion is the Three.js export host, not a substitute for the complete lowbudget3d+3dviz-pro-max workflow.
    - scientific_contract records mode (schematic or numerical_simulation), sources, coordinate frame, units, scale exaggerations; simulations additionally need equations and authoritative state. Geographic shots need real data, projection, extent and label policy.
    - Each section/shot has an editorial object: function, information_gain, viewer_question, payoff, shot_size, timing_relation (before/sync/after narration), evidence_type (evidence/reconstruction/illustration/metaphor), sources and continuity. Edit by story beats, not words. Use action -> detail -> result when it clarifies causality; wide/medium/close/detail is a coverage option, not a mandatory four-cut recipe. Hold a readable diagram while a difficult idea is explained.
    - A sourced archive/map/chart can be evidence; generated/reconstructed visuals must not masquerade as evidence. Match date, geography, object identity and scale. Require a removal test: if deleting the shot changes no understanding, emotion or progression, omit it.
    - Keep lecture lines stable; use color changes only when emphasizing a label relevant to the current action, without requiring one label per animation step.

    ### Visual Design
    - Colors: Background fixed at #000000 or #05070D, use light color for contrast.
    - IMPORTANT: Provide hexadecimal codes for colors.
    - Element Labeling: Assign clear colors and labels near all elements (formulas, etc.).

    ### Animation Effects
    - Basic Animations: Appearance, movement, color changes, fade in/out, scaling.
    - Emphasis Effects: Flashing, color changes, bolding to highlight key knowledge points.

    ### Constraints
    - Manim 2D uses its anchor scaffold; media/map layouts use explicit safe areas and measured text bounds. 3D uses explicit world coordinates and a deliberate camera angle.
    - 3D is allowed for surfaces, spheres, orbits, spatial volumes, and camera-based explanations. Keep title and lecture text fixed in frame.
    - Label every 3D object whose meaning matters. State "schematic" when geometry is illustrative rather than numerically simulated.
    - Avoid coordinate axes unless absolutely necessary.
    - Focus animations on visualizing concepts that are difficult to grasp from lecture lines alone.
    - Ensure that all animations are easy to understand.
    - Do not require external elements by default. Use only external assets that have been explicitly selected, saved locally, and recorded with source metadata.

    MUST output the storyboard design in JSON format:
    {
        "sections": [
            {
                "id": "section_1",
                "title": "Sec 1: Section Title",
                "scene_type": "2d",
                "renderer": "manim",
                "renderer_reason": "Geometry reveals the mechanism.",
                "scientific_contract": {"mode": "schematic", "sources": [], "scale_exaggerations": []},
                "vfx_events": [],
                "editorial": {"function": "explanation", "information_gain": "Expose the causal mechanism", "viewer_question": "What drives the change?", "payoff": "The visible result", "shot_size": "wide", "timing_relation": "sync", "evidence_type": "illustration", "sources": [], "continuity": "Transfer the moving subject"},
                "narration": "Complete English narration for this section.",
                "lecture_lines": ["Lecture line 1", "Lecture line 2", ...],
                "animations": [
                    "Animation step 1: ...",
                    "Animation step 2: ...",
                    ...
                ],
                "visual_thesis": "A visual claim that clarifies the idea.",
                "visual_metaphor": "The metaphor or visual system behind the scene.",
                "foreground": ["Element close to camera and its behavior"],
                "midground": ["Primary object and action"],
                "background": ["Informative atmosphere or context"],
                "primary_object": {"name": "Main object", "role": "What it teaches"},
                "secondary_objects": [{"name": "Supporting object", "role": "Why it exists", "behavior": "What it does"}],
                "object_relationships": ["Supporting object changes when primary object moves"],
                "camera_plan": ["Start wide", "Follow the reveal"],
                "transition_in": "The action inherited from the previous section.",
                "transition_out": "The action or question handed to the next section.",
                "sfx_cues": []
            },
            ...
        ]
    }
    Optional authored shots belong inside each section. Each shot has id, renderer, renderer_reason,
    scene_type, duration_frames, visual action, camera, transition, vfx_events and scientific contract.
    Browser renderers need authored render_spec (project_dir, entry_point, composition_id,
    time_model=absolute_frame, props); never fabricate executable paths in a conceptual storyboard.
    Three.js additionally needs three_contract with workflow=lowbudget3d+3dviz-pro-max,
    representation, coordinate_frame, units, scale_exaggerations and asset_provenance.
    Final executable shot durations must come from measured Kokoro speech, total exactly equal to
    section frames. Every output is 1920x1080 at 60fps. No burned subtitles, no archive/debug HUD.
    No long pauses or black padding. The assistant authors browser sources and validates assets
    before the local renderer runs; do not send them into the Manim Python generation/repair loop.
    """

    return base_prompt


def get_prompt_download_assets(storyboard_data):
    return f"""
Analyze this educational video storyboard and identify at most 4 different ESSENTIAL visual elements that MUST be represented with downloadable icons/images (not manually drawn shapes).

Content:
{storyboard_data}

Selection Criteria:
1. Only choose elements that appear in **introduction** or **application** sections, and that are:
   - Real-world, recognizable physical objects
   - Visually distinctive enough that a generic shape would not be sufficient
   - Concrete, not abstract concepts
2. Prioritize: specific animals, characters, vehicles, tools, devices, landmarks, everyday objects
3. IGNORE and NEVER include:
   - Abstract concepts (e.g., justice, communication)
   - Symbols or icons for ideas (e.g., letters, formulas, diagrams, trees in data structure)
   - Geometric shapes, arrows, or math-related visuals
   - Any object composed entirely of basic shapes without unique visual identity

Output format:
- Output ONLY the object keywords, each keyword must be one word, one per line, all lowercase, no numbering, no extra text.
"""


def get_prompt_place_assets(asset_mapping, animations_structure):
    return f"""
You need to enhance only the animations by incorporating downloaded assets where appropriate.

Asset list:
{asset_mapping}

Current Animations Data:
{animations_structure}

Instructions:
- For each animation, determine if any downloaded assets should be incorporated.
- Only choose the most relevant asset for the animation step that needs.
- Insert the **abstract path** of asset in the form: [Asset: XXX].
- CAN ONLY use the assets in **THE FIRST and THE LAST** sections.
- Keep the same structure: return an array with section_index, section_id, and enhanced animations.
- Only modify the animation descriptions to include asset references.
- Do not change section_index or section_id.

Return only the enhanced animations data as valid JSON array:
"""
