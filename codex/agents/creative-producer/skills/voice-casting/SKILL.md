---
name: voice-casting
description: Select voice direction for a video scenario, including tone, gender or neutrality, language, accent, pace, energy, and pronunciation constraints. Use before TTS generation or human voiceover briefing.
---

# Voice Casting

1. Read scenario tone, audience, and platform.
2. Select voice attributes that support the video goal.
3. Specify pacing in words per minute and per-scene energy.
4. Add pronunciation notes for names, acronyms, and technical terms.
5. Flag rights or consent issues for cloned or branded voices.

Return a voice direction brief and any provider constraints. If ElevenLabs is the chosen provider, pass the brief to `elevenlabs-voice-selection` so it can rank actual available voices instead of inventing a voice profile.
