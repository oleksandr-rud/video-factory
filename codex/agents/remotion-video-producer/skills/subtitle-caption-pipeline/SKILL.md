---
name: subtitle-caption-pipeline
description: Build the subtitle and caption pipeline for a Remotion video. Use when a run needs .srt import, audio transcription, Caption JSON normalization, burned-in animated captions, separate .srt export, or caption timing/safe-area QA.
---

# Subtitle Caption Pipeline

Build captions as a pipeline contract, not as loose transcript text. Load the built-in `remotion:remotion-best-practices` skill and use its captions/subtitle rule files when implementing.

## Inputs

- Scenario, scene ids, narration text, on-screen text, platform, aspect ratio, safe areas, and producer criteria
- Voiceover package with audio paths, ElevenLabs timestamp alignment, Caption JSON, SRT path, or manual timings when available
- Timeline sync plan when updating or reviewing caption ranges
- Remotion project contract, public asset policy, render commands, and composition ids
- Media asset manifest for audio, transcript, caption, subtitle, preview, and render assets
- Approved transcription route: existing SRT, TTS timestamps, local transcription, cloud transcription, or manual captions

## Workflow

1. Choose and record the caption source route:
   - `existing_srt`: parse with `@remotion/captions`.
   - `tts_timestamps`: convert ElevenLabs or provider character/word timings to Remotion `Caption[]`.
   - `script_known_timings`: generate `Caption[]` from known scene/voice timings.
   - `local_transcription`: run only approved local tooling.
   - `cloud_transcription`: stop until Director approval because this is external/paid.
   - `manual`: use supplied cue timing and text.
2. Normalize to Remotion `Caption[]` JSON with millisecond timing. Keep raw transcript/source sidecars when available.
3. Segment cues for readability: short phrases, two-line maximum by default, stable punctuation, reasonable reading speed, and no long-word overflow.
4. Store caption data under stable project and Remotion public paths, usually canonical project caption paths plus `remotion/public/captions/<scenario-id>.json` and optional `.srt` or `.vtt`.
5. Decide delivery mode: burned-in captions, sidecar `.srt`, sidecar `.vtt`, both burned-in and sidecar, or no captions with documented reason.
6. Define caption style: contrast, font, stroke/background, word highlight policy, safe-area placement, subtitle/lower-third conflict behavior, and platform UI avoidance.
7. Pass caption paths, cue ranges, and scene-level caption coverage into `timeline-sync-plan` so visual scene boundaries, voiceover, and subtitle ranges stay aligned.
8. QA captions against audio and visuals: drift, missing words, punctuation, line breaks, contrast, text overflow, reading speed, overlap with lower thirds/logos/CTA, overlap with important scene content, and shot/audio logic.
9. Export separate `.srt`/`.vtt` through a render artifact when required. Do not rely on remote caption files during render.

## Required Output

