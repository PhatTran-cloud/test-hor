"""Sample real local reference media at 1 Hz. No download or automatic analysis."""
import hashlib
import json
import math
from pathlib import Path
import subprocess
import tempfile
from PIL import Image, ImageDraw


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def run(command):
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode:
        raise ValueError('Reference media command failed: '+result.stderr[-1200:])
    return result.stdout


def sample_reference(source, output, source_url, start=0, seconds=180, source_offset=0):
    source, output = Path(source).resolve(), Path(output).resolve()
    if not source.is_file():
        raise ValueError('Supply a real local video file')
    if not isinstance(source_url, str) or not source_url.startswith(('https://', 'http://')):
        raise ValueError('Record the reference source URL; provenance is declared, not inferred')
    if (isinstance(seconds, bool) or not isinstance(seconds, int) or seconds <= 0
            or any(isinstance(n, bool) or not isinstance(n, (int, float)) or not math.isfinite(n) or n < 0 for n in (start, source_offset))):
        raise ValueError('Sample duration is positive whole seconds; start/offset are finite nonnegative seconds')
    if output.exists():
        raise ValueError('Use a new sample directory; preserve previous research evidence')
    info = json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(source)]))
    stream = next((s for s in info.get('streams', []) if s.get('codec_type') == 'video' and not s.get('disposition', {}).get('attached_pic')), None)
    duration = float(info.get('format', {}).get('duration', 0))
    if not stream or duration < start+seconds-0.001:
        raise ValueError('Real decoded video must cover the entire requested sample window')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='reference-sample-', dir=output.parent) as temp:
        folder = Path(temp); (folder/'frames').mkdir(); (folder/'sheets').mkdir()
        command = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-ss', str(start), '-i', str(source),
            '-map', '0:'+str(stream['index']), '-an', '-t', str(seconds), '-vf', 'fps=fps=1:start_time=0:round=up',
            '-frames:v', str(seconds), '-q:v', '2', '-start_number', '0', str(folder/'frames/%06d.jpg')]
        run(command)
        frames = sorted((folder/'frames').glob('*.jpg'))
        if len(frames) != seconds:
            raise ValueError(f'Expected {seconds} real sampled images, got {len(frames)}; do not fill gaps with copies')
        rows = []
        for index, frame in enumerate(frames):
            with Image.open(frame) as im: size = list(im.size)
            rows.append({'index':index, 'file':frame.relative_to(folder).as_posix(), 'sha256':sha256(frame),
                'nominal_file_seconds':start+index, 'nominal_source_seconds':source_offset+start+index, 'size':size})
        sheets = []
        for page in range(math.ceil(seconds/20)):
            subset = rows[page*20:(page+1)*20]
            sheet = Image.new('RGB', (1280, 5*208), '#1a1c21'); draw = ImageDraw.Draw(sheet)
            for tile, row in enumerate(subset):
                x, y = (tile%4)*320, (tile//4)*208
                with Image.open(folder/row['file']) as im:
                    im.thumbnail((320,180)); sheet.paste(im, (x+(320-im.width)//2, y))
                draw.text((x+6, y+184), f"{row['index']:03d} | source {row['nominal_source_seconds']:07.2f}s", fill='white')
            path = folder/f'sheets/{page:03d}.jpg'; sheet.save(path, quality=92)
            sheets.append({'file':path.relative_to(folder).as_posix(), 'sha256':sha256(path),
                'first_index':subset[0]['index'], 'last_index':subset[-1]['index']})
        manifest = {'schema_version':1, 'kind':'reference_1hz_sample', 'status':'SAMPLED_NOT_INSPECTED',
            'source':{'filename':source.name, 'sha256':sha256(source), 'url':source_url,
                'url_identity_status':'DECLARED_NOT_PROVEN_BY_FILE_HASH', 'duration_seconds':duration,
                'width':stream['width'], 'height':stream['height'], 'source_frame_rate':stream.get('avg_frame_rate'),
                'source_offset_seconds':source_offset},
            'window':{'file_start_seconds':start, 'duration_seconds':seconds, 'sample_rate_hz':1,
                'source_start_seconds':source_offset+start, 'source_end_seconds_exclusive':source_offset+start+seconds},
            'timestamp_precision':'Nominal one-second grid, FFmpeg fps round=up selects at or before each grid point; source-frame quantization applies. Not exact source PTS or frame-accurate cut times.',
            'tools':{'ffmpeg':run(['ffmpeg','-version']).splitlines()[0], 'ffprobe':run(['ffprobe','-version']).splitlines()[0]},
            'sampling_arguments':command[1:-1]+['frames/%06d.jpg'], 'frames':rows, 'contact_sheets':sheets,
            'audio_inspection':'NOT_PERFORMED', 'limitations':['Cuts/actions between sample points may be missed.',
                'Hashes/counts prove stored samples, not identity, full inspection or aesthetic quality.']}
        (folder/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
        annotation = {'schema_version':1, 'sample_manifest_sha256':sha256(folder/'manifest.json'),
            'reviewer':None, 'inspected_indices':[], 'sample_groups':[], 'notes':[],
            'instruction':'Inspect every frame/contact sheet. Group observed sampled views; boundary times remain uncertain by up to one second and brief cuts can be absent. Describe composition, background information, cast/props, camera and the visual link. Do not infer audio without listening.'}
        (folder/'annotations.json').write_text(json.dumps(annotation, indent=2)+'\n', encoding='utf-8')
        Path(temp).rename(output)
    return manifest


def check_reference(folder, annotations=None):
    folder = Path(folder).resolve()
    manifest_path = folder/'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if manifest.get('kind') != 'reference_1hz_sample' or manifest.get('schema_version') != 1:
        raise ValueError('Unknown reference sample format')
    count = manifest['window']['duration_seconds']; frames = manifest['frames']
    if (manifest['window']['sample_rate_hz'] != 1 or isinstance(count, bool) or not isinstance(count, int)
            or count <= 0 or [r.get('index') for r in frames] != list(range(count))):
        raise ValueError('One real indexed sample is required per second')
    for row in frames+manifest['contact_sheets']:
        path = (folder/row['file']).resolve()
        if not path.is_relative_to(folder) or sha256(path) != row['sha256']:
            raise ValueError('Reference sample evidence missing, changed or outside its directory')
    for index, row in enumerate(frames):
        expected = manifest['window']['source_start_seconds']+index
        if row.get('nominal_source_seconds') != expected:
            raise ValueError('Reference sample timestamps do not match the nominal one-second grid')
        with Image.open(folder/row['file']) as im:
            if list(im.size) != row['size']:
                raise ValueError('Reference frame dimensions changed')
    note = json.loads(Path(annotations or folder/'annotations.json').read_text(encoding='utf-8'))
    if note.get('sample_manifest_sha256') != sha256(manifest_path):
        raise ValueError('Annotations belong to a different sampling manifest')
    inspected = note.get('inspected_indices', [])
    if (not isinstance(inspected, list) or any(isinstance(i,bool) or not isinstance(i,int) or not 0 <= i < count for i in inspected)
            or len(set(inspected)) != len(inspected)):
        raise ValueError('Inspected indices must be unique real sample indices')
    groups = note.get('sample_groups', []); covered = set(); seen = set()
    if not isinstance(groups, list):
        raise ValueError('Sample groups must be a list')
    for group in groups:
        gid = group.get('id'); first = group.get('first_index'); last = group.get('last_index')
        if (not isinstance(gid,str) or not gid.strip() or gid in seen or any(isinstance(i,bool) or not isinstance(i,int) for i in (first,last))
                or not 0 <= first <= last < count):
            raise ValueError('Observed sample group needs a unique ID and valid inclusive indices')
        current = set(range(first,last+1))
        if current & covered or not current <= set(inspected):
            raise ValueError('Observed groups may not overlap or cite uninspected samples')
        for key in ('scene_id','composition','background_information','cast_and_props','camera','next_visual_link'):
            if not isinstance(group.get(key),str) or not group[key].strip():
                raise ValueError('Observed sample group needs '+key+'; unknown/not visible is valid when stated')
        seen.add(gid); covered |= current
    complete = bool(note.get('reviewer')) and set(inspected) == set(range(count)) and covered == set(range(count))
    return {'sampling':'HASHED_1HZ_SAMPLES_VALID', 'sample_count':count, 'inspected_count':len(inspected),
        'annotation_coverage_count':len(covered), 'inspection':'REVIEW_RECORDED_NOT_INDEPENDENTLY_VERIFIED' if complete else 'INCOMPLETE',
        'audio_inspection':manifest['audio_inspection'],
        'limitation':'Annotations are human/agent declarations. This checker verifies structure and hashes, not a channel storyboard standard or actual fear/acting quality.'}
