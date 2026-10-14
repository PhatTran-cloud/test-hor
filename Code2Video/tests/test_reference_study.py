"""Real FFmpeg extraction/count/clock tests; fixtures are not reference research."""
import csv
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from reference_study import sample_references, file_hash


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg required')
class ReferenceStudyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.video = self.root / 'fixture.mkv'
        subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-f', 'lavfi', '-i',
                        'testsrc2=s=64x36:r=4:d=180', '-c:v', 'ffv1', str(self.video)], check=True)
        self.manifest = self.root / 'manifest.json'
        self.videos = [{'id': 'fixture', 'file': 'fixture.mkv', 'sample_width': 160,
                        'title': 'Synthetic test fixture, not OverSimplified', 'duration_seconds': 180}]

    def run_study(self):
        self.manifest.write_text(json.dumps({'schema_version': 'reference-study/1', 'videos': self.videos}))
        result = sample_references(self.manifest, self.root / 'study')
        return json.loads(result.read_text())

    def test_three_minutes_has_180_real_images_half_open_clock_and_unreviewed_receipts(self):
        result = self.run_study()
        video = result['videos'][0]
        self.assertEqual(result['total_samples'], 180)
        self.assertEqual([f['source_second'] for f in video['frames']], list(range(180)))
        self.assertEqual([f['decoded_pts_second'] for f in video['frames']], list(range(180)))
        self.assertEqual(len(video['sheets']), 6)
        self.assertNotEqual(video['frames'][0]['sha256'], video['frames'][-1]['sha256'])
        self.assertEqual(video['source_file_sha256'], file_hash(self.video))
        for frame in video['frames']:
            self.assertEqual(frame['sha256'], file_hash(self.root / 'study/fixture' / frame['file']))
            self.assertEqual(frame['review_status'], 'UNVERIFIED')
        self.assertEqual(result['visual_review_status'], 'UNVERIFIED')
        with (self.root / 'study/fixture/annotations.csv').open(newline='') as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 180)
        self.assertTrue(all(row['scene_id'] == '' and row['notes'] == '' for row in rows))

    def test_fractional_start_and_precut_offset_record_decoded_not_invented_timestamps(self):
        self.videos[0].update(start_second=.3, duration_seconds=3, video_start_second=120)
        frames = self.run_study()['videos'][0]['frames']
        self.assertEqual([f['source_second'] for f in frames], [120.3, 121.3, 122.3])
        self.assertEqual([f['decoded_source_second'] for f in frames], [120.5, 121.5, 122.5])
        self.assertEqual([f['sampling_delay_seconds'] for f in frames], [.2, .2, .2])

    def test_missing_short_invalid_windows_and_ids_publish_no_partial_study(self):
        for update in [{'file': 'missing.mp4'}, {'duration_seconds': 181},
                       {'duration_seconds': 0}, {'duration_seconds': 1.5},
                       {'start_second': float('nan')}, {'sample_width': 161}, {'id': '../bad'}]:
            before = self.videos[0].copy()
            self.videos[0].update(update)
            with self.assertRaises(ValueError):
                self.run_study()
            self.assertFalse((self.root / 'study').exists())
            self.videos[0] = before

    def test_output_reuse_preserves_review_and_inputs(self):
        self.videos[0]['duration_seconds'] = 2
        self.run_study()
        receipt = self.root / 'study/study.json'
        before = receipt.read_bytes()
        with self.assertRaisesRegex(ValueError, 'new output'):
            self.run_study()
        self.assertEqual(receipt.read_bytes(), before)

    def test_cli_needs_no_gpu_or_voice_configuration(self):
        self.videos[0]['duration_seconds'] = 2
        self.manifest.write_text(json.dumps({'schema_version': 'reference-study/1', 'videos': self.videos}))
        run = subprocess.run([sys.executable, str(ROOT / 'local_tools/production.py'),
                              'reference-study', str(self.manifest), '--output', str(self.root / 'cli')],
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads((self.root / 'cli/study.json').read_text())['total_samples'], 2)

    def test_three_windows_keep_separate_ids_and_540_actual_samples(self):
        base = self.videos[0]
        self.videos = [{**base, 'id': f'fixture_{i}'} for i in range(3)]
        result = self.run_study()
        self.assertEqual(result['total_samples'], 540)
        self.assertEqual([v['sample_count'] for v in result['videos']], [180, 180, 180])
        self.assertEqual(len({f['id'] for v in result['videos'] for f in v['frames']}), 540)


if __name__ == '__main__':
    unittest.main()
