"""Reusable character design and compact ensemble notes in the existing V4 packet."""
import copy
import math


CHARACTER_ROLES = {'character_pose', 'character_part', 'character_model', 'crowd_group'}
IMPORTANCE = {'principal', 'supporting', 'extra'}
ATTENTION_ROLES = {'primary', 'secondary', 'ambient', 'suppressed'}


def direction(plan):
    return plan.get('production_packet', {}).get('character_direction')


def require(value, fields, label):
    if not isinstance(value, dict):
        raise ValueError(label+' must be an object')
    for field in fields:
        if field not in value or value[field] is None or value[field] in ('', [], {}):
            raise ValueError(label+' needs '+field)


def index(items, label):
    if not isinstance(items, list):
        raise ValueError(label+' must be a list')
    result = {}
    for item in items:
        require(item, ('id',), label)
        if not isinstance(item['id'], str) or not item['id'].strip() or item['id'] in result:
            raise ValueError(label+' needs unique string IDs')
        result[item['id']] = item
    return result


def actor_reference(obj):
    for field in ('character_id','crowd_group_id'):
        if field in obj and (not isinstance(obj[field],str) or not obj[field].strip()):
            raise ValueError(field+' needs a nonempty registered ID')
    if obj.get('character_id') and obj.get('crowd_group_id'):
        raise ValueError('An instance cannot be both an individual and an anonymous crowd')
    if obj.get('character_id'):
        return 'character', obj['character_id']
    if obj.get('crowd_group_id'):
        return 'crowd', obj['crowd_group_id']
    if obj.get('entity_type') in {'character', 'crowd'}:
        raise ValueError('A visible actor needs character_id or crowd_group_id')
    return None, None


def cast_entries(shot):
    entries = shot.get('cast', [])
    if not isinstance(entries, list) or any(not isinstance(e, dict) for e in entries):
        raise ValueError('Shot cast must be a list of instance notes')
    ids = [e.get('object_id') for e in entries]
    if any(not isinstance(i, str) or not i.strip() for i in ids) or len(set(ids)) != len(ids):
        raise ValueError('Shot cast needs unique object IDs')
    return entries


def _gaze(value, objects):
    if (not isinstance(value, str) or not value.strip() or
            not (value in objects or value in {'camera', 'down', 'away', 'eyes_closed'}
                 or value.startswith('offscreen:') and len(value) > len('offscreen:'))):
        raise ValueError('Gaze must name an object, camera/down/away/eyes_closed, or offscreen:SOURCE')


