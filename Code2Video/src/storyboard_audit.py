"""Scene/shot authoring structure, never an artistic or pixel continuity PASS."""
CONTRACT = 'scene-shot/1'
BACKGROUND_MODES = {'lived_in', 'explanatory_insert', 'subjective', 'empty_by_story'}
RELATIONS = {'same_scene', 'scene_change', 'time_jump', 'insert', 'return', 'end'}


def _text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{label} needs concrete text')


def audit_storyboard(plan, required=False):
    direction = plan.get('production_packet', {}).get('illustration_direction', {})
    version = direction.get('storyboard_contract')
    if version is None and not required:
        return {'status': 'NOT_DECLARED', 'artistic_review': 'UNVERIFIED'}
    if version != CONTRACT:
        raise ValueError(f'Declare illustration_direction.storyboard_contract={CONTRACT}')
    worlds = direction.get('scene_worlds', [])
    world_map = {w['id']: w for w in worlds}
    if not worlds or len(world_map) != len(worlds):
        raise ValueError('Storyboard needs unique shared scene worlds')
    for world in worlds:
        for field in ('layout', 'perspective', 'lighting', 'crop_safety'):
            _text(world.get(field), f"World {world['id']}.{field}")
        if not isinstance(world.get('required_props'), list):
            raise ValueError('World required_props must be an explicit list')
        anchors = world.get('spatial_anchors', [])
        if not anchors or any(not isinstance(a, dict) or not a.get('id') for a in anchors):
            raise ValueError('World needs named spatial_anchors')
        if len({a['id'] for a in anchors}) != len(anchors):
            raise ValueError('World spatial anchor IDs must be unique')
        for anchor in anchors:
            _text(anchor.get('description'), 'Spatial anchor description')

    shots = [s for section in plan.get('sections', []) for s in section.get('shots', [])]
    if not shots or len({s['id'] for s in shots}) != len(shots):
        raise ValueError('Storyboard needs unique shots in film order')
    objects = {o['id'] for sec in plan['sections'] for o in sec.get('objects', [])}
    edges, scene_states = [], {}
    for i, shot in enumerate(shots):
        label = f"Shot {shot['id']}"
        if shot.get('scene_id') not in world_map:
            raise ValueError(f'{label} needs a known shared scene_id')
        visible = shot.get('object_ids', [])
        if len(set(visible)) != len(visible) or not set(visible) <= objects:
            raise ValueError(f'{label} references unknown or repeated objects')
        card = shot.get('storyboard', {})
        for field in ('function', 'framing', 'attention', 'primary_action', 'background_reason'):
            _text(card.get(field), f'{label}.{field}')
        if card.get('background_mode') not in BACKGROUND_MODES:
            raise ValueError(f'{label} needs a deliberate background_mode')
        staging = card.get('staging', {})
        groups = [staging.get(layer) for layer in ('fg', 'mg', 'bg')]
        if any(not isinstance(group, list) for group in groups):
            raise ValueError(f'{label} needs explicit fg/mg/bg object lists (empty allowed)')
        layered = [oid for group in groups for oid in group]
        if len(layered) != len(set(layered)) or set(layered) != set(visible):
            raise ValueError(f'{label} staging must place each visible object once')
        _text(staging.get('screen_direction'), f'{label}.screen_direction')
        _text(staging.get('eyelines'), f'{label}.eyelines')
        for field in ('start_state', 'end_state'):
            state = card.get(field, {})
            if not isinstance(state, dict) or set(state) != set(visible):
                raise ValueError(f'{label}.{field} must cover every visible object')
            for value in state.values():
                _text(value, f'{label}.{field}')
        incoming = shots[i - 1].get('storyboard', {}).get('transition', {}) if i else {}
        if incoming.get('relation') == 'time_jump':
            # An explicit narrative time jump invalidates remembered offscreen
            # states in every world; selected adjacent carry still gets checked.
            scene_states.clear()
        remembered = scene_states.setdefault(shot['scene_id'], {})
        if incoming.get('relation') != 'time_jump':
            for oid, state in card['start_state'].items():
                if oid in remembered and remembered[oid] != state and oid not in incoming.get('state_changes', {}):
                    raise ValueError(f'{label}: {oid} resets on scene return/cut without an authored state_changes reason')
        remembered.update(card['end_state'])
        knowledge = card.get('information', {})
        for field in ('audience_in', 'audience_out', 'character_in', 'character_out', 'reveal_ceiling'):
            _text(knowledge.get(field), f'{label}.information.{field}')
        if not isinstance(knowledge.get('withheld'), list):
            raise ValueError(f'{label}.withheld needs an explicit list; empty is valid')
        transition = card.get('transition', {})
        relation = transition.get('relation')
        if relation not in RELATIONS:
            raise ValueError(f'{label} has unknown transition relation')
        for field in ('trigger', 'next_delta'):
            _text(transition.get(field), f'{label}.transition.{field}')
        channels = transition.get('carry_channels')
        preserved = transition.get('preserved_objects')
        if not isinstance(channels, list) or not isinstance(preserved, list):
            raise ValueError(f'{label} declares carry_channels and preserved_objects lists')
        if any(not isinstance(c, str) or not c.strip() for c in channels) or len(set(channels)) != len(channels):
            raise ValueError(f'{label} carry_channels must be unique nonempty names')
        if len(set(preserved)) != len(preserved) or not set(preserved) <= set(visible):
            raise ValueError(f'{label} carries unknown or repeated objects')
        changes = transition.get('state_changes', {})
        if not isinstance(changes, dict) or not set(changes) <= objects:
            raise ValueError(f'{label} state_changes must name canonical objects')
        for reason in changes.values():
            _text(reason, f'{label}.state_changes reason')
        nxt = shots[i + 1] if i + 1 < len(shots) else None
        if nxt is None:
            if relation != 'end' or transition.get('next_shot_id') is not None or preserved:
                raise ValueError('Final shot needs end relation, null next_shot_id and no carried objects')
            continue
        if relation == 'end' or transition.get('next_shot_id') != nxt['id']:
            raise ValueError(f'{label} next_shot_id must point to the actual next shot')
        same_world = shot['scene_id'] == nxt.get('scene_id')
        if relation == 'same_scene' and not same_world:
            raise ValueError('same_scene cannot silently replace the scene world')
        if relation in {'scene_change', 'insert', 'return'} and same_world:
            raise ValueError('A world-change relation needs a different scene_id')
        if not set(preserved) <= set(nxt.get('object_ids', [])):
            raise ValueError('Preserved visible objects must be present in the next shot')
        next_state = nxt.get('storyboard', {}).get('start_state', {})
        # Audit every common object in continuous same-world cuts, not only a
        # flattering subset the author listed as preserved.
        continuous = (set(visible) & set(nxt.get('object_ids', []))) if relation == 'same_scene' else set(preserved)
        for oid in continuous:
            if card['end_state'][oid] != next_state.get(oid) and oid not in changes:
                raise ValueError(f'{label}: {oid} resets across cut without an authored state_changes reason')
        edges.append({'from': shot['id'], 'to': nxt['id'], 'relation': relation,
                      'carry_channels': channels, 'next_delta': transition['next_delta']})
    return {'status': 'STRUCTURE_CHECKED', 'contract': CONTRACT, 'scenes': len(worlds),
            'shots': len(shots), 'edges': edges, 'artistic_review': 'UNVERIFIED',
            'pixel_continuity_review': 'UNVERIFIED', 'audio_review': 'UNVERIFIED'}
