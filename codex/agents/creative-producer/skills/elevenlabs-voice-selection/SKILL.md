---
name: elevenlabs-voice-selection
description: Select and prepare ElevenLabs voices for a video using channel style, reference audio, scenario tone, language, pacing, and rights constraints. Use when ElevenLabs is the requested or preferred TTS provider, when a run needs provider-ready voice candidates, or when subtitles should be synced from ElevenLabs timestamp alignment.
---

# ElevenLabs Voice Selection

Use this skill with `voice-casting` and `tts-production-plan`. The output is a voiceover package matching `codex/contracts/voiceover-package.schema.json`.

## Workflow

1. Read the scenario, channel profile, channel format, reference audio notes, platform, target language, inherited voice direction, and pacing requirements.
2. Build a voice brief: target language, target accent or accent policy, audience fit, tone, age range if relevant, gender or neutral preference, energy, speed, pronunciation needs, and must-avoid constraints.
3. Select the ElevenLabs model through `../../scripts/elevenlabs_model_policy.py` rather than hardcoding an old default:
   - `eleven_v3`: default quality-first model for highest fidelity, latest expressive single-narrator narration, content creation, and performance-heavy scripts.
   - `eleven_flash_v2_5`: use only when fast, lower-cost, low-latency, high-volume, or long-chunk constraints are explicit; it is also the preferred replacement for Turbo v2.5.
   - `eleven_multilingual_v2`: use when stable long-form narration or stronger text normalization matters more than latest expressiveness.
4. If the Director approved provider access and `ELEVENLABS_API_KEY` is present, snapshot current account-visible models with `../../scripts/fetch_elevenlabs_models.py` and available voices with `../../scripts/fetch_elevenlabs_voices.py`. Listing models/voices does not generate audio, but it still uses the user's provider account.
5. Rank available voices with `../../scripts/rank_elevenlabs_voices.py --selected-model-id <model_id> --target-language <language> --target-accent <accent>`. Quality is the main score: prioritize professional/studio-quality voices, voices verified for the target language/accent, `high_quality_base_model_ids` support for the selected model, matching fine-tuning state, and non-legacy verified voices before style/cost/speed preferences.
   - If the inherited channel profile or channel format has an ElevenLabs `provider_voice_refs[]` entry with `selection_policy: "exact_required"`, that exact `voice_id` must be selected when it exists in inventory and rights are approved.
   - If an exact channel `voice_id` is missing from inventory, rights are not approved, or it cannot support the target language/accent, return `blocked` or `needs_approval`; do not silently choose the next-ranked voice.
   - Preferred and fallback channel voices may affect ranking, but only `exact_required` is binding.
6. Prepare a generation policy that records the endpoint, model id, model profile, model quality score, target language, target accent, output format, character limit, estimated character credits, text-normalization setting, and explicit approval status.
7. Use `../../scripts/elevenlabs_tts_with_timestamps.py` only after the Director records approval. Run it in dry-run mode first; require `--execute --approved` before it calls the paid TTS endpoint.
8. Convert ElevenLabs character timestamps into Remotion Caption JSON and optional `.srt` with `../../scripts/elevenlabs_alignment_to_captions.py`.
9. Return the voiceover package path, selected voice, candidate list, generation approval state, selected model, model-selection reason, scene audio paths, alignment paths, caption paths, QA, risks, and blockers.

## Provider Rules

- Prefer `POST /v1/text-to-speech/:voice_id/with-timestamps` for generated narration because it returns audio plus character-level timing for caption and visual sync.
- Use `eleven_v3` for quality-first TTS when the scene can stay within its shorter per-request character limit.
- Use `POST /v1/text-to-dialogue/with-timestamps` with `eleven_v3` for true multi-speaker dialogue planning; keep single narrator narration on the TTS-with-timestamps route.
- Use `eleven_flash_v2_5` instead of Turbo models for low-latency or budget-sensitive work, and normalize numbers/dates before generation when using Flash unless the request explicitly sets text normalization; do not pick Flash over `eleven_v3` when quality is the only goal.
- Use `eleven_multilingual_v2` when stable long-form narration or stronger number/text normalization is more important than latest expressiveness.
- Use `GET /v2/voices` for searchable, paginated voice inventory when an API key is available.
- Use `GET /v1/models` when provider access is approved to verify `can_do_text_to_speech` and account-visible model support before paid generation.
- Use request-level voice settings rather than editing stored voice settings.
- Do not select `eleven_turbo_v2_5`, `eleven_turbo_v2`, `eleven_multilingual_v1`, or `eleven_monolingual_v1` unless the Director supplies a specific compatibility reason.
- Do not clone, imitate, or use a branded real-person voice without explicit rights confirmation.
- Do not generate paid audio, create paid voice design samples, or use cloud forced alignment without approval.
- Preserve scene ids in audio filenames, alignment files, captions, and downstream timeline sync.

## Quality Checks

- Voice matches the channel format and scenario tone without making every video sound identical.
- Voice follows explicit overrides first, then channel profile audio identity, then channel format defaults.
- Target language and target accent are explicit in the voiceover package, or a missing/neutral accent policy is documented.
- Voice ranking evidence shows quality-first ordering with `score_breakdown.quality` as the dominant score component.
- Pace supports the target duration and caption readability.
- Pronunciation notes cover names, acronyms, numbers, and technical terms.
- Generated audio has no clipping, long leading/trailing silence, major mispronunciation, or scene-order mismatch.
- Caption timings come from provider timestamps, forced alignment, or approved transcription, not guessed timing when audio exists.

## Media Manifest Policy

If this skill consumes voice previews or creates, validates, downloads, aligns, transcribes, or defers generated audio, timestamp alignment files, caption JSON, SRT files, or provider evidence sidecars, update the media asset manifest or return `manifest_actions[]`.

Each manifest action must include `action`, `asset_id`, `canonical_path`, `rights_state`, `technical_metadata_state`, `evidence_refs`, and `reason`; include `remotion_public_path` and `static_file_path` when audio or captions are mirrored for Remotion.

Use `deferred` for dry-run payloads, pending voice-generation approvals, provider previews that are not downloaded, or audio/caption outputs that will be created only after approval. Do not let the voiceover package be the only record of generated audio provenance.
