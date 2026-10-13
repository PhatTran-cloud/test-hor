"""Semantic production contract. Drafts describe intent; authored plans bind it.

Validation proves consistency and traceability, never artistic quality. All frame
numbers are section-absolute, end-exclusive, on the common 60 fps clock.
"""
import copy
import hashlib
import json
import math
import re
from pathlib import Path

from v3_contract import validate_cues, validate_editorial, validate_render_unit

PATTERNS = {
    "timeline": ("milestones",), "comparison": ("variable", "fair_conditions"),
    "before_after": ("changed_property",), "cause_effect": ("cause", "result"),
    "flow": ("connections",), "cycle": ("connections", "feedback"),
    "network": ("connections",), "hub_spoke": ("hub", "connections"),
    "scale": ("reference", "scale_relation"), "map": ("projection", "data_sources", "legend"),
    "evidence": ("sources", "inference"), "custom": ("reading_logic",),
}
MODES = {"active", "reactive", "passive", "optical", "camera_induced"}


def sha256(path):
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":")).encode()).hexdigest()


def require(value, names, context):
    for name in names:
        if name not in value or value[name] is None or value[name] == "" or value[name] == [] or value[name] == {}:
            raise ValueError(f"{context} needs {name}")


def frame(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer frame")
    return value


def unique(items, context):
    ids = [item.get("id", "") for item in items]
    if len(ids) != len(set(ids)) or any(not re.fullmatch(r"[A-Za-z0-9_-]+", sid) for sid in ids):
        raise ValueError(f"{context} needs unique safe IDs")
    return set(ids)


def refs(values, available, context):
    if not isinstance(values, list) or any(value not in available for value in values):
        raise ValueError(f"{context} contains an unknown reference")


def normalize_v4(plan):
    result = copy.deepcopy(plan)
    for key, expected in (("width", 1920), ("height", 1080), ("fps", 60)):
        if result.get(key, expected) != expected:
            raise ValueError("V4 always uses 1920x1080 at 60 fps")
        result[key] = expected
    require(result, ("topic", "visual_system", "content_profile", "sections"), "V4 plan")
    require(result["content_profile"], ("kind",), "content_profile")
    require(result["visual_system"], ("palette", "typography", "shape_language"), "visual_system")
    phase = result.setdefault("phase", "draft")
    if phase not in {"draft", "timed", "authored"}:
        raise ValueError("phase must be draft, timed, or authored")
    result.setdefault("sound_design", "adaptive")
    if result["sound_design"] not in {"voice_only", "adaptive", "sfx"}:
        raise ValueError("Unknown sound_design")
    result["pacing"] = "narration"
    result["preserve_scene_duration"] = True
    result.setdefault("tts_speed", 1.0)
    result.setdefault("workflow_revision", 2)
    if not math.isfinite(float(result["tts_speed"])) or result["tts_speed"] <= 0:
        raise ValueError("tts_speed must be positive")
    if result.get("music"):
        if result.get("music_requested") is not True:
            raise ValueError("BGM requires an explicit music_requested brief")
        music = result["music"]
        require(music, ("file", "purpose", "selection_reason", "listening_review"), "BGM")
        review = music["listening_review"]
        require(review, ("status", "reviewer", "notes", "asset_sha256"), "BGM listening review")
        if review["status"] != "PASS" or music.get("source") == "procedural":
            raise ValueError("Select/listen to the real music asset before mixing")
        validate_cues([{**music, "trigger": "film start", "role": "ambience", "relative_time": 0}])
    if result.get("subtitles") or result.get("decorative_hud"):
        raise ValueError("Burned subtitles and decorative HUD are disabled")
    sections = result["sections"]
    section_ids = unique(sections, "sections")
    if any(not re.fullmatch(r"section_[1-9][0-9]*", sid) for sid in section_ids):
        raise ValueError("Section IDs must be section_1, section_2, ...")
    all_beats, all_shots, all_events = set(), set(), set()
    film_cursor, carried_world = 0, {}
    for section in sections:
        require(section, ("title", "visual_thesis", "beats", "objects", "shots"), section["id"])
        section.setdefault("animations", [])  # legacy dataclass only, not a v4 planning quota
        section.setdefault("lecture_lines", [])
        section.setdefault("sfx_cues", [])
        if result["sound_design"] == "voice_only" and section["sfx_cues"]:
            raise ValueError("voice_only contains SFX; decide sound policy before rendering")
        fixture = bool(result.get("technical_fixture"))
        if not fixture:
            require(section, ("narration", "narration_segments"), section["id"])
            text = " ".join(s["text"] for s in section["narration_segments"])
            if " ".join(text.split()) != " ".join(section["narration"].split()):
                raise ValueError("Narration segments must cover the complete script in order")
            unique(section["narration_segments"], "narration segments")
        for value in (section.get("lead_seconds", .12), section.get("tail_seconds", .15)):
            if not math.isfinite(float(value)) or value < 0:
                raise ValueError("Narration padding must be finite and nonnegative")
        pauses = [s.get("pause_after", .12) for s in section.get("narration_segments", [])]
        if any(not math.isfinite(float(p)) or p < 0 for p in pauses):
            raise ValueError("Narration pauses must be finite and nonnegative")
        # Exterior trims retain at most .04/.06 s around a segmented utterance.
        join = section.get("lead_seconds", .12) + section.get("tail_seconds", .15) + (pauses[-1] if pauses else 0) + .1
        if (join >= 1 or any(p >= 1 for p in pauses)) and not section.get("intentional_silence"):
            raise ValueError("Long scene/segment silence needs an editorial reason")
        object_ids = unique(section["objects"], "objects")
        for obj in section["objects"]:
            require(obj, ("identity", "role", "craft"), obj["id"])
            if not isinstance(obj.get("initial_state"), dict):
                raise ValueError("Object initial_state must be a dictionary (empty is valid for static objects)")
            if obj["role"] not in {"hero", "support", "environment"}:
                raise ValueError("Object role must be hero, support, or environment")
            require(obj["craft"], ("silhouette", "construction", "material", "references", "fidelity_limits"), "object craft")
        beat_ids = unique(section["beats"], "beats")
        if all_beats & beat_ids:
            raise ValueError("Beat IDs must be unique across the film")
        all_beats |= beat_ids
        seen = set()
        for beat in section["beats"]:
            require(beat, ("purpose", "before", "after", "narration_anchor", "visual_evidence", "completion"), beat["id"])
            refs(beat.get("depends_on", []), seen, "Beat dependency (must precede reveal)")
            seen.add(beat["id"])
            anchor = beat["narration_anchor"]
            if not fixture:
                refs([anchor.get("segment_id")], {s["id"] for s in section["narration_segments"]}, "Narration anchor")
        if phase != "draft":
            require(section, ("speech",), "Timed section")
            speech = section["speech"]
            require(speech, ("file", "sha256", "frames", "anchors", "script_sha256"), "speech")
            frame(speech["frames"], "speech.frames")
            section["film_start_frame"] = film_cursor
            film_cursor += speech["frames"]
            if speech["frames"] < 1 or speech.get("fps") != 60 or speech.get("time_stretch") is not False:
                raise ValueError("Speech needs a measured 60 fps clock without time stretching")
            if speech["script_sha256"] != digest(section.get("narration", "")):
                raise ValueError("Script changed after speech measurement; prepare speech again")
            if not fixture and result.get("profile") != "horror-v4.1" and (speech.get("voice") != "am_michael" or speech.get("speed") != result["tts_speed"]):
                raise ValueError("Speech voice/speed differs from the v4 narration configuration")
            anchor_ids = unique(speech["anchors"], "speech anchors")
            if not fixture and anchor_ids != {s["id"] for s in section["narration_segments"]}:
                raise ValueError("Measured anchors must cover all narration segments")
            last_anchor_end = 0
            for anchor in speech["anchors"]:
                start, end = frame(anchor["start_frame"], "anchor start"), frame(anchor["end_frame"], "anchor end")
                if not start < end <= speech["frames"] or anchor.get("confidence") != "measured_segment":
                    raise ValueError("Anchor must be a measured recording interval inside speech")
                if start < last_anchor_end:
                    raise ValueError("Recording anchors must be ordered without overlap")
                last_anchor_end = end
                if not fixture and anchor.get("text") != next(s["text"] for s in section["narration_segments"] if s["id"] == anchor["id"]):
                    raise ValueError("Anchor text differs from the recorded script passage")
            for beat in section["beats"]:
                refs([beat["narration_anchor"].get("segment_id")], anchor_ids, "Measured beat anchor")
                if phase == "timed" and "start_frame" not in beat and "end_frame" not in beat:
                    continue
                start, end = frame(beat.get("start_frame"), "beat start"), frame(beat.get("end_frame"), "beat end")
                if not start < end <= speech["frames"]:
                    raise ValueError("Beat outside measured speech")
                anchor = next(a for a in speech["anchors"] if a["id"] == beat["narration_anchor"]["segment_id"])
                # Visuals may lead/lag recording; this must be an explicit editorial decision.
                if (start < anchor["start_frame"] or end > anchor["end_frame"]) and not beat.get("timing_reason"):
                    raise ValueError("Beat leading/lagging its anchor needs timing_reason")
            beat_lookup = {b["id"]: b for b in section["beats"]}
            for beat in section["beats"]:
                if "start_frame" in beat and any(beat_lookup[dep].get("end_frame", 0) > beat["start_frame"] for dep in beat.get("depends_on", [])):
                    raise ValueError("Dependent reveal starts before its prerequisite completes")
            tracks = section.get("state_tracks", []) if phase == "authored" else []
            unique(tracks, "state tracks")
            track_ends = {}
            track_values = {(o["id"], k): v for o in section["objects"] for k, v in o["initial_state"].items()}
            for obj in section["objects"]:
                if phase == "authored" and obj["id"] in carried_world and obj["initial_state"] != carried_world[obj["id"]]:
                    raise ValueError("A shared object must carry its previous section's final state; use a new ID for a different object")
            for track in sorted(tracks, key=lambda t: t.get("start_frame", 0)):
                require(track, ("object_id", "property", "from", "to", "cause"), "state track")
                refs([track["object_id"]], object_ids, "state track")
                start, end = frame(track["start_frame"], "state start"), frame(track["end_frame"], "state end")
                key = (track["object_id"], track["property"])
                if key not in track_values or track["from"] != track_values[key]:
                    raise ValueError("State track must continue the existing object property, not reset at a cut")
                for value in (track["from"], track["to"]):
                    if not isinstance(value, (int, float, str, bool)) or (isinstance(value, (int, float)) and not math.isfinite(value)):
                        raise ValueError("State track values must be finite numeric or discrete scalar values")
                if isinstance(track["to"], (int, float)) and not isinstance(track["to"], bool) and (not isinstance(track["from"], (int, float)) or isinstance(track["from"], bool)):
                    raise ValueError("Numeric interpolation needs numeric endpoints")
                if not start < end <= speech["frames"] or start < track_ends.get(key, 0):
                    raise ValueError("State track outside speech or conflicting property tracks")
                track_ends[key] = end
                track_values[key] = track["to"]
            carried_world.update({obj["id"]: {k: v for (oid, k), v in track_values.items() if oid == obj["id"]}
                                  for obj in section["objects"]})
        shot_ids = unique(section["shots"], "shots")
        if all_shots & shot_ids:
            raise ValueError("Shot IDs must be unique across the film")
        all_shots |= shot_ids
        coverage = {bid: [] for bid in beat_ids}
        cursor = 0
        for shot in section["shots"]:
            require(shot, ("beat_ids", "renderer", "renderer_reason", "visual_thesis", "attention", "camera", "pattern", "object_ids", "handoff"), shot["id"])
            if shot["renderer"] not in {"manim", "remotion", "threejs"}:
                raise ValueError("Unknown shot renderer, including in a draft")
            refs(shot["beat_ids"], beat_ids, "Shot beat_ids")
            refs(shot["object_ids"], object_ids, "Shot object_ids")
            refs(shot["attention"], set(shot["object_ids"]), "Shot attention")
            require(shot["camera"], ("purpose",), "camera")
            pattern = shot["pattern"]
            kind = pattern.get("kind")
            if kind not in PATTERNS:
                raise ValueError(f"Unknown pattern: {kind}")
            require(pattern, ("entities", *PATTERNS[kind]), kind)
            refs(pattern["entities"], set(shot["object_ids"]), "Pattern entities")
            if kind in {"comparison", "before_after", "cause_effect"} and len(set(pattern["entities"])) < 2:
                raise ValueError(f"{kind} needs at least two visible entities/states")
            require(shot["handoff"], ("type", "reason"), "handoff")
            if not isinstance(shot["handoff"].get("carry_state"), list):
                raise ValueError("handoff.carry_state must be a list; empty is valid for a motivated cut")
            if shot["handoff"]["type"] not in {"cut", "match", "follow", "scale", "authored_bridge", "fade"}:
                raise ValueError("Unknown handoff type")
            # Transitions live inside authored frames; assembly adds no dead air/overlap.
            if phase == "authored" and shot["handoff"]["type"] != "cut":
                require(shot["handoff"], ("implementation",), "Authored handoff")
            if shot.get("editorial"):
                validate_editorial(shot["editorial"])
            if shot.get("b_roll"):
                require(shot["b_roll"], ("function", "relation_to_main", "construction", "anchor", "return_handoff"), "B-roll")
                refs([shot["b_roll"]["anchor"]], beat_ids, "B-roll anchor")
            if phase == "authored":
                require(shot["camera"], ("implementation",), "Authored camera")
                require(pattern, ("implementation",), "Authored pattern")
                if shot["renderer"] == "manim":
                    require(shot, ("source", "scene_name"), "Manim shot")
                start, end = frame(shot.get("start_frame"), "shot start"), frame(shot.get("end_frame"), "shot end")
                if start != cursor or end <= start:
                    raise ValueError("Shots must form a contiguous section timeline without gaps/overlap")
                shot["duration_frames"] = end - start
                validate_render_unit(shot)
                cursor = end
                require(shot, ("execution",), "Authored shot")
                execution = shot["execution"]
                require(execution, ("contract_consumer", "objects", "review_frames"), "execution")
                if set(execution["objects"]) != set(shot["object_ids"]):
                    raise ValueError("Every visible object needs an execution binding")
                for obj in execution["objects"].values():
                    require(obj, ("symbol", "motion_mode", "behavior", "layout"), "Object binding")
                    if obj["motion_mode"] not in MODES:
                        raise ValueError("Unknown motion mode")
                    require(obj["layout"], ("bounds", "overlap_policy"), "layout")
                    if obj["layout"]["overlap_policy"] not in {"avoid", "intentional"}:
                        raise ValueError("overlap_policy must be avoid or intentional")
                    if obj["layout"]["overlap_policy"] == "intentional":
                        require(obj["layout"], ("reason",), "Intentional overlap")
                    bounds = obj["layout"]["bounds"]
                    if len(bounds) != 4 or any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in bounds):
                        raise ValueError("Bounds must be x,y,width,height in delivery pixels")
                    x, y, w, h = bounds
                    if w <= 0 or h <= 0:
                        raise ValueError("Object bounds must have a nonzero footprint")
                    if obj["layout"]["overlap_policy"] == "avoid" and (x < 0 or y < 0 or x+w > 1920 or y+h > 1080):
                        raise ValueError("Object planned bounds leave delivery frame")
                for sample in execution["review_frames"]:
                    if not start <= frame(sample, "review frame") < end:
                        raise ValueError("Review sample outside shot")
                for bid in shot["beat_ids"]:
                    coverage[bid].append((start, end))
            for event in shot.get("events", []):
                require(event, ("id", "kind", "source_object", "target_objects", "cause", "action", "reaction", "aftermath", "implementation"), "event")
                if event["kind"] not in {"motion", "vfx", "camera", "transition"}:
                    raise ValueError("Unknown event kind")
                if event["kind"] == "vfx":
                    require(event, ("representation", "transport", "interaction", "lighting_response"), "VFX event")
                if event["id"] in all_events:
                    raise ValueError("Event IDs must be unique across the film")
                all_events.add(event["id"])
                refs([event["source_object"], *event["target_objects"]], set(shot["object_ids"]), "Event objects")
                if phase == "authored":
                    start, peak, end = [frame(event.get(k), k) for k in ("start_frame", "peak_frame", "end_frame")]
                    limit = section["speech"]["frames"] if event.get("carry_across_shots") else shot["end_frame"]
                    if not shot["start_frame"] <= start <= peak < end <= limit:
                        raise ValueError("Event phases must lie inside their owner shot, or explicitly carry across shots")
        if phase == "authored":
            from v4_excerpt import excerpt_scope
            excerpt = excerpt_scope(result)
            visual_end = excerpt['end_frame'] if excerpt else section["speech"]["frames"]
            if cursor != visual_end:
                raise ValueError("Shot total must equal measured speech frames")
            for beat in section["beats"]:
                intervals = sorted(coverage[beat["id"]])
                cursor_beat = beat["start_frame"]
                for start, end in intervals:
                    if start <= cursor_beat < end:
                        cursor_beat = end
                if cursor_beat < beat["end_frame"]:
                    raise ValueError(f"Beat {beat['id']} is not covered by executed shots")
            # A single lookup is shared by the renderer, SFX mixer, QA and manifest.
            event_lookup = {e["id"]: e for shot in section["shots"] for e in shot.get("events", [])}
            # Capture structural boundaries and event phases, not just flattering
            # hero stills. Samples are observations, never automatic art PASS.
            for shot in section["shots"]:
                samples = set(shot["execution"]["review_frames"]) | {shot["start_frame"], shot["end_frame"] - 1}
                for event in event_lookup.values():
                    for sample in (max(0, event["start_frame"]-1), event["peak_frame"], min(section["speech"]["frames"]-1, event["end_frame"])):
                        if shot["start_frame"] <= sample < shot["end_frame"]:
                            samples.add(sample)
                shot["execution"]["review_frames"] = sorted(samples)
            for shot in section["shots"]:
                owner_ids = {e["id"] for e in shot.get("events", [])}
                refs(shot.get("event_ids", []), set(event_lookup), "Carried event references")
                for event in event_lookup.values():
                    overlaps = event["start_frame"] < shot["end_frame"] and event["end_frame"] > shot["start_frame"]
                    if overlaps and event["id"] not in owner_ids and event["id"] not in shot.get("event_ids", []):
                        raise ValueError("A continuing event must be bound by every shot it crosses")
            for cue in section["sfx_cues"]:
                require(cue, ("event_id", "source_object", "selection_reason", "listening_review", "file"), "SFX")
                if cue["event_id"] not in event_lookup:
                    raise ValueError("SFX must bind to an executed event")
                event = event_lookup[cue["event_id"]]
                if cue["source_object"] != event["source_object"]:
                    raise ValueError("SFX source differs from event source")
                if result.get("profile") == "horror-v4.1":
                    from horror_contract import validate_sfx_brief
                    validate_sfx_brief(cue)
                    offset = cue["offset_frames"]
                    cue["relative_time"] = (event[cue["sync_phase"] + "_frame"] + offset) / 60
                    if cue["relative_time"] < 0:
                        raise ValueError("SFX starts before its measured section")
                    if cue["relative_time"] + cue["duration"] > section["speech"]["frames"] / 60 and not cue.get("carry_across_sections"):
                        raise ValueError("SFX tail crossing a section needs explicit carry_across_sections")
                else:
                    offset = frame(cue.get("offset_frames", 0), "SFX offset")
                    cue["relative_time"] = (event["start_frame"] + offset) / 60
                    if cue["relative_time"] + cue.get("duration", .3) > section["speech"]["frames"] / 60:
                        raise ValueError("SFX extends beyond section")
                if cue.get("source") == "procedural":
                    raise ValueError("No procedural replacement for missing sound recordings")
                review = cue["listening_review"]
                require(review, ("status", "reviewer", "notes", "asset_sha256"), "SFX listening review")
                if review["status"] != "PASS":
                    raise ValueError("Listen/select the SFX asset before production rendering")
            validate_cues(section["sfx_cues"])
    result["visual_reference_policy"] = visual_reference_policy(result)
    from v4_workflow import validate_packet
    validate_packet(result)
    from horror_contract import validate_horror
    validate_horror(result)
    from illustration_direction import validate_direction, directed
    validate_direction(result)
    if directed(result):
        for section in result['sections']:
            section['illustration_revision'] = 1
    return result


