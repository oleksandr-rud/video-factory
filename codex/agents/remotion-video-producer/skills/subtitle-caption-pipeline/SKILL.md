---
name: subtitle-caption-pipeline
description: Build the subtitle and caption pipeline for a Remotion video. Use when a run needs .srt import, audio transcription, Caption JSON normalization, burned-in animated captions, separate .srt export, or caption timing/safe-area QA.
---

# Subtitle Caption Pipeline

Load the built-in `remotion:remotion-best-practices` skill and use its captions/subtitle rule files when implementing.

Workflow:

1. Choose source:
   - Existing `.srt`: parse with `@remotion/captions`.
   - Voiceover script with known timings: generate `Caption[]` directly.
   - ElevenLabs timestamp alignment: convert character timings to Remotion `Caption[]` with `codex/agents/creative-producer/scripts/elevenlabs_alignment_to_captions.py`.
   - Audio file: transcribe with approved local or cloud route.
2. Normalize to Remotion `Caption[]` JSON with millisecond timing.
3. Store caption data under a stable asset path, usually `public/captions/<scenario-id>.json` and optionally `public/captions/<scenario-id>.srt`.
4. Render burned-in captions with `Sequence` or caption pages. Use word highlighting only when it improves comprehension.
5. Keep captions inside platform safe areas and away from lower thirds, logos, and CTA text.
6. Export separate `.srt` through a render artifact when required.
7. QA captions against audio: drift, missing words, punctuation, line breaks, contrast, text overflow, and reading speed.

Pass caption paths and timing ranges into `timeline-sync-plan` so visual scene boundaries and subtitle ranges stay aligned with the scenario.

Rules:

- Prefer accessible high-contrast captions over decorative captions.
- Cap caption chunks to short phrases on vertical shorts.
- Use text fitting logic for long words or translated text.
- Do not rely on remote caption files during render.
- Mark cloud transcription as paid/external unless the Director approved it.

## Media Manifest Policy

If this skill consumes, creates, validates, transcribes, aligns, exports, mirrors, or defers audio files, Caption JSON, SRT/VTT files, burned-in caption previews, transcript sidecars, or subtitle QA evidence, update the media asset manifest or return `manifest_actions[]`.

Each manifest action must include `action`, `asset_id`, `canonical_path`, `remotion_public_path` and `static_file_path` when relevant, `rights_state`, `technical_metadata_state`, and `reason`.

Use `deferred` for cloud transcription awaiting approval, captions that depend on missing audio, exports not yet written, or files not yet mirrored for Remotion. Timeline sync must consume caption/audio paths from the manifest or an explicit deferred action.
