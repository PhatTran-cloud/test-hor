"""Completeness checks at prompt export, without inventing missing art direction."""

def validate_illustration_coverage(plan):
    horror=plan['horror']
    assets=horror.get('assets',[])
    lookup={a['id']:a for a in assets}
    if len(lookup)!=len(assets): raise ValueError('Duplicate illustration asset IDs')
    worlds=plan.get('production_packet',{}).get('illustration_direction',{}).get('scene_worlds',[])
    world_ids={w['id'] for w in worlds}
    if len(world_ids)!=len(worlds): raise ValueError('Duplicate scene world IDs')
    primary=horror.get('visual_reference',{}).get('primary')
    if primary=='oversimplified':
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
            if primary=='oversimplified' and shot.get('scene_id') not in world_ids:
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
            used.add(aid)
    if set(lookup)!=used:
        raise ValueError('All exported assets must belong to an explicitly generated visible object')
    for asset in assets:
        if primary=='oversimplified':
            if not asset.get('scene_ids') or not set(asset['scene_ids'])<=world_ids:
                raise ValueError(f"Asset {asset['id']} needs known scene_ids")
            for section in plan['sections']:
                for shot in section['shots']:
                    if asset['object_id'] in shot['object_ids'] and shot['scene_id'] not in asset['scene_ids']:
                        raise ValueError('Asset scene coverage does not include its visible shots')
            if not isinstance(asset.get('requires_alpha'),bool):
                raise ValueError('Every generated asset needs explicit requires_alpha')
            if asset.get('illustration_role') not in {'character_part','character_pose','prop','background','environment_layer'}:
                raise ValueError('Declare illustration_role for every generated asset')
        if asset['kind']=='sprite_sequence' and asset.get('requires_alpha',True) is not True:
            raise ValueError('Animated character cutouts require chroma-keyed alpha PNG')
        if asset.get('illustration_role') in {'character_part','character_pose'} and asset['kind']!='sprite_sequence':
            raise ValueError('Animated character parts/poses use sprite_sequence assets, not opaque prop/layer shortcuts')
        if not asset.get('views') or any(not v.get('frames') for v in asset['views']):
            raise ValueError('Every asset needs a prompt for each requested view/pose')
