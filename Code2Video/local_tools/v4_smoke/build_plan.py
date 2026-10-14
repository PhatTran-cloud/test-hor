"""Portable deterministic technical fixture; no narration or applied-skill claim."""
import json
import sys
from pathlib import Path
import numpy as np
from scipy.io import wavfile
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from v4_contract import digest,sha256,normalize_v4
from output_paths import get_output_root


def make_plan(audio):
    objects=[]
    for id,role,identity in [('lit_leaf','hero','veined stylized leaf receiving a signal'),
        ('shade_leaf','support','same leaf construction without the signal'),('signal','support','golden transport point'),
        ('leaf_response','support','localized response ring'),('comparison_axis','support','shared comparison baseline'),
        ('vein_insert','support','macro vein branch detail')]:
        objects.append({'id':id,'role':role,'identity':identity,'initial_state':{'response':0},
            'craft':{'silhouette':'tapered curved leaf or function-specific graphic','construction':'original SVG paths and branching veins',
                'material':'matte stylized ink with warm highlight','references':['authored construction study; no species claim'],
                'fidelity_limits':'graphic metaphor; not a botany simulation'}})
    common={'renderer':'remotion','renderer_reason':'SVG layers and editorial macro composition',
        'scene_type':'2d','render_spec':{'project_dir':str(Path(__file__).parent/'browser'),'entry_point':'src/index.tsx',
            'composition_id':'V4RainforestStudy','time_model':'absolute_frame'},
        'camera':{'purpose':'follow the signal then compare and inspect the same leaf','implementation':'cameraTransform'},
        'visual_thesis':'transport produces a visible response that persists into comparison',
        'handoff':{'type':'cut','reason':'preserve the same leaf position and response','carry_state':['lit_leaf.response']}}
    shots=[]
    specs=[('canopy_cause',0,180,['arrival_beat'],['lit_leaf','shade_leaf','signal','leaf_response'],
            {'kind':'cause_effect','entities':['signal','lit_leaf'],'cause':'arrival','result':'leaf response','implementation':'signalTravel'}),
           ('comparison_hold',180,360,['arrival_beat','difference_beat'],['lit_leaf','shade_leaf','comparison_axis'],
            {'kind':'comparison','entities':['lit_leaf','shade_leaf'],'variable':'signal response','fair_conditions':'same silhouette and scale',
                'implementation':'comparisonColumns'}),
           ('macro_insert',360,540,['difference_beat'],['lit_leaf','vein_insert'],
            {'kind':'scale','entities':['lit_leaf','vein_insert'],'reference':'same lit leaf','scale_relation':'1 to 2.8 illustrative camera zoom',
                'implementation':'scaleView'})]
    symbols={'lit_leaf':'Leaf','shade_leaf':'Leaf','signal':'signalTravel','leaf_response':'ring',
             'comparison_axis':'comparison','vein_insert':'veins'}
    for id,start,end,beats,ids,pattern in specs:
        shot={**common,'id':id,'start_frame':start,'end_frame':end,'duration_frames':end-start,
            'beat_ids':beats,'object_ids':ids,'attention':['lit_leaf'],'pattern':pattern,
            'execution':{'contract_consumer':'productionContract','support_files':['src/v4-runtime.ts'],
                'review_frames':[start+35,end-20],
                'objects':{obj:{'symbol':symbols[obj],'motion_mode':'reactive' if obj=='lit_leaf' else 'passive',
                    'behavior':'signal-dependent response or deliberate quiet comparison',
                    'layout':{'bounds':[200,80,1520,920],'overlap_policy':'intentional',
                              'reason':'authored environmental/optical layers; macro deliberately crops the same leaf'}} for obj in ids}}}
        if id!='macro_insert':
            shot['execution']['objects']['lit_leaf']['layout']={'bounds':[460,330,360,410],'overlap_policy':'avoid'}
            shot['execution']['objects']['shade_leaf']['layout']={'bounds':[1100,330,360,410],'overlap_policy':'avoid'}
        if id=='comparison_hold':
            shot['execution']['objects']['comparison_axis']['layout']={'bounds':[470,800,990,110],'overlap_policy':'avoid'}
        if id=='canopy_cause':
            shot['events']=[{'id':'signal_arrival','kind':'vfx','source_object':'signal','target_objects':['lit_leaf'],
                'cause':'signal reaches leaf','action':'point travels into leaf tip','reaction':'local ring and changed leaf light',
                'aftermath':'warm response persists in state track','implementation':'envelope',
                'representation':'illustrative localized ring, not biological radiation',
                'transport':'signal point reaches leaf before optical response',
                'interaction':'response alters only lit leaf state',
                'lighting_response':'localized leaf warms while comparison leaf stays unchanged',
                'start_frame':110,'peak_frame':126,'end_frame':176}]
        if id=='macro_insert':
            shot['b_roll']={'function':'inspect branching structure','relation_to_main':'same leaf used in comparison',
                'construction':'authored SVG macro insert','anchor':'difference_beat','return_handoff':'fade with leaf state retained'}
            shot['handoff']={'type':'fade','reason':'end the construction study without an added black slot',
                'carry_state':['lit_leaf.response'],'implementation':'handoff'}
        shots.append(shot)
    plan={'schema_version':4,'phase':'authored','technical_fixture':True,'topic':'V4 rainforest construction study',
        'content_profile':{'kind':'storytelling_rich'},'sound_design':'adaptive',
        'visual_system':{'palette':['#071c26','#184539','#e8c978'],'typography':'Georgia only for functional comparison labels',
            'shape_language':'veined leaf paths, layered canopy, restrained signal accent'},
        'sections':[{'id':'section_1','title':'Signal, consequence, comparison','visual_thesis':common['visual_thesis'],
            'narration':'','objects':objects,'beats':[
                {'id':'arrival_beat','purpose':'understand a transported cause','before':'no signal response','after':'leaf response persists',
                 'narration_anchor':{'segment_id':'fixture_a'},'visual_evidence':'point arrival and changed leaf','completion':'response persists',
                 'start_frame':0,'end_frame':240},
                {'id':'difference_beat','purpose':'compare and inspect the consequence','before':'one response observed','after':'difference and branching structure visible',
                 'depends_on':['arrival_beat'],'narration_anchor':{'segment_id':'fixture_b'},'visual_evidence':'same-sized paired leaves then macro',
                 'completion':'macro connects to same leaf','start_frame':240,'end_frame':540}],
            'speech':{'file':str(audio),'sha256':sha256(audio),'frames':540,'fps':60,'time_stretch':False,'script_sha256':digest(''),
                'anchors':[{'id':'fixture_a','start_frame':0,'end_frame':240,'confidence':'measured_segment'},
                           {'id':'fixture_b','start_frame':240,'end_frame':540,'confidence':'measured_segment'}]},
            'state_tracks':[{'id':'leaf_response_track','object_id':'lit_leaf','property':'response','from':0,'to':1,
                'start_frame':110,'end_frame':150,'cause':'signal arrival'}],
            'shots':shots,'sfx_cues':[],'sound_intent':'silent technical fixture; production sound not evaluated'}]}
    plan['production_packet']={
        'brief':{'audience':'pipeline reviewers','question':'Does a signal response survive a cut?',
                 'takeaway':'the same authored state persists through comparison and macro',
                 'visual_thesis':'a transported signal changes one leaf while its counterpart stays unchanged'},
        'research':{'sources':[{'id':'kage_reference','title':'Kage visual research',
            'url':'https://github.com/MengTo/kage','finding':'layered foreground and environmental depth support camera continuity',
            'visual_decision':'original SVG canopy layers; no imported code/art or website HUD'}],
            'claims':[{'id':'signal_metaphor','text':'an illustrative signal creates a persistent response',
                'kind':'metaphor','visual_treatment':'graphic transport and warmed leaf; no botanical mechanism claimed'}]},
        'representative':{'shot_id':'comparison_hold','reason':'proves same identity/state and legible comparison after the cause',
            'acceptance':['same-sized leaf silhouettes','left response remains bright','baseline/labels do not overlap leaves']},
        # Tests do not consult the user's installed production skills. Leave
        # these empty rather than fabricate receipts or require one old PC.
        # A real authored production still requires all applicable resources.
        'consulted_resources':[]}
    return normalize_v4(plan)


if __name__=='__main__':
    folder=get_output_root()/'v4_smoke_inputs'
    folder.mkdir(parents=True,exist_ok=True)
    audio=folder/'fixture_clock.wav'
    wavfile.write(audio,48000,np.zeros(540*800,dtype=np.float32))
    path=folder/'plan.json'
    path.write_text(json.dumps(make_plan(audio),indent=2),encoding='utf-8')
    print(path)