def visual_reference_policy(plan):
    profile = plan.get("content_profile", {})
    if plan.get("profile") == "horror-v4.1":
        if plan.get('horror',{}).get('visual_reference',{}).get('primary')=='kage':
            storytelling=plan.get('horror',{}).get('storytelling_reference',{}).get('primary')=='oversimplified'
            return {'kage':{'enabled':True,'reference':'https://github.com/MengTo/kage',
                    'scope':'original layered artwork, readable depth/light/materials; generated 2D assets and lowbudget3d fabrication'},
                    'oversimplified':{'enabled':storytelling,'reference':'https://www.youtube.com/@OverSimplified',
                        'scope':'economical ensemble staging and original character hierarchy adapted to restrained horror; no inherited comedy or copied designs',
                        'reason':'Recorded storytelling reference; Kage remains artwork target' if storytelling else 'No separate storytelling reference selected'}}
        if plan.get('horror',{}).get('visual_reference',{}).get('primary')=='oversimplified':
            return {'oversimplified':{'enabled':True,'reference':'https://www.youtube.com/@OverSimplified',
                    'scope':'story-led staging, shared scene worlds, expressive cutout acting and focus/zoom; original horror assets'},
                    'kage':{'enabled':False,'reason':'Historical reference superseded by current user direction'}}
        return {"kage": {"enabled": True, "reference": "https://github.com/MengTo/kage",
                "reason": "User-approved horror artwork direction; original crafted depth/light/occlusion",
                "scope": "reference principles, not copied assets, scroll runtime or complete scene images"}}
    kind = profile.get("kind", "mixed")
    if kind not in {"storytelling_rich", "formula_math", "mixed"}:
        raise ValueError("content_profile.kind must be storytelling_rich, formula_math, or mixed")
    shots = [shot for section in plan["sections"] for shot in section["shots"]]
    if plan.get("phase") == "authored":
        total = sum(s["end_frame"] - s["start_frame"] for s in shots)
        share = sum(s["end_frame"] - s["start_frame"] for s in shots if s["renderer"] == "manim") / total
        basis = "actual authored visual frame allocation"
    else:
        share = float(profile.get("planned_manim_share", 1 if kind == "formula_math" else 0))
        if not math.isfinite(share) or not 0 <= share <= 1:
            raise ValueError("planned_manim_share must be between 0 and 1")
        basis = "brief estimate; recompute after shot allocation"
    excluded = kind == "formula_math" and share >= .8
    enabled = kind == "storytelling_rich" and not excluded
    # A mixed subject may explicitly request rich storytelling treatment.
    enabled = enabled or (bool(profile.get("rich_storytelling")) and not excluded)
    return {"kage": {"enabled": enabled, "reference": "https://github.com/MengTo/kage",
            "manim_visual_share": share, "basis": basis,
            "reason": "Pure formula mathematics with >=80% Manim excludes Kage" if excluded else
                      ("Image-rich storytelling uses original art direction informed by Kage" if enabled else "No rich-storytelling brief"),
            "scope": "visual research only; do not copy code/artwork, UI, chapter counts or scroll time"}}


