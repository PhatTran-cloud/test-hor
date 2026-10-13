"""Deterministic state helpers shared conceptually with the browser runtime.

Manim sources may read CODE2VIDEO_SHOT_CONTRACT. No physics claim is implied by
interpolation; numerical simulation still needs its own equations/state proof.
"""
import json
import os
from pathlib import Path


def load_contract():
    return json.loads(Path(os.environ["CODE2VIDEO_SHOT_CONTRACT"]).read_text(encoding="utf-8"))


def absolute_frame(contract, local_frame):
    return contract["absolute_start_frame"] + local_frame


def film_frame(contract, local_frame):
    return contract["film_start_frame"] + local_frame


def progress(frame, start, end):
    return max(0., min(1., (frame - start) / max(1, end - start)))


def state_at(contract, object_id, frame):
    obj = next(o for o in contract["objects"] if o["id"] == object_id)
    state = dict(obj["initial_state"])
    for track in sorted(contract.get("state_tracks", []), key=lambda t: t["start_frame"]):
        if track["object_id"] != object_id or frame < track["start_frame"]:
            continue
        p = progress(frame, track["start_frame"], track["end_frame"])
        value = track["to"]
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            value = track["from"] + (value - track["from"]) * p
        elif p < 1:
            value = track["from"]
        state[track["property"]] = value
    return state


def envelope(event, frame):
    if frame < event["start_frame"] or frame >= event["end_frame"]:
        return 0.
    if frame <= event["peak_frame"]:
        return progress(frame, event["start_frame"], event["peak_frame"])
    return 1 - progress(frame, event["peak_frame"], event["end_frame"])


def record_execution(contract, frame, objects, pattern_kind, observed=None):
    """Record actual Manim mobject bounds at an authored sample frame.

    Call after evaluating objects at that absolute frame. Projected 3D objects
    require renderer-specific projection rather than these 2D scene coordinates.
    """
    from manim import config
    bounds = {}
    for oid, obj in objects.items():
        left, right = obj.get_left()[0], obj.get_right()[0]
        bottom, top = obj.get_bottom()[1], obj.get_top()[1]
        # A horizontal/vertical stroked path has zero geometric height/width,
        # but a nonzero rendered footprint. Include its actual stroke padding.
        stroke = float(obj.get_stroke_width()) if hasattr(obj, "get_stroke_width") else 0.
        padding = stroke / 2
        bounds[oid] = [(left+config.frame_width/2)*1920/config.frame_width-padding,
                      (config.frame_height/2-top)*1080/config.frame_height-padding,
                      (right-left)*1920/config.frame_width+stroke,
                      (top-bottom)*1080/config.frame_height+stroke]
    channels = {'camera', 'object_states', 'visibility', 'event_phases'}
    if observed is not None and (not isinstance(observed, dict) or not set(observed) <= channels | {'cast_states'}):
        raise ValueError('Observations may only contain camera/object/visibility/event/cast channels')
    if contract.get('resolved_direction',{}).get('contract_revision') == 1 and (observed is None or not channels <= set(observed)):
        raise ValueError('Directed audit requires evaluated camera/object/visibility/event observations')
    if contract.get('resolved_direction',{}).get('character_cast',{}).get('entries') and not (observed or {}).get('cast_states'):
        raise ValueError('Character audit requires evaluated cast state/gaze/crowd population')
    print("V4_EXECUTION_SAMPLE " + json.dumps({"shot": contract["shot"]["id"], "frame": frame,
        "contract_sha256": contract["contract_sha256"], "object_ids": list(objects),
        "pattern_kind": pattern_kind, "bounds": bounds, **(observed or {})}))