Return:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "caption_pipeline": {
    "caption_pipeline_id": "string",
    "scenario_id": "string",
    "source_route": "existing_srt | tts_timestamps | script_known_timings | local_transcription | cloud_transcription | manual",
    "source_paths": ["string"],
    "caption_json_path": "string",
    "srt_path": "string",
    "vtt_path": "string",
    "remotion_public_caption_path": "string",
    "static_file_path": "string",
    "delivery_mode": "burned_in | sidecar_srt | sidecar_vtt | burned_in_and_sidecar | none",
    "caption_style": {
      "style_id": "string",
      "font": "string",
      "max_lines": 2,
      "safe_area": "string",
      "word_highlight": false,
      "contrast_rule": "string",
      "overlap_avoidance": ["lower_thirds", "logos", "CTA", "platform_UI", "important_visuals"]
    },
    "scene_caption_ranges": [
      {
        "scene_id": "string",
        "start_ms": 0,
        "end_ms": 0,
        "caption_count": 0,
        "coverage": "complete | partial | missing"
      }
    ],
    "exports": [
      {
        "kind": "caption_json | srt | vtt | transcript | qa_report | preview",
        "path": "string",
        "media_asset_id": "string"
      }
    ]
  },
  "caption_qa": {
    "status": "pass | fail | partial | not_run",
    "checks": [
      {
        "check": "audio_sync | missing_words | segmentation | line_breaks | reading_speed | safe_area | contrast | overlap | timing_logic | export_integrity",
        "result": "pass | fail | partial | unknown",
        "evidence": "string",
        "scene_id": "string"
      }
    ],
    "blockers": ["string"]
  },
  "next_recommended_step": "string"
}
```

## Contract Fields Populated

- `voiceover-package.schema.json`: consumes and may populate `captions`, scene `caption_json_path`, `srt_path`, `caption_asset_id`, and `sync_notes`
- `timeline-sync-plan.schema.json`: provides caption paths, cue ranges, scene coverage, and sync notes for timeline alignment
- `render-package.schema.json`: provides subtitle/caption output paths, sidecar exports, and burned-in caption notes
- `media-asset-manifest.schema.json`: manifest entries or actions for audio, Caption JSON, SRT/VTT, transcript, preview, QA, and render artifacts
- `remotion-project.schema.json`: consumes public asset policy and render commands

## Status Policy

- Return `complete` when Caption JSON and required subtitle exports exist or are planned, manifest actions are clear, and QA passes or has non-blocking notes.
- Return `needs_approval` when cloud transcription, paid transcription, external media upload, licensed subtitle assets, or user waiver is required.
- Return `blocked` when audio/timing source is missing, caption files cannot be generated, rights prevent transcription/use, or safe-area conflicts cannot be resolved.
- Return `needs_revision` when text, timing, segmentation, style, safe-area, or export policy is incomplete or contradictory.

## Evidence Required

Every caption route must preserve source provenance: SRT path, audio path, alignment path, transcript sidecar, manual timing source, or transcription approval. Every QA failure must include scene id or timestamp evidence when possible.

## Media Manifest Policy

If this skill consumes, creates, validates, transcribes, aligns, exports, mirrors, or defers audio files, Caption JSON, SRT/VTT files, burned-in caption previews, transcript sidecars, or subtitle QA evidence, update the media asset manifest or return `manifest_actions[]`.

Each manifest action must include `action`, `asset_id`, `canonical_path`, `remotion_public_path` and `static_file_path` when relevant, `rights_state`, `technical_metadata_state`, `evidence_refs`, and `reason`.

Use `deferred` for cloud transcription awaiting approval, captions that depend on missing audio, exports not yet written, or files not yet mirrored for Remotion. Timeline sync must consume caption/audio paths from the manifest or an explicit deferred action.

## Approval And Stop Conditions

Stop before cloud transcription, paid transcription, external media upload, provider speech-to-text, or use of unapproved audio. Stop when captions cannot satisfy safe-area, readability, or sync requirements without changing the timeline, visual layout, or voiceover package; route the required owner fix through the Director.

## Definition Of Done

- Caption source route and provenance are explicit.
- Normalized Remotion `Caption[]` JSON path is created or planned with a blocker.
- SRT/VTT export policy is recorded.
- Caption style, safe areas, and burned-in/sidecar decision are explicit.
- Audio sync, reading speed, segmentation, contrast, overlap, and export integrity are QA-checked.
- Timeline sync receives caption ranges and manifest-backed paths.

## Handoff Summary Shape

Return:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "artifact_paths": ["string"],
  "changed_files": ["string"],
  "populated_contracts": ["codex/contracts/voiceover-package.schema.json", "codex/contracts/timeline-sync-plan.schema.json", "codex/contracts/render-package.schema.json"],
  "manifest_actions": [
    {
      "action": "created | updated | consumed | validated | mirrored_to_remotion_public | deferred | not_applicable",
      "asset_id": "string",
      "canonical_path": "string",
      "remotion_public_path": "string",
      "static_file_path": "string",
      "rights_state": "approved | needs_approval | blocked | unknown",
      "technical_metadata_state": "present | missing | partial | not_applicable",
      "reason": "string"
    }
  ],
  "validation_performed": ["source route", "Caption JSON normalization", "SRT/VTT export policy", "audio sync QA", "safe-area QA", "reading speed", "manifest check"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
