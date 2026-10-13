"""Deterministic sprite selection, root travel and contact correction at 60fps."""
import math


def validate_binding(asset, binding):
    track = binding["root_track"]
    if not track or track[0]["frame"] != binding["start_frame"] or track[-1]["frame"] != binding["end_frame"]:
        raise ValueError("Root track must cover the playback interval endpoints")
    previous = -1
    for key in track:
        f, p = key["frame"], key["position"]
        if isinstance(f, bool) or not isinstance(f, int) or f <= previous:
            raise ValueError("Root keys must be strictly ordered integer absolute frames")
        if len(p) != 2 or any(not isinstance(v, (int,float)) or not math.isfinite(v) for v in p):
            raise ValueError("Root position must be finite [x,y]")
        previous = f
    view = next(v for v in asset["views"] if v["id"] == binding["view_id"])
    required = set(asset["action"]["contact_requirements"])
    windows = binding["contact_windows"]
    provided = {w["socket"] for w in windows}
    if not required <= provided:
        raise ValueError("Required foot/hand contacts are missing")
    previous_end = -1
    for window in sorted(windows,key=lambda w:w["start_frame"]):
        if not binding["start_frame"] <= window["start_frame"] < window["end_frame"] <= binding["end_frame"]:
            raise ValueError("Contact interval lies outside sprite playback")
        # This root-correction adapter pins one controlling socket at a time.
        # Multiple simultaneous contacts require a rig/constraint solver, not a fake fix.
        if window["start_frame"] < previous_end and not binding.get("contact_solver", {}).get("implementation"):
            raise ValueError("Overlapping contacts require an authored rig/solver implementation")
        previous_end = window["end_frame"]
        if len(window["world_position"]) != 2 or any(not math.isfinite(x) for x in window["world_position"]):
            raise ValueError("Contact world_position must be finite")
        for pose in view["frames"]:
            if window["socket"] != "ground" and window["socket"] not in pose["sockets"]:
                raise ValueError("Contact socket missing in a registered pose")


def sprite_state(asset, binding, absolute_frame):
    """No incremental playback state. Positions/anchors are in scene pixels."""
    if binding.get("contact_solver", {}).get("implementation"):
        raise ValueError("Use the declared authored contact solver; this adapter only pins one controlling socket")
    if not math.isfinite(absolute_frame):
        raise ValueError("Frame must be finite")
    view = next(v for v in asset["views"] if v["id"] == binding["view_id"])
    poses = view["frames"]
    elapsed = max(0, absolute_frame-binding["start_frame"])
    total = sum(p["hold_frames"] for p in poses)
    t = elapsed % total if binding["loop"] else min(elapsed,total-1)
    pose = poses[-1]
    for candidate in poses:
        if t < candidate["hold_frames"]:
            pose = candidate
            break
        t -= candidate["hold_frames"]
    track = binding["root_track"]
    root = list(track[-1]["position"])
    if absolute_frame <= track[0]["frame"]:
        root = list(track[0]["position"])
    else:
        for a,b in zip(track,track[1:]):
            if absolute_frame <= b["frame"]:
                f = (absolute_frame-a["frame"])/(b["frame"]-a["frame"])
                root = [x+(y-x)*f for x,y in zip(a["position"],b["position"])]
                break
    scale = binding.get("scale",1)
    if not isinstance(scale,(int,float)) or not math.isfinite(scale) or scale <= 0:
        raise ValueError("Sprite scale must be positive")
    contact = None
    for window in binding["contact_windows"]:
        if window["start_frame"] <= absolute_frame < window["end_frame"]:
            socket = pose["ground_anchor"] if window["socket"] == "ground" else pose["sockets"][window["socket"]]
            root = [w-(s-a)*scale for w,s,a in zip(window["world_position"],socket,pose["root_anchor"])]
            contact = window["socket"]
            break
    return {"pose_id":pose["id"],"file":pose.get("file"),"root_position":root,
            "image_position":[x-a*scale for x,a in zip(root,pose["root_anchor"])],
            "scale":scale,"contact":contact,"view_id":view["id"],
            "visible":binding["start_frame"] <= absolute_frame < binding["end_frame"]}
