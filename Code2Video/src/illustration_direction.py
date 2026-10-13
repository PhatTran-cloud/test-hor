"""Additive Kage asset direction on schema 4; planning is never artwork approval."""
import copy
import math

REVISION = 1
ROLES = {"subject", "support", "foreground", "midground", "background", "atmosphere", "interactive_prop"}
PRIORITIES = {"primary", "secondary", "ambient", "suppressed"}
ROUTES = {"2d", "3d", "procedural", "existing"}
MODES = {"active", "reactive", "passive", "optical", "camera_induced"}
MODEL_SKILLS = ["3dviz-pro-max", "lowbudget3d", "lowbudget3d-illustration-bridge"]


def require(value, fields, context):
    if not isinstance(value, dict):
        raise ValueError(f"{context} must be an object")
    for field in fields:
        if field not in value or value[field] is None or value[field] in ("", [], {}):
            raise ValueError(f"{context} needs {field}")


def directed(plan):
    revision = plan.get("production_packet", {}).get("illustration_direction", {}).get("contract_revision")
    if revision is not None and (isinstance(revision, bool) or revision != REVISION):
        raise ValueError("Unknown illustration direction contract revision")
    return revision == REVISION


def lightweight(plan):
    return directed(plan) and plan['production_packet']['illustration_direction'].get('authoring_mode') == 'horror_light'


def validate_behaviors(shot, events, worlds, objects):
    """Execution detail is mandatory at motion authoring, not at light storyboard."""
    require(shot, ('behaviors',), 'Motion authoring')
    if set(shot['behaviors']) != set(shot['object_ids']):
        raise ValueError('Every shot component needs a justified temporal behavior')
    for behavior in shot['behaviors'].values():
        require(behavior, ('mode', 'motivation', 'trigger', 'response', 'secondary_response', 'settle', 'exit_state'), 'Object behavior')
        if behavior['mode'] not in MODES or not isinstance(behavior['exit_state'], dict):
            raise ValueError('Motion needs a supported mode and inspectable exit_state')
        trigger = behavior['trigger']
        require(trigger, ('kind', 'reason'), 'Behavior trigger')
        kind, ref = trigger['kind'], trigger.get('ref')
        if kind == 'event':
            if ref not in events or trigger.get('phase') not in {'start', 'peak', 'end'}:
                raise ValueError('Behavior must bind a known event phase')
        elif kind == 'camera':
            if ref != shot['id']:
                raise ValueError('Camera behavior binds this shot')
        elif kind == 'environment':
            if ref not in worlds and ref not in objects:
                raise ValueError('Environment trigger needs a known world or object')
        elif kind != 'intentional_hold' or behavior['mode'] != 'passive':
            raise ValueError('Intentional hold uses passive mode; other triggers must be known')


def validate_light_shots(plan, shots, worlds, objects, events):
    for index, shot in enumerate(shots):
        require(shot, ('action', 'sound_intent'), 'Light shot card')
        if shot.get('scene_id') not in worlds or not shot.get('attention'):
            raise ValueError('Light shot needs a known scene and focal object')
        next_id = shots[index + 1]['id'] if index + 1 < len(shots) else None
        if 'to_shot_id' not in shot['handoff'] or shot['handoff']['to_shot_id'] != next_id:
            raise ValueError('Light handoff must name the actual next shot or null at end')
        # Component/layer quotas and per-beat metaphors do not apply. If a caller
        # supplies a component inventory, it must still be truthful and complete.
        if 'components' in shot:
            if _ids(shot['components'].get('items', []), 'object_id', 'Shot components') != set(shot['object_ids']):
                raise ValueError('Shot components must cover every visible object exactly once')
        if 'behaviors' in shot or plan['phase'] == 'authored':
            validate_behaviors(shot, events, worlds, objects)
        if plan['phase'] == 'authored':
            require(shot['camera'], ('information_intent',), 'Authored camera')
            info = shot['camera']['information_intent']
            require(info, ('known_before', 'hidden_before', 'reveals', 'target_object', 'reason_for_move_or_hold'), 'Camera information intent')
            if info['target_object'] not in shot['object_ids']:
                raise ValueError('Camera focal target must be a shot component')


