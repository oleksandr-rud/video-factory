---
name: prepare-multimodal-review-package
description: Prepare a rendered video for multimodal critique by extracting representative frames, ffprobe metadata, artifact paths, captions, and timeline context. Use when a final render or render candidate must be reviewed by a vision-capable model or by an independent critic.
---

# Prepare Multimodal Review Package

Use this before `multimodal-video-critique`. The goal is to convert a video file into bounded evidence a multimodal model can inspect, while preserving the original local video path for approved hybrid/direct-video providers and extracting sampled frame stills for hybrid review.

## Workflow

1. Read the render package and locate the primary video output.
2. Collect linked artifacts: scenario, timeline sync plan, voiceover package, captions, channel format, reference analysis, media asset manifest, Remotion project contract, and rights notes.
3. Include the producer criteria artifact and previous critique report when this is a review-loop iteration.
4. Run `../../scripts/prepare_video_review_assets.py` with the video path and available artifact paths.
5. Prefer scene-aware frame samples from the timeline sync plan. If scene timing is unavailable, sample evenly across the video.
6. Keep the frame count bounded. Default to 24 frames for full-video review unless the Director requests a deeper pass.
7. For approved hybrid review, pass the same review assets package to the OpenRouter runner; it uses the original video plus sampled frame stills by default.
8. Return the review assets path, sampled frame list, metadata, original video path, media asset ids for frames when recorded, missing inputs, producer criteria path, previous critique path, and limitations.

## Rules

- Use local rendered files, not remote media URLs, for final critique.
- Mark the review package partial if frames cannot be extracted.
- Do not call a paid multimodal API from this skill. Prepare evidence only.

## Media Manifest Policy

If this skill consumes, creates, samples, validates, probes, mirrors, or defers review media, source render files, frame stills, thumbnails, metadata sidecars, prompt packages, captions, or sampled evidence assets, update the media asset manifest or return `manifest_actions[]`.

Each manifest action must include `action`, `asset_id`, `canonical_path`, `remotion_public_path` and `static_file_path` when relevant, `rights_state`, `technical_metadata_state`, and `reason`.

Use `deferred` when frame extraction, metadata probing, direct-video packaging, or review asset creation cannot run. The critic must know whether missing review media is a model limitation, media policy blocker, or technical extraction failure.
