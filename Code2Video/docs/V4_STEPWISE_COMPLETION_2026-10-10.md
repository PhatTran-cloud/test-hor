# Stepwise rule completion — 10 October 2026

Continued the interrupted rule edit from the chat “Đánh giá Code2Video cho nội dung”. Its latest human instruction was: “ở bước tiếp theo cũng phải khai báo là dùng skill nào chạy cái gì nữa”. The prior edit had established one step, report, STOP, but had not expanded the next-step declaration or verified the updated context.

## Completed

- Extended D:/manim/AGENTS.md, repo AGENTS.md and START_HERE.md: both current and proposed next steps declare scope, rule/source, skill/reference and concrete purpose, command/manual action, input/output and stopping point.
- Explicitly distinguish a proposed next step from an instruction to execute it. Repeat the declaration when the human instructs the next step. Silence, technical PASS and assistant promises do not authorize continuation.
- Updated LOCAL_GUIDE.md, REPO40_PRODUCTION_CONTRACT.md, V4_AUTHORING_GUIDE.md and both V4 prompt generators consistently.
- Removed unconditional direction-prompt wording that could ask a reading-only step to write a draft and then start Kokoro. Draft authoring and narration remain separate instructed steps.
- Updated production.py context header. Kept its renderer/backend behavior and existing visual, timing and review gates.
- Added a regression test covering both direction and execution prompts. No production artwork skill was applied: this task edits repo instructions and prompt propagation, not video art.

## Verification

- test_v4_workflow.py: 18 tests passed.
- test_v4_production.py: 12 tests passed.
- Generated and inspected a real shot context through production.py context at D:/manim/research/v4-stepwise-rule-completion/shot-context.md. Both the header and prompt include the complete declaration and stop instructions.
- git diff --check passed. Existing Windows line-ending notices were emitted.
- No video production, TTS, full render, release or later-stage background work was launched for this rule edit. Existing unrelated working-tree changes were retained.

## Limits

This completes the instruction/prompt update; it does not certify the rejected video's art or guarantee an assistant's future compliance. The CLI cannot verify what a human authorized in a chat or whether a skill was understood. No automatic approval token or replacement artistic threshold was invented. Active chats must reread the changed rules; changing a file cannot rewrite their existing context.

## Proposed next step — not run

If the user instructs a return to the rejected video, first perform step 1 (read and compare), not a render. Inputs: the user's brief, current rejected packet, D:/manim/AGENTS.md, START_HERE.md, KAGE_VISUAL_REFERENCE.md and V4_AUTHORING_GUIDE.md. Apply script-to-visual-director to compare the brief and visual thesis; lowbudget3d + the complete 3dviz-pro-max and routed references to identify the spatial craft requirements. Other motion/VFX skills are declared when their stage is actually instructed. Action: read/compare these sources and report the required renderer/craft decisions and missing work; no TTS/artwork/render command. Output: a linked requirement/route audit and concrete proposals. Stop after that report, awaiting the user's instruction for the next step.
