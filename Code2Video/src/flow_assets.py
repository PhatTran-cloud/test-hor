"""One Flowkit image batch for explicitly mapped reusable pose assets."""
import json
from pathlib import Path
from uuid import UUID
import requests
from v4_contract import digest


def uuid(value):
    try:
        parsed=UUID(value)
    except (ValueError,TypeError,AttributeError):
        raise ValueError('Flow media/project/entity/scene IDs must be UUIDs, never CAMS strings')
    return str(parsed)


def batch_payload(plan):
    flow=plan['horror'].get('flow',{})
    project=uuid(flow.get('project_id')); video=uuid(flow.get('video_id'))
    if not flow.get('material_id'): raise ValueError('Flow project must use the approved horror artwork material')
    requests=[]
    for asset in plan['horror'].get('assets',[]):
        for view in asset['views']:
            for pose in view['frames']:
                binding=pose.get('flow_binding',{})
                if binding.get('orientation') not in {'HORIZONTAL','VERTICAL'}:
                    raise ValueError('Use the configured asset orientation, never a default film orientation')
                if not binding.get('entity_media_ids'):
                    raise ValueError('Canonical entity image references must exist before pose generation')
                for media_id in binding['entity_media_ids']: uuid(media_id)
                if not binding.get('prompt_sha256'):
                    raise ValueError('Verify the Flow scene action-only prompt against the exported asset request')
                requests.append({'type':'GENERATE_IMAGE','provider':'flow','project_id':project,'video_id':video,
                                 'scene_id':uuid(binding.get('scene_id')),'orientation':binding['orientation']})
    if not requests: raise ValueError('No explicitly bound pose requests')
    if len({r['scene_id'] for r in requests})!=len(requests):
        raise ValueError('Each pose uses a distinct image job; repeated scene IDs would reuse the same image')
    return {'requests':requests}


def submit(plan,output,session=None):
    raise ValueError('Illustration is prompt_export_only: the human user runs Flow. Use production.py asset-brief; no automated submission is permitted.')


def status(plan,output):
    flow=plan['horror']['flow']; base=flow.get('endpoint','http://127.0.0.1:8100').rstrip('/')
    response=requests.get(base+'/api/requests/batch-status',params={'video_id':flow['video_id'],'type':'GENERATE_IMAGE'},timeout=30)
    response.raise_for_status(); result=response.json()
    Path(output).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result
