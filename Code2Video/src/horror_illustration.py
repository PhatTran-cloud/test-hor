"""Completeness checks at prompt export, without inventing missing art direction."""

def setting_questions(plan):
    brief=plan.get('production_packet',{}).get('character_setting_brief',{})
    questions=brief.get('unresolved_setting',[])
    if not isinstance(questions,list) or any(not isinstance(q,str) or not q.strip() for q in questions):
        raise ValueError('unresolved_setting must be a list of material design questions')
    setting=brief.get('approved_setting',{})
    if not questions and isinstance(setting,dict) and setting.get('status')=='PROPOSED_TRIAL_ONLY':
        questions=['The setting is a proposed trial, not a selected real-film setting; preserve current story/era choices and resolve affected art before generation.']
    return questions

def validate_illustration_coverage(plan):
    from illustration_direction import directed, lightweight, validate_direction, validate_model_request, require
    new_direction = directed(plan)
    validate_direction(plan)
    horror=plan['horror']
    assets=horror.get('assets',[])
    lookup={a['id']:a for a in assets}
    if len(lookup)!=len(assets): raise ValueError('Duplicate illustration asset IDs')
    worlds=plan.get('production_packet',{}).get('illustration_direction',{}).get('scene_worlds',[])
    world_ids={w['id'] for w in worlds}
    if len(world_ids)!=len(worlds): raise ValueError('Duplicate scene world IDs')
    primary=horror.get('visual_reference',{}).get('primary')
    if primary=='oversimplified' or new_direction:
        if not plan.get('production_packet',{}).get('character_setting_brief'):
            raise ValueError('Illustration needs the story-grounded character and era brief')
        for world in worlds:
            for key in ['layout','perspective','lighting','required_props','crop_safety']:
                if key not in world or world[key] is None or world[key]=='':
                    raise ValueError(f"Scene world {world['id']} needs {key}")
    objects={}
    visible=set()
    for section in plan['sections']:
        for obj in section['objects']:
            if obj['id'] in objects and objects[obj['id']].get('illustration')!=obj.get('illustration'):
                raise ValueError('Conflicting illustration ownership across sections')
            objects[obj['id']]=obj
        for shot in section['shots']:
            visible.update(shot['object_ids'])
            if (primary=='oversimplified' or new_direction) and shot.get('scene_id') not in world_ids:
                raise ValueError(f"Shot {shot['id']} needs a shared scene_id/world layout before illustration")
    used=set()
    for oid in sorted(visible):
        spec=objects.get(oid,{}).get('illustration',{})
        method=spec.get('method')
        if method not in {'generated','procedural','existing'}:
            raise ValueError(f'Object {oid} needs explicit illustration.method (including backgrounds/props)')
        if method!='generated':
            if not spec.get('reason'): raise ValueError(f'Object {oid} needs a reason for {method} artwork')
            continue
        ids=spec.get('asset_ids',[])
        if not ids or len(set(ids))!=len(ids): raise ValueError(f'Object {oid} needs unique generated asset_ids')
        for aid in ids:
            if aid not in lookup or lookup[aid]['object_id']!=oid:
                raise ValueError(f'Object {oid} has a missing or mismatched generated asset {aid}')
            if lightweight(plan):
                route = '3d' if lookup[aid]['kind'] == 'model_3d' else '2d'
                if spec.get('route') != route:
                    raise ValueError('Light illustration needs an explicit matching 2D/3D route')
            used.add(aid)
    if set(lookup)!=used:
        raise ValueError('All exported assets must belong to an explicitly generated visible object')
    for asset in assets:
        model = asset['kind']=='model_3d'
        if primary=='oversimplified' or new_direction:
            if not asset.get('scene_ids') or not set(asset['scene_ids'])<=world_ids:
                raise ValueError(f"Asset {asset['id']} needs known scene_ids")
            for section in plan['sections']:
                for shot in section['shots']:
                    if asset['object_id'] in shot['object_ids'] and shot['scene_id'] not in asset['scene_ids']:
                        raise ValueError('Asset scene coverage does not include its visible shots')
            if not isinstance(asset.get('requires_alpha'),bool):
                raise ValueError('Every generated asset needs explicit requires_alpha')
            if asset.get('illustration_role') not in {'character_part','character_pose','character_model','crowd_group','prop','background','environment_layer'}:
                raise ValueError('Declare illustration_role for every generated asset')
        if model:
            if not new_direction:
                raise ValueError('Native 3D export needs the complete directed shot contract')
            if asset.get('provider')!='lowbudget3d' or asset.get('requires_alpha') is not False:
                raise ValueError('Native 3D asset uses lowbudget3d, not a raster alpha cutout')
            validate_model_request(asset,plan['phase'])
            if lightweight(plan):
                require(asset, ('design_semantics',), 'Native construction meaning')
                require(asset['design_semantics'], ('recognition_traits','parts_or_layers','anchors','variants','closest_camera_use'), 'Native fabrication')
            continue
        if asset.get('illustration_role') == 'character_model':
            raise ValueError('Character model fabrication requires a native model_3d asset')
        if asset['kind']=='sprite_sequence' and asset.get('requires_alpha',True) is not True:
            raise ValueError('Animated character cutouts require chroma-keyed alpha PNG')
        if asset.get('illustration_role') in {'character_part','character_pose'} and asset['kind']!='sprite_sequence':
            raise ValueError('Animated character parts/poses use sprite_sequence assets, not opaque prop/layer shortcuts')
        if not asset.get('views') or any(not v.get('frames') for v in asset['views']):
            raise ValueError('Every asset needs a prompt for each requested view/pose')
    from horror_characters import validate_character_assets
    validate_character_assets(plan)
    from horror_staging import plate_current
    if plan['phase'] == 'authored' and any(not plate_current(plan, a) for a in assets):
        raise ValueError('Authored background requires the current scene_staging_sha256 and actual plate review')
    if plan['phase'] == 'authored' and setting_questions(plan):
        raise ValueError('Resolve explicitly proposed/unresolved setting before authored artwork')
