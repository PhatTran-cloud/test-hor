"""Authored-shot adapters: Manim, React/SVG Remotion, and lowbudget3d Three.js.

Remotion is also the frame/export host for a Three.js composition. It does not
replace the lowbudget3d scene, camera, asset, material, or QA authority.
"""
import json
import os
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

from v3_contract import validate_render_unit


def probe_video(path):
    result = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,avg_frame_rate,nb_frames:format=duration",
        "-of", "json", str(path)], capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    stream = data["streams"][0]
    if (stream["width"], stream["height"]) != (1920, 1080) or any(Fraction(stream[k]) != 60 for k in ("r_frame_rate", "avg_frame_rate")):
        raise ValueError(f"Renderer output is not 1080p60: {path}")
    return {**stream, "duration": float(data["format"]["duration"])}


def _run(cmd, cwd, log, timeout, env=None):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, encoding="utf-8", errors="replace", timeout=timeout, env=env)
    log.write_text(result.stdout + "\n" + result.stderr, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(f"Renderer failed; inspect {log}")


def render_unit(unit, output_dir, name, timeout=600, timing=None, production_contract=None):
    renderer = validate_render_unit(unit)
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"{name}.mp4"
    render_env = None
    if production_contract:
        from v4_contract import digest
        production_contract = {**production_contract, "contract_sha256": digest(production_contract)}
        contract_file = output_dir / f"{name}_contract.json"
        contract_file.write_text(json.dumps(production_contract, indent=2), encoding="utf-8")
        render_env = {**os.environ, "CODE2VIDEO_SHOT_CONTRACT": str(contract_file),
                      "PYTHONPATH": str(Path(__file__).parent) + os.pathsep + os.environ.get("PYTHONPATH", "")}
    if renderer == "manim":
        source = Path(unit["source"]).resolve()
        scene = unit.get("scene_name", "Section1Scene")
        media = output_dir / f"media_{name}"
        _run([sys.executable, "-m", "manim", "-qh", str(source), scene,
              "--resolution", "1920,1080", "--fps", "60", "--media_dir", str(media)],
             source.parent, output_dir / f"{name}_render.log", timeout, env=render_env)
        rendered = media / "videos" / source.stem / "1080p60" / f"{scene}.mp4"
        if not rendered.exists():
            raise FileNotFoundError(rendered)
        shutil.copy2(rendered, output)
    else:
        spec = unit["render_spec"]
        project = Path(spec["project_dir"]).resolve()
        cli = project / "node_modules" / "@remotion" / "cli" / "remotion-cli.js"
        if not cli.exists():
            raise RuntimeError(f"Run npm ci in the authored renderer project: {project}")
        props = {**spec.get("props", {}), "speechTiming": timing or {},
                 "vfxEvents": unit.get("vfx_events", []), "width": 1920, "height": 1080, "fps": 60}
        if production_contract:
            props["productionContract"] = production_contract
        if unit.get("duration_frames"):
            props["durationInFrames"] = unit["duration_frames"]
        elif timing:
            props["durationInFrames"] = timing["frames"]
        props_path = output_dir / f"{name}_props.json"
        props_path.write_text(json.dumps(props, indent=2), encoding="utf-8")
        node = shutil.which("node")
        if not node:
            raise RuntimeError("Node.js is required for Remotion/Three.js export")
        if production_contract:
            _run([node, str(Path(__file__).resolve().parents[1] / "local_tools" / "render_v4_browser.cjs"),
                  str(project), spec["entry_point"], spec["composition_id"], str(props_path), str(output)],
                 project, output_dir / f"{name}_render.log", timeout)
        else:
            _run([node, str(cli), "render", str(project / spec["entry_point"]), spec["composition_id"], str(output),
                  "--props", str(props_path), "--codec", "h264", "--pixel-format", "yuv420p",
                  "--muted", "--concurrency", "2", "--gl", "angle"],
                 project, output_dir / f"{name}_render.log", timeout)
    if production_contract and "shot" in production_contract:
        from v4_execution import validate_runtime_samples
        samples = validate_runtime_samples(production_contract, (output_dir / f"{name}_render.log").read_text(encoding="utf-8"))
        (output_dir / f"{name}_observations.json").write_text(json.dumps({"status": "OBSERVED", "samples": samples,
            "limitation": "Measured/runtime-reported objects and binding; effectiveness and fidelity need review."}, indent=2), encoding="utf-8")
    technical = probe_video(output)
    expected = unit.get("duration_frames") or (timing or {}).get("frames")
    if production_contract and expected and int(technical.get("nb_frames", 0)) != expected:
        raise ValueError(f"{name}: V4 requires exact authored frame count")
    if expected and abs(technical["duration"] * 60 - expected) > 1.1:
        raise ValueError(f"{name}: renderer duration differs from narration/shot timing")
    (output_dir / f"{name}_qa.json").write_text(json.dumps({"renderer": renderer,
        "technical": technical, "technical_status": "PASS", "visual_status": "UNVERIFIED",
        "scientific_status": "UNVERIFIED", "vfx_status": "UNVERIFIED"}, indent=2), encoding="utf-8")
    return str(output)


def render_authored_section(section, output_dir, timeout=600, preview_frames=None):
    output_dir = Path(output_dir)
    timings_path = output_dir / "speech_timing.json"
    timing = json.loads(timings_path.read_text(encoding="utf-8")).get(section.id) if timings_path.exists() else None
    if not section.shots:
        unit = {"renderer": section.renderer, "scene_type": section.scene_type,
                "render_spec": section.render_spec, "three_contract": section.three_contract,
                "vfx_events": section.vfx_events}
        return render_unit(unit, output_dir, section.id, timeout, timing)
    # Explicit candidate preview clips keep the complete speech receipt frozen.
    # Only their visual assembly uses the authorized shorter frame allocation.
    expected_frames = preview_frames if preview_frames is not None else timing["frames"] if timing else None
    if expected_frames is not None and sum(s["duration_frames"] for s in section.shots) != expected_frames:
        raise ValueError(f"{section.id}: shot frame total must equal measured speech frames ({timing['frames']})")
    production = getattr(section, "production_contract", None)
    if production:
        from v4_contract import shot_contract
    clips = [render_unit(shot, output_dir, f"{section.id}__{shot['id']}", timeout,
                         timing=timing if production else None,
                         production_contract=shot_contract(production, shot, getattr(section,'production_plan',None)) if production else None)
             for shot in section.shots]
    listing = output_dir / f"{section.id}_shots.txt"
    listing.write_text("".join("file '" + Path(clip).as_posix().replace("'", "'\\''") + "'\n" for clip in clips), encoding="utf-8")
    output = output_dir / f"{section.id}.mp4"
    # Normalize encoding across renderers; do not concat-copy incompatible streams.
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listing), "-an",
          "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "60", str(output)],
         output_dir, output_dir / f"{section.id}_shots.log", timeout)
    probe_video(output)
    return str(output)
