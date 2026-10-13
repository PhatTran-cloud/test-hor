# Horror profile template

New default: `horror_light`. Start with docs/HORROR_LIGHT_WORKFLOW.md and
`horror-light-washer-draft.json`: three proposed shots, four reusable 2D assets,
four prompts and one localized VFX proposal. Narrator/art/timing are unverified.

```bash
python local_tools/production.py check examples/horror-light-washer-draft.json
python local_tools/production.py asset-brief examples/horror-light-washer-draft.json --output ../outputs/horror-light-trial/illustration.json
python local_tools/production.py motion-brief examples/horror-light-washer-draft.json --output ../outputs/horror-light-trial/motion.json
```

The rainforest examples below are historical explainer/hybrid experiments,
preserved for regression. They are not the current horror authoring model.

`horror-ensemble-draft.json` tests the same light pipeline with two proposed
principal characters, one supporting character and an anonymous crowd. Three
shots represent 9, 4 and 1 people; the crowd uses six-person/two-person cutout
variants when visible. Twelve image requests cover required performances only.
Visible ages and appearance remain proposed/unresolved before generation;
no cast selection, measured narration, artwork or animation is produced here.
Read docs/HORROR_CHARACTERS.md. Run only the currently authorized export/check:

```bash
python local_tools/production.py check examples/horror-ensemble-draft.json
python local_tools/production.py asset-brief examples/horror-ensemble-draft.json --output ../outputs/horror-ensemble-trial/illustration.json
python local_tools/production.py motion-brief examples/horror-ensemble-draft.json --output ../outputs/horror-ensemble-trial/motion.json
```

horror-profile-template.json is an unselected field template, not a ready plan or
approved story. Language, main/dialogue cast, style bible, research packet and
sections must be authored for the actual user brief. Null selections are intentional;
the validator rejects them rather than inventing English/default speaker/timestamps.
Read docs/HORROR_CONTRACT.md and START_HERE.md. local_tools/v4_smoke examples are
inherited contract regression fixtures, not production horror plans.

`kage-request-benchmark.json` is a self-contained **technical fixture**, not an
approved film, measured timing or generated artwork. It demonstrates 2D leaf,
background and insect requests, a native 3D trunk request, and procedural fog
inside one complete-shot direction contract. Export without generating assets:

```bash
python local_tools/production.py asset-brief examples/kage-request-benchmark.json --output ../outputs/illustration/benchmark-prompts.json
```

JSON and sibling Markdown contain prompts, model briefs, shot inventory and
the motion/VFX handoff. Full 3dviz-pro-max availability, asset fabrication and
actual artwork review remain unverified. Follow docs/KAGE_ILLUSTRATION_PIPELINE.md
to author a real plan while preserving its approved story/cast/era.

`forest-listens-storyboard-draft.json` is a creative trial with five shots and
24 seconds of **provisional** editing time. It uses the full draft validator
(`technical_fixture=false`) and preserves the user's one rainforest sentence.
Its narrator is explicitly unassigned, its imagery is fictional, and no audio,
artwork or native model has been generated. It does not change an approved film.

```bash
python local_tools/production.py check examples/forest-listens-storyboard-draft.json
python local_tools/production.py asset-brief examples/forest-listens-storyboard-draft.json --output ../outputs/storyboard-forest-trial/prompts.json
python local_tools/production.py context examples/forest-listens-storyboard-draft.json --shot macro_identify --output ../outputs/storyboard-forest-trial/macro-context.md
```

The export has five 2D assets (13 view/pose prompts), one native 3D request and
five complete-shot inventories. Event `cause_event_ids` preserve the upstream
signal/pressure/drop chain in the macro context without replaying those causes.
Textual reveal consistency still needs editorial review; a valid draft is not
renderable or artistically approved. Measured timing and real assets come later.
