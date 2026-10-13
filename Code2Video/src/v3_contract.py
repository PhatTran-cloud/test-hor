"""Renderer-neutral production contract. Legacy Manim plans remain valid."""
import copy
import math
import re

RENDERERS = {"manim", "remotion", "threejs"}


def _number(value, name, minimum=0):
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite number")
    value = float(value)
    if not math.isfinite(value) or value < minimum:
        raise ValueError(f"{name} must be finite and >= {minimum}")
    return value


def validate_cues(cues):
    for cue in cues:
        for name in ("trigger", "purpose"):
            if not str(cue.get(name, "")).strip():
                raise ValueError(f"SFX needs {name}; isolated keywords are not sound direction")
        _number(cue.get("relative_time", 0), "SFX relative_time")
        _number(cue.get("duration", .3), "SFX duration", .01)
        gain = float(cue.get("gain_db", -18))
        if not math.isfinite(gain) or not -60 <= gain <= 0:
            raise ValueError("SFX gain_db must be between -60 and 0")
        if cue.get("role", "event") not in {"event", "foley", "ambience", "transition"}:
            raise ValueError("Unknown SFX role")
        if not -1 <= float(cue.get("pan", 0)) <= 1:
            raise ValueError("SFX pan must be between -1 and 1")
        for key in ("asset_offset", "fade_in", "fade_out"):
            _number(cue.get(key, 0), f"SFX {key}")


def validate_vfx(events):
    for event in events:
        for key in ("id", "cause", "source", "trigger", "representation", "interaction", "residue", "lighting_response", "transition_handoff"):
            if not event.get(key):
                raise ValueError(f"VFX event needs {key}")
        start = _number(event.get("start", 0), "VFX start")
        peak = _number(event.get("peak", start), "VFX peak")
        end = _number(event.get("end", peak), "VFX end")
        if not start <= peak <= end:
            raise ValueError("VFX phases must satisfy start <= peak <= end")


def validate_editorial(editorial):
    if not editorial:
        return
    if editorial.get("timing_relation", "sync") not in {"before", "sync", "after"}:
        raise ValueError("Editorial timing_relation must be before, sync, or after")
    evidence_type = editorial.get("evidence_type", "illustration")
    if evidence_type not in {"evidence", "reconstruction", "illustration", "metaphor"}:
        raise ValueError("Unknown editorial evidence_type")
    if evidence_type == "evidence" and not editorial.get("sources"):
        raise ValueError("Evidence shots need verifiable sources; generated imagery is not evidence")


def validate_render_unit(unit):
    renderer = unit.get("renderer", "manim")
    if renderer not in RENDERERS:
        raise ValueError(f"Unknown renderer: {renderer}")
    if unit.get("scene_type", "2d") not in {"2d", "3d"}:
        raise ValueError("scene_type must be 2d or 3d")
    if renderer == "threejs":
        if unit.get("scene_type") != "3d":
            raise ValueError("threejs requires scene_type=3d")
        contract = unit.get("three_contract", {})
        for key in ("representation", "coordinate_frame", "units", "scale_exaggerations", "asset_provenance"):
            if key not in contract:
                raise ValueError(f"lowbudget3d scene needs three_contract.{key}")
        if contract.get("workflow") != "lowbudget3d+3dviz-pro-max":
            raise ValueError("Three.js authoring must preserve the complete lowbudget3d+3dviz-pro-max workflow")
    if renderer != "manim":
        spec = unit.get("render_spec", {})
        for key in ("project_dir", "entry_point", "composition_id"):
            if not spec.get(key):
                raise ValueError(f"{renderer} needs render_spec.{key}")
        if spec.get("time_model") != "absolute_frame":
            raise ValueError("Browser renderers require absolute_frame time, never playback-dependent simulation")
    validate_vfx(unit.get("vfx_events", []))
    validate_editorial(unit.get("editorial", {}))
    if unit.get("duration_frames"):
        duration = float(unit["duration_frames"]) / 60
        if any(float(event.get("end", 0)) > duration for event in unit.get("vfx_events", [])):
            raise ValueError("VFX event exceeds shot duration")
    scientific = unit.get("scientific_contract", {})
    if scientific.get("mode") == "numerical_simulation" and not all(scientific.get(k) for k in ("equations", "state", "sources")):
        raise ValueError("A numerical simulation needs equations, authoritative state, and sources")
    return renderer


def normalize_plan(plan):
    if plan.get("schema_version") == 4:
        from v4_contract import normalize_v4
        return normalize_v4(plan)
    result = copy.deepcopy(plan)
    version = result.get("schema_version", 2)
    if version not in (1, 2, 3):
        raise ValueError("schema_version must be 1, 2, 3, or 4")
    for key, expected in (("width", 1920), ("height", 1080), ("fps", 60)):
        if result.get(key, expected) != expected:
            raise ValueError("All output, previews, and smoke tests must be 1920x1080 at 60 fps")
        result[key] = expected
    result.setdefault("sound_design", "adaptive" if version == 3 else "voice_only")
    if result["sound_design"] not in {"voice_only", "adaptive", "sfx"}:
        raise ValueError("sound_design must be voice_only, adaptive, or sfx")
    if version == 3:
        result.setdefault("pacing", "narration")
        result.setdefault("preserve_scene_duration", True)
    sections = result.get("sections", [])
    ids = [s.get("id", "") for s in sections]
    if not sections or len(ids) != len(set(ids)) or any(not re.fullmatch(r"section_[1-9][0-9]*", sid) for sid in ids):
        raise ValueError("Plan needs unique section_1, section_2, ... IDs")
    for section in sections:
        section.setdefault("renderer", "manim")
        shots = section.get("shots", [])
        validate_cues(section.get("sfx_cues", []))
        validate_vfx(section.get("vfx_events", []))
        validate_editorial(section.get("editorial", {}))
        scientific = section.get("scientific_contract", {})
        if scientific.get("mode") == "numerical_simulation" and not all(scientific.get(k) for k in ("equations", "state", "sources")):
            raise ValueError("A numerical simulation needs equations, authoritative state, and sources")
        if shots:
            shot_ids = [shot.get("id", "") for shot in shots]
            if len(shot_ids) != len(set(shot_ids)) or any(not re.fullmatch(r"[A-Za-z0-9_-]+", sid) for sid in shot_ids):
                raise ValueError("Shot IDs must be unique safe names within each section")
            for shot in shots:
                shot.setdefault("renderer", section["renderer"])
                validate_render_unit(shot)
                if shot["renderer"] == "manim" and not shot.get("source"):
                    raise ValueError("Manim shots need source")
                if "duration_frames" not in shot:
                    raise ValueError("Authored shots need duration_frames from measured narration")
                frames = _number(shot["duration_frames"], "duration_frames", 1)
                if frames != int(frames):
                    raise ValueError("duration_frames must be an integer")
                shot["duration_frames"] = int(frames)
        else:
            validate_render_unit(section)
    return result