def validate_character_direction(plan, for_illustration=False):
    registry = direction(plan)
    objects = [o for sec in plan['sections'] for o in sec['objects']]
    character_assets = [a for a in plan.get('horror', {}).get('assets', [])
                        if a.get('illustration_role') in CHARACTER_ROLES]
    if registry is None:
        from illustration_direction import lightweight
        new_crowds = any(a.get('illustration_role')=='crowd_group' for a in character_assets) or any('crowd_group_id' in o for o in objects)
        if new_crowds or lightweight(plan) and (character_assets or any(actor_reference(o)[0] for o in objects)):
            raise ValueError('New horror characters need production_packet.character_direction and shot cast notes')
        return
    require(registry, ('contract_revision', 'tone', 'humor'), 'Character direction')
    if isinstance(registry['contract_revision'], bool) or registry['contract_revision'] != 1:
        raise ValueError('Unknown character direction revision')
    if registry['tone'] != 'restrained_horror' or registry['humor'] != 'none':
        raise ValueError('Current character direction is restrained_horror with humor=none')
    characters = index(registry.get('characters'), 'Characters')
    groups = index(registry.get('crowd_groups'), 'Crowd groups')
    for character in characters.values():
        require(character, ('importance', 'identity', 'states'), 'Character')
        if character['importance'] not in IMPORTANCE:
            raise ValueError('Character importance is principal, supporting or extra')
        for state in index(character['states'], 'Character states').values():
            require(state, ('emotion', 'intent'), 'Character state')
    for group in groups.values():
        require(group, ('identity', 'grouping_reason', 'states'), 'Crowd group')
        for state in index(group['states'], 'Crowd states').values():
            require(state, ('appearance', 'behavior'), 'Crowd state')
    owners = {}
    for obj in objects:
        kind, ref = actor_reference(obj)
        if kind and (ref not in (characters if kind == 'character' else groups)):
            raise ValueError('Instance references an unknown character or crowd group')
        if obj['id'] in owners and owners[obj['id']] != (kind, ref):
            raise ValueError('Character/crowd ownership cannot change across sections')
        owners[obj['id']] = kind, ref
    for asset in character_assets:
        if not owners.get(asset['object_id'], (None, None))[0]:
            raise ValueError('Every generated character/crowd asset needs a registered actor instance')
    all_ids = {o['id'] for o in objects}
    used_characters = set()
    used_groups = set()
    last_states = {}
    for section in plan['sections']:
        lookup = {o['id']: o for o in section['objects']}
        for shot in section['shots']:
            entries = cast_entries(shot)
            visible = {oid for oid in shot['object_ids'] if actor_reference(lookup[oid])[0]}
            if {e['object_id'] for e in entries} != visible:
                raise ValueError('Shot cast must note every visible individual and crowd exactly once')
            for entry in entries:
                require(entry, ('attention_role', 'state_ids', 'blocking'), 'Cast note')
                if entry['attention_role'] not in ATTENTION_ROLES:
                    raise ValueError('Cast note needs a supported attention role')
                if entry['attention_role'] == 'primary' and entry['object_id'] not in shot['attention']:
                    raise ValueError('Primary actor must belong to the shot attention target')
                kind, ref = actor_reference(lookup[entry['object_id']])
                definition = (characters if kind == 'character' else groups)[ref]
                states = index(definition['states'], 'Performance states')
                ids = entry['state_ids']
                if not isinstance(ids, list) or not ids or any(not isinstance(s, str) or s not in states for s in ids):
                    raise ValueError('Cast note needs known performance state IDs')
                if kind == 'character':
                    require(entry, ('gaze_target',), 'Individual cast note')
                    _gaze(entry['gaze_target'], all_ids)
                    targets=entry.get('gaze_targets',{})
                    if not isinstance(targets,dict) or not set(targets) <= set(ids):
                        raise ValueError('Per-state gaze_targets must reference this shot state sequence')
                    for target in targets.values():
                        _gaze(target,all_ids)
                    used_characters.add(ref)
                    if for_illustration:
                        for sid in set(ids):
                            require(states[sid], ('expression', 'pose'), 'Drawable character performance')
                            require(states[sid]['expression'], ('eyes', 'brows', 'mouth'), 'Character expression')
                else:
                    used_groups.add(ref)
                    count = entry.get('count')
                    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
                        raise ValueError('Crowd note needs a positive visible member count')
                    if any(entry.get(k) for k in ('speaking', 'independent_action', 'individual_focus')):
                        raise ValueError('Promote a speaking, independently acting or individually focused extra to a character instance')
                    if entry['object_id'] in shot['attention'] and entry.get('focus_mode') != 'collective':
                        raise ValueError('A focused crowd must explicitly declare collective focus; individuals need separate IDs')
                previous=last_states.get(entry['object_id'])
                if (plan['phase']=='authored' and previous is not None and previous != ids[0]
                        and not entry.get('entry_change_reason')):
                    raise ValueError('Actor state changed across cuts without an entry_change_reason')
                last_states[entry['object_id']]=ids[-1]
            if plan['phase'] == 'authored' and entries:
                _validate_performance_tracks(shot, entries, all_ids)
    if for_illustration:
        for cid in used_characters:
            character = characters[cid]
            require(character, ('design',), 'Character illustration')
            require(character['design'], ('silhouette', 'proportions', 'costume', 'identity_anchors', 'detail_strategy'), 'Character design')
            if character['importance'] == 'principal':
                require(character['design'], ('face_features',), 'Principal character design')
    if plan['phase']=='authored' and any(d.get('unresolved') for d in
            [characters[cid] for cid in used_characters]+[groups[gid] for gid in used_groups]):
        raise ValueError('Resolve explicit character/crowd design choices before authored production')


def _validate_performance_tracks(shot, entries, objects):
    tracks = shot.get('performance_tracks', {})
    if not isinstance(tracks, dict) or set(tracks) != {e['object_id'] for e in entries}:
        raise ValueError('Authored actors need performance_tracks for every visible individual/group')
    for entry in entries:
        keys = tracks[entry['object_id']]
        if not isinstance(keys, list) or not keys:
            raise ValueError('Performance track must contain absolute-frame state keys')
        previous = -1
        sequence = []
        for key in keys:
            require(key, ('frame', 'state_id'), 'Performance key')
            frame = key['frame']
            if (isinstance(frame, bool) or not isinstance(frame, int) or frame <= previous
                    or not shot['start_frame'] <= frame < shot['end_frame']):
                raise ValueError('Performance keys need ordered section-absolute frames inside the shot')
            if key['state_id'] not in entry['state_ids']:
                raise ValueError('Performance key would invent an undeclared character/crowd state')
            if key.get('gaze_target') is not None:
                _gaze(key['gaze_target'], objects)
            if not sequence or sequence[-1] != key['state_id']:
                sequence.append(key['state_id'])
            previous = frame
        if keys[0]['frame'] != shot['start_frame'] or sequence != entry['state_ids']:
            raise ValueError('Performance track must execute the declared state sequence from the shot start')


