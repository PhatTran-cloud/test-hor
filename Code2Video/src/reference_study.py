"""Local 1 Hz reference sampling. Extraction never implies visual review."""
import csv
import hashlib
import json
import math
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw


def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def _seconds(value, name, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f'{name} must be a finite number')
    if not math.isfinite(value) or value < 0 or (positive and value <= 0):
        raise ValueError(f'{name} must be finite and nonnegative (duration positive)')
    return value


def _probe(path):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_format', '-show_streams',
                             '-of', 'json', str(path)], capture_output=True, text=True, check=True)
    info = json.loads(result.stdout)
    if not any(s.get('codec_type') == 'video' for s in info['streams']):
        raise ValueError(f'No video stream: {path.name}')
    duration = float(info['format'].get('duration', 0))
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError(f'No finite video duration: {path.name}')
    return duration


def _sheets(folder, frames):
    sheets = []
    for start in range(0, len(frames), 30):
        batch = frames[start:start + 30]
        columns = min(5, len(batch))
        sheet = Image.new('RGB', (columns * 320, math.ceil(len(batch) / columns) * 204), '#17191e')
        draw = ImageDraw.Draw(sheet)
        for i, frame in enumerate(batch):
            x, y = (i % columns) * 320, (i // columns) * 204
            with Image.open(folder / frame['file']) as original:
                thumb = original.convert('RGB')
                thumb.thumbnail((320, 180))
                sheet.paste(thumb, (x + (320 - thumb.width) // 2, y))
            draw.text((x + 5, y + 182), f"{frame['id']} | source {frame['source_second']:g}s", fill='white')
        name = f'sheet_{start:03d}_{start + len(batch) - 1:03d}.jpg'
        sheet.save(folder / name, quality=92)
        sheets.append({'file': name, 'sha256': file_hash(folder / name),
                       'frame_ids': [f['id'] for f in batch], 'review_status': 'UNVERIFIED'})
    return sheets


def sample_references(manifest_path, output):
    """Sample the first decoded frame at/after each requested integer second.

    video_start_second maps local time zero to the original source clock. A
    pre-cut 180s clip therefore needs start_second=0 and its original offset.
    Fail on missing intervals instead of padding/duplicating a failed download.
    """
    manifest_path, output = Path(manifest_path).resolve(), Path(output).resolve()
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if manifest.get('schema_version') != 'reference-study/1':
        raise ValueError('Expected schema_version=reference-study/1')
    if not manifest.get('videos'):
        raise ValueError('Manifest needs local videos')
    if output.exists():
        raise ValueError('Choose a new output directory; preserve earlier samples/reviews')
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        raise ValueError('Install FFmpeg and FFprobe; no image or transcript substitute is used')
    prepared, ids = [], set()
    for video in manifest['videos']:
        vid = video.get('id', '')
        if not isinstance(vid, str) or not re.fullmatch(r'[a-zA-Z0-9_-]+', vid) or vid in ids:
            raise ValueError('Use unique simple video IDs')
        ids.add(vid)
        source = (manifest_path.parent / video['file']).resolve()
        if not source.is_file():
            raise ValueError(f'Missing local video: {source.name}; provide an actual video file')
        start = _seconds(video.get('start_second', 0), 'start_second')
        duration = _seconds(video.get('duration_seconds', 180), 'duration_seconds', positive=True)
        offset = _seconds(video.get('video_start_second', 0), 'video_start_second')
        if not float(duration).is_integer():
            raise ValueError('Use an integer duration: one sample per integer second')
        width = video.get('sample_width', 960)
        if isinstance(width, bool) or not isinstance(width, int) or not 160 <= width <= 3840 or width % 2:
            raise ValueError('sample_width must be an even integer from 160 to 3840')
        available = _probe(source)
        if start + duration > available + .001:
            raise ValueError(f'{vid}: requested window exceeds actual video duration')
        prepared.append((video, source, start, int(duration), offset, width))

    output.parent.mkdir(parents=True, exist_ok=True)
    # Publish the directory only after every clip has real frames and receipts.
    with tempfile.TemporaryDirectory(prefix='reference-study-', dir=output.parent) as tmp:
        work = Path(tmp)
        result = {'schema_version': 'reference-study/1', 'sample_rate_hz': 1,
                  'interval': 'half-open; 180s means seconds 0..179, not 0..180',
                  'manifest_sha256': file_hash(manifest_path),
                  'ffmpeg_version': subprocess.run(['ffmpeg', '-version'], capture_output=True,
                                                   text=True, check=True).stdout.splitlines()[0],
                  'visual_review_status': 'UNVERIFIED', 'audio_review_status': 'UNVERIFIED', 'videos': []}
        for video, source, start, duration, offset, width in prepared:
            folder = work / video['id']
            folder.mkdir()
            vf = (f"setpts=PTS-STARTPTS,select='gte(t,{start}+selected_n)*lt(t,{start + duration})',"
                  f'scale={width}:-2:flags=lanczos,showinfo')
            command = ['ffmpeg', '-hide_banner', '-nostdin', '-i', str(source), '-map', '0:v:0',
                       '-an', '-vf', vf, '-fps_mode', 'passthrough', '-frames:v', str(duration),
                       '-q:v', '2', '-start_number', '0', str(folder / 'frame_%03d.jpg')]
            run = subprocess.run(command, capture_output=True, text=True)
            if run.returncode:
                raise ValueError(f"{video['id']}: FFmpeg failed; no study published. {run.stderr[-1500:]}")
            pts = [float(t) for t in re.findall(r'\bn:\s*\d+.*?\bpts_time:([\d.eE+-]+)', run.stderr)]
            files = sorted(folder.glob('frame_*.jpg'), key=lambda f: int(f.stem.split('_')[-1]))
            if len(files) != duration or len(pts) != duration:
                raise ValueError(f"{video['id']}: missing decoded frames; expected {duration}, got {len(files)}")
            frames = []
            for i, (file, actual) in enumerate(zip(files, pts)):
                target = start + i
                if actual < target - .0001 or actual >= target + 1:
                    raise ValueError(f"{video['id']}: no decoded frame in second {target:g}")
                with Image.open(file) as im:
                    dimensions = list(im.size)
                frames.append({'id': f"{video['id']}_{i:03d}", 'file': file.name,
                               'local_second': target, 'source_second': offset + target,
                               'decoded_source_second': offset + actual,
                               'decoded_pts_second': actual, 'sampling_delay_seconds': round(actual - target, 6),
                               'dimensions': dimensions, 'sha256': file_hash(file), 'review_status': 'UNVERIFIED'})
            sheets = _sheets(folder, frames)
            fields = ['id', 'file', 'source_second', 'decoded_source_second', 'decoded_pts_second', 'sha256', 'review_status',
                      'scene_id', 'shot_id', 'background_anchors', 'foreground', 'midground', 'background',
                      'attention', 'action', 'camera', 'knowledge_delta', 'cut_trigger', 'carried_state', 'notes']
            with (folder / 'annotations.csv').open('w', encoding='utf-8', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                for frame in frames:
                    writer.writerow({k: frame[k] for k in fields if k in frame})
            result['videos'].append({'id': video['id'], 'title': video.get('title', video['id']),
                                     'source_url': video.get('source_url'), 'file': video['file'],
                                     'source_file_sha256': file_hash(source), 'start_second': start,
                                     'video_start_second': offset, 'duration_seconds': duration,
                                     'sample_count': len(frames), 'frames': frames, 'sheets': sheets})
        result['total_samples'] = sum(v['sample_count'] for v in result['videos'])
        (work / 'study.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        work.rename(output)
    return output / 'study.json'
