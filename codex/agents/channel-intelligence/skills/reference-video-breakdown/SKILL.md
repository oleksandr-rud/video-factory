---
name: reference-video-breakdown
description: Analyze reference videos in depth, including transcript rhythm, shot structure, pacing, camera movement, visual style, captions, graphics, audio, packaging, and reusable production patterns. Use when reference videos, video URLs, local media, transcripts, or screenshots are supplied.
---

# Reference Video Breakdown

Read `../../references/reference-analysis-dimensions.md` before analyzing videos.

Workflow:

1. Prefer direct evidence: transcript, timecoded notes, screenshots, thumbnails, local media metadata, media asset manifest entries, and approved direct-video model observations when available.
2. Segment the video into meaningful beats or shots with timestamps.
3. Capture narrative structure: hook, setup, proof, tension, payoff, CTA, and recurring sections.
4. Capture visual production patterns: shot size, camera movement, B-roll type, graphics, captions, motion, color, typography, transitions, and thumbnail/opening-frame conventions.
5. Capture audio patterns: voice style, pacing, music, SFX, pauses, ambience, and mix density.
6. Extract reusable patterns separately from one-off choices.
7. Flag content that should not be copied directly, including proprietary footage, likeness, exact phrasing, or overly similar edits.

Direct-video model analysis belongs here for upstream reference breakdowns, not in Visual Producer. Use it only after Director approval for API spend and media handling, keep the transcript/caption source separate from visual observations, and record limitations when the model cannot verify audio or rights.

Return a timecoded analysis and reusable pattern summary for `codex/contracts/reference-analysis.schema.json`. When a local video, transcript, thumbnail, sampled frame, or model-observation artifact is used, record or reference the corresponding asset id from `codex/contracts/media-asset-manifest.schema.json`.
