"""Shared output location for topic runs and production artifacts."""
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def get_output_root():
    """Use the shared output folder beside Code2Video (D:/manim/outputs here)."""
    configured = os.environ.get("CODE2VIDEO_OUTPUT_ROOT", "").strip()
    return (Path(configured).expanduser() if configured else
            REPO_ROOT.parent / "outputs").resolve()
