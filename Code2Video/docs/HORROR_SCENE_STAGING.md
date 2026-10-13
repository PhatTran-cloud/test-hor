# One scene, several purposeful shots

This is an original project proposal responding to the user's staging/continuity
requirements. It is **not** a finding from a completed 540-frame OverSimplified
study. See [the sampling status](research/2026-10-13_oversimplified_sampling_status.md).
Keep Kage artwork, original restrained horror, humor=none and the light storyboard.

A scene owns stable geography, architecture and lighting. A shot selects what
the audience sees of that world. A face change, gesture or focal change inside a
continuous view is a new acting beat/panel, not automatically a new shot or scene.
Changing the crop must not move furniture, delete offscreen people, restart an
event or generate an entirely new room image.

## Small additive contract

Select `production_packet.illustration_direction.staging_revision=1` for new
plans. Earlier frozen plans without this field keep their original checks.
Keep schema_version=4 and the same production entrypoint/60fps section clock.

In each `scene_world`, author **one** `staging` definition:

- `master_plate_object_id`: the canonical empty background object;
- `views`: named `{id, kind, plate_object_id, framing}` presets. `kind=master`
  establishes geography; `crop` reuses that plate; `new_view` explicitly requests
  a different supported viewpoint/plate when needed;
- optional `static_details`: `{id, plate_object_id, description,
  readable_in_view_ids}`. List story-bearing fixed details that the background
  artist must preserve. Do not inventory every tile or add a layer quota.

The shot's existing camera field adds only `stage_view_id`. Its existing handoff
adds `link_kind`; the existing reason explains the specific information/action
that motivates the next shot. There is no new per-second storyboard ledger.

| link_kind | Relationship |
| --- | --- |
| question_answer | Established uncertainty motivates the next observation |
| cause_reaction | An action produces a readable response |
| evidence_return | Revisit earlier evidence after its meaning changes; supply returns_to_shot_id |
| spatial | Show another part of the same geography |
| sound_bridge | Intended sound connects the next view; audible execution still needs review |
| location_change | Move to a different scene geography |
| time_change | Explicitly change story time |
| parallel | Connect simultaneous or compared information |
| end | Only the sequence's final shot |

These are authoring options, not measured reference-channel transition statistics.
`handoff.type` still controls the implementation: a simple cut is valid for any
appropriate story link. No requirement for a fancy transition or constant motion.

## Illustration owns the reusable world

`production.py asset-brief` exports the background's selected views and relevant
fixed details in its **copyable prompt**, not just a separate documentation note.
Draw the clean plate once and keep enough resolution/crop margin for its closest
use. Author measured crop/scale/anchors after actual artwork returns. A camera
crop cannot expose an undrawn side; choose a new view or the full native 3D route.

An empty socket can be baked into a static wall. A plug, hatch, hand, person,
moving shadow or anything that changes/acts independently remains a separately
registered object. `shot.object_ids` and `shot.cast` describe what is present in
this view. Omission alone says **outside this shot**; an exit/destruction needs
its own story/action/state. Crowds keep their declared count and shared behavior.
Principal/supporting importance does not force a close-up in every shot.

Background requests export an expected `scene_staging_sha256`. Bind that value
to the returned asset only after actual registration and review. Changes to the
world/layout/light/static-detail brief invalidate it. Exporting the expected hash
does not approve images. Background art checks also bind real files/anchors.

## Motion and actual review

`production.py motion-brief` carries selected scene view, readable static details,
objects outside this shot and typed story link alongside existing cast, events,
camera and persistent state. Mount the same scene in the existing assembly;
change framing/attention, then execute the authored response. A hold is valid.
VFX remains caused by an event; do not add fog, shake or animation to fill space.

Python/runtime execution context includes `resolved_direction.scene_staging`;
representative identity changes with that contract. Actual review includes
`staging:SHOT`, `background_detail:SCENE:DETAIL` and `story_link:SHOT` where
applicable. Inspect real geography, clue readability, cropping/population and
before/after links. Structural checks do not prove the image, staging or scare.

The washer/ensemble examples reuse one room in three views: establish the
disconnected supply → inspect the knock/reaction → return to the same supply.
The last view excludes the washer body/hatch from the visible inventory while
carrying their offscreen event/source state. The ensemble still represents 9, 4
and 1 people with 8 assets/12 image requests;
cast/age/appearance choices and provisional timing remain unapproved.
