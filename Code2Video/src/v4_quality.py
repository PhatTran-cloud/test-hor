"""Scoped review evidence and build integrity; never automatic artistic approval."""
import json
import subprocess
from pathlib import Path
from v4_contract import digest, sha256

GATES = ("visual", "scientific", "motion", "vfx", "editorial", "layout", "listening")


def review_targets(plan, manifest):
    rendered = {s["shot"] for s in manifest["shots"]}
    shots = [s for sec in plan["sections"] for s in sec["shots"] if s["id"] in rendered]
    ids = {"shot:" + s["id"] for s in shots}
    beats = {"beat:" + b for s in shots for b in s["beat_ids"]}
    vfx = {"event:" + e["id"] for sec in plan["sections"] for s in sec["shots"] for e in s.get("events", [])
           if e["kind"] == "vfx" and (s["id"] in rendered or any(e["id"] in sh.get("event_ids", []) for sh in shots))}
    facts = {"claim:" + c["id"] for c in plan.get("production_packet", {}).get("research", {}).get("claims", []) if c["kind"] == "fact"}
    science = facts | {"shot:" + s["id"] for s in shots if s.get("scientific_contract") or s["pattern"]["kind"] in {"map", "evidence"}}
    if any(sec.get("scientific_contract") for sec in plan["sections"]):
        science |= ids
    return {"visual": sorted(ids), "layout": sorted(ids), "motion": sorted(ids),
            "editorial": sorted(ids | beats | {"boundary:" + s["id"] for s in shots}),
            "vfx": sorted(vfx), "scientific": sorted(science),
            "listening": [] if plan.get("technical_fixture") else ["film_mix"]}


def _inside(folder, path):
    result = (folder / path).resolve()
    if not result.is_relative_to(folder):
        raise ValueError("Evidence path leaves this frozen run")
    return result


def integrity(folder):
    folder = Path(folder).resolve()
    def read(name):
        return json.loads((folder / name).read_text(encoding="utf-8"))
    report, manifest, plan, source = [read(n) for n in ("quality_report.json", "execution_manifest.json", "plan.json", "source_manifest.json")]
    if manifest.get("plan_sha256") != digest(plan) or report.get("plan_sha256") != digest(plan):
        raise ValueError("Frozen plan changed")
    video = _inside(folder, manifest["video"])
    if sha256(video) != manifest.get("video_sha256") or sha256(video) != report.get("video_sha256"):
        raise ValueError("Rendered video changed")
    if not source.get("files") or source.get("plan_sha256") != digest(plan):
        raise ValueError("Missing/stale source manifest")
    for relative, expected in source["files"].items():
        if sha256(_inside(folder, relative)) != expected:
            raise ValueError("Frozen source changed")
    for shot in manifest["shots"]:
        if sha256(_inside(folder, shot["output"])) != shot["output_sha256"]:
            raise ValueError("Shot output changed")
        if shot.get("runtime_observations") and sha256(_inside(folder, shot["runtime_observations"])) != shot.get("runtime_observations_sha256"):
            raise ValueError("Runtime observation evidence changed")
        for sample in shot.get("samples", []):
            if sha256(_inside(folder, sample["file"])) != sample["sha256"]:
                raise ValueError("QA frame changed")
    if set(report.get("gates", {})) != set(GATES) | {"technical"}:
        raise ValueError("Every independent quality gate must remain present")
    if bool(report.get("technical_fixture")) != bool(plan.get("technical_fixture")):
        raise ValueError("Cannot relabel a technical fixture as production")
    return folder, report, manifest, plan


