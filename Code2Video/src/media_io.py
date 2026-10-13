"""Provider-independent media probing and native-frame audio mux."""
import json
import math
import subprocess
from pathlib import Path

def probe_duration(path):
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                            "-of", "default=nw=1:nk=1", str(path)],
                           capture_output=True, encoding="utf-8", errors="replace", check=True)
    duration = float(probe.stdout.strip())
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError(f"Invalid media duration: {path}")
    return duration


def attach_narration(video, audio, output, preserve_video_duration=False):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    duration = probe_duration(video)
    target = duration if preserve_video_duration else probe_duration(audio) + 0.4
    if preserve_video_duration and probe_duration(audio) > duration + .04:
        raise ValueError("Speech exceeds native scene duration; rerender from speech timing")
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                            "-show_entries", "stream=width,height,r_frame_rate", "-of", "json", str(video)],
                           capture_output=True, encoding="utf-8", errors="replace", check=True)
    stream = json.loads(probe.stdout)["streams"][0]
    if (stream["width"], stream["height"], stream["r_frame_rate"]) != (1920, 1080, "60/1"):
        raise ValueError("Narration source must be rendered at 1920x1080, 60 fps")
    # Keep the entire animation and narration. This is section alignment,
    # not word-level sync; avoid suggesting physical time is preserved.
    factor = target / duration
    video_filter = "fps=60" if preserve_video_duration else f"setpts={factor:.10f}*(PTS-STARTPTS),fps=60"
    cmd = ["ffmpeg", "-y", "-i", str(video), "-i", str(audio),
           "-vf", video_filter,
           "-af", "apad=pad_dur=0.4", "-map", "0:v:0", "-map", "1:a:0",
           "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-ar", "48000", "-ac", "2", "-t", f"{target:.6f}",
           "-movflags", "+faststart", str(output)]
    result = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace", timeout=180)
    if result.returncode:
        raise RuntimeError("Narration mux failed: " + result.stderr[-2000:])
    return str(output)
