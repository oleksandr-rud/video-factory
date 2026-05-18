---
name: ai-video-prompt-builder
description: Build model-ready positive prompts and InVideo prompt guide notes for AI-generated clips. Use for scene-specific InVideo, Veo, Sora, Kling, or Agent One generation prompts that need camera, subject, action, environment, lighting, style, audio, references, and duration constraints.
---

# AI Video Prompt Builder

Read `../../references/invideo-ai-generation.md` when model-specific prompt structure matters.

Build a provider-ready prompt package after model selection but before approval. Do not submit the prompt to a provider in this skill.

## Inputs

- Visual Producer AI generation brief and scene visual pack entry
- Selected model route/settings from `invideo-model-selection`
- Scenario scene, narration, desired on-screen text policy, and continuity notes
- Producer criteria, channel format, approved reference assets, and evidence refs
- Negative constraints from `negative-prompt-guardrails`
- Provider prompt guide requirements and media asset manifest rights state

## Workflow

1. Start from the visual pack scene goal and selected model route.
2. Write one concrete positive prompt using visual filmmaking language:
   - camera/lens
   - subject
   - action
   - environment
   - lighting
   - style
   - audio
   - duration/aspect/reference constraints
3. Keep the clip scoped to one primary action unless the model route explicitly supports multi-shot sequencing.
4. If the brief includes parsed web content, use claim/source/evidence refs for factual grounding but do not copy article text or page imagery into the prompt unless rights are approved.
5. For image-to-video, describe motion and temporal progression more than static image details.
6. Add Prompt Guide notes for stable brand, character, camera, lighting, or voice rules that should persist across generations.
7. Keep text rendering requests minimal unless the provider and model are known to handle text reliably.
8. Add output fields for `positive_prompt`, `prompt_guides`, `settings`, and `reference_assets` in `codex/contracts/ai-video-generation-package.schema.json`.

## Required Output

Return:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "scene_id": "string",
  "generation_id": "string",
  "positive_prompt": "string",
  "negative_prompt": "string",
  "negative_prompt_mode": "separate_field | converted_to_positive_constraints | prompt_guide | unsupported | not_used",
  "prompt_guides": ["string"],
  "settings": {
    "duration_seconds": 0,
    "aspect_ratio": "string",
    "resolution": "string",
    "shot_type": "string",
    "native_audio": false,
    "lip_sync": false,
    "loop": false,
    "variant_count": 1
  },
  "reference_assets": [
    {
      "label": "string",
      "path_or_url": "string",
      "intended_use": "string",
      "rights_notes": "string"
    }
  ],
  "residual_risks": ["string"],
  "next_recommended_step": "string"
}
```

## Contract Fields Populated

- `ai-video-generation-package.schema.json`: `positive_prompt`, `negative_prompt`, `negative_prompt_mode`, `prompt_guides`, `settings`, `reference_assets`, `evidence_refs`, `approval.status: pending`, and `qa.status: not_run`
- `media-asset-manifest.schema.json`: no generated assets; deferred manifest actions only for provider-submitted references or future outputs

## Status Policy

- Return `complete` when the prompt package is ready for `generation-approval-package`.
- Return `needs_approval` when prompt use depends on source image submission, paid generation, likeness/logo use, or provider upload.
- Return `blocked` when rights, model limits, or contradictory requirements make the prompt unsafe or unbuildable.
- Return `needs_revision` when the scene brief lacks visual intent, duration/aspect, source grounding, or target model route.

## Evidence Required

Preserve scene id, model decision, visual brief path, evidence refs, reference asset ids, prompt guide sources, and any assumptions about provider capabilities.

## Media Manifest Policy

Do not create media assets. Return `manifest_actions[]` with `deferred` for approved reference assets that may be submitted to a provider and for planned generated outputs that will need QA before timeline use.

## Approval And Stop Conditions

Stop before provider submission, generation, paid modes, reference image upload, or external media transfer without Director approval. If a prompt requires unapproved page imagery, copyrighted text, real-person likeness, logos, or unsafe endorsement, return `needs_approval` or `blocked`.

## Definition Of Done

- Positive prompt is concrete, scoped, and model-aware.
- Negative constraints are represented in the supported mode.
- Settings and reference assets match the selected model route.
- Prompt guide notes carry only reusable constraints.
- Approval needs and residual risks are explicit.

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
      "action": "deferred | not_applicable",
      "asset_id": "string",
      "reason": "string"
    }
  ],
  "validation_performed": ["model alignment", "prompt specificity", "negative constraint check", "reference rights check", "approval gate check"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
