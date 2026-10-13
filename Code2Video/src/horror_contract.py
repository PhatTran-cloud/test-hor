"""V4.1 horror additions to schema 4; no alternate renderer or timeline."""
import copy
import math
from pathlib import Path

PROFILE = "horror-v4.1"


def is_horror(plan):
    return plan.get("profile") == PROFILE


def need(value, keys, context):
    for key in keys:
        if key not in value or value[key] is None or value[key] == "":
            raise ValueError(f"{context} needs {key}")


def positive(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{label} must be explicitly positive and finite")
    return value


def point(value, label):
    if not isinstance(value, list) or len(value) != 2 or any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) for x in value):
        raise ValueError(f"{label} must be a finite [x,y] point")


def validate_horror(plan):
    if not is_horror(plan):
        return
    from v4_contract import unique, refs
    if plan.get("content_profile", {}).get("genre") != "horror":
        raise ValueError("The dedicated profile requires content_profile.genre=horror")
    if plan.get("language_id") not in {"en", "vi"}:
        raise ValueError("The user selects language_id en or vi per video; there is no default")
    need(plan, ("horror", "cast"), "horror plan")
    horror, cast = plan["horror"], plan["cast"]
    style = horror.get("artwork_style")
    if style not in {"3d_horror_cartoon", "2d_flat_geometric_vector"} or horror.get("artwork_provider") != "flow":
        raise ValueError("Horror artwork needs a supported user-selected style and Flow assets")
    reference=horror.get('visual_reference',{}).get('primary')
    if reference=='oversimplified':
        if style!='2d_flat_geometric_vector': raise ValueError('OverSimplified direction uses the selected 2D illustrated style')
        decision=plan.get('production_packet',{}).get('visual_style_decision',{})
        if decision.get('primary_reference')!='oversimplified':
            raise ValueError('Record the user-selected OverSimplified primary reference')
        illustrator=horror.get('illustrator',{})
        if (illustrator.get('mode')!='prompt_export_only' or illustrator.get('generation_operator')!='human user'
                or illustrator.get('chroma_key_color')!='#00FF00' or not illustrator.get('model')):
            raise ValueError('Illustration must export human-run Flow prompts with uniform #00FF00 for alpha assets')
    elif reference not in {None,'kage'} or horror.get('kage_reference') is not True:
        raise ValueError('Historical plans need Kage; current plans use the recorded OverSimplified reference')
    if style == "2d_flat_geometric_vector":
        decision = plan.get("production_packet", {}).get("visual_style_decision", {})
        if (decision.get("status") != "USER_SELECTED" or decision.get("selected_style") != style
                or decision.get("authorization", {}).get("reviewer") != "human user"
                or not decision.get("authorization", {}).get("request")):
            raise ValueError("Flat geometric vector artwork needs the recorded user style selection")
    if horror.get("voice_provider") != "omnivoice" or horror.get("sfx_provider") != "stable_audio_3_small_sfx":
        raise ValueError("Horror uses OmniVoice and Stable Audio 3 Small-SFX only")
    need(cast, ("library", "narrator", "characters"), "cast")
    if not isinstance(cast["narrator"], str) or not isinstance(cast["characters"], dict):
        raise ValueError("Exactly one narrator speaker ID and a character-to-speaker map are required")
    if cast.get("narrator_instruct") is not None:
        raise ValueError("Narrator instruction is forbidden")
    need(horror, ("style_bible",), "horror artwork direction")
    need(horror["style_bible"], ("canonical_prompt", "proportions", "materials", "lighting", "depth", "identity_rules"), "style bible")
    from omnivoice_tts import line_identity
    for sec in plan["sections"]:
        for seg in sec.get("narration_segments", []):
            line_identity(plan, seg)
        unique(sec.get("sfx_cues", []), "SFX cues")
        for cue in sec.get("sfx_cues", []):
            validate_sfx_brief(cue)
        if plan["phase"] != "draft" and not plan.get("technical_fixture"):
            speech = sec["speech"]
            need(speech, ("provider", "configuration_sha256", "cast_references", "utterances"), "OmniVoice speech")
            if speech["provider"] != "omnivoice" or speech.get("voice") != cast["narrator"]:
                raise ValueError("Prepared speech must use the selected OmniVoice cast")
            if speech.get("speed") != plan["tts_speed"]:
                raise ValueError("Speech speed differs from measured configuration")
            if plan["phase"] == "authored":
                from v4_excerpt import voice_review_deferred
                deferred = voice_review_deferred(plan, speech)
                for u in speech["utterances"]:
                    review = u.get("listening_review", {})
                    if not deferred and (review.get("status") != "PASS" or review.get("asset_sha256") != u["take_sha256"] or not review.get("reviewer") or not review.get("notes")):
                        raise ValueError("Voice takes need current identity/acting listening review before authored rendering")
            actual = [u["line_identity"] for u in speech["utterances"]]
            if actual != [line_identity(plan, s) for s in sec["narration_segments"]]:
                raise ValueError("Script, cast, instruction or acting brief changed after voice preparation")
    assets = horror.get("assets", [])
    if reference=='oversimplified' and plan['phase']=='authored':
        from horror_illustration import validate_illustration_coverage
        validate_illustration_coverage(plan)
    ids = unique(assets, "horror assets")
    all_objects = {o["id"] for sec in plan["sections"] for o in sec["objects"]}
    for asset in assets:
        need(asset, ("object_id", "kind", "identity", "action", "views"), "Flow asset")
        if asset.get("provider") != "flow" or asset["kind"] not in {"sprite_sequence", "prop", "layer"}:
            raise ValueError("Flow assets must be separate sprites, props or environment layers")
        refs([asset["object_id"]], all_objects, "asset object")
        action = asset["action"]
        need(action, ("intent", "mechanics", "source_ids", "entry_state", "exit_state", "contact_requirements"), "behavior research before Flow")
        sources = {s["id"] for s in plan.get("production_packet", {}).get("research", {}).get("sources", [])}
        if not action["source_ids"] or not set(action["source_ids"]) <= sources:
            raise ValueError("Action research must bind to inspected packet sources")
        view_ids = unique(asset["views"], "asset views")
        if not view_ids:
            raise ValueError("Asset needs the views required by the storyboard")
        for view in asset["views"]:
            need(view, ("camera_region", "frames"), "asset view")
            if not view["frames"]:
                raise ValueError("A view cannot have an empty pose list")
            unique(view["frames"], "pose frames")
            for pose in view["frames"]:
                need(pose, ("description", "id", "width", "height", "root_anchor", "ground_anchor", "sockets", "hold_frames"), "registered pose")
                for key in ("width", "height", "hold_frames"):
                    if isinstance(pose[key], bool) or not isinstance(pose[key], int) or pose[key] < 1:
                        raise ValueError(f"Pose {key} must be a positive integer")
                for key in ("root_anchor", "ground_anchor"):
                    point(pose[key], key)
                for name, p in pose["sockets"].items():
                    point(p, name)
                if plan["phase"] == "authored":
                    need(pose, ("file", "sha256"), "approved pose file")
        if plan["phase"] == "authored":
            review = asset.get("review", {})
            need(review, ("reviewer", "notes", "asset_digest"), "asset visual review")
            if review.get("status") != "PASS" or review["asset_digest"] != asset_digest(asset):
                raise ValueError("Flow artwork needs an actual current visual review before authored motion")
    for sec in plan["sections"]:
        sec["horror_assets"] = [a for a in assets if a["object_id"] in {o["id"] for o in sec["objects"]}]
    lookup = {a["id"]: a for a in assets}
    for sec in plan["sections"]:
        for shot in sec["shots"]:
            for binding in shot.get("sprite_bindings", []):
                need(binding, ("object_id", "asset_id", "view_id", "loop", "contact_windows"), "sprite binding")
                refs([binding["asset_id"]], ids, "sprite asset")
                refs([binding["object_id"]], set(shot["object_ids"]), "sprite instance")
                asset = lookup[binding["asset_id"]]
                if asset["object_id"] != binding["object_id"]:
                    raise ValueError("Sprite asset belongs to another canonical object")
                if binding["view_id"] not in {v["id"] for v in asset["views"]}:
                    raise ValueError("Camera requires an unavailable sprite view")
                if binding["view_id"] not in shot["camera"].get("supported_sprite_views", []):
                    raise ValueError("Camera must declare the sprite views its path supports")
                if not isinstance(binding["loop"], bool):
                    raise ValueError("Sprite loop must be an explicit boolean")
                if plan["phase"] == "authored":
                    need(binding, ("start_frame", "end_frame", "root_track"), "authored sprite")
                    if not shot["start_frame"] <= binding["start_frame"] < binding["end_frame"] <= shot["end_frame"]:
                        raise ValueError("Sprite playback lies outside its shot")
                    from horror_sprites import validate_binding
                    validate_binding(asset, binding)
            if plan["phase"] == "authored":
                bound = {b["object_id"] for b in shot.get("sprite_bindings", [])}
                for oid, execution in shot["execution"]["objects"].items():
                    if execution.get("asset_mode") == "sprite" and oid not in bound:
                        raise ValueError("Sprite execution object lacks an asset/action/view binding")
    if plan["phase"] == "authored":
        total = sum(sec["speech"]["frames"] for sec in plan["sections"])/60
        for sec in plan["sections"]:
            for cue in sec.get("sfx_cues", []):
                if sec["film_start_frame"]/60 + cue["relative_time"] + cue["duration"] > total + 1e-9:
                    raise ValueError("SFX tail exceeds the measured film timeline")


