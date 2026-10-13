"""Regression tests for real workflow escape paths, not artistic judgments."""
import copy
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
from scipy.io import wavfile

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src"), str(ROOT / "local_tools")]
from v3_contract import normalize_plan
from v4_contract import digest, sha256, shot_contract, validate_files
from v4_execution import identifiers, validate_runtime_samples
from v4_quality import GATES, apply_review, release_check, review_targets
from v4_workflow import check_representative, representative_fingerprint, skill_routes
from v4_pipeline import prepare
from prompts.v4 import STEPWISE, get_v4_direction_prompt, get_v4_execution_prompt

spec = importlib.util.spec_from_file_location("example", ROOT / "local_tools/v4_smoke/build_plan.py")
example = importlib.util.module_from_spec(spec)
spec.loader.exec_module(example)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        audio = self.folder / "clock.wav"
        wavfile.write(audio, 48000, np.zeros(540*800, dtype=np.float32))
        self.plan = example.make_plan(audio)

    def draft(self):
        p = copy.deepcopy(self.plan)
        p.update(phase="draft", technical_fixture=False)
        section = p["sections"][0]
        section.update(narration="First. Second.", narration_segments=[{"id": "shared", "text": "First. Second."}])
        section.pop("speech")
        for beat in section["beats"]:
            beat["narration_anchor"]["segment_id"] = "shared"
            beat.pop("start_frame"); beat.pop("end_frame")
        return normalize_plan(p)

    def quality_files(self, scope="production", production=False):
        plan = copy.deepcopy(self.plan)
        plan["technical_fixture"] = not production
        video = self.folder / "video.mp4"
        video.write_bytes(b"unit review integrity fixture, not a media quality claim")
        planfile = self.folder / "plan.json"
        planfile.write_text(json.dumps(plan), encoding="utf-8")
        manifest = {"scope": scope, "video": str(video), "video_sha256": sha256(video), "plan_sha256": digest(plan),
            "shots": [{"shot": s["id"], "output": str(video), "output_sha256": sha256(video)} for s in plan["sections"][0]["shots"]]}
        source = {"plan_sha256": digest(plan), "files": {"plan.json": sha256(planfile)}}
        report = {"technical_fixture": not production, "video_sha256": sha256(video), "plan_sha256": digest(plan),
            "gates": {g: {"status": "UNVERIFIED", "notes": "pending"} for g in (*GATES, "technical")}}
        for name, value in [("source_manifest.json", source), ("quality_report.json", report), ("execution_manifest.json", manifest)]:
            (self.folder / name).write_text(json.dumps(value), encoding="utf-8")
        review = {"reviewer": "unit regression test", "video_sha256": sha256(video), "plan_sha256": digest(plan), "gates": {}}
        return plan, manifest, report, review

    def test_prepare_shared_recording_anchor_does_not_force_same_semantic_slot(self):
        draft = self.draft()
        def speech(plan, section, output, **kwargs):
            text = section["narration"]
            wavfile.write(output, 48000, np.zeros(300*800, dtype=np.float32))
            return {"file": str(output), "frames": 300, "duration": 5, "speech_start": .12, "speech_end": 4.8,
                "voice": "am_michael", "speed": 1, "time_stretch": False,
                "beats": [{"id": "shared", "text": text, "start": .12, "end": 4.9}]}
        args = SimpleNamespace(plan=self.folder/"draft.json", tts_endpoint="unused mock", voice="am_michael")
        with patch("v4_pipeline.prepare_section", side_effect=speech):
            timed = prepare(draft, self.folder, args)
        self.assertEqual(timed["phase"], "timed")
        for beat in timed["sections"][0]["beats"]:
            self.assertNotIn("start_frame", beat)
            self.assertEqual(beat["anchor_interval"]["start_frame"], 7)
        self.assertTrue(Path(timed["sections"][0]["speech"]["measurement_file"]).exists())

    def test_missing_research_or_unknown_draft_renderer_is_rejected(self):
        p = self.draft(); p.pop("production_packet")
        with self.assertRaises(ValueError): normalize_plan(p)
        p = self.draft(); p["sections"][0]["shots"][0]["renderer"] = "imaginary"
        with self.assertRaises(ValueError): normalize_plan(p)

    def test_comment_and_string_names_do_not_count_as_implementations(self):
        self.assertNotIn("PretendPattern", identifiers('// PretendPattern\nconst caption="PretendPattern";'))
        self.assertNotIn("PretendPattern", identifiers('# PretendPattern\ntext="PretendPattern"', python=True))
        self.assertIn("ActualPattern", identifiers('function ActualPattern() { return 1; }'))
        p = copy.deepcopy(self.plan)
        project = self.folder / "browser"
        shutil.copytree(ROOT / "local_tools/v4_smoke/browser/src", project / "src")
        for shot in p["sections"][0]["shots"]:
            shot["render_spec"]["project_dir"] = str(project)
        path = project/"src/index.tsx"
        path.write_text(path.read_text(encoding="utf-8") + '\n// ImaginaryPattern\n', encoding="utf-8")
        p["sections"][0]["shots"][0]["pattern"]["implementation"] = "ImaginaryPattern"
        with self.assertRaises(ValueError): validate_files(p, self.folder)

    def test_empty_static_state_and_cut_carry_list_are_valid(self):
        p = self.draft()
        p["sections"][0]["objects"][0]["initial_state"] = {}
        p["sections"][0]["shots"][0]["handoff"]["carry_state"] = []
        self.assertEqual(normalize_plan(p)["phase"], "draft")

    def test_review_sampling_includes_boundary_and_vfx_peak(self):
        s = self.plan["sections"][0]["shots"][0]
        self.assertTrue({0, 109, 126, 176, 179} <= set(s["execution"]["review_frames"]))

    def test_justified_foreground_crop_is_allowed_but_avoid_crop_is_not(self):
        p=copy.deepcopy(self.plan)
        layout=p["sections"][0]["shots"][2]["execution"]["objects"]["lit_leaf"]["layout"]
        layout.update(bounds=[-200, -100, 2400, 1400], overlap_policy="intentional", reason="same leaf enlarged for a macro crop")
        self.assertEqual(normalize_plan(p)["phase"],"authored")
        layout["overlap_policy"]="avoid"
        with self.assertRaises(ValueError): normalize_plan(p)

    def test_renderer_must_observe_current_contract_objects_and_all_samples(self):
        section = self.plan["sections"][0]
        c = shot_contract(section, section["shots"][1]); c["contract_sha256"] = digest(c)
        def sample(f):
            return {"shot": c["shot"]["id"], "frame": f, "contract_sha256": c["contract_sha256"],
                "object_ids": c["shot"]["object_ids"], "pattern_kind": "comparison",
                "bounds": {oid: [100+i*200, 100, 100, 100] for i,oid in enumerate(c["shot"]["object_ids"])}}
        observations = [sample(f) for f in c["shot"]["execution"]["review_frames"]]
        log = "\n".join("V4_EXECUTION_SAMPLE " + json.dumps(o) for o in observations)
        self.assertEqual(len(validate_runtime_samples(c, log)), len(observations))
        with self.assertRaises(ValueError): validate_runtime_samples(c, "")
        observations[0]["contract_sha256"] = "old"
        with self.assertRaises(ValueError): validate_runtime_samples(c, "\n".join("V4_EXECUTION_SAMPLE " + json.dumps(o) for o in observations))

    def test_prototype_required_and_fingerprint_changes_with_actual_source(self):
        p = self.plan
        p = copy.deepcopy(p); p["technical_fixture"] = False
        with self.assertRaises(ValueError): check_representative(p, self.folder)
        project = self.folder / "browser"
        shutil.copytree(ROOT / "local_tools/v4_smoke/browser/src", project / "src")
        for shot in p["sections"][0]["shots"]: shot["render_spec"]["project_dir"] = str(project)
        before = representative_fingerprint(p, self.folder)
        file = project / "src/index.tsx"
        file.write_text(file.read_text(encoding="utf-8")+'\n// actual source edit invalidates art review\n', encoding="utf-8")
        self.assertNotEqual(before, representative_fingerprint(p, self.folder))

    def test_context_focuses_one_shot_and_recomputes_reference_policy(self):
        text = get_v4_execution_prompt(self.plan, "comparison_hold")
        # Neighbor handoffs stay visible, but their full shot cards must not
        # compete with the shot being implemented.
        self.assertNotIn('"function": "inspect branching structure"', text)
        self.assertIn('"id": "comparison_hold"', text)
        with self.assertRaises(ValueError): get_v4_execution_prompt(self.plan, "unknown")

    def test_direction_and_shot_context_retain_user_step_declarations(self):
        direction = get_v4_direction_prompt({"content_profile": {"kind": "mixed"}}, {}, "Script")
        execution = get_v4_execution_prompt(self.plan, "comparison_hold")
        for context in (direction, execution):
            self.assertIn(STEPWISE, context)
            self.assertIn("PROPOSED-NEXT-STEP DECLARATION", context)
            self.assertIn("PROPOSED, NOT RUN", context)
            self.assertIn("command or manual action", context)
            self.assertIn("stopping point", context)
        self.assertIn("reading/research-only step", direction)
        self.assertIn("separately instructed narration step", direction)
        self.assertIn("implement only what the current human-authorized step permits", execution)

    def test_focused_context_retains_handoff_across_section_boundary(self):
        p=copy.deepcopy(self.plan)
        following=copy.deepcopy(p["sections"][0])
        following["shots"]=[copy.deepcopy(following["shots"][0])]
        following["shots"][0]["id"]="next_section_open"
        p["sections"].append(following)
        text=get_v4_execution_prompt(p,"macro_insert")
        self.assertIn('"id": "next_section_open"',text)
        self.assertEqual(text.count('"renderer_reason"'),1)

    def test_motion_pass_requires_clip_and_complete_shot_coverage(self):
        plan, manifest, report, review = self.quality_files()
        evidence = {"id": "source", "kind": "measurement", "file": "plan.json", "sha256": sha256(self.folder/"plan.json")}
        targets = review_targets(plan, manifest)["motion"]
        review["gates"]["motion"] = {"status": "PASS", "notes": "unit regression only", "evidence": [evidence],
            "observations": [{"target": t, "expected": "movement", "observed": "unit check", "evidence_ids": ["source"]} for t in targets]}
        with self.assertRaises(ValueError): apply_review(self.folder, review)
        review["gates"]["motion"]["evidence"] = [{"id": "source", "kind": "clip", "file": "video.mp4", "sha256": report["video_sha256"]}]
        review["gates"]["motion"]["observations"].pop()
        with self.assertRaises(ValueError): apply_review(self.folder, review)

    def test_visual_pass_requires_rendered_evidence(self):
        plan, manifest, report, review = self.quality_files()
        review["gates"]["visual"] = {"status":"PASS", "notes":"source names do not prove artwork",
            "evidence":[{"id":"json", "kind":"measurement", "file":"plan.json", "sha256":sha256(self.folder/"plan.json")}],
            "observations":[{"target":t,"expected":"art","observed":"unit only","evidence_ids":["json"]}
                for t in review_targets(plan,manifest)["visual"]]}
        with self.assertRaises(ValueError): apply_review(self.folder,review)

    def test_runtime_reports_reject_unintentional_overlap(self):
        shot=self.plan["sections"][0]["shots"][1]
        contract=shot_contract(self.plan["sections"][0],shot)
        contract["contract_sha256"]=digest(contract)
        rows=[]
        for frame in shot["execution"]["review_frames"]:
            rows.append("V4_EXECUTION_SAMPLE "+json.dumps({"shot":shot["id"],"frame":frame,
                "contract_sha256":contract["contract_sha256"],"object_ids":shot["object_ids"],
                "pattern_kind":"comparison","bounds":{o:[100,100,200,200] for o in shot["object_ids"]}}))
        with self.assertRaises(ValueError): validate_runtime_samples(contract,"\n".join(rows))

    def test_measured_receipt_rejects_edited_anchor(self):
        p=copy.deepcopy(self.plan)
        p["technical_fixture"]=False
        speech=p["sections"][0]["speech"]
        receipt=self.folder/"measurement.json"
        receipt.write_text(json.dumps(speech),encoding="utf-8")
        speech.update(measurement_file=str(receipt),measurement_sha256=sha256(receipt))
        speech["anchors"][0]["end_frame"]-=1
        with self.assertRaisesRegex(ValueError,"anchors"): validate_files(p,self.folder)

    def test_review_cannot_skip_gate_or_waive_factual_claim(self):
        plan, manifest, report, review = self.quality_files(production=True)
        review["gates"]["listening"] = {"status": "NOT_APPLICABLE", "notes": "cannot waive production audio"}
        with self.assertRaises(ValueError): apply_review(self.folder, review)
        report["gates"].pop("motion")
        (self.folder/"quality_report.json").write_text(json.dumps(report), encoding="utf-8")
        with self.assertRaises(ValueError): apply_review(self.folder, review)

    def test_listening_pass_requires_listening_to_actual_complete_mix(self):
        plan, manifest, report, review = self.quality_files(production=True)
        review["gates"]["listening"] = {"status": "PASS", "notes": "meters alone are insufficient",
            "evidence": [{"id": "audio", "kind": "clip", "file": "video.mp4", "sha256": report["video_sha256"], "method": "metered"}],
            "observations": [{"target": "film_mix", "expected": "clear narration", "observed": "meter only", "evidence_ids": ["audio"]}]}
        with self.assertRaises(ValueError): apply_review(self.folder, review)

    def test_preview_cannot_be_released_even_if_report_is_relabelled(self):
        plan, manifest, report, review = self.quality_files(scope="representative", production=True)
        with self.assertRaises(ValueError): release_check(self.folder)

    def test_candidate_excerpt_cannot_release_or_approve_representative(self):
        plan, manifest, report, review = self.quality_files(scope="candidate_excerpt", production=True)
        checked = apply_review(self.folder, review)
        self.assertEqual(checked['release_status'], 'REVIEW_REQUIRED')
        with self.assertRaises(ValueError): release_check(self.folder)


if __name__ == "__main__":
    unittest.main()
