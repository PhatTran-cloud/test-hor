"""Compact shared-scene staging. Planning metadata is never rendered evidence."""
import copy
import hashlib
import json

LINK_KINDS = {'question_answer', 'cause_reaction', 'evidence_return', 'spatial',
              'sound_bridge', 'location_change', 'time_change', 'parallel', 'end'}


def enabled(plan):
    revision = plan.get('production_packet', {}).get('illustration_direction', {}).get('staging_revision')
    if revision is not None and (isinstance(revision, bool) or revision != 1):
        raise ValueError('Unknown scene staging revision')
    return revision == 1


def nonempty(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(label+' must be nonempty text')


def validate_staging(plan):
    if not enabled(plan):
        return
    direction = plan['production_packet']['illustration_direction']
    if direction.get('contract_revision') != 1:
        raise ValueError('Scene staging needs the directed illustration contract')
    objects = {o['id']: o for sec in plan['sections'] for o in sec['objects']}
    assets = {a['id']: a for a in plan.get('horror', {}).get('assets', [])}
    shots = [sh for sec in plan['sections'] for sh in sec['shots']]
    worlds = {w['id']: w for w in direction['scene_worlds']}
    views = {}

    def plate(oid):
        if oid not in objects:
            raise ValueError('Staging references an unknown background plate object')
        spec = objects[oid].get('illustration', {})
        if spec.get('method') == 'generated':
            ids = spec.get('asset_ids', [])
            if not ids or any(aid not in assets or assets[aid].get('illustration_role') != 'background' for aid in ids):
                raise ValueError('A staging plate must use background assets, not baked actors or props')

    for wid, world in worlds.items():
        stage = world.get('staging')
        if not isinstance(stage, dict):
            raise ValueError('Scene world needs one shared staging definition')
        plate(stage.get('master_plate_object_id'))
        rows = stage.get('views')
        if not isinstance(rows, list) or not rows:
            raise ValueError('Staging needs named views')
        lookup = {}
        for view in rows:
            if not isinstance(view, dict):
                raise ValueError('Stage view must be an object')
            vid = view.get('id'); nonempty(vid, 'Stage view id')
            if vid in lookup or view.get('kind') not in {'master', 'crop', 'new_view'}:
                raise ValueError('Stage views need unique IDs and a supported kind')
            nonempty(view.get('framing'), 'Stage view framing')
            plate(view.get('plate_object_id'))
            if view['kind'] in {'master', 'crop'} and view['plate_object_id'] != stage['master_plate_object_id']:
                raise ValueError('Master/crop views reuse the same plate; a different angle needs new_view')
            lookup[vid] = view
        views[wid] = lookup
        details = stage.get('static_details', [])
        if not isinstance(details, list):
            raise ValueError('Static background details must be a list')
        ids = set()
        for detail in details:
            if not isinstance(detail, dict):
                raise ValueError('Static background detail must be an object')
            did = detail.get('id'); nonempty(did, 'Static detail id')
            if did in ids or did in objects:
                raise ValueError('Static detail IDs are unique; interactive objects remain separate instances')
            ids.add(did)
            nonempty(detail.get('description'), 'Static detail description')
            plate(detail.get('plate_object_id'))
            readable = detail.get('readable_in_view_ids')
            if (not isinstance(readable, list) or not readable or len(set(readable)) != len(readable)
                    or any(v not in lookup or lookup[v]['plate_object_id'] != detail['plate_object_id'] for v in readable)):
                raise ValueError('Static detail must name the views of its own plate where it is readable')
    seen = {}
    for index, shot in enumerate(shots):
        wid = shot.get('scene_id')
        vid = shot.get('camera', {}).get('stage_view_id')
        if wid not in views or vid not in views[wid]:
            raise ValueError('Shot camera must select a known view in its own scene')
        if views[wid][vid]['plate_object_id'] not in shot['object_ids']:
            raise ValueError('Selected background plate must be present in the shot inventory')
        handoff = shot['handoff']; kind = handoff.get('link_kind')
        next_shot = shots[index+1] if index+1 < len(shots) else None
        if kind not in LINK_KINDS or (next_shot is None) != (kind == 'end'):
            raise ValueError('Handoff needs a story link kind; only the last shot ends')
        if handoff.get('to_shot_id') != (next_shot['id'] if next_shot else None):
            raise ValueError('Story link must point to the actual next shot')
        if next_shot:
            if kind == 'location_change' and next_shot.get('scene_id') == wid:
                raise ValueError('Location change must change scene geography')
            if kind in {'spatial', 'evidence_return'} and next_shot.get('scene_id') != wid:
                raise ValueError('Spatial/evidence-return link must preserve scene geography')
            if kind == 'evidence_return':
                earlier = seen.get(handoff.get('returns_to_shot_id'))
                if not earlier or earlier.get('scene_id') != next_shot.get('scene_id'):
                    raise ValueError('Evidence return must reference an earlier shot in the destination scene')
            elif handoff.get('returns_to_shot_id') is not None:
                raise ValueError('Only evidence_return declares returns_to_shot_id')
        if kind == 'end' and handoff.get('returns_to_shot_id') is not None:
            raise ValueError('Ending does not return to another shot')
        seen[shot['id']] = shot


def resolve_staging(plan, shot):
    if not enabled(plan):
        return None
    world = next(w for w in plan['production_packet']['illustration_direction']['scene_worlds'] if w['id'] == shot['scene_id'])
    stage = world['staging']
    view = next(v for v in stage['views'] if v['id'] == shot['camera']['stage_view_id'])
    same_scene = [s for sec in plan['sections'] for s in sec['shots'] if s.get('scene_id') == shot['scene_id']]
    all_ids = {oid for s in same_scene for oid in s['object_ids']}
    return copy.deepcopy({'scene_id':world['id'], 'master_plate_object_id':stage['master_plate_object_id'],
        'view':view, 'static_details':[d for d in stage.get('static_details', []) if view['id'] in d['readable_in_view_ids']],
        'outside_this_shot_object_ids':sorted(all_ids-set(shot['object_ids'])),
        'outside_note':'Outside this shot does not establish an exit, deletion or reset; preserve declared continuity.',
        'story_link':shot['handoff']})


def plate_usage(plan, asset):
    if not enabled(plan) or asset.get('illustration_role') != 'background':
        return []
    oid = asset['object_id']; rows = []
    for world in plan['production_packet']['illustration_direction']['scene_worlds']:
        stage = world['staging']
        relevant = [v for v in stage['views'] if v['plate_object_id'] == oid]
        if relevant:
            rows.append({'scene_id':world['id'], 'views':copy.deepcopy(relevant),
                'static_details':copy.deepcopy([d for d in stage.get('static_details', []) if d['plate_object_id'] == oid]),
                'instruction':'One reusable empty plate for these views. Keep listed static details readable; dynamic/interacting props and actors are separate assets.'})
    return rows


def plate_fingerprint(plan, asset):
    usage = plate_usage(plan, asset)
    if not usage:
        return None
    relevant_ids = {row['scene_id'] for row in usage}
    worlds = [w for w in plan['production_packet']['illustration_direction']['scene_worlds'] if w['id'] in relevant_ids]
    payload = {'asset_id':asset['id'], 'identity':asset['identity'], 'worlds':worlds,
        'style_bible':plan['horror']['style_bible'], 'visual_system':plan.get('visual_system', {})}
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()


def plate_current(plan, asset):
    expected = plate_fingerprint(plan, asset)
    return expected is None or asset.get('scene_staging_sha256') == expected
