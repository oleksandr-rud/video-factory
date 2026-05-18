---
name: reference-video-breakdown
description: Analyze reference videos in depth with timecoded evidence, media manifest actions, reusable production patterns, and do-not-copy risks. Use when reference videos, video URLs, local media, transcripts, screenshots, thumbnails, or direct-video observations are supplied before channel format, scenario, visual, Remotion, or critique work.
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
9. Return manifest actions for every local reference file, transcript, thumbnail, keyframe, OCR output, scene JSON, probe JSON, model-observation artifact, or sampled frame that was created, consumed, validated, or deferred.
10. Build `reference_beats[]` as the flattened evidence graph for downstream agents, with transcript, shot, audio, caption/graphics, reusable-pattern, and do-not-copy evidence per beat.
11. Return `invalidation_impact[]` when missing or changed reference evidence could invalidate channel format rules, scenario assumptions, visual route choices, Remotion styling, render criteria, or critique gates.

## Required Output

Return or update `codex/contracts/reference-analysis.schema.json` with:

- `processing_runs[]` for local extraction tools, model observations, status, outputs, and limitations
- `sources[]` entries with source ids, rights notes, local paths, and captured artifacts
- `source_ledger[]` entries with `kind`, rights state, reusable scope, missing assets, evidence refs, and confidence
- `reference_videos[]` entries with technical metadata, artifact paths, timecoded beats, keyframe paths, transcript path, OCR path, and evidence refs
- `claim_ledger[]` as an empty array when the video breakdown does not extract factual script claims
- `reference_beats[]` as the flattened downstream evidence graph
- `findings` with narrative patterns, visual patterns, audio patterns, visual evidence opportunities, source claims, rights/policy risks, evidence gaps, and confidence notes
- `downstream_guidance` for Creative Producer, Visual Producer, InVideo AI Generator, Remotion Clip Builder, Remotion Video Producer, and Video Critic
- `invalidation_impact[]` entries or an empty array when no downstream invalidation risk is found

Use this shape for flattened beat and invalidation details:

```json
{
  "reference_beats": [
    {
      "beat_id": "string",
      "video_id": "string",
      "source_id": "string",
      "start_seconds": 0,
      "end_seconds": 0,
      "purpose": "hook | setup | proof | tension | payoff | cta | transition | other",
      "transcript_evidence": {
        "text": "string",
        "path": "string",
        "confidence": "high | medium | low | unknown"
      },
      "shot_evidence": {
        "shot_size": "string",
        "camera_motion": "string",
        "keyframe_paths": ["string"],
        "confidence": "high | medium | low | unknown"
      },
      "audio_evidence": {
        "music_sfx_voice_notes": "string",
        "pacing_notes": "string",
        "confidence": "high | medium | low | unknown"
      },
      "caption_graphics_evidence": {
        "caption_style": "string",
        "graphics_notes": "string",
        "ocr_path": "string",
        "confidence": "high | medium | low | unknown"
      },
      "reusable_patterns": ["string"],
      "do_not_copy_risks": ["string"],
      "evidence_refs": [],
      "confidence": "high | medium | low | unknown"
    }
  ],
  "invalidation_impact": [
    {
      "impact_id": "string",
      "change_or_gap": "reference_added | reference_removed | transcript_changed | beat_changed | rights_changed | model_observation_changed",
      "affected_artifacts": ["channel_format | scenario | visual_pack | ai_generation | remotion_template | remotion_clip | timeline_sync | render | critique"],
      "reason": "string",
      "owner_agent": "channel-intelligence | creative-producer | visual-producer | invideo-ai-generator | remotion-clip-builder | remotion-video-producer | video-critic",
      "severity": "blocker | major | minor | note",
      "recommended_action": "string"
    }
  ]
}
```

Every `reference_videos[]` entry must include or explicitly defer:

```json
{
  "video_id": "string",
  "source_id": "string",
  "media_asset_id": "string",
  "duration_seconds": 0,
  "technical": {
    "duration_seconds": 0,
    "width": 0,
    "height": 0,
    "fps": 0,
    "video_codec": "string",
    "audio_codec": "string",
    "has_audio": true,
    "probe_path": "string"
  },
  "artifacts": {
    "probe_json_path": "string",
    "scenes_json_path": "string",
    "frame_samples_json_path": "string",
    "keyframe_dir": "string",
    "ocr_json_path": "string",
    "transcript_path": "string",
    "model_observation_path": "string"
  },
  "beats": [
    {
      "beat_id": "string",
      "start_seconds": 0,
      "end_seconds": 0,
      "purpose": "hook | setup | proof | tension | payoff | cta | transition | other",
      "shot_size": "string",
      "camera_motion": "string",
      "visual_notes": "string",
      "audio_notes": "string",
      "caption_or_graphics_notes": "string",
      "pattern_tags": ["string"],
      "keyframe_paths": ["string"],
      "evidence_refs": []
    }
  ],
  "do_not_copy_risks": ["string"],
  "model_limitations": ["string"],
  "confidence": "high | medium | low | unknown"
}
```