def asset_digest(asset):
    from v4_contract import digest
    data = copy.deepcopy(asset)
    data.pop("review", None)
    for view in data["views"]:
        for pose in view["frames"]:
            pose.pop("file", None)  # bind content, not location after snapshot
    return digest(data)


def validate_sfx_brief(cue):
    need(cue, ("id", "event_id", "source_object", "duration", "sync_phase", "offset_frames", "generation", "perspective"), "horror SFX")
    positive(cue["duration"], "SFX audible duration")
    if cue["sync_phase"] not in {"start", "peak", "end"}:
        raise ValueError("SFX sync_phase must select the event start, peak or end")
    if isinstance(cue["offset_frames"], bool) or not isinstance(cue["offset_frames"], int):
        raise ValueError("SFX offset_frames must be an integer")
    if cue["offset_frames"] < 0 and not cue.get("timing_reason"):
        raise ValueError("Anticipating sound needs an editorial timing_reason")
    if any(key in cue for key in ("query", "sound_id")) or cue.get("source") in {"freesound", "procedural", "kokoro"}:
        raise ValueError("Horror SFX uses generated Small-SFX assets only")
    g = cue["generation"]
    need(g, ("prompt", "seconds", "seed"), "Small-SFX generation")
    if not isinstance(g["prompt"], str) or not g["prompt"].strip():
        raise ValueError("SFX prompt must describe the acoustic event")
    positive(g["seconds"], "SFX generation seconds")
    if not isinstance(g["seed"], int) or isinstance(g["seed"], bool) or g["seed"] < 0:
        raise ValueError("SFX seed must be an explicit nonnegative integer")
    offset = cue.get("asset_offset", 0)
    if not isinstance(offset, (int, float)) or isinstance(offset, bool) or not math.isfinite(offset) or offset < 0:
        raise ValueError("asset_offset must be finite and nonnegative")
    if not cue.get("loop") and offset + cue["duration"] > g["seconds"] + 1/44100:
        raise ValueError("Explicit generation length must cover the selected audible interval and tail")
    need(cue["perspective"], ("space", "distance", "occlusion", "reason"), "SFX acoustic perspective")


