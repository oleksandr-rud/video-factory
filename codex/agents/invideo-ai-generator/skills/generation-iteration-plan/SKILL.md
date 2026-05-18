---
name: generation-iteration-plan
description: Plan AI video generation variants and rerolls with controlled prompt changes. Use when a scene needs 2-3 candidate clips, model comparisons, or targeted regeneration after QA failures.
---

# Generation Iteration Plan

Plan bounded AI-video variants and rerolls. This skill prevents uncontrolled credit spend by changing one variable at a time and stopping when quality or budget cannot converge.

## Inputs

- Baseline AI generation package, model decision, and approval packet
- Generated clip QA findings, failed gates, or Visual Producer feedback when this is a reroll
- Budget policy, approved variant count, credit/cost ceiling, and stop conditions
- Scenario scene, producer criteria, channel format, reference asset policy, and fallback routes
- Media asset manifest path and existing generated output assets when available

## Workflow

1. Define the baseline prompt and target model/settings.
2. Plan 2-3 variants only when the budget allows and approval scope covers them:
   - camera variant
   - performance/action variant
   - lighting/style variant
   - model/quality variant
3. Change one meaningful variable at a time so QA can attribute improvements or failures.
4. Preserve version ids, prompts, negative constraints, settings, reference assets, and credit estimates.
5. Tie each variant to a QA target such as prompt adherence, motion quality, continuity, editability, or artifact reduction.
6. After QA, decide whether to accept, reroll with a targeted fix, switch model, fall back to stock, or fall back to Remotion.
7. Stop when the max variant count, credit ceiling, repeated failure, rights blocker, or fallback preference is reached.

## Required Output

Return:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "scene_id": "string",
  "generation_id": "string",
  "max_variants": 3,
  "credit_ceiling": "string",
  "variant_plan": [
    {
      "variant_id": "string",
      "parent_generation_id": "string",
      "changed_variable": "camera | action | lighting | style | model | quality_mode | seed | duration | reference_asset | negative_constraint",
      "change_summary": "string",
      "qa_target": "string",
      "prompt_delta": "string",
      "settings_delta": {},
      "approval_covered": false
    }
  ],
  "stop_conditions": ["string"],
  "fallback_decision": {
    "fallback_stock": "string",
    "fallback_remotion": "string",
    "switch_model": "string"
  },
  "next_recommended_step": "string"
}
```

## Contract Fields Populated

- `ai-video-generation-package.schema.json`: `iteration.version`, `parent_generation_id`, `changed_variable`, `reroll_reason`, `next_action`, and planned output slots when applicable
- `clip-candidate.schema.json`: not updated until generated output QA creates or updates candidates
- `media-asset-manifest.schema.json`: deferred entries for planned variants or updated entries for generated outputs when files exist

## Status Policy

- Return `complete` when variants, changed variables, approval coverage, and stop conditions are clear.
- Return `needs_approval` when planned variants exceed approved scope, spend credits, upload references, or download provider outputs.
- Return `blocked` when no bounded variant can address the QA failure under budget/rights/provider limits.
- Return `needs_revision` when QA findings are too vague to target a single change.

## Media Manifest Policy

If this skill consumes, validates, compares, or defers generated variants, reference assets, provider previews, downloaded outputs, thumbnails, prompt sidecars, or QA evidence media, update the media asset manifest or return `manifest_actions[]`.

Each manifest action must include `action`, `asset_id`, `canonical_path`, `rights_state`, `technical_metadata_state`, and `reason`; include `remotion_public_path` and `static_file_path` when an accepted output will be mirrored for Remotion.

Use `deferred` for planned variants before generation approval, rerolls that may spend credits, provider outputs not yet downloaded, or files that still need QA before becoming timeline candidates.

## Evidence Required

Each variant must reference:

- parent generation id
- prompt/package version
- QA finding id or reroll reason
- changed variable
- credit estimate or budget assumption
- approval id or explicit `needs_approval`

## Approval And Stop Conditions

Stop before generating variants unless approval covers provider, model, settings, reference assets, variant count, and credit ceiling. Stop after repeated same-failure QA, budget ceiling, rights blocker, provider outage, or when a stock/Remotion fallback is more reliable.

## Definition Of Done

- Variant count is bounded and budget-aware.
- Each variant changes one meaningful variable.
- QA target and stop condition are explicit.
- Approval coverage is checked per variant.
- Fallback route is named before further generation.

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
      "action": "created | updated | not_applicable | deferred",
      "asset_id": "string",
      "reason": "string"
    }
  ],
  "validation_performed": ["variant bound check", "one-variable-change check", "approval coverage check", "budget ceiling check", "fallback check"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
