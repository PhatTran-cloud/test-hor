"""Self-contained request-only fixture; never production approval or artwork."""
import copy


def kage_plan():
    objects=[]; assets=[]
    specs=[('leaf_fg','hero','foreground','2d'),('trunk_mg','support','midground','3d'),
           ('forest_bg','environment','background','2d'),('insect','support','midground','2d'),
           ('fog','environment','background','procedural')]
    for oid,role,depth,route in specs:
        spec={'method':'procedural','reason':'Authored atmospheric layer, fixture only'} if route=='procedural' else {'method':'generated','asset_ids':['art_'+oid]}
        objects.append({'id':oid,'identity':oid+' original benchmark component','role':role,
            'initial_state':{'activity':'rest'},'illustration':spec,
            'craft':{'silhouette':'recognizable component','construction':'separate editable component',
                'material':'authored original surface','references':['request-only construction proposal'],
                'fidelity_limits':'synthetic fixture; not artwork or biology proof'}})
        if route=='procedural': continue
        pose={'id':'rest','description':'readable isolated resting component','width':256,'height':256,
            'root_anchor':[128,128],'ground_anchor':[128,256],'sockets':{},'hold_frames':12}
        asset={'id':'art_'+oid,'object_id':oid,'provider':'lowbudget3d' if route=='3d' else 'flow',
            'kind':'model_3d' if route=='3d' else 'sprite_sequence' if oid=='leaf_fg' else 'layer' if oid=='forest_bg' else 'prop',
            'illustration_role':'background' if oid=='forest_bg' else 'environment_layer' if oid=='leaf_fg' else 'prop',
            'requires_alpha':route=='2d' and oid!='forest_bg','scene_ids':['forest_world'],
            'identity':oid+'; original fixture artwork request, no species claim',
            'action':{'intent':'make latent activity discoverable','mechanics':'separate stable anchors; no arbitrary idle loop',
                'entry_state':'rest','exit_state':'recognizable evidence','source_ids':['construction_proposal'],'contact_requirements':[]},
            'design_semantics':{'role':role,'meaning':'a hidden activity becomes readable',
                'recognition_traits':['consistent silhouette'],'parts_or_layers':['independent component'],
                'anchors':{'root':'registered after artwork return'},'variants':['rest','revealed'],
                'closest_camera_use':'macro-readable original surface, no flattened camera plate'},
            'views':[{'id':'front','camera_region':'front','frames':[pose]}]}
        if route=='3d':
            asset['views']=[{'id':'front','camera_region':'front three-quarter','inspection_purpose':'silhouette and scale'},
                            {'id':'closest','camera_region':'closest macro use','inspection_purpose':'surface and part fidelity'}]
            asset['model_spec']={'representation':'threejs_module','dimensions':{'unit':'metres','size':[1,3,1]},
                'parts':[{'id':'bole','parent_id':None,'pivot':[0,0,0],'material_region':'bark'}],
                'anchors':{'ground':[0,0,0]},'variants':['dry'], 'surface_regions':['bark'],
                'texture_plan':[{'region':'bark','method':'authored surface after domain research'}],
                'articulation':'fixed bole; no organic deformation claimed','closest_camera_use':'macro bark inspection'}
        assets.append(asset)
    roles={'leaf_fg':['foreground'],'trunk_mg':['midground','interactive_prop'],
        'forest_bg':['background'],'insect':['subject','support'],'fog':['atmosphere']}
    behaviors={o['id']:{'mode':'passive','motivation':'intentional baseline before discovery',
        'trigger':{'kind':'intentional_hold','reason':'establish the normal world'},
        'response':'hold','secondary_response':'none during baseline','settle':'remain stable',
        'exit_state':{'activity':'rest'}} for o in objects}
    shot={'id':'forest_open','scene_id':'forest_world','beat_ids':['forest_idea'],
        'renderer':'remotion','scene_type':'3d','renderer_reason':'Remotion hosts spatial Three.js plus 2D layers',
        'visual_thesis':'latent activity becomes readable through occlusion',
        'attention':['insect'],'camera':{'purpose':'discover the source of a small signal',
            'information_intent':{'known_before':'forest looks quiet','hidden_before':'small source behind leaves',
                'reveals':'a localized activity source','target_object':'insect','reason_for_move_or_hold':'open the occluded region before following the source'}},
        'pattern':{'kind':'custom','entities':['leaf_fg','insect'],'reading_logic':'occlusion opens into specific evidence'},
        'object_ids':[o['id'] for o in objects],
        'components':{'required_roles':sorted({r for rs in roles.values() for r in rs}),'omissions':{},
            'items':[{'object_id':oid,'roles':roles[oid],'route':route} for oid,_,_,route in specs]},
        'attention_plan':[{'object_id':o['id'],'priority':'primary' if o['id']=='insect' else 'ambient' if o['id']=='fog' else 'secondary',
            'reason':'support the reveal without competing'} for o in objects],
        'behaviors':behaviors,
        'handoff':{'type':'cut','reason':'end this request-only benchmark','carry_state':[],
            'semantic_link':{'to_shot_id':None,'kind':'end','relation':'stop after discovery','invariants':[]}}}
    beat={'id':'forest_idea','purpose':'discover activity instead of repeating a noun',
        'before':'apparently quiet','after':'a source becomes readable','narration_anchor':{'segment_id':'n1'},
        'visual_evidence':'layers open to reveal an original small source','completion':'source can be recognized',
        'direction':{'idea':'the forest is not truly silent','visual_proposition':'quietness is incomplete perception',
            'metaphor':{'source':'layered conversation','target':'many small activities coexist',
                'mapping':'different regions yield evidence at different moments','limits':'no literal speech or botanical mechanism asserted'},
            'adds_information':'source and scale absent from the narration','object_ids':['leaf_fg','insect','forest_bg'],
            'knowledge':{'before':'only apparent quiet','after':'one activity source identified','withheld':'all other sources'},
            'payoff':'the same source can motivate a later macro'}}
    return {'schema_version':4,'profile':'horror-v4.1','phase':'draft','technical_fixture':True,
        'topic':'Kage request-only illustration benchmark','language_id':'vi','tts_speed':1,
        'cast':{'library':'unused_fixture','narrator':'unused_fixture','characters':{}},
        'content_profile':{'kind':'storytelling_rich','genre':'horror'},'sound_design':'adaptive',
        'visual_system':{'palette':['#112126','#bf9b69'],'typography':'functional text only','shape_language':'original organic silhouettes',
            'bindings':{'color_roles':{'latent':'#112126','revealed':'#bf9b69'},'shape_roles':{'evidence':'localized shape'},
                'typography_roles':{'functional':'only if necessary'},'transition_rules':{'follow':'same source retains identity'}}},
        'horror':{'artwork_style':'kage_illustrated_hybrid','artwork_provider':'hybrid',
            'visual_reference':{'primary':'kage'},'kage_reference':True,
            'illustrator':{'mode':'prompt_export_only','generation_operator':'human user','model':'fixture 2D model',
                'chroma_key_color':'#00FF00','three_d_skill':'lowbudget3d'},
            'voice_provider':'omnivoice','sfx_provider':'stable_audio_3_small_sfx',
            'style_bible':dict.fromkeys(['canonical_prompt','proportions','materials','lighting','depth','identity_rules'],
                'Original Kage-informed fixture artwork; request only, not approval'),'assets':assets},
        'production_packet':{'brief':{'audience':'pipeline reviewers','question':'Do complete-shot asset requests preserve meaning?',
                'takeaway':'request coverage is distinct from artwork','visual_thesis':'unseen activity becomes readable'},
            'research':{'sources':[{'id':'construction_proposal','title':'Synthetic fixture proposal','url':'https://example.com/fixture',
                'finding':'not an observational study','visual_decision':'request-only benchmark, no biology proof'}],
                'claims':[{'id':'forest_metaphor','text':'layered activity is like conversation','kind':'metaphor',
                    'visual_treatment':'original source revealed through layers'}]},
            'representative':{'shot_id':'forest_open','reason':'check mixed-route coverage','acceptance':['preserve the same source and world']},
            'visual_style_decision':{'status':'USER_SELECTED','selected_style':'kage_illustrated_hybrid','primary_reference':'kage',
                'authorization':{'reviewer':'human user','request':'SYNTHETIC TEST METADATA ONLY; NOT PRODUCTION AUTHORIZATION'}},
            'character_setting_brief':{'script_facts':['separate rainforest benchmark, no cast'],
                'approved_setting':{'status':'fixture only; era unspecified'},'style':'original layered Kage-informed artwork'},
            'illustration_direction':{'contract_revision':1,'target_artwork':'kage','scene_worlds':[{'id':'forest_world',
                'layout':'foreground leaf, midground trunk/source, deep forest','perspective':'coherent original depth',
                'lighting':'same practical direction across layers','required_props':['trunk_mg','insect'],'crop_safety':'reveal region stays readable',
                'semantic_layers':[{'object_id':oid,'depth':depth,'information':'support latent activity becoming visible',
                    'function':'evidence or meaningful occlusion'} for oid,_,depth,_ in specs]}]}},
        'sections':[{'id':'section_1','title':'request benchmark','visual_thesis':shot['visual_thesis'],
            'narration':'Rừng mưa không bao giờ thật sự im lặng.',
            'narration_segments':[{'id':'n1','text':'Rừng mưa không bao giờ thật sự im lặng.','role':'narrator'}],
            'objects':objects,'beats':[beat],'shots':[shot],'sfx_cues':[]}]}
