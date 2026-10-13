"""Record reviews or enforce release readiness; does not invent visual judgments."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from v4_quality import apply_review, release_check

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("--review", type=Path)
group.add_argument("--release-check", action="store_true")
args = parser.parse_args()
report = release_check(args.run) if args.release_check else apply_review(args.run, json.loads(args.review.read_text(encoding="utf-8")))
print(json.dumps(report, ensure_ascii=False, indent=2))
