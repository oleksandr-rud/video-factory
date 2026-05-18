---
name: tts-production-plan
description: Prepare provider-ready text-to-speech requests, audio filenames, timing expectations, and QA checks. Use with OpenAI audio, ElevenLabs, or another approved TTS provider after the scenario is stable.
---

# TTS Production Plan

1. Split narration by scene.
2. Choose provider only from user-approved options and inherited channel provider preferences.
3. Build request fields: text, voice, model, format, scene id, and output filename.
4. Include expected duration and retake notes.
5. Add audio QA checks for clipping, pacing, pronunciation, loudness, silence trimming, and channel voice continuity.

For ElevenLabs, use `elevenlabs-voice-selection` and write a package matching `codex/contracts/voiceover-package.schema.json`. Use `../../scripts/elevenlabs_tts_with_timestamps.py` in dry-run mode before approval, then with `--execute --approved` only after the Director records the approval. Convert timestamp alignment to Remotion Caption JSON with `../../scripts/elevenlabs_alignment_to_captions.py`.

Do not call paid generation unless the Director provides explicit approval.
