---
name: multimodal-video-critique
description: Run or prepare a comprehensive multimodal critique of a rendered video using approved hybrid video analysis when available: direct video input plus sampled frame stills, transcript or captions, timeline data, media asset manifest, scenario, channel format, and render artifacts. Use when final output needs extensive visual, audio, story, subtitle, brand, platform, and delivery criticism.
---

# Multimodal Video Critique

Read `../../references/video-critique-rubric.md` before writing the critique. Use `prepare-multimodal-review-package` first so metadata, artifact paths, media asset provenance, and sampled frame stills are available. When the Director provides production criteria, treat them as binding review instructions. The general rubric fills gaps; it does not override user, producer, channel, rights, or platform rules.

## Model Route

Use approved hybrid analysis as the preferred route when the rendered video fits provider limits and the Director has approved API spend and media handling.

Preferred route:

- OpenRouter hybrid video review with `qwen/qwen3.6-plus` through `../../scripts/run_openrouter_video_critique.py`.
- Requires `OPENROUTER_API_KEY`, explicit `--approved`, and either `review_assets.video_path` for base64 upload or `--video-url` for hosted media.
- Sends direct video plus up to `OPENROUTER_VIDEO_REVIEW_MAX_FRAME_IMAGES` sampled frame stills by default. Use `--max-frame-images` to tune this or `--no-frame-images` for direct-video-only.
- Produces `review_mode: hybrid` when sampled frame stills are attached, or `review_mode: direct_video` when they are not. It writes an OpenRouter prompt, request preview, raw response when executed, and critique report.
- Treat Qwen video review as strong visual/video understanding, not a substitute for transcript/caption evidence. Do not infer spoken audio content unless supplied by captions, transcript, voiceover artifacts, or an audio-capable provider.

Fallback route:

- OpenAI Responses API with sampled frame images and artifact text through `../../scripts/run_openai_multimodal_critique.py`.
- Use when OpenRouter hybrid/direct video input is unavailable, blocked by size/format/provider limits, not approved, or insufficient for the needed evidence.

Run `../../scripts/run_openai_multimodal_critique.py` only when:

- the Director approved API spend and media handling
- `OPENAI_API_KEY` is present
- the review assets package exists
- the target model is set explicitly or through `OPENAI_VISION_MODEL`
- producer criteria and previous critique paths are included when this is a review-loop iteration

Run `../../scripts/run_openrouter_video_critique.py` only when:

- the Director approved OpenRouter API spend and media handling
- `OPENROUTER_API_KEY` is present
- the review assets package exists
- the target model is set explicitly or through `OPENROUTER_VIDEO_MODEL`; default is `qwen/qwen3.6-plus`
- producer criteria and previous critique paths are included when this is a review-loop iteration

Without approval, run either script without `--execute` to produce the prompt package and a `needs_approval` critique report.

## Critique Dimensions

Score and critique:

- hook and retention risk
- story clarity, payoff, and source alignment
- scene-level visual relevance and quality
- edit rhythm, pacing, and continuity
- voiceover clarity, mix, music, and SFX
- caption accuracy, sync, safe area, and readability
- brand/channel fit and anti-redundancy
- VFX quality, channel-format VFX compliance, alpha/export artifacts, and visible render-performance compromises
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