def apply_review(folder, review, persist=True):
    folder, report, manifest, plan = integrity(folder)
    if review.get("video_sha256") != report["video_sha256"] or review.get("plan_sha256") != report["plan_sha256"]:
        raise ValueError("Review belongs to another build")
    if not review.get("reviewer"):
        raise ValueError("Review needs a named reviewer")
    targets = review_targets(plan, manifest)
    suffixes = {"frame": {".png", ".jpg", ".jpeg", ".webp"}, "clip": {".mp4", ".mov", ".mkv"},
                "audio": {".wav", ".mp3", ".flac", ".mp4"}, "measurement": {".json"}}
    for name, gate in review.get("gates", {}).items():
        if name not in GATES or gate.get("status") not in {"PASS", "FAIL", "PARTIAL", "UNVERIFIED", "NOT_APPLICABLE"} or not gate.get("notes"):
            raise ValueError("Unknown gate/status or missing observations")
        evidence = gate.get("evidence", [])
        if gate["status"] in {"PASS", "PARTIAL", "FAIL"} and not evidence:
            raise ValueError("Conclusions require evidence")
        if len({e.get("id") for e in evidence}) != len(evidence):
            raise ValueError("Evidence IDs must be unique")
        for item in evidence:
            path = _inside(folder, item["file"])
            if not item.get("id") or item.get("kind") not in suffixes or path.suffix.lower() not in suffixes[item["kind"]]:
                raise ValueError("Evidence needs ID and correct frame/clip/audio/measurement type")
            if sha256(path) != item["sha256"]:
                raise ValueError("Evidence changed")
        if gate["status"] == "NOT_APPLICABLE" and (targets[name] or name not in {"scientific", "vfx", "listening"}):
            raise ValueError(f"Cannot waive required {name} review")
        if gate["status"] == "PASS":
            observations = gate.get("observations", [])
            if not observations or {o.get("target") for o in observations} != set(targets[name]):
                raise ValueError(f"{name} PASS needs observations covering {targets[name]}")
            for observation in observations:
                if not observation.get("expected") or not observation.get("observed") or not observation.get("evidence_ids"):
                    raise ValueError("Observation needs expected/observed behavior and evidence references")
                if not set(observation["evidence_ids"]) <= {e["id"] for e in evidence}:
                    raise ValueError("Observation references absent evidence")
                items = [e for e in evidence if e["id"] in observation["evidence_ids"]]
                if name in {"visual", "layout"} and not any(e["kind"] in {"frame", "clip"} for e in items):
                    raise ValueError("Artwork/layout cannot pass from source JSON or measurements alone")
                if name in {"motion", "editorial", "vfx"} and not any(e["kind"] == "clip" for e in items):
                    raise ValueError("Temporal quality cannot pass from stills/source JSON")
                if name == "listening":
                    if not any(e["kind"] in {"clip", "audio"} and e.get("method") == "listened" and _inside(folder, e["file"]) == _inside(folder, manifest["video"]) for e in items):
                        raise ValueError("Listening PASS must refer to listening to this complete final mix")
                    data = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "json", str(_inside(folder, manifest["video"]))])
                    if not json.loads(data)["streams"]:
                        raise ValueError("Final mix has no audio stream")
        report["gates"][name] = {**gate, "reviewer": gate.get("reviewer", review["reviewer"])}
    report["required_targets"] = targets
    ready = all(report["gates"][g]["status"] in {"PASS", "NOT_APPLICABLE"} for g in GATES)
    if plan.get("technical_fixture"):
        status = "TECHNICAL_FIXTURE_ONLY"
    elif manifest.get("scope") == "candidate_excerpt":
        status = "REVIEW_REQUIRED"
    elif manifest.get("scope") == "representative":
        status = "REPRESENTATIVE_REVIEWED" if all(report["gates"][g]["status"] == "PASS" for g in ("visual", "layout", "motion", "editorial")) else "REVIEW_REQUIRED"
    else:
        status = "READY" if ready and report["gates"]["technical"]["status"] == "PASS" else "REVIEW_REQUIRED"
    report["release_status"] = status
    if persist:
        (folder / "quality_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def release_check(folder):
    folder, report, manifest, plan = integrity(folder)
    if plan.get("technical_fixture") or manifest.get("scope") != "production":
        raise ValueError("Previews and technical fixtures cannot be released as production")
    from renderers import probe_video
    metadata = probe_video(manifest["video"])
    if int(metadata.get("nb_frames", 0)) != sum(s["speech"]["frames"] for s in plan["sections"]):
        raise ValueError("Release requires the complete current production, not a preview")
    checked = apply_review(folder, {"reviewer": "consistency check", "video_sha256": report["video_sha256"],
        "plan_sha256": report["plan_sha256"], "gates": {k: v for k, v in report["gates"].items() if k in GATES}}, persist=False)
    if checked["release_status"] != "READY":
        raise ValueError("Release requires all independent reviews on a production build")
    return checked


def review_template(plan, manifest):
    return {"reviewer": "", "video_sha256": manifest["video_sha256"], "plan_sha256": manifest["plan_sha256"],
        "gates": {name: {"status": "UNVERIFIED", "notes": "", "evidence": [],
            "observations": [{"target": t, "expected": "", "observed": "", "evidence_ids": []} for t in ids]}
            for name, ids in review_targets(plan, manifest).items()}}