def resolve_character_cast(plan, section, shot):
    registry = direction(plan)
    if registry is None:
        return None
    characters = index(registry['characters'], 'Characters')
    groups = index(registry['crowd_groups'], 'Crowd groups')
    objects = {o['id']: o for o in section['objects']}
    entries = cast_entries(shot)
    individual_ids = {objects[e['object_id']]['character_id'] for e in entries if objects[e['object_id']].get('character_id')}
    group_ids = {objects[e['object_id']]['crowd_group_id'] for e in entries if objects[e['object_id']].get('crowd_group_id')}
    crowd_count = sum(e['count'] for e in entries if objects[e['object_id']].get('crowd_group_id'))
    individuals = [e['object_id'] for e in entries if objects[e['object_id']].get('character_id')]
    return copy.deepcopy({'tone':registry['tone'], 'humor':registry['humor'], 'entries':entries,
        'characters':{i:c for i,c in characters.items() if i in individual_ids},
        'crowd_groups':{i:g for i,g in groups.items() if i in group_ids},
        'individual_instance_ids':individuals, 'crowd_count':crowd_count,
        'total_visible_people':len(individuals)+crowd_count})


def scene_cast_inventory(plan):
    scenes = {}
    if direction(plan) is None:
        return []
    for section in plan['sections']:
        for shot in section['shots']:
            cast = resolve_character_cast(plan, section, shot)
            scenes.setdefault(shot['scene_id'], {'scene_id':shot['scene_id'], 'shots':[]})['shots'].append({
                'shot_id':shot['id'], 'individual_instance_ids':cast['individual_instance_ids'],
                'crowd_count':cast['crowd_count'], 'total_visible_people':cast['total_visible_people'],
                'cast':cast['entries']})
    return list(scenes.values())


def asset_actor_context(plan, asset, pose=None):
    registry = direction(plan)
    if registry is None:
        return None
    obj = next((o for sec in plan['sections'] for o in sec['objects'] if o['id'] == asset['object_id']), None)
    kind, ref = actor_reference(obj) if obj else (None, None)
    if kind is None:
        return None
    definition = next(d for d in registry['characters' if kind == 'character' else 'crowd_groups'] if d['id'] == ref)
    data = copy.deepcopy(definition)
    if pose is not None:
        ids = pose.get('performance_state_ids', [])
        data['states'] = [s for s in data['states'] if s['id'] in ids]
    return {'kind':kind, 'tone':registry['tone'], 'humor':registry['humor'], 'definition':data,
            'member_count':pose.get('member_count') if pose else None}


def character_asset_fingerprint(plan, asset):
    context = asset_actor_context(plan, asset)
    if context is None:
        return None
    from v4_contract import digest
    brief=plan['production_packet'].get('character_setting_brief',{})
    art_brief={k:brief[k] for k in ['script_facts','approved_visual_age_bands','approved_setting',
        'reference_design_choices_to_review','style','state_design_correction'] if k in brief}
    # Actual drawable variants/files are bound by asset_digest. A valid excerpt
    # or tighter crop can reuse a reviewed superset without fabricating new art.
    return digest({'actor':context,'character_and_setting':art_brief,
        'style_bible':plan['horror']['style_bible'],'visual_system':plan.get('visual_system',{})})


def character_asset_current(plan, asset):
    expected = character_asset_fingerprint(plan, asset)
    return expected is None or asset.get('character_design_sha256') == expected


