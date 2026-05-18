---
name: generation-approval-package
description: Prepare approval packets for InVideo AI and paid AI video generation, including model, prompt, duration, aspect ratio, resolution, generation count, credit/cost estimate, and approval status. Use before spending credits or triggering generation.
---

# Generation Approval Package

Create the exact approval packet that the Director can show the user before any InVideo or AI-video credits are spent.

## Inputs

- Model decision from `invideo-model-selection`
- Positive prompt, negative constraints, prompt guide notes, and reference assets
- Scene id, project path, channel fields, media asset manifest path, and candidate id when known
- Duration, aspect ratio, resolution, fps, native audio/lip-sync flags, seed, and variant count
- Provider UI/account estimate or known plan data
- Producer criteria, budget policy, source rights policy, and Director approval record when already granted

## Workflow

1. Collect model route, quality mode, prompt, negative constraints, reference assets, duration, aspect ratio, resolution, and number of variants.
2. Estimate credits/cost from current provider UI or known plan data when available; mark as `unknown` if not available.
3. Check parsed web reference assets: page images/screenshots must have media-manifest approval before they can be submitted as generation references.
4. Check likeness, logo, brand, music/audio, and source rights risks before approval.
5. Mark approval state:
   - `pending` before Director approval.
   - `approved` only after explicit approval.
   - `rejected` when Director denies or budget blocks the run.
6. Record exactly what the generation dialog will submit: prompt, model, duration, aspect ratio, quality mode, reference assets, expected outputs, and target media asset manifest path.
7. Include an expiry or re-confirmation note when provider UI estimates, credits, or model availability may change before execution.
8. If approval is missing, return a package with status `needs_approval`; do not run generation.

## Required Output

Return an approval-ready package matching `codex/contracts/ai-video-generation-package.schema.json`:

```json
{
  "status": "needs_approval | approved | blocked | rejected",
  "generation_package_path": "string",
  "approval_packet": {
    "scene_id": "string",
    "provider": "string",
    "platform_route": "string",
    "model": {
      "name": "string",
      "quality_mode": "string"
    },
    "positive_prompt": "string",
    "negative_prompt": "string",
    "negative_prompt_mode": "string",
    "prompt_guides": ["string"],
    "settings": {
      "duration_seconds": 0,
      "aspect_ratio": "string",
      "resolution": "string",
      "variant_count": 1,
      "native_audio": false,
      "lip_sync": false
    },
    "reference_assets": [
      {
        "label": "string",
        "path_or_url": "string",
        "rights_notes": "string",
        "approved_for_provider_submission": false
      }
    ],
    "credit_estimate": "string",
    "cost_estimate": "string",
    "approval_state": "pending | approved | rejected",
    "approval_scope": "string",
    "expires_or_reconfirm_after": "string"
  },
  "approvals_needed": ["generation | provider_upload | reference_asset_use | paid_quality_mode | file_download"],
  "next_recommended_step": "string"
}
```

## Contract Fields Populated

- `ai-video-generation-package.schema.json`: `generation_id`, `scene_id`, project/channel fields, `provider`, `platform_route`, `model`, `status`, prompts, settings, reference assets, evidence refs, `approval`, `outputs`, `iteration`, and `qa`
- `media-asset-manifest.schema.json`: deferred input/output assets and future generated output slots when relevant

## Status Policy

- Return `needs_approval` when all packet fields are ready but Director/user approval is not recorded.
- Return `approved` only when approval is explicit, scoped to the same provider/model/settings/reference assets, and still valid.
- Return `blocked` when cost, rights, reference assets, provider terms, or missing inputs make safe approval impossible.
- Return `rejected` when the Director/user denies the generation or the budget policy forbids it.

## Media Manifest Policy

If this skill consumes, references, validates, or defers reference assets, seed images, source clips, generated-output placeholders, provider previews, or future downloaded generation files, update the media asset manifest or return `manifest_actions[]`.

Each manifest action must include `action`, `asset_id`, `canonical_path`, `rights_state`, `technical_metadata_state`, and `reason`; include `remotion_public_path` and `static_file_path` when approved outputs will be mirrored for Remotion.

Use `deferred` until generation is approved and actual files exist. The approval package must identify which source asset ids and future output asset ids will need manifest entries before downstream timeline work.

## Evidence Required

Preserve:

- exact prompt text and negative prompt mode
- model, quality mode, duration, aspect ratio, resolution, variant count, and seed when available
- credit/cost estimate source or `unknown`
- reference asset ids and rights notes
- approval id, approver, timestamp, approval scope, and expiry/reconfirm note when approved

## Approval And Stop Conditions

Stop before generation unless approval is explicit and matches the exact packet fields. If any field changes after approval, return `needs_approval` again. Stop when reference assets, source images, likeness/logos, provider uploads, paid quality modes, or file downloads are outside the approved scope.

## Definition Of Done

- The approval packet exactly mirrors the provider submission.
- Cost/credit and rights risks are explicit.
- Approval state is `pending`, `approved`, `rejected`, or blocked with a reason.
- Deferred manifest actions identify source assets and future outputs.
- No generation call is made by this skill.

## Handoff Summary Shape

Return:

```json
{
  "status": "needs_approval | approved | blocked | rejected",
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
  "validation_performed": ["packet completeness", "approval scope check", "cost estimate check", "reference rights check", "manifest deferral check"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
