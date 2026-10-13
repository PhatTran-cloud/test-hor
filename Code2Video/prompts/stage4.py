# MLLM feedback


def get_prompt4_layout_feedback(section, position_table):
    if getattr(section, "scene_type", "2d") == "3d":
        return f"""
Review this Manim 3D educational video for visible spatial layout issues.
Title: {section.title}
Lecture lines: {section.lecture_lines}
Animation intent: {section.animations}
Do not apply the 2D anchor grid to this scene. Inspect the actual projected view.
Check: occlusion/clipping, label-object association, contrast, depth clarity,
fixed-in-frame text obstructed by geometry, and important views during camera motion.
Also check the foreground/midground/background hierarchy, whether secondary objects have visible causal behavior,
whether the camera reveals the intended relationship, and whether the transition state is legible.
Suggest world-coordinate, object-scale, camera-angle, or fixed-label corrections.
Keep title and lecture text sizes/positions fixed. No new unrelated objects.
A plausible image does not prove scientific accuracy; do not certify physics/data.
Output JSON only, with up to three actionable visible layout issues:
{{"layout": {{"has_issues": false, "improvements": [
  {{"problem": "Visible issue", "solution": "Specific code correction",
    "line_number": 1, "object_affected": "object_name"}}
]}}}}
Use an empty improvements array when there is no visible layout issue.
"""
    return f"""
1. ANALYSIS REQUIREMENTS:
- Analyze this Manim educational video ONLY for layout and spatial positioning issues.
- Use the provided reference image for precise spatial analysis.
- Focus on eliminating overlaps, obstructions, and optimizing grid space utilization.
- Also inspect visual hierarchy, metaphor clarity, object behavior, camera intent, and continuity into/out of the scene.

2. Content Context:
- Title: {section.title}
- Lecture Lines: {'; '.join(section.lecture_lines)}
- Current Grid Occupancy: {position_table}

3. Visual Anchor System (6*6 grid, right side only):
```
lecture |  A1  A2  A3  A4  A5  A6
        |  B1  B2  B3  B4  B5  B6
        |  C1  C2  C3  C4  C5  C6
        |  D1  D2  D3  D4  D5  D6
        |  E1  E2  E3  E4  E5  E6
        |  F1  F2  F3  F4  F5  F6
```
- Point positioning (point, one-word label): self.place_at_grid(obj, 'B2', scale_factor=0.8)
- Area positioning (over-two-words label, fomula, group): self.place_in_area(obj, 'A1', 'C3', scale_factor=0.7)

4. LAYOUT ASSESSMENT (Check ALL):
- Obstruction: Animations blocking left-side lecture notes [ATTENTION]
- Overlap: Animation elements (formulas, labels, shapes) overlapping
- Off-screen: Elements cut off or outside visible area [ESPECIALLY for LONG LABEL]
- Grid violations: Poor grid space utilization
- Check if there are any elements that should fade out but do not

5. MANDATORY CONSTRAINTS:
- Color: Provide hexadecimal color codes for unclear colors.
- Font/Scale: Adjust font sizes and asset scales for grid positions.
- Consistency: Do not apply any animation to the lecture lines except for color changes; The lecture lines and title's size and position must remain unchanged.
- Asset: Only adjust Existing PNG assets' size and position.
- Proximity: Ensure labels stay within 1 grid unit of their objects.

6. IMPORTANT: Output MUST follow this exact JSON structure:
{{
    "layout": {{
        "has_issues": true,
        "improvements": [
            {{
                "problem": "Specific issue description (concise)",
                "solution": "Line X: self.place_at_grid() or self.place_in_area()",
                "line_number": X,
                "object_affected": "obj_name"
            }},
            ...
        ]
    }}
}}

7. SOLUTION REQUIREMENTS:
- Provide specific grid coordinates in solutions
- List up to 3 layout problems that most affect the visual experience!
- Do not give the video timestamp
- Give concise problem descriptions but detailed, actionable solutions
- Subsequent solution positions should not overlap with previous solution positions
"""


def get_feedback_list_prefix(feedback_improvements):
    """
    Please specifically focus on:
    - Making sure animations correspond correctly to lecture content
    - Improving animation clarity and readability
    - Fixing any positioning or alignment issues
    - Ensuring proper visual hierarchy and focus
    """
    # -----------------------------------------------------------------------------
    return f"""       
MLLM FEEDBACK IMPROVEMENTS: Based on video analysis, please address these issues:
{chr(10).join([f"- {improvement}" for improvement in feedback_improvements])}
"""


def get_feedback_improve_code(feedback, code):
    return f"""
You are a Manim v0.19.0 educational animation expert.

MUST KEEP (MANDATORY):
- Based on the following feedback, improve the current Manim code.
- Use light colors in the animations or labels!
- Do not apply any animation to the lecture lines except for color changes; their size and position must remain unchanged.
- Output only the updated full Python code. No explanation.

Feedback:
{feedback}

---

Current Code:
```python
{code}
```
"""
