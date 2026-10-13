# El Nino: When the Ocean Shifts

Delivery: duration follows natural narration, 1920x1080 at 60 fps, English male Kokoro `am_michael`, clean picture with no burned subtitles.

The film explains ENSO through one causal chain: trade winds push warm water west; the thermocline tilts; weakened winds let warm water move east; rainfall follows the warm pool; distant weather responds.

Visual language: schematic Pacific maps, ocean cross sections, a restrained 3D globe, warm/cool color coding, and camera movement that follows the water rather than decorative overlays.

Audio: narration-only. No music bed and no SFX. Trim exterior silence while preserving internal speech pauses. Native scene lengths come from measured Kokoro audio with a 0.12s lead and 0.15s tail. No speed adjustment to hit a runtime and no long black transitions.

Scientific reference: NOAA PMEL and NASA sources listed in `plan.json`. Map coastlines come from public-domain Natural Earth 1:110m land data. Temperature fields, ocean depth, and atmospheric paths are conceptual illustrations; they are not measured forecasts or fluid simulations. Blue is cooler water, orange is warm water, and the salmon band identifies El Nino warming.

Render from the repository root:

```powershell
.venv/Scripts/python.exe local_tools/render_local.py local_tools/pilot_elnino/plan.json
.venv/Scripts/python.exe local_tools/pilot_elnino/finalize.py src/CASES/LOCAL_ASSISTANT_<run>/0-El_Nino_When_the_Ocean_Shifts
```

Finalization uses the native rendered frame counts, continuous narration, and only frame-rounding silence padding. It verifies 1080p60, all decoded frames, stereo 48 kHz audio, and sub-second narration joins, then exports a contact sheet of decoded early/middle/late frames from each scene.