def index_worlds(plan):
    return {w["id"]: w for w in plan.get("production_packet", {}).get("illustration_direction", {}).get("scene_worlds", [])}


def _ids(items, field, label):
    if not isinstance(items, list) or not items:
        raise ValueError(f"{label} must be a nonempty list")
    values = [i.get(field) for i in items]
    if any(not isinstance(v, str) or not v.strip() for v in values) or len(set(values)) != len(values):
        raise ValueError(f"{label} needs unique IDs")
    return set(values)


def validate_model_request(asset, phase):
    require(asset, ("model_spec",), "3D asset")
    model = asset["model_spec"]
    require(model, ("representation", "dimensions", "parts", "anchors", "variants", "surface_regions", "texture_plan", "articulation", "closest_camera_use"), "3D fabrication brief")
    if model["representation"] not in {"glb", "threejs_module"}:
        raise ValueError("3D asset must be a GLB or editable Three.js module")
    dimensions = model["dimensions"]
    require(dimensions, ("unit", "size"), "3D dimensions")
    if dimensions["unit"] != "metres" or len(dimensions["size"]) != 3 or any(
            isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v <= 0 for v in dimensions["size"]):
        raise ValueError("3D dimensions need three positive metre sizes")
    parts = _ids(model["parts"], "id", "3D named parts")
    for part in model["parts"]:
        require(part, ("pivot", "material_region"), "3D part")
        if part.get("parent_id") is not None and part["parent_id"] not in parts:
            raise ValueError("Unknown 3D parent part")
        pivot = part['pivot']
        if not isinstance(pivot, list) or len(pivot) != 3 or any(
                isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in pivot):
            raise ValueError('3D pivot must be a finite local-space XYZ point')
    parents = {part['id']: part.get('parent_id') for part in model['parts']}
    for pid in parents:
        seen, current = set(), pid
        while current is not None:
            if current in seen:
                raise ValueError('3D part hierarchy cannot contain a cycle')
            seen.add(current)
            current = parents[current]
    for view in asset["views"]:
        require(view, ("id", "camera_region", "inspection_purpose"), "3D inspection view")
    if phase == "authored":
        require(model, ("file", "sha256", "inspection_evidence"), "Built 3D asset")
        if not isinstance(model.get("resources", []), list):
            raise ValueError("3D resources must be a list")
        for resource in model.get("resources", []):
            require(resource, ("file", "sha256"), "3D resource")
        view_ids = {v["id"] for v in asset["views"]}
        evidence_ids = _ids(model["inspection_evidence"], "view_id", "3D inspection evidence")
        if evidence_ids != view_ids:
            raise ValueError("3D artwork needs evidence for every requested inspection view")
        for evidence in model["inspection_evidence"]:
            require(evidence, ("file", "sha256"), "3D inspection evidence")


