---
name: ai-video-generation-brief
description: Prepare route-level AI video generation briefs for scenes, including visual goal, prompt intent, constraints, references, aspect ratio, duration, fallback, and cost risk. Use when Visual Producer needs to decide whether to hand a scene to InVideo AI Generator or another approved provider.
---

# AI Video Generation Brief

Prepare the Visual Producer's route brief for AI video generation. This is not a provider-final prompt and must not spend credits or call an AI-video provider.

## Inputs

- Scene visual pack entry, scenario scene, and candidate requirements
- Producer criteria, channel format, and reference analysis
- Approved reference assets, media asset manifest state, and evidence refs
- Desired aspect ratio, duration, resolution, first/last frame needs, loop needs, and continuity requirements
- Budget policy, provider availability, approval state, and fallback route

## Workflow

1. Convert the visual goal into a route brief, not a final provider prompt.
2. Add desired camera motion, subject action, lighting, environment, mood, pacing, style, and continuity needs.
3. Include reference assets only as source/evidence refs unless the media manifest approves the asset for provider submission.
4. Add known unwanted artifacts and constraints for downstream prompt building. Include "do not copy supplied article/page imagery or exact text" when rights are not approved.
5. Specify aspect ratio, duration, resolution, keyframes or first/last frame needs, loop needs, and technical constraints.
6. Estimate risk: identity drift, text rendering, physics, hand detail, brand mismatch, cost, rights, editability, reroll likelihood, and fallback cost.
7. Add one non-AI fallback route and one stock/Remotion fallback when possible.
8. If AI generation is still justified, add a Director-facing `handoff_recommendations[]` entry for `invideo-ai-generator`; do not read or execute that agent's skills.
9. Include recommended objective, required scene inputs, approval notes, fallback route, output contract, stop conditions, and definition of done.

## Required Output

Embed a brief in `scene-visual-pack.schema.json` and return:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "scene_briefs": [
    {
      "scene_id": "string",
      "route": "ai_video_generation",
      "prompt_intent": "string",
      "camera_motion": "string",
      "subject_action": "string",
      "environment_lighting_style": "string",
      "reference_assets": [
        {
          "asset_id": "string",
          "path_or_url": "string",
          "allowed_for_provider_submission": false,
          "rights_notes": "string"
        }
      ],
      "constraints": ["string"],
      "negative_constraints": ["string"],
      "settings_target": {
        "duration_seconds": 0,
        "aspect_ratio": "string",
        "resolution": "string",
        "first_frame_needed": false,
        "last_frame_needed": false,
        "loop": false
      },
      "risk_assessment": {
        "cost_risk": "low | medium | high | unknown",
        "rights_risk": "low | medium | high | unknown",
        "artifact_risk": "low | medium | high | unknown",
        "editability_risk": "low | medium | high | unknown"
      },
      "fallback_route": "stock_clip | remotion_generated | source_card_recreation | user_supplied_media",
      "handoff_recommendation_id": "string"
    }
  ],
  "next_recommended_step": "string"
}
```

## Contract Fields Populated

- `scene-visual-pack.schema.json`: `ai_video_generation_brief`, `ai_generation_prompts`, `negative_constraints`, `reference_asset_paths`, `invideo_model_hint`, and `handoff_recommendations[]`
- `agent-handoff.schema.json`: not written here; the Director converts handoff recommendations into formal handoffs
- `ai-video-generation-package.schema.json`: not written here; InVideo AI Generator owns the generation package

## Status Policy

- Return `complete` when the route brief is clear and the Director can decide whether to hand off to InVideo AI Generator.
- Return `needs_approval` when provider submission, generation, reference asset use, paid credits, likeness/logo use, or licensed material needs approval.
- Return `blocked` when AI generation is not viable and no fallback route exists.
- Return `needs_revision` when the scene intent, source rights, duration, or technical requirements are too vague.

## Evidence Required

Each brief must cite scene id plus any relevant source ids, evidence refs, channel-format rules, producer criteria, and media asset ids. If the brief is creative-only, mark the evidence state as exploratory.

## Media Manifest Policy

Do not create generated media assets. Return `manifest_actions[]` with `deferred` for reference assets that may be submitted to a provider, future generated outputs, or assets that will need Remotion public projection after approval and QA.

## Approval And Stop Conditions

Stop before sending source assets to a provider, generating media, spending credits, using paid modes, or using rights-sensitive likeness/logo/source material. The only allowed output before approval is a route brief and a Director-routable handoff recommendation.

## Definition Of Done

- Prompt intent, constraints, target settings, risk, and fallback route are explicit.
- Reference asset rights and provider-submission eligibility are clear.
- InVideo handoff recommendation is implementation-neutral and contract-shaped.
- No provider-final prompt or generation execution is implied.

## Handoff Summary Shape

Return:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "artifact_paths": ["string"],
  "changed_files": ["string"],
  "populated_contracts": ["codex/contracts/scene-visual-pack.schema.json"],
  "manifest_actions": [
    {
      "action": "deferred | not_applicable",
      "asset_id": "string",
      "reason": "string"
    }
  ],
  "validation_performed": ["route brief", "reference rights check", "target settings check", "risk assessment", "fallback check"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
