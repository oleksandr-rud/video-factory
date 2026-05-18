---
name: generated-clip-qa
description: QA AI-generated video clips from InVideo or related models and convert acceptable outputs into clip candidates with pass/fail evidence, reroll decisions, rights checks, manifest actions, and Director-routable blockers. Use after generation to inspect prompt adherence, visual artifacts, continuity, audio, technical metadata, and editability.
---

# Generated Clip QA

Treat generated clips as candidates until QA proves they are usable. Do not promote a generated output into timeline-ready status because it looks acceptable at a glance.

## Inputs

- AI video generation package matching `codex/contracts/ai-video-generation-package.schema.json`
- Generated outputs, previews, thumbnails, provider asset ids, request ids, and download paths when available
- Original scene visual brief, scenario scene, producer criteria, channel format, and reference asset rules
- Approval record for generation, download, paid provider use, likeness/logo use, or licensed source material
- Media asset manifest path and Remotion public/static path policy when local editing is expected
- Existing clip candidate to update, when the package already has `candidate_id`

## Workflow

1. Verify package identity: `generation_id`, `scene_id`, provider/model, approval status, settings, prompts, outputs, and variant lineage.
2. Confirm the output is the approved/generated variant, not a stale preview or unrelated provider asset.
3. Review prompt adherence against the scene brief:
   - subject/action/location/mood
   - camera and motion intent
   - reference asset use
   - required exclusions or converted negative constraints
4. Check technical fit:
   - duration, aspect ratio, resolution, fps, codec/probe data when available
   - local path and Remotion `staticFile()` path when downloaded for editing
   - audio presence, looping, clean start/end, crop/safe-area risk
5. Check generated artifact risk:
   - flicker, morphing, hands/faces, text/logo errors, physics, temporal consistency, unwanted subtitles/watermarks
6. Check rights and approval state:
   - provider terms, credit/cost record, likeness/logo risk, reference asset rights, download approval
7. Check continuity and brand fit against adjacent scenes and channel format.
8. Decide recommendation: accept as candidate, accept as fallback only, reroll, switch model, fallback to stock, fallback to Remotion, or block.
9. Update the generation package QA and create/update the matching clip candidate.

## Required Output

Update `codex/contracts/ai-video-generation-package.schema.json`:

- `status`
- `outputs[]`
- `iteration.next_action`
- `qa.status`
- `qa.summary`
- `qa.findings[]`

Create or update `codex/contracts/clip-candidate.schema.json`:

- `candidate_id`
- `scene_id`
- `route: ai_video_generation`
- `provider`
- `local_path`
- `remotion_static_file_path`
- `ai_video_generation_package_path`
- `generation_id`
- `technical`
- `license_summary`
- `media_asset_id`
- `scores`
- `status`
- `rejection_reason` when rejected

Return this QA summary:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "generation_id": "string",
  "scene_id": "string",
  "candidate_id": "string",
  "output_reviews": [
    {
      "output_id": "string",
      "path_or_url": "string",
      "prompt_adherence": { "status": "pass | fail | partial | unknown", "evidence": "string" },
      "technical_fit": { "status": "pass | fail | partial | unknown", "evidence": "string" },
      "rights_fit": { "status": "pass | fail | unknown | needs_approval", "evidence": "string" },
      "continuity_fit": { "status": "pass | fail | partial | unknown", "evidence": "string" },
      "brand_fit": { "status": "pass | fail | partial | unknown", "evidence": "string" },
      "editability": { "status": "pass | fail | partial | unknown", "evidence": "string" },
      "artifact_risk": { "status": "pass | fail | partial | unknown", "evidence": "string" },
      "recommendation": "accept_candidate | fallback_only | reroll | switch_model | fallback_stock | fallback_remotion | reject | needs_approval",
      "reroll_needed": false,
      "blocking_reasons": ["string"]
    }
  ],
  "candidate_update": {
    "candidate_id": "string",
    "status": "proposed | needs_approval | approved | rejected | downloaded | generated",
    "score_summary": "string"
  },
  "next_recommended_step": "string"
}
```

## Contract Fields Populated

- `ai-video-generation-package.schema.json`: `status`, `outputs`, `iteration`, `qa`
- `clip-candidate.schema.json`: generated candidate identity, paths, technical metadata, scores, status, rejection reason
- `media-asset-manifest.schema.json`: asset entries for downloaded/generated videos, thumbnails, metadata, QA reports, or Remotion public projections

## Status Policy

- Use `complete` only when QA is finished and the package/candidate status is updated.
- Use `needs_approval` when rights, provider terms, download, paid generation, likeness/logo use, or external media handling still needs Director approval.
- Use `blocked` when the generated clip cannot be used and reroll/fallback cannot proceed safely.
- Use `needs_revision` when prompt/package inputs are stale, contradictory, or insufficient for QA.
- Set generation package `qa.status` to `pass`, `partial`, `fail`, or `not_run` according to evidence; do not use `pass` with unknown rights or missing output identity.

## Evidence Required

Each output review must cite at least one of:

- generated output path or provider URL
- provider asset id/request id
- prompt or generation package field
- visual inspection timestamp
- thumbnail/preview path
- media asset id
- technical metadata or probe path
- producer criteria or channel-format rule

Missing direct video access must be recorded as a limitation and may force `partial` or `unknown`.

## Media Manifest Policy

When a real generated file, preview, thumbnail, metadata file, QA report, or Remotion public projection exists, update or request update of `media-asset-manifest.schema.json` with:

- `asset_id`
- `kind: ai_generated_clip`, `thumbnail`, `metadata`, or `other`
- `origin: ai_generation`
- `canonical_path`
- `remotion_public_path` and `static_file_path` when relevant
- rights and approval state
- technical metadata
- source generation id and related contract paths

Return `manifest_actions[]` with `updated`, `created`, `deferred`, or `not_applicable`.

## Approval And Stop Conditions

Stop and return `needs_approval` before downloading, spending credits, using premium modes, approving likeness/logo risk, or sending media to another external provider.

Stop and return `blocked` when:

- the generated output is unavailable or does not match the generation package
- provider terms or rights are incompatible with the intended use
- artifacts make the clip misleading, unusable, or brand unsafe
- no reroll/fallback path is allowed under budget policy
- local editing is required but no usable file/static path can be obtained

## Definition Of Done

- Every generated output has a QA decision and evidence.
- The generation package `qa` object is updated.
- The clip candidate is created or updated with route, paths, scores, status, and rejection reason when needed.
- Manifest actions are reported for every local/generated/review artifact.
- Reroll or fallback guidance is explicit and bounded.

## Handoff Summary Shape

Return:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "artifact_paths": ["string"],
  "changed_files": ["string"],
  "populated_contracts": [
    "codex/contracts/ai-video-generation-package.schema.json",
    "codex/contracts/clip-candidate.schema.json"
  ],
  "manifest_actions": [
    {
      "action": "created | updated | not_applicable | deferred",
      "asset_id": "string",
      "reason": "string"
    }
  ],
  "validation_performed": ["prompt adherence", "technical fit", "rights fit", "continuity fit", "brand fit", "editability", "artifact risk"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
