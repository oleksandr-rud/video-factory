---
name: negative-prompt-guardrails
description: Build negative constraints for AI video generation and convert them into model-safe positive phrasing when needed. Use when prompts must prevent artifacts, unwanted style, identity drift, random logos, unreadable text, camera shake, or other generation failures.
---

# Negative Prompt Guardrails

Read `../../references/invideo-ai-generation.md` before deciding whether to use a separate negative prompt or a positive rewrite.

Convert risk controls into the negative-prompt mode that the chosen provider can actually apply.

## Inputs

- Visual Producer route brief, selected model route, and draft positive prompt
- Scene risks, producer criteria, channel format, brand/rights constraints, and QA findings when rerolling
- Provider/model support for negative prompts, prompt guides, or positive constraint phrasing

## Workflow

1. List risks from the scene: artifacts, identity drift, wrong brand, wrong setting, unwanted camera motion, unreadable text, unsafe imagery, bad hands/faces, flicker, or style mismatch.
2. Decide negative mode:
   - `separate_field` when the model supports negative prompts.
   - `converted_to_positive_constraints` when the model prefers positive phrasing.
   - `prompt_guide` when the constraint should persist across multiple generations.
   - `unsupported` when the provider cannot apply it reliably.
3. For separate negative prompts, write visible unwanted elements as a compact comma-separated list. Avoid command language such as "no" and "do not".
4. For positive rewrites, describe the desired state. Example: "locked camera, steady tripod shot" instead of "no camera shake".
5. Check that negative constraints do not contradict the positive prompt.

## Required Output

Return:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "negative_prompt": "string",
  "negative_prompt_mode": "separate_field | converted_to_positive_constraints | prompt_guide | unsupported | not_used",
  "positive_rewrite_notes": ["string"],
  "prompt_guide_constraints": ["string"],
  "residual_risks": ["string"],
  "contradictions_found": ["string"],
  "next_recommended_step": "string"
}
```

## Contract Fields Populated

- `ai-video-generation-package.schema.json`: `negative_prompt`, `negative_prompt_mode`, `prompt_guides`, and `qa.findings[]` context for rerolls

## Status Policy

- Return `complete` when constraints are mode-compatible and non-contradictory.
- Return `needs_approval` when constraints depend on rights-sensitive likeness/logo/source material decisions.
- Return `blocked` when the scene requires constraints the provider cannot reliably enforce and no fallback exists.
- Return `needs_revision` when the positive prompt or model route is missing or contradictory.

## Evidence Required

Preserve the source of each constraint: scene brief, producer criteria, channel rule, provider limit, or QA finding id.

## Media Manifest Policy

No media files are created. Return `manifest_actions[]` as `not_applicable` unless a constraint depends on a reference asset whose rights state should be deferred for approval.

## Approval And Stop Conditions

Stop when a negative constraint attempts to bypass rights, safety, likeness, logo, or provider policy limits. Do not use negative wording as a substitute for Director approval.

## Definition Of Done

- Negative mode matches the selected provider/model.
- Constraints do not contradict the positive prompt.
- Provider-unsupported risks are recorded as residual risks or fallback triggers.
- Approval-sensitive constraints are escalated.

## Handoff Summary Shape

Return:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "artifact_paths": ["string"],
  "changed_files": ["string"],
  "populated_contracts": ["codex/contracts/ai-video-generation-package.schema.json"],
  "manifest_actions": [
    {
      "action": "not_applicable | deferred",
      "asset_id": "string",
      "reason": "string"
    }
  ],
  "validation_performed": ["risk list", "negative mode decision", "contradiction check", "provider support check"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
