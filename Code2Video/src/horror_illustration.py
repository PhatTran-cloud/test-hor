"""Completeness checks at prompt export, without inventing missing art direction."""


def asset_shots(plan, asset, view=None, pose=None):
    """Resolve declared image-request scope in film order, not runtime playback."""
    shots = [s for section in plan['sections'] for s in section['shots']]
    scope = [s for s in shots if asset['object_id'] in s['object_ids']
             and (not asset.get('scene_ids') or s.get('scene_id') in asset['scene_ids'])]
    for item, label in [(asset, 'asset'), (view, 'view'), (pose, 'pose')]:
        if item is None or 'shot_ids' not in item:
            continue
        ids = item['shot_ids']
        if (not isinstance(ids, list) or not ids or any(not isinstance(s, str) or not s for s in ids)
                or len(set(ids)) != len(ids)):
            raise ValueError(f'{label}.shot_ids needs unique nonempty shot IDs')
        if not set(ids) <= {s['id'] for s in scope}:
            raise ValueError(f'{label}.shot_ids must stay inside its parent scope and visible scene/object usage')
        scope = [s for s in scope if s['id'] in ids]
    if not scope:
        raise ValueError(f"Asset {asset['id']} has no visible shot usage for this view/pose")
    return scope


def shot_image_context(shot, object_id):
    """Only drawable constraints enter an image prompt; editorial truth stays out."""
    card = shot.get('storyboard', {})
    result = {'shot_id': shot['id'], 'scene_id': shot.get('scene_id')}
    for key in ('function', 'framing', 'attention', 'background_mode', 'background_reason'):
        if key in card:
            result[key] = card[key]
    if 'staging' in card:
        result['staging'] = {k: card['staging'][k] for k in ('fg', 'mg', 'bg', 'screen_direction', 'eyelines')
                             if k in card['staging']}
    if card.get('information', {}).get('reveal_ceiling'):
        result['reveal_ceiling'] = card['information']['reveal_ceiling']
    return result

def validate_illustration_coverage(plan):
    from storyboard_audit import audit_storyboard
    audit_storyboard(plan)
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
    covered = set()
    shots = [s for section in plan['sections'] for s in section['shots']]
    if len({s['id'] for s in shots}) != len(shots):
        raise ValueError('Illustration needs unique shot IDs across sections')
    for asset in assets:
        if primary=='oversimplified':
            if not asset.get('scene_ids') or not set(asset['scene_ids'])<=world_ids:
                raise ValueError(f"Asset {asset['id']} needs known scene_ids")
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
        for view in asset['views']:
            for pose in view['frames']:
                constraints = pose.get('image_constraints', [])
                if (not isinstance(constraints, list)
                        or any(not isinstance(c, str) or not c.strip() for c in constraints)):
                    raise ValueError('pose.image_constraints must be an explicit list of image instructions')
                for shot in asset_shots(plan, asset, view, pose):
                    covered.add((shot['id'], asset['object_id']))
    for shot in shots:
        for oid in shot['object_ids']:
            if objects[oid]['illustration']['method'] == 'generated' and (shot['id'], oid) not in covered:
                raise ValueError(f"Shot {shot['id']}: generated object {oid} has no scoped asset/view/pose prompt")
