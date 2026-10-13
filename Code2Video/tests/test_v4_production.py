import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
import numpy as np
from scipy.io import wavfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from v3_contract import normalize_plan
from v4_contract import digest,sha256,validate_files,visual_reference_policy,shot_contract
from v4_runtime import state_at,absolute_frame,envelope
from v4_quality import apply_review,release_check
spec=importlib.util.spec_from_file_location('v4_example',ROOT/'local_tools/v4_smoke/build_plan.py')
example=importlib.util.module_from_spec(spec)
spec.loader.exec_module(example)


class V4Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder=Path(self.temp.name)
        self.audio=self.folder/'speech.wav'
        wavfile.write(self.audio,48000,np.zeros(540*800,dtype=np.float32))
        self.plan=example.make_plan(self.audio)

    def test_many_to_many_beats_are_preserved_and_input_not_mutated(self):
        original=copy.deepcopy(self.plan)
        normalized=normalize_plan(self.plan)
        self.assertEqual(normalized,self.plan)
        self.assertEqual(self.plan,original)
        shots=normalized['sections'][0]['shots']
        self.assertEqual(len(shots[1]['beat_ids']),2)
        self.assertIn(shots[0]['beat_ids'][0],shots[1]['beat_ids'])

    def test_reject_gaps_coverage_early_reveal_and_fractional_clock(self):
        mutations=[lambda p:p['sections'][0]['shots'][1].update(start_frame=181),
            lambda p:p['sections'][0]['shots'][1].update(beat_ids=['difference_beat']),
            lambda p:p['sections'][0]['beats'][1].update(start_frame=230),
            lambda p:p['sections'][0]['shots'][0].update(end_frame=180.5),
            lambda p:p.update(fps=30),
            lambda p:p['sections'][0]['shots'][0]['execution']['objects'].pop('signal'),
            lambda p:p['sections'][0]['shots'][0]['events'][0].update(start_frame=190),
            lambda p:p['sections'][0]['shots'][0]['pattern'].update(entities=['lit_leaf'])]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                bad=copy.deepcopy(self.plan)
                mutate(bad)
                with self.assertRaises(ValueError): normalize_plan(bad)

    def test_state_continues_across_shots_and_random_seek_is_deterministic(self):
        section=self.plan['sections'][0]
        a=shot_contract(section,section['shots'][0])
        b=shot_contract(section,section['shots'][1])
        self.assertEqual(state_at(a,'lit_leaf',150)['response'],1)
        self.assertEqual(state_at(b,'lit_leaf',absolute_frame(b,0))['response'],1)
        self.assertEqual(state_at(b,'lit_leaf',0)['response'],0)
        self.assertEqual(state_at(b,'lit_leaf',130)['response'],.5)
        self.assertEqual(state_at(b,'lit_leaf',130),state_at(a,'lit_leaf',130))
        event=section['shots'][0]['events'][0]
        self.assertEqual(envelope(event,126),1)
        self.assertEqual(envelope(event,176),0)

    def test_stale_audio_script_and_source_bindings_rejected(self):
        validate_files(self.plan,self.folder)
        bad=copy.deepcopy(self.plan)
        bad['sections'][0]['shots'][0]['execution']['contract_consumer']='ImaginaryRendererConsumer'
        with self.assertRaises(ValueError): validate_files(bad,self.folder)
        bad=copy.deepcopy(self.plan)
        bad['sections'][0]['narration']='Changed after recording'
        with self.assertRaises(ValueError): normalize_plan(bad)
        self.audio.write_bytes(self.audio.read_bytes()+b'changed')
        with self.assertRaises(ValueError): validate_files(self.plan,self.folder)

    def test_event_drives_sfx_time_and_rejects_unheard_assets(self):
        cue={'event_id':'signal_arrival','source_object':'signal','selection_reason':'physical arrival, no generic whoosh',
             'trigger':'arrival','purpose':'mark localized response','file':str(self.audio),'duration':.2,
             'offset_frames':6,'listening_review':{'status':'PASS','reviewer':'fixture test only',
             'notes':'unit fixture; not a production listening judgment','asset_sha256':sha256(self.audio)}}
        p=copy.deepcopy(self.plan)
        p['sections'][0]['sfx_cues']=[cue]
        result=normalize_plan(p)
        self.assertEqual(result['sections'][0]['sfx_cues'][0]['relative_time'],116/60)
        for mutation in [lambda c:c.update(event_id='no_event'),lambda c:c.update(source_object='shade_leaf'),
                         lambda c:c.update(source='procedural'),lambda c:c['listening_review'].update(status='UNVERIFIED')]:
            bad=copy.deepcopy(p)
            mutation(bad['sections'][0]['sfx_cues'][0])
            with self.assertRaises(ValueError): normalize_plan(bad)

    def test_kage_rule_uses_time_not_shot_count(self):
        p={'phase':'authored','content_profile':{'kind':'formula_math','rich_storytelling':True},'sections':[{'shots':[
            {'renderer':'manim','start_frame':0,'end_frame':800},
            {'renderer':'remotion','start_frame':800,'end_frame':900},
            {'renderer':'remotion','start_frame':900,'end_frame':1000}]}]}
        policy=visual_reference_policy(p)['kage']
        self.assertEqual(policy['manim_visual_share'],.8)
        self.assertFalse(policy['enabled'])
        p['content_profile']={'kind':'storytelling_rich'}
        self.assertTrue(visual_reference_policy(p)['kage']['enabled'])

    def test_music_is_optional_requested_and_bound_to_listened_asset(self):
        p=copy.deepcopy(self.plan)
        p['music']={'file':str(self.audio),'purpose':'unit fixture only','selection_reason':'test optional bed policy',
            'listening_review':{'status':'PASS','reviewer':'unit test fixture','notes':'not a production listening claim',
                                'asset_sha256':sha256(self.audio)}}
        with self.assertRaises(ValueError): normalize_plan(p)
        p['music_requested']=True
        normalized=normalize_plan(p)
        validate_files(normalized,self.folder)
        p['music']['listening_review']['asset_sha256']='wrong'
        with self.assertRaises(ValueError): validate_files(p,self.folder)

    def test_state_track_cannot_reset_property_at_next_shot(self):
        bad=copy.deepcopy(self.plan)
        bad['sections'][0]['state_tracks'].append({'id':'bad_reset','object_id':'lit_leaf','property':'response',
            'from':0,'to':1,'start_frame':200,'end_frame':220,'cause':'would accidentally reset the already lit leaf'})
        with self.assertRaises(ValueError): normalize_plan(bad)

    def test_events_can_cross_cuts_only_with_explicit_continuation_binding(self):
        p=copy.deepcopy(self.plan)
        section=p['sections'][0]
        section['shots'][0]['events'][0].update(end_frame=220,carry_across_shots=True)
        with self.assertRaises(ValueError): normalize_plan(p)
        section['shots'][1]['event_ids']=['signal_arrival']
        result=normalize_plan(p)
        contract=shot_contract(result['sections'][0],result['sections'][0]['shots'][1])
        self.assertEqual(contract['shot']['events'][0]['start_frame'],110)
        self.assertGreater(envelope(contract['shot']['events'][0],180),0)

    def test_film_clock_and_world_state_continue_across_sections(self):
        p=copy.deepcopy(self.plan)
        second=copy.deepcopy(p['sections'][0]);second['id']='section_2'
        for beat in second['beats']:
            beat['id']+='_second'
            beat['depends_on']=[x+'_second' for x in beat.get('depends_on',[])]
        for shot in second['shots']:
            shot['id']+='_second'
            shot['beat_ids']=[x+'_second' for x in shot['beat_ids']]
            if shot.get('b_roll'): shot['b_roll']['anchor']+='_second'
            for event in shot.get('events',[]): event['id']+='_second'
        p['sections'].append(second)
        with self.assertRaises(ValueError): normalize_plan(p)
        second['objects'][0]['initial_state']['response']=1
        second['state_tracks'][0].update(id='second_response_track',**{'from':1,'to':.5})
        result=normalize_plan(p)
        self.assertEqual(result['sections'][1]['film_start_frame'],540)
        contract=shot_contract(result['sections'][1],result['sections'][1]['shots'][1])
        self.assertEqual(contract['film_start_frame'],720)
        self.assertEqual(state_at(contract,'lit_leaf',180)['response'],.5)

    def test_draft_requires_complete_script_segments_but_not_fake_shot_timing(self):
        draft=copy.deepcopy(self.plan)
        draft.update(phase='draft',technical_fixture=False)
        section=draft['sections'][0]
        section.update(narration='First. Second.',narration_segments=[{'id':'fixture_a','text':'First.'},{'id':'fixture_b','text':'Second.'}])
        section.pop('speech')
        for shot in section['shots']:
            for key in ('start_frame','end_frame','duration_frames','execution'): shot.pop(key)
        self.assertEqual(normalize_plan(draft)['phase'],'draft')
        section['narration_segments'][1]['text']='Missing content.'
        with self.assertRaises(ValueError): normalize_plan(draft)

    def test_review_is_independent_stale_hash_fails_and_fixture_cannot_release(self):
        folder=self.folder
        video=folder/'test.mp4'
        video.write_bytes(b'technical fixture artifact')
        planfile=folder/'plan.json'
        planfile.write_text(json.dumps(self.plan),encoding='utf-8')
        def write(name,data): (folder/name).write_text(json.dumps(data),encoding='utf-8')
        write('source_manifest.json',{'files':{'plan.json':sha256(planfile)},'plan_sha256':digest(self.plan)})
        manifest={'video':str(video),'video_sha256':sha256(video),'plan_sha256':digest(self.plan),
            'scope':'production','shots':[{'shot':s['id'],'output':str(video),'output_sha256':sha256(video)} for s in self.plan['sections'][0]['shots']]}
        write('execution_manifest.json',manifest)
        report={'technical_fixture':True,'video_sha256':sha256(video),'plan_sha256':digest(self.plan),
            'gates':{name:{'status':'UNVERIFIED','notes':'pending'} for name in
                ['visual','scientific','motion','vfx','editorial','layout','listening','technical']}}
        write('quality_report.json',report)
        review={'reviewer':'test','video_sha256':sha256(video),'plan_sha256':digest(self.plan),
                'gates':{'visual':{'status':'PASS','notes':'fixture consistency only',
                    'evidence':[{'id':'clip','kind':'clip','file':'test.mp4','sha256':sha256(video)}],
                    'observations':[{'target':'shot:'+s['id'],'expected':'fixture consistency',
                        'observed':'fixture review unit test only','evidence_ids':['clip']} for s in self.plan['sections'][0]['shots']]}}}
        applied=apply_review(folder,review)
        self.assertEqual(applied['gates']['motion']['status'],'UNVERIFIED')
        with self.assertRaises(ValueError): release_check(folder)
        review['gates']['visual'].pop('evidence')
        with self.assertRaises(ValueError): apply_review(folder,review)
        review['gates']={}
        video.write_bytes(b'changed')
        with self.assertRaises(ValueError): apply_review(folder,review)


if __name__=='__main__': unittest.main()