def validate_files(plan, base_dir):
    """Reject stale audio and dangling source bindings before expensive rendering."""
    base = Path(base_dir)
    if plan.get("music") and sha256(base / plan["music"]["file"]) != plan["music"]["listening_review"]["asset_sha256"]:
        raise ValueError("BGM asset changed after listening review")
    for section in plan["sections"]:
        if plan["phase"] != "draft":
            speech = section["speech"]
            path = (base / speech["file"]).resolve()
            if sha256(path) != speech["sha256"]:
                raise ValueError("Audio changed after timing measurement")
            from media_io import probe_duration
            if abs(probe_duration(path) * 60 - speech["frames"]) > 1:
                raise ValueError("Speech duration does not match measured frames")
            if not plan.get("technical_fixture"):
                require(speech, ("measurement_file", "measurement_sha256"), "Prepared speech receipt")
                measured_path = base / speech["measurement_file"]
                if sha256(measured_path) != speech["measurement_sha256"]:
                    raise ValueError("Speech measurement receipt changed")
                measured = json.loads(measured_path.read_text(encoding="utf-8"))
                for key in ("sha256", "script_sha256", "anchors", "voice", "speed", "fps", "frames", "speech_start", "speech_end"):
                    if measured.get(key) != speech.get(key):
                        raise ValueError(f"Authored speech differs from preparation receipt: {key}")
                if plan.get("profile") == "horror-v4.1":
                    for key in ("provider", "configuration_sha256"):
                        if measured.get(key) != speech.get(key):
                            raise ValueError("OmniVoice provider/configuration differs from measurement")
                    omit = {"take_file", "take_receipt", "listening_review", "listening_status"}
                    clean = lambda data: [{k:v for k,v in u.items() if k not in omit} for u in data]
                    if clean(measured.get("utterances", [])) != clean(speech.get("utterances", [])):
                        raise ValueError("Voice utterance interval/take identity differs from measurement")
        if plan["phase"] != "authored":
            continue
        for shot in section["shots"]:
            if shot["renderer"] == "manim":
                source = (base / shot["source"]).resolve()
                files = [source] + [(base / p).resolve() for p in plan.get("support_files", [])]
            else:
                spec = shot["render_spec"]
                project = (base / spec["project_dir"]).resolve()
                files = [(project / spec["entry_point"]).resolve()]
                for file in shot["execution"].get("support_files", []):
                    path = (project / file).resolve()
                    if not path.is_relative_to(project):
                        raise ValueError("Execution file leaves renderer project")
                    files.append(path)
            from v4_execution import identifiers
            bound_names = set().union(*(identifiers(p.read_text(encoding="utf-8"), python=shot["renderer"] == "manim") for p in files))
            symbols = [shot["execution"]["contract_consumer"], shot["pattern"]["implementation"],
                       shot["camera"]["implementation"], *[o["symbol"] for o in shot["execution"]["objects"].values()],
                       *[e["implementation"] for e in shot.get("events", [])],
                       *[b['instance_symbol'] for b in shot.get('model_bindings',[])],
                       *[b["contact_solver"]["implementation"] for b in shot.get("sprite_bindings", []) if b.get("contact_solver", {}).get("implementation")]]
            if shot["handoff"]["type"] != "cut":
                symbols.append(shot["handoff"]["implementation"])
            for symbol in symbols:
                if not isinstance(symbol, str) or symbol not in bound_names:
                    raise ValueError(f"Execution binding not found in source: {symbol}")
        for cue in section["sfx_cues"]:
            if sha256(base / cue["file"]) != cue["listening_review"]["asset_sha256"]:
                raise ValueError("SFX asset changed after listening review")
    from horror_contract import check_horror_files
    check_horror_files(plan, base)
    from v4_workflow import check_resources
    check_resources(plan)
    if not plan.get("technical_fixture") and plan["phase"] != "draft":
        for previous, following in zip(plan["sections"], plan["sections"][1:]):
            a, b = previous["speech"], following["speech"]
            gap = a["frames"] / 60 - a["speech_end"] + b["speech_start"]
            if gap >= 1 and not following.get("intentional_silence"):
                raise ValueError("Measured narration join exceeds one second without story justification")


