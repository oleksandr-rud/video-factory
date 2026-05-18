---
name: multimodal-video-critique
description: Run or prepare a comprehensive multimodal critique of a rendered video using sampled frames, transcript or captions, timeline data, scenario, channel format, and render artifacts. Use when final output needs extensive visual, audio, story, subtitle, brand, platform, and delivery criticism.
---

# Multimodal Video Critique

Read `../../references/video-critique-rubric.md` before writing the critique. Use `prepare-multimodal-review-package` first. When the Director provides production criteria, treat them as binding review instructions. The general rubric fills gaps; it does not override user, producer, channel, rights, or platform rules.

## Model Route

Use a vision-capable model through the approved provider. For OpenAI, use the Responses API with sampled frame images and artifact text. Current OpenAI docs support image inputs in Responses API; treat video review as sampled-frame plus transcript/artifact analysis unless the Director provides a provider with direct video input.

Run `../../scripts/run_openai_multimodal_critique.py` only when:

- the Director approved API spend and media handling
- `OPENAI_API_KEY` is present
- the review assets package exists
- the target model is set explicitly or through `OPENAI_VISION_MODEL`
- producer criteria and previous critique paths are included when this is a review-loop iteration

Without approval, run the script in dry-run mode to produce the prompt package and a `needs_approval` critique report.

## Critique Dimensions

Score and critique:

- hook and retention risk
- story clarity, payoff, and source alignment
- scene-level visual relevance and quality
- edit rhythm, pacing, and continuity
- voiceover clarity, mix, music, and SFX
- caption accuracy, sync, safe area, and readability
- brand/channel fit and anti-redundancy
- platform fit: duration, aspect ratio, opening frame, CTA, and mobile readability
- factual, rights, likeness, watermark, and delivery risks
- accessibility and viewer comprehension

## Output

Return `codex/contracts/critique-report.schema.json` with:

- timestamped observations
- scene-by-scene reviews and gate results
- severity-ranked findings
- numeric category scores
- concrete recommendations
- owner agent for each fix
- limitations of the review method
- prioritized revision plan
- release-candidate gate decision

Do not rewrite the video directly. The Director routes revisions.
