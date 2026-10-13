"""Assistant-authored V4 workflow: prepare -> author -> render -> inspect/review.

No provider/subprocess LLM. Unreviewed exports are review candidates, not releases.
"""
import copy
import json
import math
import shutil
import subprocess
import uuid
from pathlib import Path
from types import SimpleNamespace

from omnivoice_tts import prepare_section, configuration_identity
from media_io import attach_narration
from output_paths import get_output_root
from renderers import render_authored_section, render_unit, probe_video
from sfx_assets import prepare_cues, freeze_music
from sfx import mix_narration_with_sfx
from v4_contract import digest, normalize_v4, sha256, shot_contract, validate_files


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def prepare(plan, folder, args):
    result = copy.deepcopy(plan)
    result["phase"] = "timed"
    for section in result["sections"]:
        audio = folder / "audio" / (section["id"] + ".wav")
        audio.parent.mkdir(exist_ok=True)
        timing = prepare_section(plan, section, audio, endpoint=args.tts_endpoint)
        anchors = [{"id": s["id"], "start_frame": round(s["start"]*60),
                    "end_frame": min(timing["frames"], round(s["end"]*60)),
                    "confidence": "measured_segment", "text": s["text"]}
                   for s in timing["beats"]]
        section["speech"] = {**timing, "sha256": sha256(audio), "fps": 60,
                             "script_sha256": digest(section["narration"]), "anchors": anchors,
                             "alignment": "recording segments; no invented word timestamps"}
        measurement = folder / "audio" / (section["id"] + "_measurement.json")
        write(measurement, {k: v for k, v in section["speech"].items() if k != "file"})
        section["speech"].update(measurement_file=str(measurement), measurement_sha256=sha256(measurement))
        for beat in section["beats"]:
            anchor = next(a for a in anchors if a["id"] == beat["narration_anchor"]["segment_id"])
            # A recording passage may anchor several semantic changes. Allocate
            # their visual timing during direction, never force identical slots.
            beat.pop("start_frame", None)
            beat.pop("end_frame", None)
            beat["anchor_interval"] = {"start_frame": anchor["start_frame"], "end_frame": anchor["end_frame"]}
        print(f"Measured {section['id']}: {timing['frames']} frames, {len(anchors)} recording anchors", flush=True)
    # Paths remain absolute so the measured plan can be authored beside original sources.
    result["asset_base_dir"] = str(args.plan.parent.resolve())
    result["support_files"] = [str((args.plan.parent / p).resolve()) for p in result.get("support_files", [])]
    if result.get("music", {}).get("file"):
        result["music"]["file"] = str((args.plan.parent / result["music"]["file"]).resolve())
    for section in result["sections"]:
        for cue in section["sfx_cues"]:
            if cue.get("file"):
                cue["file"] = str((args.plan.parent / cue["file"]).resolve())
        for shot in section["shots"]:
            if shot.get("source"):
                shot["source"] = str((args.plan.parent / shot["source"]).resolve())
            if shot.get("render_spec"):
                spec = shot["render_spec"]
                spec["project_dir"] = str((args.plan.parent / spec["project_dir"]).resolve())
    result = normalize_v4(result)
    write(folder / "timed_plan.json", result)
    return result