Return this additional top-level action list:

```json
{
  "manifest_actions": [
    {
      "action": "created | updated | consumed | validated | mirrored_to_remotion_public | deferred | not_applicable",
      "asset_id": "string",
      "canonical_path": "string",
      "remotion_public_path": "string",
      "static_file_path": "string",
      "rights_state": "approved | needs_approval | blocked | unknown",
      "technical_metadata_state": "present | missing | partial",
      "reason": "string"
    }
  ]
}
```

## Contract Fields Populated

- `reference-analysis.schema.json`: required fields `analysis_id`, `status`, `sources[]`, `source_ledger[]`, `claim_ledger[]`, `reference_beats[]`, `findings`, `downstream_guidance`, and `invalidation_impact[]`, plus `media_asset_manifest_path`, `processing_runs[]`, `reference_videos[]`, and `evidence_refs`
- `reference-analysis.schema.json` reference video objects: `video_id`, `source_id`, `media_asset_id`, `technical`, `artifacts`, transcript/thumbnail paths, `beats[]`, timecoded evidence refs, limitations, and confidence notes
- Additional reference-analysis fields allowed by the contract: beat-level transcript/shot/audio/caption evidence, `do_not_copy_risks`, `model_limitations`, and confidence values
- `media-asset-manifest.schema.json`: entries or deferred actions for local reference videos, thumbnails, keyframes, frame samples, transcripts, OCR, probes, scene JSON, model observations, and embedding indexes

## Status Policy

- `complete`: deterministic evidence exists, important beats are timecoded, `reference_beats[]` is populated, and reusable patterns are interpreted with confidence notes.
- `partial`: metadata/frames or transcript/OCR/model evidence is missing, but enough evidence exists to guide production with limitations.
- `blocked`: no usable local media, no transcript/screenshots, inaccessible source, unclear rights, or required approval is missing.

## Evidence Required

For every important observation, cite one or more of:

- `source_id`
- media asset id
- timestamp range
- transcript line or caption artifact
- keyframe/frame path
- screenshot or thumbnail path
- probe/scene/OCR JSON path
- model observation artifact path plus model limitations
- confidence note

Separate deterministic evidence from model-inferred evidence. Do not promote a pattern to channel format unless the evidence and confidence justify reuse.

## Media Manifest Policy

When a local video, transcript, thumbnail, keyframe, OCR output, scene JSON, probe JSON, embedding index, or model-observation artifact is created, consumed, validated, mirrored, or deferred, return `manifest_actions[]`:

```json
{
  "action": "created | updated | consumed | validated | mirrored_to_remotion_public | deferred | not_applicable",
  "asset_id": "string",
  "canonical_path": "string",
  "remotion_public_path": "string",
  "static_file_path": "string",
  "rights_state": "approved | needs_approval | blocked | unknown",
  "technical_metadata_state": "present | missing | partial",
  "reason": "string"
}
```

When a local video, transcript, thumbnail, keyframe, OCR output, scene JSON, probe JSON, embedding index, or model-observation artifact is used, record or reference the corresponding asset id from `codex/contracts/media-asset-manifest.schema.json`. If manifest update is deferred, state why and list the artifacts that still need entries.

## Approval And Stop Conditions

Stop with `blocked` when the source cannot be accessed, required rights are unclear for analysis, local media handling is not approved, a paid/cloud model call is required but not approved, or the evidence is too weak to support production guidance.

Return `needs_approval` before paid/cloud transcription, direct-video model calls, external provider uploads, sensitive media handling, or licensed asset use.

## Definition Of Done

- Every analyzed reference video has a source id and evidence provenance.
- Metadata, frame evidence, transcript/OCR/model limitations, and confidence notes are explicit.
- `reference_beats[]`, `downstream_guidance`, and `invalidation_impact[]` are populated or explicitly deferred.
- Reusable patterns are separated from one-off content and do-not-copy risks.
- Every local media or sidecar artifact is covered by `manifest_actions[]`.
- Downstream agents can use the artifact without re-reading raw reference files.

## Handoff Summary Shape

Return:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "artifact_paths": ["string"],
  "changed_files": ["string"],
  "populated_contracts": ["codex/contracts/reference-analysis.schema.json", "codex/contracts/media-asset-manifest.schema.json"],
  "manifest_actions": [
    {
      "action": "created | updated | consumed | validated | mirrored_to_remotion_public | deferred | not_applicable",
      "asset_id": "string",
      "reason": "string"
    }
  ],
  "validation_performed": ["metadata extraction", "timecoded beat review", "transcript/OCR review", "pattern extraction", "do-not-copy review", "manifest action review"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