def shot_contract(section, shot, plan=None):
    """Transport semantics + section clock intact; never restart beats per shot."""
    if section.get('illustration_revision') and plan is None:
        raise ValueError('Directed shot contract requires its owning plan')
    active_events = [e for s in section["shots"] for e in s.get("events", [])
                     if e["start_frame"] < shot["end_frame"] and e["end_frame"] > shot["start_frame"]]
    effective_shot = {**shot, "events": active_events}
    result = {"schema_version": 4, "fps": 60, "section_id": section["id"],
            "speech": section["speech"], "objects": section["objects"],
            "beats": [b for b in section["beats"] if b["id"] in shot["beat_ids"]],
            "shot": effective_shot, "absolute_start_frame": shot["start_frame"],
            "film_start_frame": section.get("film_start_frame", 0) + shot["start_frame"],
            "duration_frames": shot["duration_frames"],
            "state_tracks": section.get("state_tracks", []),
            "horror_assets": [a for a in section.get("horror_assets", []) if a["object_id"] in shot["object_ids"]]}
    if plan is not None:
        from illustration_direction import resolve_shot_direction
        result['resolved_direction'] = resolve_shot_direction(plan, section, shot)
        result['visual_system'] = copy.deepcopy(plan['visual_system'])
        result['scene_world'] = result['resolved_direction']['scene_world']
    return result
