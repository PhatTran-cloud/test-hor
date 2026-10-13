"""Author a short adapter check using an already measured, real Kokoro passage.

This verifies production transport; it never awards artistic/listening PASS.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(Path(__file__).parent)]
from build_plan import make_plan
from v4_contract import normalize_v4

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("timed_plan", type=Path)
args = parser.parse_args()
timed = json.loads(args.timed_plan.read_text(encoding="utf-8"))
recording = timed["sections"][0]
plan = make_plan(Path(recording["speech"]["file"]))
plan.update(technical_fixture=False, topic="V4 hardened measured representative check")
section = plan["sections"][0]
for key in ("narration", "narration_segments", "speech"):
    section[key] = recording[key]
frames = section["speech"]["frames"]
if frames < 290:
    raise ValueError("This short transport fixture needs at least 290 measured frames")
for beat, start, end in zip(section["beats"], [0, 130], [130, frames]):
    beat.update(start_frame=start, end_frame=end,
                timing_reason="authored visual lead/settle within the measured recording; no audio extension")
    beat["narration_anchor"] = {"segment_id": recording["narration_segments"][0]["id"]}
for shot, start, end in zip(section["shots"], [0, 130, 230], [130, 230, frames]):
    shot.update(start_frame=start, end_frame=end, duration_frames=end-start)
    shot["execution"]["review_frames"] = [start+20, end-10]
section["shots"][1]["beat_ids"] = ["difference_beat"]
section["shots"][0]["events"][0].update(start_frame=65, peak_frame=80, end_frame=112)
section["state_tracks"][0].update(start_frame=65, end_frame=100)
plan = normalize_v4(plan)
output = args.timed_plan.parent / "authored_preview_check.json"
output.write_text(json.dumps(plan, indent=2), encoding="utf-8")
print(output)
