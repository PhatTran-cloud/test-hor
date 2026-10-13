"""Opening test clips retain the full WAV identity and cannot approve production."""
import copy
import sys
import unittest
import json
import tempfile
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from v4_excerpt import excerpt_scope, voice_review_deferred
from v4_workflow import check_representative
from renderers import render_authored_section


class ExcerptTests(unittest.TestCase):
    def setUp(self):
        self.plan = {
            'profile': 'horror-v4.1', 'sections': [{'id': 'section_1', 'speech': {'frames': 16541, 'sha256': 'original'}}],
            'preview_scope': {'kind': 'candidate_excerpt', 'section_id': 'section_1', 'start_frame': 0,
                              'end_frame': 3600, 'source_audio_sha256': 'original',
                              'authorization': {'reviewer': 'human user', 'request': 'First minute sample'},
                              'voice_review_deferred': {'status': 'USER_RETAINS_TEST_AUDIO_WITH_KNOWN_DEFECTS',
                                  'asset_sha256': 'original', 'request': 'Retain test WAV', 'limitations': ['Unreviewed acting; buzz']}}
        }

    def test_excerpt_keeps_full_measured_clock_and_is_not_representative_approval(self):
        before = copy.deepcopy(self.plan)
        self.assertEqual(excerpt_scope(self.plan)['end_frame'], 3600)
        self.assertTrue(voice_review_deferred(self.plan, self.plan['sections'][0]['speech']))
        self.assertEqual(self.plan, before)
        with self.assertRaisesRegex(ValueError, 'cannot substitute'):
            check_representative(self.plan, '.')

    def test_stale_wav_and_unrequested_or_invalid_ranges_cannot_defer_review(self):
        for update in ({'source_audio_sha256': 'other'}, {'start_frame': 20}, {'end_frame': 17000},
                       {'end_frame': True}, {'authorization': {}}, {'kind': 'production'}):
            p = copy.deepcopy(self.plan)
            p['preview_scope'].update(update)
            with self.assertRaises(ValueError):
                excerpt_scope(p)
        p = copy.deepcopy(self.plan)
        p['preview_scope']['voice_review_deferred']['asset_sha256'] = 'other'
        self.assertFalse(voice_review_deferred(p, p['sections'][0]['speech']))

    def test_normal_plan_does_not_defer_voice_review(self):
        p = copy.deepcopy(self.plan)
        p.pop('preview_scope')
        self.assertIsNone(excerpt_scope(p))
        self.assertFalse(voice_review_deferred(p, p['sections'][0]['speech']))

    def test_excerpt_renderer_keeps_complete_receipt_and_normal_render_rejects_short_assembly(self):
        section = SimpleNamespace(id='section_1', shots=[{'id':'opening', 'duration_frames':3600}])
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            receipt={'section_1':{'frames':16541,'sha256':'original'}}
            receipt_file=folder/'speech_timing.json'
            receipt_file.write_text(json.dumps(receipt))
            before=receipt_file.read_bytes()
            with self.assertRaisesRegex(ValueError, 'frame total'):
                render_authored_section(section, folder)
            with patch('renderers.render_unit', return_value=str(folder/'opening.mp4')) as unit, \
                 patch('renderers._run'), patch('renderers.probe_video', return_value={'nb_frames':'3600','duration':60}):
                render_authored_section(section, folder, preview_frames=3600)
                self.assertEqual(unit.call_count,1)
            self.assertEqual(receipt_file.read_bytes(),before)


if __name__ == '__main__':
    unittest.main()
