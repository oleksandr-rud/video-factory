---
name: elevenlabs-voice-selection
description: Select and prepare ElevenLabs voices for a video using channel style, reference audio, scenario tone, language, pacing, and rights constraints. Use when ElevenLabs is the requested or preferred TTS provider, when a run needs provider-ready voice candidates, or when subtitles should be synced from ElevenLabs timestamp alignment.
---

# ElevenLabs Voice Selection

Use this skill with `voice-casting` and `tts-production-plan`. The output is a voiceover package matching `codex/contracts/voiceover-package.schema.json`.

## Workflow

1. Read the scenario, channel format, reference audio notes, platform, target language, and pacing requirements.
2. Build a voice brief: audience fit, tone, accent, age range if relevant, gender or neutral preference, energy, speed, pronunciation needs, and must-avoid constraints.
3. If the Director approved provider access and `ELEVENLABS_API_KEY` is present, snapshot available voices with `../../scripts/fetch_elevenlabs_voices.py`. Voice listing does not generate audio, but it still uses the user's provider account.
4. Rank available voices with `../../scripts/rank_elevenlabs_voices.py`. Keep the top candidates and a short reason for the selected voice.
5. Prepare a generation policy that records the endpoint, model, output format, estimated character credits, and explicit approval status.
6. Use `../../scripts/elevenlabs_tts_with_timestamps.py` only after the Director records approval. Run it in dry-run mode first; require `--execute --approved` before it calls the paid TTS endpoint.
7. Convert ElevenLabs character timestamps into Remotion Caption JSON and optional `.srt` with `../../scripts/elevenlabs_alignment_to_captions.py`.
8. Return the voiceover package path, selected voice, candidate list, generation approval state, scene audio paths, alignment paths, caption paths, QA, risks, and blockers.

## Provider Rules

- Prefer `POST /v1/text-to-speech/:voice_id/with-timestamps` for generated narration because it returns audio plus character-level timing for caption and visual sync.
- Use `GET /v2/voices` for searchable, paginated voice inventory when an API key is available.
- Use request-level voice settings rather than editing stored voice settings.
- Do not clone, imitate, or use a branded real-person voice without explicit rights confirmation.
- Do not generate paid audio, create paid voice design samples, or use cloud forced alignment without approval.
- Preserve scene ids in audio filenames, alignment files, captions, and downstream timeline sync.

## Quality Checks

- Voice matches the channel format and scenario tone without making every video sound identical.
- Pace supports the target duration and caption readability.
- Pronunciation notes cover names, acronyms, numbers, and technical terms.
- Generated audio has no clipping, long leading/trailing silence, major mispronunciation, or scene-order mismatch.
- Caption timings come from provider timestamps, forced alignment, or approved transcription, not guessed timing when audio exists.
