"""One production packet and explicit stage boundaries for current-session work."""
import copy
from pathlib import Path

from v4_contract import digest, require, sha256, unique


def skill_routes(plan):
    shots = [s for section in plan["sections"] for s in section["shots"]]
    skills = {"script-to-visual-director", "storyboard-motion-executor", "cinematic-motion-director"}
    renderers = {s["renderer"] for s in shots}
    if "manim" in renderers:
        skills.add("manimce-best-practices")
    if renderers & {"remotion", "threejs"}:
        skills.add("remotion-best-practices")
    if "threejs" in renderers or any(s.get("scene_type") == "3d" for s in shots):
        skills.update({"lowbudget3d", "3dviz-pro-max"})
    if any(e.get("kind") == "vfx" for s in shots for e in s.get("events", [])):
        skills.add("cinematic-vfx-director")
    if plan.get("content_profile", {}).get("genre") == "horror" and renderers & {"remotion", "threejs"}:
        skills.add("remotion-horror-vfx")
    if plan.get("profile") == "horror-v4.1":
        skills.update({"horror-asset-director", "horror-audio-director", "cinematic-vfx-director"})
        characters=plan.get('production_packet',{}).get('character_direction',{})
        if characters.get('characters') or characters.get('crowd_groups'):
            skills.add('horror-cartoon-storyboard')
    if any(a.get('kind') == 'model_3d' for a in plan.get('horror',{}).get('assets',[])):
        skills.update({'lowbudget3d','3dviz-pro-max','lowbudget3d-illustration-bridge'})
    return sorted(skills)


def validate_packet(plan):
    if plan.get("technical_fixture"):
        return
    require(plan, ("production_packet",), "V4 production (see START_HERE.md)")
    packet = plan["production_packet"]
    require(packet, ("brief", "research", "representative"), "production_packet")
    require(packet["brief"], ("audience", "question", "takeaway", "visual_thesis"), "brief")
    research = packet["research"]
    require(research, ("sources", "claims"), "research")
    source_ids = unique(research["sources"], "research sources")
    for source in research["sources"]:
        require(source, ("title", "url", "finding", "visual_decision"), "Research source")
    unique(research["claims"], "claims")
    for claim in research["claims"]:
        require(claim, ("text", "kind", "visual_treatment"), "claim")
        if claim["kind"] not in {"fact", "illustration", "metaphor", "fiction"}:
            raise ValueError("Claim kind must distinguish fact from illustration/metaphor/fiction")
        if claim["kind"] == "fact" and (not claim.get("source_ids") or not set(claim["source_ids"]) <= source_ids):
            raise ValueError("Factual claims need known research source IDs")
    representative = packet["representative"]
    require(representative, ("shot_id", "reason", "acceptance"), "representative shot")
    if representative["shot_id"] not in {s["id"] for section in plan["sections"] for s in section["shots"]}:
        raise ValueError("Representative shot does not exist")
    if plan["phase"] == "authored":
        consulted = packet.get("consulted_resources", [])
        require(packet, ("consulted_resources",), "Authored packet")
        for resource in consulted:
            require(resource, ("skill", "file", "sha256", "applied_to", "decision"), "Consulted skill resource")
            if not isinstance(resource["applied_to"], list) or not set(resource["applied_to"]) <= {s["id"] for sec in plan["sections"] for s in sec["shots"]}:
                raise ValueError("Consulted skill decisions must reference actual shot IDs")
        missing = set(skill_routes(plan)) - {r["skill"] for r in consulted}
        if missing:
            raise ValueError("Missing applicable skill research: " + ", ".join(sorted(missing)))
        if "3dviz-pro-max" in skill_routes(plan):
            if not any(r["skill"] == "3dviz-pro-max" and r.get("resource_name", Path(r["file"]).name) != "SKILL.md" for r in consulted):
                raise ValueError("Full 3D workflow needs relevant base references, not only the SKILL.md name")


def check_resources(plan):
    for resource in plan.get("production_packet", {}).get("consulted_resources", []):
        if sha256(resource["file"]) != resource["sha256"]:
            raise ValueError("Consulted skill changed; refresh the authoring decision against the current resource")


def representative_fingerprint(plan, base):
    """Bind a representative approval to its actual source/timing/style, not run ID."""
    shot_id = plan["production_packet"]["representative"]["shot_id"]
    section = next(s for s in plan["sections"] if any(sh["id"] == shot_id for sh in s["shots"]))
    shot = next(sh for sh in section["shots"] if sh["id"] == shot_id)
    from v4_contract import shot_contract
    contract = shot_contract(section, shot, plan)
    shot_data = copy.deepcopy(contract["shot"])
    if shot["renderer"] == "manim":
        source = Path(base) / shot["source"]
        files = [("shot_source", sha256(source))]
        shot_data.pop("source")
        for relative in plan.get("support_files", []) + plan.get("asset_files", []):
            asset_base = plan.get("asset_base_dir", base) if relative in plan.get("asset_files", []) else base
            files.append((Path(relative).name, sha256(Path(asset_base) / relative)))
    else:
        project = Path(base) / shot["render_spec"]["project_dir"]
        # Include source, public assets and lockfiles. Avoid traversing dependencies.
        import os
        files = []
        for directory, dirs, names in os.walk(project):
            dirs[:] = [d for d in dirs if d not in {"node_modules", ".git", "out", "dist", "build", ".cache"}]
            for name in names:
                if name.startswith(".env") or name.endswith((".key", ".log")):
                    continue
                path = Path(directory) / name
                files.append((path.relative_to(project).as_posix(), sha256(path)))
        shot_data["render_spec"].pop("project_dir")
    contract["shot"] = shot_data
    contract["speech"] = {k: v for k, v in contract["speech"].items() if k not in {"file", "measurement_file"}}
    return digest({"contract": contract, "visual_system": plan["visual_system"],
                   "reference_policy": plan["visual_reference_policy"], "files": sorted(files),
                   "acceptance": plan["production_packet"]["representative"]["acceptance"]})


def check_representative(plan, base):
    if plan.get('preview_scope'):
        raise ValueError('A candidate excerpt cannot substitute for a representative approval')
    if plan.get("technical_fixture"):
        return
    review = plan["production_packet"]["representative"].get("review")
    if not review:
        raise ValueError("Render/review the representative shot with production.py preview before a full render")
    import json
    from v4_quality import apply_review
    run = Path(review["run_dir"])
    manifest = json.loads((run / "execution_manifest.json").read_text(encoding="utf-8"))
    if manifest.get("scope") != "representative" or manifest.get("representative_fingerprint") != representative_fingerprint(plan, base):
        raise ValueError("Representative sources/timing/style changed; preview/review it again")
    report = json.loads((run / "quality_report.json").read_text(encoding="utf-8"))
    checked = apply_review(run, {"reviewer": "representative consistency check",
        "video_sha256": report["video_sha256"], "plan_sha256": report["plan_sha256"],
        "gates": {k: v for k, v in report["gates"].items() if k != "technical"}}, persist=False)
    if checked.get("technical_fixture"):
        raise ValueError("A technical fixture cannot stand in for production art review")
    if not all(checked["gates"][g]["status"] == "PASS" for g in ("visual", "layout", "motion", "editorial")):
        raise ValueError("Representative visual/layout/motion/editorial reviews must pass before multiplying its style")
