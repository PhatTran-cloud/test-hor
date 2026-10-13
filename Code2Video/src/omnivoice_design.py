"""Audition designed dialogue references through the production entrypoint.

This stage never approves or registers a reference and never synthesizes a film.
The cloning adapter and its reference/listening gates remain unchanged.
"""
import json
import math
import shutil
from pathlib import Path

import numpy as np
from scipy.io import wavfile

from gpu_lifecycle import audio_stage
from v4_contract import digest, sha256


CHOICES = {
    'gender': {'male': 'Male / 男', 'female': 'Female / 女'},
    'age': {'child': 'Child / 儿童', 'teenager': 'Teenager / 少年',
            'young adult': 'Young Adult / 青年', 'middle-aged': 'Middle-aged / 中年',
            'elderly': 'Elderly / 老年'},
    'pitch': {'very low pitch': 'Very Low Pitch / 极低音调', 'low pitch': 'Low Pitch / 低音调',
              'moderate pitch': 'Moderate Pitch / 中音调', 'high pitch': 'High Pitch / 高音调',
              'very high pitch': 'Very High Pitch / 极高音调'},
    'style': {'whisper': 'Whisper / 耳语'},
}
API_NAMES = ['text', 'lang', 'ns', 'gs', 'dn', 'sp', 'du', 'pp', 'po'] + [f'param_{i}' for i in range(9, 15)]


def validate_request(request):
    if request.get('language_id') not in {'en', 'vi'}:
        raise ValueError('Explicit language_id en or vi required')
    if not isinstance(request.get('authorization'), str) or not request['authorization'].strip():
        raise ValueError('Record human authorization for the audition')
    voices = request.get('voices')
    if not isinstance(voices, list) or not voices:
        raise ValueError('Audition needs dialogue voice requests')
    ids = set()
    for voice in voices:
        vid = voice.get('id', '')
        if not isinstance(vid, str) or not vid or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789_-' for c in vid) or vid in ids:
            raise ValueError('Unique safe voice IDs required')
        ids.add(vid)
        if voice.get('role') != 'dialogue' or not voice.get('character_id'):
            raise ValueError('Voice design audition is dialogue-only; narrator remains canonical')
        if not isinstance(voice.get('text'), str) or not voice['text'].strip():
            raise ValueError('Audition text required')
        attributes = voice.get('attributes')
        if not isinstance(attributes, dict) or not attributes or set(attributes) - set(CHOICES):
            raise ValueError('Use supported speaker attributes, not arbitrary emotion prompts')
        for key, value in attributes.items():
            if not isinstance(value, str) or value not in CHOICES[key]:
                raise ValueError(f'Unsupported {key} attribute: {value}')
    return request


def design_arguments(request, voice):
    groups = [CHOICES[key][voice['attributes'][key]] if key in voice['attributes'] else 'Auto'
              for key in ('gender', 'age', 'pitch', 'style')]
    # Accent/dialect controls only affect English/Chinese; do not invent Vietnamese dialect tags.
    return [voice['text'], {'vi': 'Vietnamese', 'en': 'English'}[request['language_id']],
            32, 2.0, False, 1.0, None, False, False, *groups, 'Auto', 'Auto']


def run_audition(request_path, output):
    import requests
    from gradio_client import Client
    request_path = Path(request_path).resolve()
    request = validate_request(json.loads(request_path.read_text(encoding='utf-8')))
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    (output / 'request.json').write_text(json.dumps(request, ensure_ascii=False, indent=2), encoding='utf-8')
    ledger = {'status': 'STARTING', 'request_sha256': sha256(request_path), 'voices': [],
              'listening_review': 'UNVERIFIED', 'model_revision': 'NOT_EXPOSED_BY_RUNTIME',
              'seed': 'NOT_EXPOSED_BY_RUNTIME', 'time_stretch': False,
              'purpose': 'Two-role cast audition; not full film speech or ASR alignment'}
    try:
        with audio_stage('voice', output) as config:
            endpoint = config['omnivoice']['endpoint']
            response = requests.get(endpoint.rstrip('/') + '/gradio_api/info', timeout=30)
            response.raise_for_status()
            metadata = response.json()
            (output / 'api-info.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
            api = metadata.get('named_endpoints', {}).get('/_design_fn', {})
            names = [p.get('parameter_name') for p in api.get('parameters', [])]
            if names != API_NAMES:
                raise ValueError(f'OmniVoice design API changed; audit before inference: {names}')
            client = Client(endpoint, verbose=False)
            for voice in request['voices']:
                arguments = design_arguments(request, voice)
                generated = client.predict(*arguments, api_name='/_design_fn')
                source = generated[0]
                if isinstance(source, dict):
                    source = source.get('path')
                if not source or not Path(source).is_file():
                    raise RuntimeError(f'Voice design returned no audio: {generated[1:]}')
                target = output / (voice['id'] + '.wav')
                shutil.copy2(source, target)
                rate, pcm = wavfile.read(target)
                if not pcm.size or not np.isfinite(pcm).all() or not np.any(pcm):
                    raise ValueError('Empty, non-finite or silent design take')
                duration = len(pcm) / rate
                if not math.isfinite(duration) or duration <= 0:
                    raise ValueError('Invalid take duration')
                transcript = target.with_suffix('.txt')
                transcript.write_text(voice['text'] + '\n', encoding='utf-8')
                item = {**voice, 'file': str(target), 'sha256': sha256(target),
                        'sample_rate': rate, 'channels': 1 if pcm.ndim == 1 else pcm.shape[1],
                        'duration_s': duration, 'transcript_path': str(transcript),
                        'transcript_sha256': sha256(transcript), 'transcript_status': 'INPUT_TEXT_UNVERIFIED',
                        'endpoint': endpoint, 'api': '/_design_fn', 'arguments': arguments,
                        'request_digest': digest(arguments), 'runtime_status': str(generated[1:]),
                        'listening_review': {'status': 'UNVERIFIED', 'asset_sha256': sha256(target)},
                        'selection_status': 'AUDITION_NOT_SELECTED', 'word_alignment_status': 'NOT_RUN'}
                ledger['voices'].append(item)
                (output / 'receipt.json').write_text(json.dumps(ledger, ensure_ascii=False, indent=2), encoding='utf-8')
        ledger['status'] = 'GENERATED_PENDING_LISTENING'
    except BaseException as exc:
        ledger['status'] = 'FAILED'
        ledger['error'] = str(exc)
        raise
    finally:
        (output / 'receipt.json').write_text(json.dumps(ledger, ensure_ascii=False, indent=2), encoding='utf-8')
    return output / 'receipt.json'