def check_horror_files(plan, base):
    if not is_horror(plan):
        return
    from v4_contract import sha256
    from omnivoice_tts import configuration_identity
    for sec in plan["sections"]:
        if plan["phase"] != "draft" and not plan.get("technical_fixture"):
            for u in sec["speech"]["utterances"]:
                for key, hash_key in (("take_file", "take_sha256"), ("take_receipt", "take_receipt_sha256")):
                    if sha256(Path(base)/u[key]) != u[hash_key]:
                        raise ValueError("Voice take or provider receipt changed")
            if configuration_identity(plan, sec)["sha256"] != sec["speech"]["configuration_sha256"]:
                raise ValueError("Voice reference/transcript/settings changed after measurement")
    if plan["phase"] == "authored":
        from PIL import Image
        for asset in plan["horror"].get("assets", []):
            for view in asset["views"]:
                for pose in view["frames"]:
                    path = (Path(plan.get("asset_base_dir", base)) / pose["file"]).resolve()
                    if sha256(path) != pose["sha256"]:
                        raise ValueError("Flow pose changed after artwork review")
                    with Image.open(path) as im:
                        if im.size != (pose["width"], pose["height"]):
                            raise ValueError("Pose dimensions differ from registration")
                        alpha_required=asset.get('requires_alpha',asset['kind']!='layer')
                        if alpha_required and (im.format!='PNG' or "A" not in im.getbands()):
                            raise ValueError("Sprites/props need actual alpha separation before animation")
                        if alpha_required and im.getchannel("A").getextrema()[0] == 255:
                            raise ValueError("A fully opaque RGBA image is not a separated sprite/prop")
                        if alpha_required and im.getchannel('A').getextrema()[1]==0:
                            raise ValueError('An entirely transparent image is not a usable cutout')
        from sfx_assets import prepare_cues
        for sec in plan["sections"]:
            prepare_cues(sec["sfx_cues"], base)
