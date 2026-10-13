"""Real FFmpeg sampling of generated test media; never OverSimplified evidence."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from reference_study import sample_reference, check_reference, sha256


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'FFmpeg reference sampling requires its actual tools')
class ReferenceStudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.root=Path(cls.tmp.name);cls.source=cls.root/'technical-only.mp4'
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-f','lavfi','-i','testsrc2=size=160x90:rate=10:duration=4',
            '-c:v','libx264','-pix_fmt','yuv420p',str(cls.source)],check=True)

    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def setUp(self):
        self.case=tempfile.TemporaryDirectory(dir=self.root);self.addCleanup(self.case.cleanup)
        self.folder=Path(self.case.name)/'samples'

    def sample(self):
        return sample_reference(self.source,self.folder,'https://example.org/technical-fixture',start=1,seconds=2,source_offset=120)

    def test_real_images_hashes_contact_sheet_and_nominal_source_clock(self):
        m=self.sample()
        self.assertEqual(len(m['frames']),2)
        self.assertEqual([r['nominal_source_seconds'] for r in m['frames']],[121,122])
        self.assertEqual(m['source']['width'],160)
        self.assertEqual(m['source']['sha256'],sha256(self.source))
        self.assertNotEqual(m['frames'][0]['sha256'],m['frames'][1]['sha256'])
        expected=Path(self.case.name)/'at-one-second.jpg'
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss','1','-i',str(self.source),
            '-frames:v','1','-q:v','2',str(expected)],check=True)
        self.assertEqual(m['frames'][0]['sha256'],sha256(expected))
        self.assertTrue((self.folder/'sheets/000.jpg').is_file())
        report=check_reference(self.folder)
        self.assertEqual(report['sample_count'],2)
        self.assertEqual(report['inspected_count'],0)
        self.assertEqual(report['inspection'],'INCOMPLETE')
        self.assertEqual(report['audio_inspection'],'NOT_PERFORMED')

    def test_html_missing_short_invalid_and_existing_sources_fail_without_filler(self):
        html=self.root/'rejected.html';html.write_text('<html>Site Unavailable</html>')
        for source,kwargs in [(html,{}),(self.root/'missing.mp4',{}),(self.source,{'start':3,'seconds':2}),
            (self.source,{'seconds':True}),(self.source,{'start':float('nan')})]:
            with self.assertRaises(ValueError):sample_reference(source,self.folder,'https://example.org/fixture',**kwargs)
            self.assertFalse(self.folder.exists())
        self.sample()
        with self.assertRaises(ValueError):self.sample()

    def test_changed_frame_or_manifest_bound_notes_are_rejected(self):
        self.sample();path=self.folder/'frames/000001.jpg';path.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'evidence'):check_reference(self.folder)

    def test_annotation_requires_real_inspected_nonoverlapping_groups(self):
        self.sample();path=self.folder/'annotations.json';note=json.loads(path.read_text())
        group={'id':'view','first_index':0,'last_index':1,'scene_id':'fixture',
            'composition':'moving test pattern','background_information':'technical fixture',
            'cast_and_props':'none','camera':'fixed generated fixture','next_visual_link':'end of test only'}
        note.update(reviewer='unit fixture declaration',inspected_indices=[0],sample_groups=[group]);path.write_text(json.dumps(note))
        with self.assertRaisesRegex(ValueError,'uninspected'):check_reference(self.folder)
        note['inspected_indices']=[0,1];path.write_text(json.dumps(note))
        self.assertEqual(check_reference(self.folder)['inspection'],'REVIEW_RECORDED_NOT_INDEPENDENTLY_VERIFIED')
        note['sample_groups'].append({**group,'id':'overlap'});path.write_text(json.dumps(note))
        with self.assertRaisesRegex(ValueError,'overlap'):check_reference(self.folder)

    def test_grid_and_annotation_hash_cannot_silently_change(self):
        self.sample();path=self.folder/'manifest.json';manifest=json.loads(path.read_text())
        manifest['frames'][1]['nominal_source_seconds']=999;path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError,'timestamps'):check_reference(self.folder)
        manifest['frames'][1]['nominal_source_seconds']=122;path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError,'different sampling'):check_reference(self.folder)


if __name__=='__main__':unittest.main()
