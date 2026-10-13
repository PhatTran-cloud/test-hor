"""Source references plus runtime observations. Neither establishes art quality."""
import ast
import json
import math
import re


def identifiers(text, python=False):
    if python:
        tree = ast.parse(text)
        names = set()
        for node in ast.walk(tree):
            for key in ("id", "name", "arg", "attr"):
                value = getattr(node, key, None)
                if isinstance(value, str):
                    names.add(value)
        return names
    # Strings/comments never count as an implementation. This is a lexer,
    # not a substitute for TypeScript compilation or execution observations.
    tokens = re.finditer(r'''(?P<ignored>"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`|/\*[\s\S]*?\*/|//[^\n]*)|(?P<id>[A-Za-z_$][A-Za-z0-9_$]*)''', text)
    return {m.group("id") for m in tokens if m.group("id")}


def validate_runtime_samples(contract, log):
    shot = contract["shot"]
    expected = set(shot["execution"]["review_frames"])
    samples = {}
    for line in log.splitlines():
        if "V4_EXECUTION_SAMPLE " not in line:
            continue
        raw = line.split("V4_EXECUTION_SAMPLE ", 1)[1].strip()
        try:
            sample = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if sample.get("shot") != shot["id"] or sample.get("frame") not in expected:
            continue
        if sample.get("contract_sha256") != contract["contract_sha256"]:
            raise ValueError("Renderer observed a different contract")
        if set(sample.get("object_ids", [])) != set(shot["object_ids"]):
            raise ValueError("Renderer did not observe every planned visible object")
        if sample.get("pattern_kind") != shot["pattern"]["kind"]:
            raise ValueError("Renderer observed a different pattern")
        bounds = sample.get("bounds", {})
        from horror_characters import validate_cast_sample
        validate_cast_sample(contract,sample)
        directed = contract.get('resolved_direction',{}).get('contract_revision') == 1
        if directed:
            camera = sample.get('camera',{})
            transform = camera.get('transform',[])
            if (not isinstance(transform,list) or len(transform) not in {6,16}
                    or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in transform)
                    or camera.get('target_object') not in shot['object_ids']):
                raise ValueError('Directed runtime needs an observed camera transform and focal object')
            states = sample.get('object_states',{})
            visibility = sample.get('visibility',{})
            if set(states) != set(shot['object_ids']) or set(visibility) != set(shot['object_ids']):
                raise ValueError('Directed runtime needs observed state/visibility for every shot component')
            behaviors = contract['resolved_direction']['behaviors']
            for oid in shot['object_ids']:
                if not isinstance(states[oid],dict) or not set(behaviors[oid]['exit_state']) <= set(states[oid]):
                    raise ValueError('Runtime state is missing declared behavior properties')
                vis = visibility[oid]
                opacity = vis.get('opacity')
                if (isinstance(opacity,bool) or not isinstance(opacity,(int,float)) or not math.isfinite(opacity)
                        or not 0 <= opacity <= 1 or not isinstance(vis.get('hidden'),bool)):
                    raise ValueError('Observed visibility needs opacity and hidden status')
            phases = sample.get('event_phases',{})
            if set(phases) != {e['id'] for e in shot.get('events',[])} or any(not isinstance(v,str) or not v.strip() for v in phases.values()):
                raise ValueError('Directed runtime needs observed phases for every active event')
        if set(bounds) != set(shot["object_ids"]):
            raise ValueError("Runtime sample needs measured bounds for every visible object")
        for oid, values in bounds.items():
            if len(values) != 4 or any(isinstance(v, bool) or not isinstance(v, (float, int)) or not math.isfinite(v) for v in values):
                raise ValueError("Runtime bounds must be finite delivery-pixel x,y,width,height")
            if (values[2] <= 0 or values[3] <= 0) and not (directed and sample['visibility'][oid]['hidden']):
                raise ValueError("Runtime sample contains an invisible/empty object")
            if shot["execution"]["objects"][oid]["layout"]["overlap_policy"] == "avoid":
                x, y, w, h = values
                if x < -2 or y < -2 or x+w > 1922 or y+h > 1082:
                    raise ValueError("Runtime object leaves delivery bounds")
        avoid = [oid for oid in bounds if shot["execution"]["objects"][oid]["layout"]["overlap_policy"] == "avoid"]
        for i, first in enumerate(avoid):
            for second in avoid[i+1:]:
                x,y,w,h = bounds[first]
                a,b,c,d = bounds[second]
                if min(x+w,a+c)-max(x,a)>2 and min(y+h,b+d)-max(y,b)>2:
                    raise ValueError("Runtime objects overlap without intentional-overlap policy")
        samples[sample["frame"]] = sample
    if set(samples) != expected:
        raise ValueError("Renderer did not emit execution observations at every requested review frame")
    return [samples[f] for f in sorted(samples)]