def validate_character_assets(plan):
    validate_character_direction(plan, for_illustration=True)
    if direction(plan) is None:
        return
    assets = {a['id']:a for a in plan['horror'].get('assets', [])}
    for asset in assets.values():
        context = asset_actor_context(plan, asset)
        if context is None:
            continue
        if asset['kind'] not in {'sprite_sequence', 'model_3d'}:
            raise ValueError('Character/crowd assets need animated sprites or a native model, not a prop shortcut')
        if context['kind'] == 'crowd' and asset.get('illustration_role') != 'crowd_group':
            raise ValueError('Anonymous group artwork must be declared as crowd_group')
        if context['kind'] == 'character' and asset.get('illustration_role') not in {'character_pose','character_part','character_model'}:
            raise ValueError('Individual artwork needs an explicit character pose/part/model role')
        states = {s['id'] for s in context['definition']['states']}
        poses = (asset['model_spec']['variants'] if asset['kind'] == 'model_3d' else
                 [p for v in asset['views'] for p in v['frames']])
        if not isinstance(poses, list) or not poses:
            raise ValueError('Actor asset needs explicit drawable/native performance variants')
        for pose in poses:
            require(pose,('id','performance_state_ids'),'Actor pose/variant')
            ids = pose.get('performance_state_ids', [])
            if (not isinstance(ids, list) or not ids
                    or any(not isinstance(s, str) or s not in states for s in ids) or len(set(ids)) != len(ids)):
                raise ValueError('Actor pose/variant needs known performance_state_ids')
            if context['kind'] == 'crowd':
                count = pose.get('member_count')
                if isinstance(count, bool) or not isinstance(count, int) or count < 1:
                    raise ValueError('Crowd pose/variant needs an explicit positive member_count')
        if plan['phase'] == 'authored' and not character_asset_current(plan, asset):
            raise ValueError('Character design changed or is unbound; register/review artwork against character_design_sha256')
    for section in plan['sections']:
        objects = {o['id']:o for o in section['objects']}
        for shot in section['shots']:
            for entry in cast_entries(shot):
                obj = objects[entry['object_id']]
                spec = obj['illustration']
                if spec['method'] != 'generated':
                    continue
                for aid in spec['asset_ids']:
                    asset = assets[aid]
                    if asset['kind'] == 'model_3d':
                        poses = asset['model_spec']['variants']
                    else:
                        if not entry.get('view_id'):
                            raise ValueError('2D cast note needs its required view_id before illustration export')
                        view = next((v for v in asset['views'] if v['id'] == entry['view_id']), None)
                        if view is None:
                            raise ValueError('Actor asset lacks the cast-required camera view')
                        poses = view['frames']
                    for sid in entry['state_ids']:
                        if not any(sid in p.get('performance_state_ids', [])
                                   and (not obj.get('crowd_group_id') or p.get('member_count') == entry['count']) for p in poses):
                            raise ValueError('Illustration does not cover a required actor state/view or crowd count')
                    if plan['phase'] == 'authored' and asset['kind'] != 'model_3d':
                        bindings = [b for b in shot.get('sprite_bindings', []) if b['object_id'] == obj['id'] and b['asset_id'] == aid]
                        if len(bindings) != 1 or bindings[0]['view_id'] != entry['view_id']:
                            raise ValueError('Every actor component needs its actual asset/view sprite binding')
                        keys = bindings[0].get('pose_track', [])
                        expected = [(k['frame'], k['state_id']) for k in shot['performance_tracks'][obj['id']]]
                        if [(k.get('frame'), k.get('performance_state_id')) for k in keys] != expected:
                            raise ValueError('Actor pose_track must execute its absolute-frame performance track')
                        if obj.get('crowd_group_id'):
                            poses_by_id={p['id']:p for p in poses}
                            if any(poses_by_id.get(k.get('pose_id'),{}).get('member_count') != entry['count'] for k in keys):
                                raise ValueError('Selected crowd pose does not match the shot population')


def performance_at(contract, object_id, frame):
    """Control intent at absolute time; this helper is not a rendered observation."""
    if isinstance(frame,bool) or not isinstance(frame,(int,float)) or not math.isfinite(frame):
        raise ValueError('Performance frame must be finite')
    entries = contract.get('resolved_direction',{}).get('character_cast',{}).get('entries',[])
    entry = next((e for e in entries if e['object_id'] == object_id),None)
    keys = contract.get('shot',{}).get('performance_tracks',{}).get(object_id)
    if entry is None or not keys:
        raise ValueError('Missing performance track '+object_id)
    key = keys[0]
    for candidate in keys:
        if candidate['frame'] > frame:
            break
        key = candidate
    result = {'state_id':key['state_id']}
    if 'count' in entry:
        result['member_count']=entry['count']
    else:
        result['gaze_target']=key.get('gaze_target',entry.get('gaze_targets',{}).get(key['state_id'],entry['gaze_target']))
    return result


def validate_cast_sample(contract, sample):
    cast = contract.get('resolved_direction', {}).get('character_cast')
    if not cast or not cast['entries']:
        return
    observed = sample.get('cast_states', {})
    if not isinstance(observed, dict) or set(observed) != {e['object_id'] for e in cast['entries']}:
        raise ValueError('Runtime must observe the state of every individual and crowd group')
    for entry in cast['entries']:
        expected = performance_at(contract,entry['object_id'],sample['frame'])
        actual = observed[entry['object_id']]
        if not isinstance(actual, dict) or actual.get('state_id') != expected['state_id']:
            raise ValueError('Runtime actor expression/state differs from the current performance track')
        if 'count' in entry:
            if isinstance(actual.get('member_count'), bool) or actual.get('member_count') != entry['count']:
                raise ValueError('Runtime crowd population differs from the declared group variant')
        elif actual.get('gaze_target') != expected['gaze_target']:
            raise ValueError('Runtime actor gaze differs from the current performance intent')
