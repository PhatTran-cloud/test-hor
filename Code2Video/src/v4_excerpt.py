"""Explicit review-only excerpt scope; never a production approval."""

def excerpt_scope(plan):
    scope = plan.get('preview_scope')
    if scope is None:
        return None
    if plan.get('technical_fixture') or plan.get('profile') != 'horror-v4.1':
        raise ValueError('Candidate excerpts require the real measured horror plan')
    if scope.get('kind') != 'candidate_excerpt' or len(plan['sections']) != 1:
        raise ValueError('Candidate excerpt must select one measured section')
    section = plan['sections'][0]
    if scope.get('section_id') != section['id']:
        raise ValueError('Excerpt section does not match the measured section')
    a,b = scope.get('start_frame'),scope.get('end_frame')
    if any(isinstance(v,bool) or not isinstance(v,int) for v in (a,b)) or a != 0 or not a < b <= section['speech']['frames']:
        raise ValueError('Opening excerpt needs an exact nonempty interval on the measured clock')
    authorization = scope.get('authorization',{})
    if authorization.get('reviewer') != 'human user' or not authorization.get('request'):
        raise ValueError('Excerpt needs the recorded human request; this is not a quality review')
    if scope.get('source_audio_sha256') != section['speech']['sha256']:
        raise ValueError('Excerpt authorization belongs to another measured WAV')
    return scope


def voice_review_deferred(plan, speech):
    scope = excerpt_scope(plan)
    if not scope:
        return False
    known = scope.get('voice_review_deferred',{})
    return (known.get('status') == 'USER_RETAINS_TEST_AUDIO_WITH_KNOWN_DEFECTS'
            and known.get('asset_sha256') == speech['sha256']
            and bool(known.get('request')) and bool(known.get('limitations')))
