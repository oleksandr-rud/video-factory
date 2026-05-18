---
name: invideo-model-selection
description: Choose the correct InVideo AI route, quality mode, and model for AI-generated video clips or full InVideo-managed scenes. Use when a scene is marked for ai_video_generation and needs Agent One, Basic, Pro, Ultra, Sora 2, Veo 3.1, Kling 3.0, or a fallback model decision.
---

# InVideo Model Selection

Read `../../references/invideo-ai-generation.md` before selecting a model.

Choose the lowest adequate AI video route before prompt construction or approval packaging. Do not generate media in this skill.

## Inputs

- Visual Producer AI video route brief and `handoff_recommendation`
- Scenario scene, duration, aspect ratio, platform, and continuity requirements
- Producer criteria, channel format, and approved reference asset policy
- Budget policy, credit/cost ceiling, provider availability, account/UI state, and Director approval state
- Existing generated variants or QA failures when this is a reroute

## Workflow

1. Classify the scene: background visual, product/brand shot, human performance, dialogue/lipsync, multi-character scene, transition insert, full story segment, or short clip.
2. Choose the lowest adequate quality mode:
   - Basic: stock-backed background or straightforward clip.
   - Pro: important generated clip with realistic motion or acting.
   - Ultra: high-stakes realism, brand/product integration, or full story generation.
3. Choose model route:
   - Sora 2 Pro for 4-12 second clips when Sora is explicitly desired.
   - Veo 3.1 for high-fidelity cinematic 4-8 second shots, camera/lens control, first/last frame continuity, or product demo shots.
   - Kling 3.0 for 3-15 second clips with native audio, multi-shot sequencing, multi-character continuity, or lip sync.
   - Agent One for full InVideo-managed videos or conversational iterative editing.
4. Record duration, aspect ratio, resolution, input types, reference assets, and credit/cost risk.
5. Check provider limits against the requested scene. Mark unknown limits rather than guessing.
6. Provide one cheaper fallback and one non-AI fallback when possible.
7. Stop at `needs_approval` when the selected route implies credits, paid modes, provider uploads, or rights-sensitive references.

## Required Output

Return this model decision and use it to populate the generation package:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "scene_id": "string",
  "model_decision": {
    "provider": "invideo_ai | sora | veo | kling | other",
    "platform_route": "invideo_agent_one | invideo_generative_model | manual_provider | api_provider",
    "model_name": "string",
    "quality_mode": "basic | pro | ultra | lite | model_direct | unknown",
    "duration_seconds": 0,
    "aspect_ratio": "string",
    "resolution": "string",
    "native_audio": false,
    "lip_sync": false,
    "reference_input_types": ["none | image | video | first_frame | last_frame | text"],
    "rationale": "string"
  },
  "cost_risk": {
    "credit_estimate": "string",
    "cost_estimate": "string",
    "risk_level": "low | medium | high | unknown",
    "budget_policy_fit": "pass | fail | needs_approval | unknown"
  },
  "fallbacks": [
    {
      "route": "string",
      "model_or_method": "string",
      "tradeoff": "string"
    }
  ],
  "approvals_needed": ["generation | provider_upload | reference_asset_use | paid_quality_mode"],
  "next_recommended_step": "string"
}
```

## Contract Fields Populated

- `ai-video-generation-package.schema.json`: `provider`, `platform_route`, `model`, `settings`, `reference_assets`, `approval`, and `status`
- `scene-visual-pack.schema.json`: consumes `ai_video_generation_brief`; does not modify Visual Producer output unless explicitly asked
- `media-asset-manifest.schema.json`: no new media entries; return deferred actions for reference assets that may be submitted to a provider

## Status Policy

- Return `complete` when a model/settings decision is ready for prompt building and approval packaging.
- Return `needs_approval` when credits, paid quality modes, provider uploads, reference asset use, likeness/logo use, or generation execution needs Director approval.
- Return `blocked` when no model route can satisfy duration, aspect ratio, rights, budget, or provider limits.
- Return `needs_revision` when the Visual Producer brief or scene requirements are too vague or contradictory.

## Evidence Required

Preserve:

- scene id and Visual Producer route brief id/path
- model/provider source used for limits when available
- provider UI/account notes when used
- credit/cost estimate source or `unknown`
- fallback rationale and non-AI fallback

## Media Manifest Policy

Do not write generated-output assets. If reference assets are proposed for provider upload, return `manifest_actions[]` as `deferred` with the source asset id, rights state, and reason.

## Approval And Stop Conditions

Stop before any generation, paid mode, provider upload, reference-image submission, or rights-sensitive use without Director approval. This skill may prepare a decision object and an approval requirement only.

## Definition Of Done

- Scene classification and model route are explicit.
- Duration/aspect/resolution and input types are compatible or marked unknown.
- Cost/credit risk and approval need are explicit.
- Cheaper and non-AI fallback paths are recorded.

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
  "validation_performed": ["scene classification", "model limit check", "cost risk check", "fallback check", "approval gate check"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