def validate_direction(plan):
    from horror_staging import validate_staging
    validate_staging(plan)
    if not directed(plan):
        return
    direction = plan["production_packet"]["illustration_direction"]
    if direction.get("target_artwork") != "kage":
        raise ValueError("This illustration revision targets Kage artwork principles")
    if direction.get('authoring_mode', 'full') not in {'full', 'horror_light'}:
        raise ValueError('Unknown illustration authoring mode')
    light = lightweight(plan)
    if not light:
        require(plan["visual_system"], ("bindings",), "Directed visual system")
        require(plan["visual_system"]["bindings"], ("color_roles", "shape_roles", "typography_roles", "transition_rules"), "Visual system bindings")
    _ids(direction.get("scene_worlds", []), "id", "Scene worlds")
    worlds = index_worlds(plan)
    objects = {o["id"]: o for s in plan["sections"] for o in s["objects"]}
    shots = [sh for sec in plan["sections"] for sh in sec["shots"]]
    events = {e["id"]: e for sh in shots for e in sh.get("events", [])}
    completed = set()
    def inspect_causes(eid, visiting):
        if eid in completed:
            return
        if eid in visiting:
            raise ValueError('Event cause graph cannot contain a cycle')
        causes = events[eid].get('cause_event_ids', [])
        if (not isinstance(causes, list) or any(not isinstance(c, str) or c not in events for c in causes)
                or len(set(causes)) != len(causes)):
            raise ValueError('Event causes need unique known event IDs')
        for cause in causes:
            inspect_causes(cause, visiting | {eid})
        completed.add(eid)
    for eid in events:
        inspect_causes(eid, set())
    for world in worlds.values():
        require(world, ("layout", "perspective", "lighting", "crop_safety"), "Scene world")
        if light and 'semantic_layers' not in world:
            continue
        require(world, ('semantic_layers',), 'Scene world')
        layer_ids = _ids(world["semantic_layers"], "object_id", "Semantic layers")
        if not layer_ids <= set(objects):
            raise ValueError("Scene world references unknown objects")
        for layer in world["semantic_layers"]:
            require(layer, ("depth", "information", "function"), "Semantic layer")
            if layer["depth"] not in {"foreground", "midground", "background"}:
                raise ValueError("Semantic layer needs foreground/midground/background depth")
    if light:
        validate_light_shots(plan, shots, worlds, objects, events)
        return
    for section in plan["sections"]:
        for beat in section["beats"]:
            require(beat, ("direction",), "Semantic beat")
            meaning = beat["direction"]
            require(meaning, ("idea", "visual_proposition", "metaphor", "adds_information", "object_ids", "knowledge", "payoff"), "Beat visual argument")
            require(meaning["metaphor"], ("source", "target", "mapping", "limits"), "Visual metaphor")
            require(meaning["knowledge"], ("before", "after", "withheld"), "Viewer information")
            if not set(meaning["object_ids"]) <= {o["id"] for o in section["objects"]}:
                raise ValueError("Metaphor references unknown section objects")
    for index, shot in enumerate(shots):
        visible = set(shot["object_ids"])
        if shot.get("scene_id") not in worlds:
            raise ValueError("Every directed shot needs a known scene world")
        if not visible <= {l["object_id"] for l in worlds[shot["scene_id"]]["semantic_layers"]}:
            raise ValueError("Every shot object needs a world layer and information function")
        require(shot, ("components", "attention_plan", "behaviors"), "Complete directed shot")
        components = shot["components"]
        ids = _ids(components.get("items", []), "object_id", "Shot components")
        if ids != visible:
            raise ValueError("Shot components must cover every visible object exactly once")
        required = components.get("required_roles", [])
        omitted = components.get("omissions", {})
        if (not isinstance(required, list) or not required or len(set(required)) != len(required)
                or not set(required) <= ROLES or not isinstance(omitted, dict)
                or set(required) & set(omitted) or set(required) | set(omitted) != ROLES
                or any(not isinstance(v, str) or not v.strip() for v in omitted.values())):
            raise ValueError("Account for every component role as required or explicitly unnecessary")
        covered = set()
        for item in components["items"]:
            require(item, ("roles", "route"), "Shot component")
            if not set(item["roles"]) <= set(required) or item["route"] not in ROUTES:
                raise ValueError("Unknown/unneeded component role or fabrication route")
            covered.update(item["roles"])
            method = objects[item["object_id"]].get("illustration", {}).get("method")
            if item["route"] in {"2d", "3d"} and method != "generated":
                raise ValueError("2D/3D fabrication component needs explicit generated assets")
            if item["route"] in {"existing", "procedural"} and method != item["route"]:
                raise ValueError("Component route disagrees with object illustration method")
        if covered != set(required):
            raise ValueError("Shot is missing a required component role")
        if _ids(shot["attention_plan"], "object_id", "Attention plan") != visible:
            raise ValueError("Every shot component needs an attention priority")
        for entry in shot["attention_plan"]:
            require(entry, ("priority", "reason"), "Attention entry")
            if entry["priority"] not in PRIORITIES:
                raise ValueError("Unknown attention priority")
        if not any(a["priority"] == "primary" for a in shot["attention_plan"]):
            raise ValueError("Directed shot needs a focal priority")
        if set(shot["behaviors"]) != visible:
            raise ValueError("Every shot component needs a justified temporal behavior")
        for oid, behavior in shot["behaviors"].items():
            require(behavior, ("mode", "motivation", "trigger", "response", "secondary_response", "settle", "exit_state"), "Object behavior")
            if behavior["mode"] not in MODES:
                raise ValueError("Unknown directed motion mode")
            if not isinstance(behavior['exit_state'],dict):
                raise ValueError('Behavior exit_state must name inspectable state properties')
            trigger = behavior["trigger"]
            require(trigger, ("kind", "reason"), "Behavior trigger")
            if trigger["kind"] == "event":
                if trigger.get("ref") not in events or trigger.get("phase") not in {"start", "peak", "end"}:
                    raise ValueError("Behavior must bind a known event phase")
            elif trigger["kind"] == "camera":
                if trigger.get("ref") != shot["id"]:
                    raise ValueError("Camera-induced behavior binds this shot's camera")
            elif trigger["kind"] == "environment":
                if trigger.get("ref") not in worlds and trigger.get("ref") not in objects:
                    raise ValueError("Environment trigger needs a world or source object")
            elif trigger["kind"] != "intentional_hold":
                raise ValueError("Unknown behavior trigger")
            if trigger["kind"] == "intentional_hold" and behavior["mode"] != "passive":
                raise ValueError("Intentional hold uses passive mode, not invented active motion")
        require(shot["camera"], ("information_intent",), "Directed camera")
        info = shot["camera"]["information_intent"]
        require(info, ("known_before", "hidden_before", "reveals", "target_object", "reason_for_move_or_hold"), "Camera information intent")
        if info["target_object"] not in visible:
            raise ValueError("Camera focal target must be a shot component")
        require(shot["handoff"], ("semantic_link",), "Directed handoff")
        link = shot["handoff"]["semantic_link"]
        require(link, ("kind", "relation"), "Scene relationship")
        next_id = shots[index+1]["id"] if index+1 < len(shots) else None
        if link.get("to_shot_id") != next_id or link["kind"] not in {"causal", "semantic", "spatial", "sound", "end"}:
            raise ValueError("Handoff must name the actual next shot and relationship")
        if next_id is None:
            if link["kind"] != "end":
                raise ValueError("Last shot explicitly ends the sequence")
        elif link["kind"] == "end" or not link.get("invariants"):
            raise ValueError("Adjacent scenes need an invariant, not a generic next scene")
        if link.get("trigger_event_id") and link["trigger_event_id"] not in events:
            raise ValueError("Handoff references an unknown event")
    assets = {a["id"]: a for a in plan.get("horror", {}).get("assets", [])}
    for shot in shots:
        for item in shot["components"]["items"]:
            if item["route"] not in {"2d", "3d"}:
                continue
            spec = objects[item["object_id"]]["illustration"]
            ids = spec.get("asset_ids", [])
            if not ids:
                raise ValueError("Fabricated component has no assets")
            for aid in ids:
                asset = assets.get(aid)
                if not asset or asset["object_id"] != item["object_id"]:
                    raise ValueError("Fabricated component has missing/mismatched assets")
                route = "3d" if asset.get("kind") == "model_3d" else "2d"
                if route != item["route"]:
                    raise ValueError("A 3D component cannot silently become a flat image")
                require(asset, ("design_semantics",), "Fabrication semantics")
                require(asset["design_semantics"], ("role", "meaning", "recognition_traits", "parts_or_layers", "anchors", "variants", "closest_camera_use"), "Asset construction meaning")


