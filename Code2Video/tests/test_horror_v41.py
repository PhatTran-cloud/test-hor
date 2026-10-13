"""Behavioral regression for the horror fork. No artwork/listening quality claims."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from scipy.io import wavfile

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'local_tools')]
from horror_contract import validate_horror,validate_sfx_brief,asset_digest
from horror_sprites import sprite_state,validate_binding
from omnivoice_tts import line_identity,prepare_section,configuration_identity,resolve_references
from sfx_assets import prepare_cues
from sfx import mix_narration_with_sfx,_read_stereo
from v4_contract import sha256,digest
from gpu_lifecycle import audio_stage,renderer_guard


class HorrorTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup); self.folder=Path(self.tmp.name)
        self.reference=self.folder/'ref.wav'
        wave=np.sin(np.arange(12000)*.07).astype(np.float32)*.05
        wavfile.write(self.reference,24000,wave)
        transcript=self.folder/'ref.txt'; transcript.write_text('Reviewed unit fixture text.',encoding='utf-8')
        ref={'path':str(self.reference),'sha256':sha256(self.reference),'transcript_path':str(transcript),'transcript_status':'REVIEWED',
             'listening_review':{'status':'PASS','asset_sha256':sha256(self.reference),'reviewer':'unit fixture only','notes':'not a production listening judgment'}}
        library=self.folder/'library.json'
        library.write_text(json.dumps({'entries':[{'speaker_id':'main-fixture','role':'narrator','language_id':'en','reference':ref},
            {'speaker_id':'dialogue-fixture','role':'dialogue','language_id':'en','reference':copy.deepcopy(ref)}]}),encoding='utf-8')
        self.plan={'schema_version':4,'profile':'horror-v4.1','language_id':'en','tts_speed':1,'phase':'draft',
            'content_profile':{'genre':'horror','kind':'storytelling_rich'},
            'cast':{'library':str(library),'narrator':'main-fixture','characters':{'actor':'dialogue-fixture'}},
            'horror':{'artwork_style':'3d_horror_cartoon','artwork_provider':'flow','kage_reference':True,
                      'voice_provider':'omnivoice','sfx_provider':'stable_audio_3_small_sfx','assets':[],
                      'style_bible':dict.fromkeys(['canonical_prompt','proportions','materials','lighting','depth','identity_rules'],'unit fixture only')},
            'sections':[{'id':'section_1','objects':[],'shots':[],'sfx_cues':[],
                'narration_segments':[{'id':'n1','role':'narrator','text':'A knock.'},
                    {'id':'d1','role':'dialogue','character_id':'actor','text':'Who is there?',
                     'acting_direction':{'mood':'restrained fear','intention':'identify the unseen visitor'},'instruct':'whisper'}]}]}
        self.asset={'id':'walk','object_id':'actor','views':[{'id':'side','frames':[
            {'id':'a','hold_frames':3,'root_anchor':[10,10],'ground_anchor':[10,20],'sockets':{'foot':[12,20]}},
            {'id':'b','hold_frames':5,'root_anchor':[11,10],'ground_anchor':[11,20],'sockets':{'foot':[14,20]}}]}],
            'action':{'contact_requirements':['foot']}}
        self.binding={'view_id':'side','loop':False,'start_frame':100,'end_frame':120,
            'root_track':[{'frame':100,'position':[100,100]},{'frame':120,'position':[120,100]}],
            'contact_windows':[{'socket':'foot','start_frame':100,'end_frame':110,'world_position':[115,130]}]}
        self.cue={'id':'knock','event_id':'e','source_object':'door','duration':.3,'sync_phase':'peak','offset_frames':0,
            'generation':{'prompt':'Unit provider fixture: one dry wood knock, no speech/music','seconds':1.25,'seed':7},
            'perspective':{'space':'room','distance':'near','occlusion':'none','reason':'unit fixture'}}

    def test_profile_keeps_art_providers_and_explicit_language(self):
        validate_horror(self.plan)
        for mutation in [lambda p:p.update(language_id=None),lambda p:p['horror'].update(kage_reference=False),
                         lambda p:p['horror'].update(voice_provider='kokoro'),lambda p:p['horror'].update(sfx_provider='freesound')]:
            bad=copy.deepcopy(self.plan); mutation(bad)
            with self.assertRaises(ValueError): validate_horror(bad)

    def test_narrator_has_no_instruction_and_emotion_is_not_provider_tag(self):
        for instruction in ['whisper','scared']:
            bad=copy.deepcopy(self.plan['sections'][0]['narration_segments'][0]); bad['instruct']=instruction
            with self.assertRaises(ValueError): line_identity(self.plan,bad)
        bad=copy.deepcopy(self.plan['sections'][0]['narration_segments'][1]); bad['instruct']='angry'
        with self.assertRaises(ValueError): line_identity(self.plan,bad)
        identity=line_identity(self.plan,self.plan['sections'][0]['narration_segments'][1])
        self.assertEqual(identity['instruct'],'whisper'); self.assertEqual(identity['acting_direction']['mood'],'restrained fear')

    def test_flat_vector_style_requires_explicit_selection_and_keeps_provider_checks(self):
        self.plan['horror']['artwork_style']='2d_flat_geometric_vector'
        with self.assertRaisesRegex(ValueError,'recorded user style selection'):
            validate_horror(self.plan)
        self.plan['production_packet']={'visual_style_decision':{
            'status':'USER_SELECTED','selected_style':'2d_flat_geometric_vector',
            'authorization':{'reviewer':'human user','request':'Switch to flat geometric vector art'}}}
        validate_horror(self.plan)
        for mutation in [lambda p:p['horror'].update(artwork_provider='other'),
                         lambda p:p['horror'].update(kage_reference=False),
                         lambda p:p['production_packet']['visual_style_decision'].update(selected_style='3d_horror_cartoon')]:
            bad=copy.deepcopy(self.plan); mutation(bad)
            with self.assertRaises(ValueError): validate_horror(bad)

    def test_reference_role_language_transcript_and_hash_are_enforced(self):
        resolve_references(self.plan,self.plan['sections'][0])
        self.plan['language_id']='vi'
        with self.assertRaises(ValueError): resolve_references(self.plan,self.plan['sections'][0])
        self.plan['language_id']='en'; self.plan['cast']['narrator']='dialogue-fixture'
        with self.assertRaises(ValueError): resolve_references(self.plan,self.plan['sections'][0])
        self.plan['cast']['narrator']='main-fixture'
        self.reference.write_bytes(self.reference.read_bytes()+b'change')
        with self.assertRaises(ValueError): resolve_references(self.plan,self.plan['sections'][0])

    def test_missing_transcript_cannot_start_cloning(self):
        library=Path(self.plan['cast']['library']); data=json.loads(library.read_text())
        data['entries'][0]['reference']['transcript_status']='NOT_TRANSCRIBED'; library.write_text(json.dumps(data))
        with self.assertRaises(ValueError): configuration_identity(self.plan,self.plan['sections'][0])

    def test_real_wav_measurement_multi_speaker_and_whisper_payload(self):
        calls=[]
        raw=self.folder/'generated.wav'; wavfile.write(raw,24000,np.sin(np.arange(9000)*.07).astype(np.float32)*.001)
        class Fake:
            receipt={'test':'unit transport fixture, not actual model'}
            def clone(inner,text,language,reference,instruction,settings):
                calls.append((reference['speaker_id'],instruction,settings['duration'])); return raw,'fixture'
        speech=prepare_section(self.plan,self.plan['sections'][0],self.folder/'voice.wav','mock',Fake())
        self.assertEqual(calls,[('main-fixture',None,None),('dialogue-fixture','whisper',None)])
        rate,pcm=wavfile.read(speech['file']); self.assertEqual(rate,48000); self.assertEqual(len(pcm),speech['frames']*800)
        self.assertFalse(speech['time_stretch']); self.assertEqual(speech['provider'],'omnivoice')
        self.assertGreater(speech['utterances'][1]['start'],speech['utterances'][0]['end']-1e-8)
        self.assertEqual(speech['utterances'][1]['listening_review']['status'],'UNVERIFIED')
        self.plan['sections'][0]['narration_segments'][1]['acting_direction']['mood']='anger'
        self.assertNotEqual(configuration_identity(self.plan,self.plan['sections'][0])['sha256'],speech['configuration_sha256'])

    def test_cache_tamper_forces_new_take(self):
        raw=self.folder/'generated.wav'; wavfile.write(raw,24000,np.ones(2400,np.float32)*.001)
        calls=[]
        class Fake:
            receipt={'fixture':True}
            def clone(inner,*args): calls.append(1); return raw,'fixture'
        path=self.folder/'voice.wav'; section=self.plan['sections'][0]
        prepare_section(self.plan,section,path,'mock',Fake()); prepare_section(self.plan,section,path,'mock',Fake())
        self.assertEqual(len(calls),2)
        (self.folder/'voice_takes/n1_raw.wav').write_bytes(b'corrupted')
        prepare_section(self.plan,section,path,'mock',Fake()); self.assertEqual(len(calls),3)

    def test_gradio_language_dropdown_receives_display_name_not_iso_code(self):
        from omnivoice_tts import OmniVoiceClient
        from unittest.mock import MagicMock
        client=object.__new__(OmniVoiceClient); client.client=MagicMock()
        client.client.predict.return_value=(str(self.reference),'unit transport fixture')
        settings={'steps':32,'guidance':2,'denoise':False,'speed':1,'preprocess':False,'postprocess':False}
        ref={'file':str(self.reference),'ref_text':'Unit fixture.'}
        for code,display in [('en','English'),('vi','Vietnamese')]:
            client.clone('Unit text.',code,ref,None,settings)
            self.assertEqual(client.client.predict.call_args.args[1],display)

    def test_pose_seek_holds_root_and_foot_contact(self):
        validate_binding(self.asset,self.binding)
        values=[sprite_state(self.asset,self.binding,f) for f in [109,100,119,103,109]]
        self.assertEqual(values[0],values[-1]); self.assertEqual(values[1]['pose_id'],'a'); self.assertEqual(values[2]['pose_id'],'b')
        for f in [100,103,109]:
            s=sprite_state(self.asset,self.binding,f); pose=next(p for p in self.asset['views'][0]['frames'] if p['id']==s['pose_id'])
            self.assertEqual([s['image_position'][i]+pose['sockets']['foot'][i] for i in range(2)],[115,130])

    def test_loop_and_missing_contact_solver(self):
        self.binding['loop']=True
        self.assertEqual(sprite_state(self.asset,self.binding,100)['pose_id'],sprite_state(self.asset,self.binding,108)['pose_id'])
        self.binding['contact_windows']=[]
        with self.assertRaises(ValueError): validate_binding(self.asset,self.binding)

    def test_browser_and_python_sprite_evaluations_agree(self):
        args=json.dumps({'asset':self.asset,'binding':self.binding,'frames':[119,100,105,110]})
        code="import {spriteState} from './runtime/horror-sprites.mjs'; const d=JSON.parse(process.argv[1]); console.log(JSON.stringify(d.frames.map(f=>spriteState(d.asset,d.binding,f))));"
        js=json.loads(subprocess.check_output(['node','--input-type=module','-e',code,args],cwd=ROOT,text=True))
        py=[sprite_state(self.asset,self.binding,f) for f in [119,100,105,110]]
        self.assertEqual(js,py)

    def test_sfx_has_no_default_duration_or_recording_search(self):
        validate_sfx_brief(self.cue)
        for mutate in [lambda c:c.pop('duration'),lambda c:c.update(duration=8),lambda c:c.update(query='knock'),
                       lambda c:c['generation'].update(seconds=0),lambda c:c.update(offset_frames=-3)]:
            bad=copy.deepcopy(self.cue); mutate(bad)
            with self.assertRaises(ValueError): validate_sfx_brief(bad)

    def test_generated_provenance_and_actual_length_are_checked(self):
        path=self.folder/'sfx.wav'; wavfile.write(path,44100,np.ones((44100,2),np.float32)*.01)
        cue={**self.cue,'file':str(path),'provenance':{'provider':'stable_audio_3_small_sfx','source':'model_generated',
            'sha256':sha256(path),'request_sha256':digest(self.cue['generation'])},
            'listening_review':{'status':'PASS','reviewer':'unit fixture only','notes':'not listening evidence','asset_sha256':sha256(path)}}
        self.assertEqual(prepare_cues([cue],self.folder)[0]['source'],'model_generated')
        cue['duration']=1.1
        with self.assertRaises(ValueError): prepare_cues([cue],self.folder)
        cue['duration']=.3; cue['listening_review']['status']='UNVERIFIED'
        with self.assertRaises(ValueError): prepare_cues([cue],self.folder)

    def test_quiet_speech_is_ducked_without_rms_cutoff(self):
        voice=self.folder/'quiet.wav'; fx=self.folder/'fx.wav'
        wavfile.write(voice,48000,np.ones((48000,2),np.float32)*.0001)
        wavfile.write(fx,48000,np.ones((48000,2),np.float32)*.1)
        cue={'file':str(fx),'relative_time':0,'duration':1,'gain_db':0,'duck_db':-18,'fade_in':0,'fade_out':0}
        mix_narration_with_sfx(voice,self.folder/'a.wav',[cue],speech_intervals=[[.3,.7]])
        mix_narration_with_sfx(voice,self.folder/'b.wav',[cue],speech_intervals=[[0,.05]])
        a=_read_stereo(self.folder/'a.wav'); b=_read_stereo(self.folder/'b.wav')
        self.assertLess(float(np.mean(a[24000:25000]- .0001)),float(np.mean(b[24000:25000]-.0001))*.2)
        with self.assertRaises(ValueError): mix_narration_with_sfx(voice,self.folder/'c.wav',[{'file':str(fx)}])

    def test_film_tail_continues_across_section_cut(self):
        from horror_audio import film_mix
        wav=self.folder/'section.wav'; fx=self.folder/'fx.wav'
        wavfile.write(wav,48000,np.ones((48000,2),np.float32)*.01)
        wavfile.write(fx,48000,np.ones((48000,2),np.float32)*.1)
        sections=[{'speech':{'file':str(wav),'frames':60,'utterances':[]},'sfx_cues':[{'file':str(fx),'relative_time':.8,'duration':.7,'gain_db':0,'fade_in':0,'fade_out':0}]},
                  {'speech':{'file':str(wav),'frames':60,'utterances':[]},'sfx_cues':[]}]
        mixed=_read_stereo(film_mix({'sections':sections},self.folder,False))
        self.assertEqual(len(mixed),96000); self.assertGreater(float(mixed[55000,0]),float(mixed[80000,0]))

    def test_gpu_stage_lock_is_exclusive_and_always_removed(self):
        import gpu_lifecycle as gl
        config={'omnivoice':{'container':'fixture'},'vram_release_tolerance_mib':0}
        with patch.object(gl,'WORKSPACE',self.folder),patch.object(gl,'configuration',return_value=config),patch.object(gl,'stop_voice') as stop,patch.object(gl,'memory_mib',return_value=[100]):
            with audio_stage('sfx',self.folder):
                with self.assertRaises(FileExistsError):
                    with audio_stage('sfx',self.folder): pass
            self.assertFalse((self.folder/'.audio-gpu.lock').exists()); self.assertEqual(stop.call_count,2)
            with self.assertRaises(RuntimeError):
                with audio_stage('sfx',self.folder): raise RuntimeError('provider failed')
            self.assertFalse((self.folder/'.audio-gpu.lock').exists())

    def test_render_guard_rejects_live_voice_model(self):
        import gpu_lifecycle as gl
        with patch.object(gl,'configuration',return_value={'omnivoice':{'container':'fixture'}}),patch.object(gl,'container_state',return_value=True):
            with self.assertRaises(RuntimeError): renderer_guard()

    def test_render_holds_exclusive_gpu_lock_until_exit(self):
        import gpu_lifecycle as gl
        with patch.object(gl,'WORKSPACE',self.folder),patch.object(gl,'configuration',return_value={'omnivoice':{'container':'fixture'}}),patch.object(gl,'container_state',return_value=False):
            with gl.render_stage():
                self.assertTrue((self.folder/'.audio-gpu.lock').exists())
                with self.assertRaises(FileExistsError):
                    with audio_stage('sfx',self.folder): pass
            self.assertFalse((self.folder/'.audio-gpu.lock').exists())

    def test_historical_flow_payload_is_inspectable_but_submission_is_disabled(self):
        from flow_assets import submit,batch_payload
        from uuid import uuid4
        pid,vid,sid,mid=[str(uuid4()) for _ in range(4)]
        prompt='Isolated action pose: weight on planted left foot, head turning toward sound.'
        p=copy.deepcopy(self.plan)
        p['horror']['flow']={'project_id':pid,'video_id':vid,'material_id':'horror_cartoon','endpoint':'http://fixture'}
        p['horror']['assets']=[{'views':[{'frames':[{'flow_binding':{'orientation':'VERTICAL','scene_id':sid,
            'entity_media_ids':[mid],'prompt_sha256':digest(prompt)}}]}]}]
        class Response:
            def __init__(inner,data): inner.data=data
            def raise_for_status(inner): pass
            def json(inner): return inner.data
        class Session:
            def __init__(inner): inner.posts=[]
            def get(inner,url,**kwargs):
                if url.endswith('/health'): return Response({'extension_connected':True})
                if url.endswith('/characters'): return Response([{'media_id':mid}])
                if url.endswith('/scenes'): return Response([{'id':sid,'prompt':prompt,'chain_type':'ROOT'}])
                return Response({'material':'horror_cartoon'})
            def post(inner,url,**kwargs): inner.posts.append((url,kwargs)); return Response({'queued':1})
        session=Session()
        with self.assertRaisesRegex(ValueError,'prompt_export_only'):
            submit(p,self.folder/'flow.json',session)
        self.assertEqual(session.posts,[])
        request=batch_payload(p)['requests'][0]
        self.assertEqual(request['type'],'GENERATE_IMAGE'); self.assertEqual(request['provider'],'flow')
        p['horror']['assets'][0]['views'][0]['frames'][0]['flow_binding']['entity_media_ids']=['CAMSbad']
        with self.assertRaises(ValueError): batch_payload(p)

    def test_full_normalization_and_preparation_keep_horror_cast_and_receipts(self):
        spec=importlib.util.spec_from_file_location('example',ROOT/'local_tools/v4_smoke/build_plan.py')
        example=importlib.util.module_from_spec(spec); spec.loader.exec_module(example)
        clock=self.folder/'clock.wav'; wavfile.write(clock,48000,np.zeros(540*800,np.float32))
        full=example.make_plan(clock); full.update({k:copy.deepcopy(v) for k,v in self.plan.items() if k!='sections'})
        full['technical_fixture']=False
        section=full['sections'][0]; section.pop('speech')
        section['narration_segments']=copy.deepcopy(self.plan['sections'][0]['narration_segments'])
        section['narration']=' '.join(s['text'] for s in section['narration_segments'])
        for beat in section['beats']:
            beat['narration_anchor']={'segment_id':'n1'}; beat.pop('start_frame'); beat.pop('end_frame')
        from v3_contract import normalize_plan
        from v4_contract import validate_files
        draft=normalize_plan(full)
        from v4_pipeline import prepare
        from types import SimpleNamespace
        raw=self.folder/'generated.wav'; wavfile.write(raw,24000,np.ones(9000,np.float32)*.001)
        class Fake:
            receipt={'unit_fixture':True}
            def clone(inner,*args): return raw,'fixture'
        args=SimpleNamespace(plan=self.folder/'draft.json',tts_endpoint='mock')
        def fake_prepare(plan,sec,output,endpoint):
            return prepare_section(plan,sec,output,endpoint,Fake())
        with patch('v4_pipeline.prepare_section',side_effect=fake_prepare):
            timed=prepare(draft,self.folder,args)
        self.assertEqual(timed['phase'],'timed'); self.assertTrue(timed['visual_reference_policy']['kage']['enabled'])
        validate_files(timed,self.folder)
        bad=copy.deepcopy(timed); bad['sections'][0]['speech']['utterances'][0]['speech_end']+=.01
        with self.assertRaises(ValueError): validate_files(bad,self.folder)
        bad=copy.deepcopy(timed); bad['cast']['narrator']='dialogue-fixture'
        with self.assertRaises(ValueError): normalize_plan(bad)

    def test_horror_snapshot_is_independent_and_retains_reference_identity(self):
        from horror_snapshot import freeze_horror_assets
        p=copy.deepcopy(self.plan); section=p['sections'][0]
        raw=self.folder/'generated.wav'; wavfile.write(raw,24000,np.ones(9000,np.float32)*.001)
        class Fake:
            receipt={'unit_fixture':True}
            def clone(inner,*args): return raw,'fixture'
        section['speech']=prepare_section(p,section,self.folder/'voice.wav','mock',Fake())
        expected=configuration_identity(p,section)['sha256']
        frozen=self.folder/'run'; frozen.mkdir()
        freeze_horror_assets(p,self.folder,frozen)
        self.assertEqual(configuration_identity(p,section)['sha256'],expected)
        self.assertTrue(Path(p['cast']['library']).is_relative_to(frozen))
        self.reference.unlink()
        resolve_references(p,section)


if __name__=='__main__': unittest.main()
