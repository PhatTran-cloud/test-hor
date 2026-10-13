def get_prompt1_outline(knowledge_point, duration=None, reference_image_path=None):
    base_prompt = f""" 
    As an outstanding instructional design expert, design a logically clear, step-by-step, example-driven teaching outline.

    Knowledge Point: {knowledge_point}
    """

    # Add reference image guidance
    if reference_image_path:
        base_prompt += f"""

    ## Reference Image Available
    A reference image has been provided that relates to this knowledge point.

    ### How to Use the Reference Image for Outline Design:
    - Examine the key concepts, diagrams, and visual elements shown in the image
    - Identify which aspects of the knowledge point are emphasized or highlighted in the image
    - Design key section that can effectively utilize the visual concepts from the image
    - Prioritize sections that can benefit from the visual elements demonstrated in the image
    """

    base_prompt += f"""

    MUST output the teaching outline in JSON format as follows:
    {{
        "topic": "Topic Name",
        "target_audience": "Target Audience (e.g., high school students, university students, etc.)",
        "sections": [
            {{
                "id": "section_1",
                "title": "Section Title",
                "content": "Description of the section content",
                "example": "XXX",
                "scene_type": "2d",
                "renderer": "manim",
                "renderer_reason": "The mechanism needs mathematical geometry rather than media layout."
            }},
            ...
        ]
    }}

    Requirements:
    1. Choose the number of sections from the causal structure of the topic. Treat any duration estimate as a soft planning hint; final runtime follows the measured narration and should not be padded to a fixed length.
    2. The sections should be arranged in a progressive and logical order.
    3. Emphasize key concepts and critical knowledge points.
    4. When presenting mathematical concepts, prefer representations that integrate graphical elements to enhance comprehension.
    5. The outline should be suitable for animation and visual presentation.
    6. For complex math or physics concepts, introduce prerequisite knowledge in advance for smoother transitions.
    7. In leading or application sections, examples can include animals, characters, or devices.
    8. Set scene_type to "3d" only when depth, a 3D surface, sphere, orbit, camera movement, or spatial volume teaches the concept; otherwise use "2d".
    9. A 3D scene must state whether it is a schematic illustration or a numerical simulation; never imply simulation without equations/state updates.
    10. Give every section a visual thesis: an image-based claim that adds meaning beyond drawing the nouns in the narration.
    11. Prefer a causal visual progression where the next section is born from the previous section's action, reveal, or question.
    12. Choose by visual task, never by YouTube niche alone: Manim for proofs, equations, diagrams, mechanism and geometric 3D; Remotion for maps, media, comparisons, typography and editorial composition; Three.js via lowbudget3d+complete 3dviz-pro-max for materially convincing worlds, recognizable objects, spatial camera, lighting and atmosphere. Remotion 3D is an export/integration host, not a competing art-quality skill.
    13. A section may contain shots from different renderers. Explain renderer_reason and keep one shared visual system, source data, narrative clock and continuity handoff. Do not force a renderer into a task it cannot express clearly.
    14. Plan restrained causal VFX and selective SFX only where they clarify an action, environment, scale or emotional beat. Silence is valid. Never assign whooshes to every label or generic impacts to every fact.
    """

    return base_prompt
