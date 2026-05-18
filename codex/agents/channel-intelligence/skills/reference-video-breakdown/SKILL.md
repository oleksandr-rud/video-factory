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
2. For YouTube or other video-platform URLs, download first after Director approval, then analyze the local file. Preserve the original URL, platform id, title/owner, thumbnail, subtitles, and info JSON as source artifacts and manifest actions. Use a bounded `yt-dlp` capture such as:
   ```powershell
   yt-dlp `
     --write-info-json `
     --write-thumbnail `
     --write-subs `
     --write-auto-subs `
     --sub-langs "en.*,uk.*,ru.*" `
     --merge-output-format mp4 `
     --paths "channels/<channel-slug>/projects/<project-slug>/source-media/reference-videos/<source-id>" `
     --output "%(id)s.%(ext)s" `
     "<youtube-url>"
   ```
   If download approval is missing, return `needs_approval` with deferred manifest actions. If `yt-dlp` is missing or the platform blocks capture, return `partial` or `blocked` with the exact missing local evidence.
3. For local files, run `../../scripts/analyze_reference_video.py` to prepare ffprobe metadata, scene/segment JSON, keyframes, optional OCR, and a contract-shaped reference analysis fragment:
   ```powershell
   python codex/agents/channel-intelligence/scripts/analyze_reference_video.py `
     --video <local-reference-video> `
     --source-id <source-id> `
     --work-dir <project-or-channel-reference-work-dir> `
     --output <reference-analysis-json> `
     --content-alignment <match|partial|mismatch|unknown> `
     --allowed-content-use <content_and_visual|visual_format_only|content_only|do_not_use|unknown> `
     --target-content-substitution "<how target content replaces mismatched reference content>"
   ```
4. If OpenRouter direct-video observation is approved for the reference, run the generic helper on the downloaded/local file after deterministic sidecars exist. Save the prompt, request preview, raw response, and a short parsed `model-observation.json` in the same reference-analysis work directory, then pass that path through `--model-observation-path` or merge it into the reference analysis:
   ```powershell
   python codex/scripts/openrouter_video_request.py `
     --prompt "Analyze this reference video scene by scene. Return JSON with overall_summary, scene_decomposition, reusable_patterns, do_not_copy_risks, model_limitations, and evidence timestamps." `
     --video "<downloaded-reference-video.mp4>" `
     --output "<work-dir>/openrouter-reference-observation.json" `
     --response-format json_object `
     --execute `
     --approved
   ```
   Use local/base64 video upload by default for YouTube captures so provider-specific watch-URL support does not control the pipeline. Use `--video-url` only when the provider/model route explicitly supports that URL form and the Director approved external media handling.
5. If the local script returns `partial`, preserve the artifacts it did produce and list missing tools or evidence gaps instead of inventing observations.
6. Segment the video into meaningful beats or shots with timestamps. Use PySceneDetect output when available; otherwise use fallback segments as provisional timing evidence.
7. Interpret deterministic and approved model evidence into production observations: hook, setup, proof, tension, payoff, CTA, recurring sections, shot grammar, caption/graphics usage, motion language, audio rhythm, and packaging conventions.
8. Extract reusable patterns separately from one-off choices. Keep exact clip choices out of channel rules unless they are legitimate reusable assets.
9. Flag content that should not be copied directly, including proprietary footage, likeness, exact phrasing, exact edit rhythm, or overly similar shots.
10. Direct-video model analysis belongs here for upstream reference breakdowns, not in Visual Producer. Use it only after Director approval for API spend and media handling; keep transcript/caption evidence separate from model visual observations.
11. Return manifest actions for every local reference file, transcript, thumbnail, keyframe, OCR output, scene JSON, probe JSON, model-observation artifact, or sampled frame that was created, consumed, validated, or deferred.
12. Build `overall_summary` and `scene_decomposition[]` before downstream handoff. `overall_summary` combines deterministic metadata, transcript/OCR status, model limitations, reusable patterns, do-not-copy risks, and evidence gaps. `scene_decomposition[]` maps each beat/shot to source id, timestamps, evidence refs, keyframes, transcript/caption/visual/audio notes, reusable patterns, and confidence.
13. When reference subject matter conflicts with the target channel/project description, treat the reference as visual-format evidence unless the Director explicitly says it should also supply claims. Still research, decompose, and analyze it scene by scene and as a whole video. Mark `content_alignment: mismatch`, set `allowed_content_use: visual_format_only`, and extract composition, shot grammar, pacing, caption/graphics, motion, transition, source-card, and VFX patterns for the target video's format plan.
14. Build `reference_video_plan` as the bridge from mismatched or matched references to the target composition. It should state which visual structures transfer, which subjects/facts must be replaced with target content, which moments need new source evidence, and how the whole-video reference summary informs the target scene plan.
15. Build `reference_beats[]` as the flattened evidence graph for downstream agents, with transcript, shot, audio, caption/graphics, reusable-pattern, and do-not-copy evidence per beat.
16. Return `invalidation_impact[]` when missing or changed reference evidence could invalidate channel format rules, scenario assumptions, visual route choices, Remotion styling, render criteria, or critique gates.

## Required Output

Return or update `codex/contracts/reference-analysis.schema.json` with:

- `processing_runs[]` for local extraction tools, model observations, status, outputs, and limitations
- `sources[]` entries with source ids, rights notes, local paths, and captured artifacts
- `source_ledger[]` entries with `kind`, rights state, reusable scope, missing assets, evidence refs, and confidence
- `reference_videos[]` entries with technical metadata, artifact paths, timecoded beats, keyframe paths, transcript path, OCR path, and evidence refs
- `overall_summary` with combined deterministic/model evidence, reusable patterns, do-not-copy risks, limitations, and evidence coverage
- `scene_decomposition[]` with one object per analyzed beat/scene and the reference materials needed for scene-by-scene downstream analysis
- `reference_video_plan` with target-content mismatch handling, transferable visual-format patterns, required substitutions, and composition guidance for the target video
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
