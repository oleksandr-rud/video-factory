# InVideo AI Generation Spec

## Purpose

This spec defines how the Video Factory uses InVideo AI and model-backed AI video generation for scene clips. The InVideo AI Generator is a production agent because AI generation has provider-specific prompts, credits, approval gates, model limits, variants, and output QA that should not live inside the general Visual Producer.

## Agent Boundary

Visual Producer owns the decision that a scene should use `ai_video_generation` and writes the scene-level route brief plus downstream handoff recommendation.

InVideo AI Generator owns:

- InVideo model/quality route selection
- Positive prompt and prompt guide construction
- Negative constraints or positive constraint rewrites
- Approval packet and credit/cost estimate
- Controlled variants and regeneration plans
- Generated clip QA and clip candidate packaging

Remotion Video Producer consumes the approved generated clip candidate. It does not regenerate AI media.

## Workflow

1. Visual Producer marks a scene route as `ai_video_generation` and provides visual goal, duration, aspect ratio, reference assets, continuity constraints, fallback route, and a Director-facing handoff recommendation.
2. Director converts the recommendation into an `agent-handoff` for InVideo AI Generator when the route is approved or needs specialist feasibility.
3. InVideo AI Generator chooses model route and quality mode.
4. InVideo AI Generator builds `positive_prompt`, `negative_prompt`, `prompt_guides`, settings, reference asset labels, and approval package.
5. Director approves or blocks credit spend.
6. After approval, generation is submitted manually or through an available provider workflow.
7. InVideo AI Generator records output paths/URLs, metadata, prompt version, credit use, and QA.
8. Accepted outputs become `clip-candidate` artifacts; rejected outputs keep rejection reasons and reroll recommendations.

## Positive Prompt Structure

Default prompt structure:

```text
<camera/lens>, <subject> <action> in <environment>, <lighting>, <style>, <audio>, <duration/aspect/reference constraints>.
```

Use concrete visual language. Prefer one primary action per short clip. For image-to-video, focus on motion: subject action, environmental motion, camera motion, motion style, timing, direction, and speed.

For Veo 3.1, use:

```text
Camera/Lens -> Subject -> Action -> Environment -> Lighting -> Style -> Audio
```

For Kling 3.0, use one structured statement with scene, distinct characters, action, camera, and audio direction.

For InVideo Agent One, write like a production brief to a colleague, include product URLs or image labels when available, and avoid dumping unreviewed prompts from another LLM.

## Negative Prompt Policy

Keep negative constraints in a separate internal field even if the provider route ultimately needs a positive rewrite.

Use `separate_field` only when the model supports negative prompts. Write unwanted visual elements as a compact list, not as commands.

Use `converted_to_positive_constraints` when a model responds better to positive phrasing. Example: use "locked camera, steady tripod shot" instead of "no camera movement".

Use `prompt_guide` for persistent brand, character, camera, lighting, or style constraints across multiple clips.

Never contradict the positive prompt.

## Pre-Generation Checklist

- Scene id and candidate id are stable.
- Route is approved by Visual Producer.
- Model, quality mode, duration, aspect ratio, resolution, and input type match provider limits.
- Positive prompt is clear, concrete, and clip-scoped.
- Negative constraints are separated or rewritten appropriately.
- Reference assets have labels, local paths, and rights notes.
- Credit/cost estimate is recorded.
- Director approval is recorded before generation.

## Post-Generation Checklist

- Output URL/path, model, prompt version, settings, and credit use are recorded.
- Clip is reviewed for prompt adherence, continuity, artifacts, rights, audio, and editability.
- Best outputs are converted to clip candidates.
- Failed outputs include rejection reasons and a targeted reroll plan.
- Fallback route remains available if generation does not converge.
