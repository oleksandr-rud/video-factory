---
name: tts-production-plan
description: Prepare provider-ready text-to-speech packages with approval gates, dry-run payloads, scene-stable filenames, expected timing, timestamp/caption alignment, QA checks, and stop conditions. Use with ElevenLabs, OpenAI audio, human narration, or another approved provider after the scenario is stable.
---

# TTS Production Plan

Treat TTS as an approval-gated production path. Planning and dry-run payloads are safe; paid generation, voice design, cloud alignment, transcription, or provider downloads require Director approval.

## Inputs

- Scenario scenes with stable `scene_id`, script text, timing, platform, language, and duration target
- Voice direction, channel profile/provider preferences, pronunciation notes, and producer criteria
- Approved provider list, budget policy, and any existing voiceover package
- Target output directory and naming convention
- Media asset manifest path when generated audio, captions, or alignment files should be tracked as project assets

## Workflow

1. Confirm the scenario is stable enough for audio. If scene ids or scripts are still volatile, return `needs_revision`.
2. Split narration by scene and preserve exact `scene_id` in filenames and request payloads.
3. Choose provider only from user-approved options and inherited channel provider preferences.
4. Build provider request fields: text, voice, model id, model profile, model quality score, target language, target accent, API language code when known, format, scene id, output filename, text-normalization setting, seed when used, and generation settings.
5. Estimate duration per scene and compare against scene timing. Mark drift that could break timeline sync.
6. Prepare dry-run payloads before any paid generation.
7. Define QA checks before execution: clipping, pacing, pronunciation, loudness, silence trimming, channel voice continuity, and timestamp/caption alignment.
8. For generated audio, record request ids, audio paths, audio asset ids, alignment paths, caption asset ids, caption JSON, SRT, and QA findings.

For ElevenLabs, use `elevenlabs-voice-selection` and write a package matching `codex/contracts/voiceover-package.schema.json`. Pick models through `../../scripts/elevenlabs_model_policy.py`: quality is the main criterion, so default content narration to `eleven_v3`, use `eleven_flash_v2_5` only for explicit fast/budget-sensitive or long-chunk constraints, and use `eleven_multilingual_v2` for stable long-form narration or stronger text normalization. Use `../../scripts/fetch_elevenlabs_models.py` after approved provider access when the run needs account-visible model verification. Use `../../scripts/elevenlabs_tts_with_timestamps.py` in dry-run mode before approval, passing target language/accent, then with `--execute --approved` only after the Director records the approval. Convert timestamp alignment to Remotion Caption JSON with `../../scripts/elevenlabs_alignment_to_captions.py`.

When the channel profile or channel format provides an exact provider voice, copy it into `voice_selection` with `selection_policy: "exact_required"` and `selection_source: "channel_profile"` or `"channel_format"`. Do not regenerate voice selection from generic ranking unless the Director explicitly overrides the channel voice or the exact voice is unavailable/blocked.

Do not call paid generation unless the Director provides explicit approval.

## Required Output

Populate or update `codex/contracts/voiceover-package.schema.json`:

- `voiceover_id`, `scenario_id`, project/channel/reference/media-manifest fields when supplied
- `provider`
- `status`
- `voice_selection`
- `voice_direction`
- `generation_policy`
- `pronunciation_notes`
- `continuity_notes`
- `scenes[]`
- `captions`
- `scripts`
- `qa`

Return this handoff summary:

```json
{
  "status": "planned | voice_selected | ready_for_approval | generated | blocked",
  "voiceover_id": "string",
  "scenario_id": "string",
  "provider": "elevenlabs | openai_audio | human | other",
  "approval_required": true,
  "approval_id": "string",
  "dry_run_payload_path": "string",
  "model_id": "eleven_v3 | eleven_flash_v2_5 | eleven_multilingual_v2 | other",
  "model_profile": "highest_quality | latest_expressive | fast_balanced | stable_content | other",
  "model_selection_reason": "string",
  "target_language": "string",
  "target_accent": "string",
  "scene_requests": [
    {
      "scene_id": "string",
      "text": "string",
      "expected_duration_seconds": 0,
      "output_audio_path": "string",
      "output_alignment_path": "string",
      "output_caption_json_path": "string",
      "output_srt_path": "string",
      "timing_risk": "none | minor | major",
      "retake_notes": "string"
    }
  ],
  "qa_plan": ["string"],
  "blockers": ["string"],
  "next_recommended_step": "string"
}
```

## Status Policy

- Use `planned` before voice/provider selection is complete.
- Use `voice_selected` after provider and voice are selected but before payload approval.
- Use `ready_for_approval` when request payloads are prepared and generation would spend credits or use a paid endpoint.
- Use `generated` only after approved generation completes and output paths are recorded.
- Use `blocked` when provider access, rights, voice consent, missing text, or unstable scene ids prevent safe progress.

## Definition Of Done

- Every voiced scene has text, expected duration, output filenames, and request payload data.
- Paid/provider execution is impossible without explicit approval.
- Scene ids are preserved in audio, alignment, caption, and SRT filenames.
- Timestamp alignment and caption export are planned when supported by the provider.
- ElevenLabs requests use current quality-first model policy, target language/accent are recorded, and legacy Turbo/v1 models are replaced or explicitly justified.
- Exact channel voices are preserved as binding `voice_selection` values unless a higher-priority override or blocker is recorded.
- QA criteria exist before generation and are filled after generation.

## Media Manifest Policy

If this skill creates, consumes, validates, aligns, transcribes, exports, or defers narration audio, provider payload sidecars, timestamp alignment files, caption JSON, SRT files, or human narration files, update the media asset manifest or return `manifest_actions[]`.

Each manifest action must include `action`, `asset_id`, `canonical_path`, `rights_state`, `technical_metadata_state`, `evidence_refs`, and `reason`; include `remotion_public_path` and `static_file_path` when audio or captions are mirrored for Remotion.

Use `deferred` when planned TTS, forced alignment, transcription, or caption files require approval or have not been generated yet. Timeline sync must receive manifest-backed audio/caption paths or explicit deferred actions.
