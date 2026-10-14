"""Current-session authoring prompts, separate from the original API pipeline."""
import json
from pathlib import Path

STEPWISE = """MANDATORY USER MODE: Execute only the current human-authorized step.
Before working, state the task, exact applicable repo rules and skills. Read and
apply their full relevant instructions/references. After working, report actual
actions, concrete rule/skill application, linked artifacts, unmet/unverified
requirements and the proposed next step, then STOP and end the turn.
Continue only after the human's next instruction. Never background later stages,
self-author easier acceptance, auto-PASS, or chain authoring/preview/full render.
Reading a skill name/hash is not applying it. Preserve the user's actual visual
requirements; present new art/renderer decisions as proposals before implementing.
Follow the TOP of START_HERE.md; earlier autonomous end-to-end text is superseded.
CURRENT-STEP DECLARATION and PROPOSED-NEXT-STEP DECLARATION each specify:
task/scope, exact rule/source, skill/reference -> concrete purpose, intended
command or manual action, input, reviewable output and stopping point. If no
skill/command applies, say not applicable with a reason; never invent one.
Label the next step PROPOSED, NOT RUN. It is not authorization. Announce it
again before acting on the next human instruction. Silence, PASS and assistant
promises do not authorize continuation.
Name each next-step skill and its concrete purpose directly in the user-facing
proposal; a linked file or "relevant skills" alone is insufficient.
"""

SPRITE_25D_GUIDANCE = """V4.1 authoring guidance, conditional on 2.5D sprite work:
Read docs/V4_AUTHORING_GUIDE.md's behavior-led 2.5D sprite section.
Research character intention and action mechanics before pose prompts: reference
observations, support/weight transfer, gaze, contacts, key poses and final state.
Flow draws the 2.5D assets/poses; code registers and plays them. Image polish,
rigid cutout transforms and parallax do not prove character acting. No mandatory
skeletal rig or fixed pose count. Keep asset identity, root/ground/grip anchors,
frame order/holds, one-shot/loop intent and prop ownership explicit. Derive sprite
state from absolute time and measured beat allocations; inspect encoded motion,
contacts, flicker, boundaries and non-sequential seeks at 1920x1080, 60fps output.
Use script-to-visual-director for behavior/story research, cinematic-motion-director
for mechanics and storyboard-motion-executor for asset/timing/contact bindings.
Research, artwork and motion remain separately authorized steps. This guidance
does not change schema_version=4, the V4 runner or the complete 3D skill route.
"""


def _kage_guidance(profile):
    kind = profile.get("kind", "mixed")
    if kind == "formula_math" and profile.get("planned_manim_share", 1) >= .8:
        return "Kage reference is excluded: formula mathematics with >=80% planned Manim. Prioritize mathematical clarity."
    if kind == "storytelling_rich" or profile.get("rich_storytelling"):
        return (Path(__file__).resolve().parents[1] / "docs" / "KAGE_VISUAL_REFERENCE.md").read_text(encoding="utf-8")
    return "Do not assume the Kage visual reference applies; use the brief's visual needs."


def _reference_guidance(plan):
    if plan.get('horror',{}).get('visual_reference',{}).get('primary')=='oversimplified':
        return (Path(__file__).resolve().parents[1]/'docs'/'OVERSIMPLIFIED_ILLUSTRATION.md').read_text(encoding='utf-8')
    return _kage_guidance(plan.get('content_profile',{}))


def get_v4_direction_prompt(brief, research, script):
    guide = (Path(__file__).resolve().parents[1] / "docs" / "V4_AUTHORING_GUIDE.md").read_text(encoding="utf-8")
    guide += "\n" + (Path(__file__).resolve().parents[1] / "docs" / "HORROR_CONTRACT.md").read_text(encoding="utf-8")
    return f"""Act as the visual director in the current assistant conversation.
{STEPWISE}
Read the complete relevant skill resources, not just a renderer's API summary.
Research: {research}
Brief: {brief}
Complete script: {script}
{_reference_guidance(brief if isinstance(brief,dict) else {})}
{guide}
When the authorized step is direction/storyboard, return a schema_version=4,
phase=draft plan with semantic beats and shot cards. A reading/research-only step
does not authorize writing that plan. Do not invent measured timing or quality
PASS. OmniVoice cast preparation belongs to its separately instructed narration step,
before final shot allocation; do not start it as a hidden follow-up.
"""


def get_v4_execution_prompt(timed_plan, shot_id):
    from v4_contract import visual_reference_policy
    import copy
    section = next((s for s in timed_plan["sections"] if any(sh["id"] == shot_id for sh in s["shots"])), None)
    if section is None:
        raise ValueError("Unknown shot ID")
    shot = next(sh for sh in section["shots"] if sh["id"] == shot_id)
    # Keep the selected section's state/anchors and immediate boundaries. Do not
    # flood each implementation turn with every unrelated shot/object in a film.
    focused = copy.deepcopy({k: v for k, v in timed_plan.items() if k != "sections"})
    focused["sections"] = [{**section, "shots": [shot]}]
    focused["sections"][0]["beats"] = [b for b in section["beats"] if b["id"] in shot["beat_ids"]]
    focused["sections"][0]["objects"] = [o for o in section["objects"] if o["id"] in shot["object_ids"]]
    film_shots = [s for sec in timed_plan["sections"] for s in sec["shots"]]
    index = film_shots.index(shot)
    focused["adjacent_handoffs"] = [{"id": s["id"], "scene_id": s.get('scene_id'),
                                    "handoff": s["handoff"], "storyboard": s.get('storyboard')}
                                   for s in film_shots[max(0,index-1):index+2]]
    focused["visual_reference_policy"] = visual_reference_policy(timed_plan)
    policy = focused["visual_reference_policy"].get("kage", {})
    reference = (_reference_guidance(timed_plan) if focused['visual_reference_policy'].get('oversimplified',{}).get('enabled') else
                 (Path(__file__).resolve().parents[1] / "docs" / "KAGE_VISUAL_REFERENCE.md").read_text(encoding="utf-8")
                 if policy.get("enabled") else "Kage visual reference is not active for this plan.")
    return f"""Execution context for shot {shot_id}; implement only what the current human-authorized step permits:
{STEPWISE}
{json.dumps(focused, ensure_ascii=False, indent=2)}
{reference}
{SPRITE_25D_GUIDANCE}
{(Path(__file__).resolve().parents[1] / "docs" / "HORROR_CONTRACT.md").read_text(encoding="utf-8")}
Use productionContract in Remotion/Three.js or CODE2VIDEO_SHOT_CONTRACT in Manim.
Derive state from the section-absolute frame. Keep object identity through shot changes.
Draw the actual reading structure of the chosen pattern; a pattern name is not implementation.
Implement cause/action/reaction/aftermath and the handoff inside allocated frames.
Use researched artwork, supporting objects with a purpose, and frame-measured label bounds.
Do not add default headers, subtitles, archive codes, looping sine motion or generic overlays.
Write source bindings and review frame requests; leave artistic/audio gates UNVERIFIED until inspected.
At requested samples emit actual runtime observations with the current contract hash,
object bounds and pattern kind (useV4LayoutAudit / record_execution or an equivalent).
Record object craft and the researched claim boundary in the existing production_packet.
"""
