"""An explicitly scoped supplied-asset preview, without production/release approval."""
import json
from pathlib import Path

from PIL import Image

from v4_contract import sha256


def read_sprite_spec(path):
    path = Path(path).resolve()
    spec = json.loads(path.read_text(encoding='utf-8'))
    if spec.get('schema_version') != 4 or spec.get('profile') != 'horror-v4.1':
        raise ValueError('Sprite tests retain schema 4 and horror-v4.1')
    if spec.get('scope') != 'isolated_sprite_test':
        raise ValueError('This command cannot render a film or approve a representative shot')
    if not isinstance(spec.get('duration_frames'), int) or spec['duration_frames'] <= 0:
        raise ValueError('Author a positive integer frame allocation')
    frames = spec.get('frames', [])
    if not frames:
        raise ValueError('Supply measured alpha sprite frames')
    for item in frames:
        frame_path = (path.parent / item['file']).resolve()
        if sha256(frame_path) != item['sha256']:
            raise ValueError(f'Sprite changed: {frame_path}')
        with Image.open(frame_path) as image:
            if image.mode != 'RGBA' or image.getextrema()[3][0] != 0 or image.getextrema()[3][1] == 0:
                raise ValueError(f'Sprite needs both transparent and visible pixels: {frame_path}')
        rendered = (path.parent / item['rendered_file']).resolve()
        if sha256(rendered) != item['registered_sha256']:
            raise ValueError(f'Rendered sprite differs from registered asset: {rendered}')
    spec['render_spec']['project_dir'] = str((path.parent / spec['render_spec']['project_dir']).resolve())
    return spec


def render_sprite_preview(spec_path, output):
    from gpu_lifecycle import render_stage
    from renderers import render_unit

    spec_path = Path(spec_path).resolve()
    spec = read_sprite_spec(spec_path)
    output = Path(output).resolve()
    if output.suffix.lower() != '.mp4' or output.exists():
        raise ValueError('Use a new .mp4 output; existing artifacts are preserved')
    unit = {'renderer': 'remotion', 'scene_type': '2d',
            'duration_frames': spec['duration_frames'], 'render_spec': spec['render_spec']}
    with render_stage():
        result = render_unit(unit, output.parent, output.stem)
    receipt = {'schema_version': 4, 'profile': 'horror-v4.1', 'scope': 'isolated_sprite_test',
               'spec': str(spec_path), 'spec_sha256': sha256(spec_path),
               'video': result, 'video_sha256': sha256(result),
               'technical_receipt': str(output.with_name(output.stem + '_qa.json')),
               'artwork_status': 'UNVERIFIED', 'animation_status': 'UNVERIFIED',
               'release_eligible': False, 'audio': 'silent asset test; no audio generation'}
    output.with_suffix('.receipt.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    return receipt