def resolve_shot_direction(plan, section, shot):
    """One scoped authority payload for prompts, renderers and review invalidation."""
    world = index_worlds(plan).get(shot.get("scene_id"))
    beat_lookup = {b["id"]: b for b in section.get("beats",[])}
    needed = set(shot.get("beat_ids",[]))
    pending = list(needed)
    while pending:
        for dep in beat_lookup[pending.pop()].get("depends_on", []):
            if dep not in needed:
                needed.add(dep); pending.append(dep)
    if "start_frame" in shot and "end_frame" in shot:
        events = [e for s in section["shots"] for e in s.get("events", [])
                  if e.get("start_frame", math.inf) < shot["end_frame"] and e.get("end_frame", -1) > shot["start_frame"]]
    else:
        event_ids = set(shot.get("event_ids", [])) | {e["id"] for e in shot.get("events", [])}
        events = [e for s in section["shots"] for e in s.get("events", []) if e["id"] in event_ids]
    event_lookup = {e['id']:{**e,'owner_section_id':sec['id'],'owner_film_start_frame':sec.get('film_start_frame')}
                    for sec in plan['sections'] for s in sec['shots'] for e in s.get('events',[])}
    dependency_ids = {e['id'] for e in events}
    dependency_ids.update(b['trigger']['ref'] for b in shot.get('behaviors',{}).values() if b.get('trigger',{}).get('kind')=='event')
    handoff_event = shot.get('handoff',{}).get('semantic_link',{}).get('trigger_event_id')
    if handoff_event: dependency_ids.add(handoff_event)
    pending = list(dependency_ids)
    while pending:
        for cause in event_lookup[pending.pop()].get('cause_event_ids', []):
            if cause not in dependency_ids:
                dependency_ids.add(cause)
                pending.append(cause)
    dependencies = [e for eid,e in event_lookup.items() if eid in dependency_ids]
    object_ids = set(shot["object_ids"])
    for event in dependencies:
        object_ids.update([event["source_object"], *event["target_objects"]])
    film_shots = [s for sec in plan["sections"] for s in sec["shots"]]
    index = next(i for i,s in enumerate(film_shots) if s["id"] == shot["id"])
    assets = [a for a in plan.get("horror", {}).get("assets", []) if a["object_id"] in object_ids]
    packet = plan.get("production_packet", {})
    objects = {}
    for sec in plan['sections']:
        for obj in sec['objects']:
            if obj['id'] in object_ids:
                objects.setdefault(obj['id'], obj)
    # A later section may reuse the canonical identity with a different state.
    # It must not overwrite the state at this shot's section entry.
    objects.update({o['id']: o for o in section['objects'] if o['id'] in object_ids})
    result = {"contract_revision": packet.get("illustration_direction", {}).get("contract_revision"),
        "target_artwork": packet.get("illustration_direction", {}).get("target_artwork"),
        "visual_system": plan.get("visual_system", {}), "scene_world": world,
        "character_setting_brief": packet.get("character_setting_brief", {}),
        "visual_style_decision": packet.get("visual_style_decision", {}),
        "beats": [b for b in section.get("beats",[]) if b["id"] in needed],
        "objects": list(objects.values()),
        "active_events": events, "dependency_events":dependencies, "assets": assets,
        "adjacent_handoffs": [{"id":s["id"], "handoff":s.get("handoff",{})} for s in film_shots[max(0,index-1):index+2]],
        "components": shot.get("components"), "behaviors": shot.get("behaviors"),
        "attention_plan": shot.get("attention_plan"), "camera": shot.get("camera",{}), "handoff": shot.get("handoff",{})}
    if lightweight(plan):
        result.update(authoring_mode='horror_light', action=shot['action'], sound_intent=shot['sound_intent'])
    from horror_staging import resolve_staging
    stage = resolve_staging(plan, shot)
    if stage is not None:
        result['scene_staging'] = stage
    from horror_characters import resolve_character_cast
    cast = resolve_character_cast(plan, section, shot)
    if cast is not None:
        result['character_cast'] = cast
    return copy.deepcopy(result)


def shot_inventory(plan):
    assets = {a["id"]:a for a in plan["horror"].get("assets", [])}
    rows = []
    for section in plan["sections"]:
        objects = {o["id"]:o for o in section["objects"]}
        for shot in section["shots"]:
            entries = []
            for oid in shot["object_ids"]:
                spec = objects[oid]["illustration"]
                ids = spec.get("asset_ids", []) if spec['method'] == 'generated' else []
                entries.append({"object_id":oid,"method":spec["method"],"asset_ids":ids,
                    "routes":["3d" if assets[aid].get("kind") == "model_3d" else "2d" for aid in ids],
                    "reason":spec.get("reason")})
            rows.append({"shot_id":shot["id"],"scene_id":shot.get("scene_id"),"components":entries,
                "status":"REQUEST_COVERAGE_CHECKED_NOT_ARTWORK_APPROVED",
                "direction":resolve_shot_direction(plan,section,shot)})
            cast = rows[-1]['direction'].get('character_cast')
            if cast is not None:
                rows[-1]['cast'] = {k:v for k,v in cast.items() if k not in {'characters','crowd_groups'}}
            if rows[-1]['direction'].get('scene_staging') is not None:
                rows[-1]['staging'] = rows[-1]['direction']['scene_staging']
    return rows
