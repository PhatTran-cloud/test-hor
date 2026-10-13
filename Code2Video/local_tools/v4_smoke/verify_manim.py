import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from renderers import render_unit
from output_paths import get_output_root

folder=get_output_root()/'v4_adapter_clock_check'
contract={'schema_version':4,'fps':60,'absolute_start_frame':180,'duration_frames':60,
          'objects':[{'id':'point','initial_state':{'x':0}},{'id':'axis','initial_state':{}}],
          'shot':{'id':'manim_clock','object_ids':['axis','point'],'pattern':{'kind':'custom'},
            'execution':{'review_frames':[180,210,239], 'objects':{
                'axis':{'layout':{'overlap_policy':'intentional'}},
                'point':{'layout':{'overlap_policy':'intentional'}}}}},
          'state_tracks':[{'object_id':'point','property':'x','from':0,'to':3,'start_frame':0,'end_frame':150}]}
unit={'renderer':'manim','scene_type':'2d','source':str(Path(__file__).parent/'manim_scene.py'),
      'scene_name':'V4ClockProof','duration_frames':60}
video=render_unit(unit,folder,'manim_clock',production_contract=contract)
log=(folder/'manim_clock_render.log').read_text(encoding='utf-8')
if 'V4_CLOCK_PROOF absolute_start=180 point.x=3' not in log:
    raise ValueError('Manim did not consume the absolute frame/state contract')
print(json.dumps({'video':video,'absolute_clock':'PASS','runtime_samples':3,'visual_quality':'UNVERIFIED'},indent=2))