def freeze(plan, base, folder, snapshot_browser_project):
    frozen = copy.deepcopy(plan)
    snapshots = {}
    for resource in frozen.get("production_packet", {}).get("consulted_resources", []):
        original = Path(resource["file"])
        target = folder / "research_resources" / resource["skill"] / (resource["sha256"][:12] + "_" + original.name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(original, target)
        resource.setdefault("resource_name", original.name)
        resource["file"] = str(target)
    if frozen.get("music"):
        cue = freeze_music(frozen["music"], base)
        source = Path(cue["file"])
        target = folder / "audio_assets" / (sha256(source)[:16] + source.suffix)
        target.parent.mkdir(exist_ok=True)
        shutil.copy2(source, target)
        frozen["music"] = {**cue, "file": str(target)}
    for asset in plan.get("asset_files", []):
        source = (Path(plan.get("asset_base_dir", base)) / asset).resolve()
        relative = Path(asset)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("asset_files must be contained relative paths")
        target = folder / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    from horror_snapshot import freeze_horror_assets
    freeze_horror_assets(frozen, base, folder)
    support_names = set()
    frozen["support_files"] = []
    for module in plan.get("support_files", []):
        source = (base / module).resolve()
        if source.name in support_names:
            raise ValueError("Support module names collide; use unique module names")
        support_names.add(source.name)
        shutil.copy2(source, folder / source.name)
        frozen["support_files"].append(source.name)
    for section in frozen["sections"]:
        original_audio = (base / section["speech"]["file"]).resolve()
        target = folder / "audio" / (section["id"] + ".wav")
        target.parent.mkdir(exist_ok=True)
        shutil.copy2(original_audio, target)
        section["speech"]["file"] = str(target)
        if section["speech"].get("measurement_file"):
            original = (base / section["speech"]["measurement_file"]).resolve()
            target = folder / "audio" / (section["id"] + "_measurement.json")
            shutil.copy2(original, target)
            section["speech"]["measurement_file"] = str(target)
        if frozen["sound_design"] == "voice_only" and section["sfx_cues"]:
            raise ValueError("voice_only plan contains SFX cues; decide sound policy explicitly")
        section["sfx_cues"] = prepare_cues(section["sfx_cues"], base, allow_legacy=False)
        for cue in section["sfx_cues"]:
            source = Path(cue["file"])
            target = folder / "audio_assets" / (sha256(source)[:16] + source.suffix)
            target.parent.mkdir(exist_ok=True)
            shutil.copy2(source, target)
            cue["file"] = str(target)
        for shot in section["shots"]:
            if shot["renderer"] == "manim":
                source = (base / shot["source"]).resolve()
                target = folder / (section["id"] + "__" + shot["id"] + ".py")
                shutil.copy2(source, target)
                shot["source"] = str(target)
            else:
                snapshot_browser_project(shot["render_spec"], base, folder, snapshots)
    validate_files(frozen, folder)
    write(folder / "plan.json", frozen)
    write(folder / "speech_timing.json", {s["id"]: s["speech"] for s in frozen["sections"]})
    files = {}
    import os
    for directory, dirs, names in os.walk(folder):
        dirs[:] = [d for d in dirs if d not in {"node_modules", ".git", ".cache"}]
        for name in names:
            path = Path(directory) / name
            files[path.relative_to(folder).as_posix()] = sha256(path)
    write(folder / "source_manifest.json", {"files": files, "plan_sha256": digest(frozen),
          "dependency_note": "Browser dependencies use the installed project node_modules; source snapshots are frozen."})
    return frozen


def run_v4(plan, args, snapshot_browser_project):
    if plan.get("profile") != "horror-v4.1" and not plan.get("technical_fixture"):
        raise ValueError("This workspace runs horror-v4.1 only; use the original workspace for V4")
    base = args.plan.resolve().parent
    validate_files(plan, base)
    if args.validate_only:
        print(json.dumps({"contract": "v4", "valid": True, "phase": plan["phase"],
                          "renderable": plan["phase"] == "authored",
                          "quality": "UNVERIFIED; validation is not visual/listening review"}, indent=2))
        return
    if args.prepare_only and plan["phase"] != "draft":
        raise ValueError("--prepare-only takes a draft; measured audio is reused for authored renders")
    if not args.prepare_only and plan["phase"] != "authored":
        raise ValueError("Prepare narration, author shot frames/source against timed_plan.json, then set phase=authored")
    if args.no_tts and not plan.get("technical_fixture"):
        raise ValueError("V4 production always uses the measured narration; --no-tts is for technical fixtures only")
    if args.no_tts and plan.get("music"):
        raise ValueError("A music bed needs a production narration mix")
    preview = getattr(args, "preview_shot", None)
    from v4_excerpt import excerpt_scope
    excerpt = excerpt_scope(plan)
    if excerpt and not preview:
        raise ValueError('Candidate excerpt is preview-only; production rendering requires the unchanged full quality gates')
    from v4_workflow import check_representative, representative_fingerprint
    if not args.prepare_only:
        if preview:
            if preview != plan.get("production_packet", {}).get("representative", {}).get("shot_id"):
                raise ValueError("Preview must use the packet's selected representative shot")
        else:
            check_representative(plan, base)
    fingerprint = representative_fingerprint(plan, base) if preview else None
    root = args.output_root.resolve() if args.output_root else get_output_root()
    import re
    topic = re.sub(r"[^\w-]+", "_", plan["topic"]).strip("_")[:100] or "topic"
    folder = root / topic / "runs" / ("V4_1_Horror_" + uuid.uuid4().hex[:8])
    folder.mkdir(parents=True)
    if args.prepare_only:
        if args.no_tts:
            raise ValueError("Cannot measure speech with --no-tts")
        # Resolve/audit all selected references before starting any model.
        for section in plan["sections"]:
            configuration_identity(plan, section)
        from gpu_lifecycle import audio_stage
        with audio_stage("voice", folder):
            prepare(plan, folder, args)
        print(json.dumps({"timed_plan": str(folder / "timed_plan.json"), "next": "Author shots on these recording anchors; no automatic shot quota."}, indent=2))
        return
    frozen = freeze(plan, base, folder, snapshot_browser_project)
    film_audio = None
    if not args.no_tts:
        from horror_audio import film_mix
        film_audio = film_mix(frozen, folder, include_music=not preview)
    clips, ledger, global_start = [], [], 0
    for section in frozen["sections"]:
        if preview and not excerpt and not any(s["id"] == preview for s in section["shots"]):
            continue
        section_obj = SimpleNamespace(**section, production_contract=section, production_plan=frozen)
        selected_shots = [s for s in section["shots"] if not preview or excerpt or s["id"] == preview]
        if excerpt:
            # Same renderer/shot contracts and original voice receipt; no remeasurement or stretching.
            video = render_authored_section(section_obj, folder, plan.get('render_timeout',600), preview_frames=excerpt['end_frame'])
            clip_frames = excerpt['end_frame'] - excerpt['start_frame']
        elif preview:
            shot = selected_shots[0]
            video = render_unit(shot, folder, section["id"] + "__" + shot["id"], plan.get("render_timeout", 600),
                                timing=section["speech"], production_contract=shot_contract(section, shot, frozen))
            clip_frames = shot["duration_frames"]
        else:
            video = render_authored_section(section_obj, folder, plan.get("render_timeout", 600))
            clip_frames = section["speech"]["frames"]
        if not args.no_tts:
            cut_audio = folder / "audio" / (section["id"] + "_selected_mix.wav")
            start_frame = section["film_start_frame"] + (excerpt['start_frame'] if excerpt else shot["start_frame"] if preview else 0)
            end_frame = start_frame + clip_frames
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(film_audio), "-af",
                f"atrim=start_sample={start_frame*800}:end_sample={end_frame*800},asetpts=PTS-STARTPTS", "-ar", "48000", str(cut_audio)], check=True)
            video = attach_narration(video, cut_audio, folder / (section["id"] + "_narrated.mp4"), preserve_video_duration=True)
        clips.append(video)
        for shot in selected_shots:
            output = folder / (section["id"] + "__" + shot["id"] + ".mp4")
            samples = []
            for index, frame in enumerate(shot["execution"]["review_frames"]):
                sample = folder / "qa_frames" / (shot["id"] + f"_{index}.png")
                sample.parent.mkdir(exist_ok=True)
                local_frame = frame - shot["start_frame"]
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(output),
                                "-vf", f"select=eq(n\\,{local_frame})", "-frames:v", "1", str(sample)],
                               check=True, capture_output=True)
                if not sample.is_file():
                    raise ValueError("QA frame extraction returned no image")
                samples.append({"absolute_section_frame": frame, "file": str(sample), "sha256": sha256(sample)})
            ledger.append({"section": section["id"], "shot": shot["id"], "renderer": shot["renderer"],
                "film_start_frame": section["film_start_frame"] + shot["start_frame"], "section_start_frame": shot["start_frame"],
                "beat_ids": shot["beat_ids"], "pattern": shot["pattern"], "events": shot.get("events", []),
                "b_roll": shot.get("b_roll"), "handoff": shot["handoff"], "output": str(output),
                "output_sha256": sha256(output), "samples": samples,
                "runtime_observations": str(folder / (section["id"] + "__" + shot["id"] + "_observations.json")),
                "runtime_observations_sha256": sha256(folder / (section["id"] + "__" + shot["id"] + "_observations.json")),
                "duration_frames": shot["duration_frames"],
                "execution_status": "RENDERED; semantic/visual effectiveness needs review"})
        global_start += clip_frames
    listing = folder / "sections.txt"
    listing.write_text("".join("file '" + Path(p).as_posix().replace("'", "'\\''") + "'\n" for p in clips), encoding="utf-8")
    output = folder / "final.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
                    "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "60",
                    "-frames:v", str(global_start), "-c:a", "aac", "-ar", "48000", "-ac", "2",
                    "-movflags", "+faststart", str(output)], check=True)
    technical = probe_video(output)
    if int(technical.get("nb_frames", 0)) != global_start:
        raise ValueError("Final frame count differs from measured section timeline")
    manifest = {"schema_version": 4, "llm_api_calls": 0, "scope": "candidate_excerpt" if excerpt else "representative" if preview else "production",
          "representative_fingerprint": fingerprint,
          "plan_sha256": digest(frozen), "video": str(output), "video_sha256": sha256(output), "shots": ledger}
    write(folder / "execution_manifest.json", manifest)
    from v4_quality import review_template, review_targets
    write(folder / "review_template.json", review_template(frozen, manifest))
    gates = {name: {"status": "UNVERIFIED", "notes": "Inspect current output and attach review evidence."}
             for name in ("visual", "scientific", "motion", "vfx", "editorial", "layout", "listening")}
    gates["technical"] = {"status": "PASS", "evidence": technical}
    write(folder / "quality_report.json", {"release_status": "REVIEW_REQUIRED", "gates": gates,
          "required_targets": review_targets(frozen, manifest),
          "video_sha256": sha256(output), "plan_sha256": digest(frozen), "technical_fixture": bool(plan.get("technical_fixture"))})
    print(json.dumps({"video": str(output), "execution_manifest": str(folder / "execution_manifest.json"),
                      "quality_report": str(folder / "quality_report.json"), "release_status": "REVIEW_REQUIRED",
                      "llm_api_calls": 0}, indent=2))
