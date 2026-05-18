---
name: reference-video-breakdown
description: Analyze reference videos in depth, including transcript rhythm, shot structure, pacing, camera movement, visual style, captions, graphics, audio, packaging, and reusable production patterns. Use when reference videos, video URLs, local media, transcripts, or screenshots are supplied.
---

# Reference Video Breakdown

Read `../../references/reference-analysis-dimensions.md` before analyzing videos.

## Inputs

- Reference video path or URL, source id, and rights notes from source corpus ingestion
- Project path, channel profile path, media asset manifest path, and existing reference analysis when available
- Transcript, screenshots, thumbnail, timecoded notes, or direct-video observations when already approved and captured
- Director approval state for paid/cloud transcription, direct-video model calls, and media handling

## Workflow

1. Prefer deterministic evidence before interpretation: local metadata, shot/segment boundaries, keyframes, transcript, OCR, and media manifest entries.
2. For local files, run `../../scripts/analyze_reference_video.py` to prepare ffprobe metadata, scene/segment JSON, keyframes, optional OCR, and a contract-shaped reference analysis fragment:
   ```powershell
   python codex/agents/channel-intelligence/scripts/analyze_reference_video.py `
     --video <local-reference-video> `
     --source-id <source-id> `
     --work-dir <project-or-channel-reference-work-dir> `
     --output <reference-analysis-json>
   ```
3. If the local script returns `partial`, preserve the artifacts it did produce and list missing tools or evidence gaps instead of inventing observations.
4. Segment the video into meaningful beats or shots with timestamps. Use PySceneDetect output when available; otherwise use fallback segments as provisional timing evidence.
5. Interpret the deterministic evidence into production observations: hook, setup, proof, tension, payoff, CTA, recurring sections, shot grammar, caption/graphics usage, motion language, audio rhythm, and packaging conventions.
6. Extract reusable patterns separately from one-off choices. Keep exact clip choices out of channel rules unless they are legitimate reusable assets.
7. Flag content that should not be copied directly, including proprietary footage, likeness, exact phrasing, exact edit rhythm, or overly similar shots.
8. Direct-video model analysis belongs here for upstream reference breakdowns, not in Visual Producer. Use it only after Director approval for API spend and media handling; keep transcript/caption evidence separate from model visual observations.

## Required Output

Return or update `codex/contracts/reference-analysis.schema.json` with:

- `processing_runs[]` for local extraction tools, model observations, status, outputs, and limitations
- `sources[]` entries with source ids, rights notes, local paths, and captured artifacts
- `reference_videos[]` entries with technical metadata, artifact paths, timecoded beats, keyframe paths, transcript path, OCR path, and evidence refs
- `findings` with narrative patterns, visual patterns, audio patterns, visual evidence opportunities, source claims, rights/policy risks, evidence gaps, and confidence notes
- `downstream_guidance` for Creative Producer, Visual Producer, InVideo AI Generator, Remotion Clip Builder, Remotion Video Producer, and Video Critic

## Status Policy

- `complete`: deterministic evidence exists, important beats are timecoded, and reusable patterns are interpreted with confidence notes.
- `partial`: metadata/frames or transcript/OCR/model evidence is missing, but enough evidence exists to guide production with limitations.
- `blocked`: no usable local media, no transcript/screenshots, inaccessible source, unclear rights, or required approval is missing.

## Evidence And Manifest Policy

When a local video, transcript, thumbnail, keyframe, OCR output, scene JSON, probe JSON, embedding index, or model-observation artifact is used, record or reference the corresponding asset id from `codex/contracts/media-asset-manifest.schema.json`. If manifest update is deferred, state why and list the artifacts that still need entries.

## Stop Conditions

Stop with `blocked` when the source cannot be accessed, required rights are unclear for analysis, local media handling is not approved, a paid/cloud model call is required but not approved, or the evidence is too weak to support production guidance.

## Definition Of Done

- Every analyzed reference video has a source id and evidence provenance.
- Metadata, frame evidence, transcript/OCR/model limitations, and confidence notes are explicit.
- Reusable patterns are separated from one-off content and do-not-copy risks.
- Downstream agents can use the artifact without re-reading raw reference files.
