---
name: voice-casting
description: Select voice direction for a video scenario, including tone, gender or neutrality, language, accent, pace, energy, and pronunciation constraints. Use before TTS generation or human voiceover briefing.
---

# Voice Casting

1. Read explicit user/Director instructions, producer criteria, scenario tone, audience, platform, channel profile, channel format, and reference voice evidence.
2. Build the inheritance chain:
   - explicit user or Director override
   - producer criteria
   - scenario tone and scene voice notes
   - `channel-profile.audio_identity.voice_profile`
   - `channel-format.audio_system`
   - reference analysis voice evidence
   - provider inventory and availability
3. Select voice attributes that support the video goal and channel continuity:
   - narrator persona and authority level
   - warmth, energy, seriousness, humor, urgency, and emotional distance
   - language, accent policy, age range if relevant, and gender or neutral preference
   - pace in words per minute, pause density, and per-scene energy
   - pronunciation risk for names, acronyms, numbers, and technical terms
4. Score suitability before provider selection:
   - audience fit
   - domain credibility
   - scenario tone fit
   - channel continuity
   - platform pacing
   - pronunciation safety
   - rights/consent safety
   - provider availability
5. Flag rights or consent issues for cloned, branded, celebrity-like, or real-person voices.

Return a voice direction brief, inherited source notes, suitability rubric, provider constraints, and pronunciation requirements. If ElevenLabs is the chosen provider, pass the brief to `elevenlabs-voice-selection` so it can rank actual available voices instead of inventing a voice profile.

## Approval And Stop Conditions

Stop and return `needs_approval` before voice cloning, celebrity-like imitation, branded/person-specific voice matching, paid provider generation, or use of a real person's voice without explicit rights confirmation. Voice direction may be planned before approval; provider generation and rights-sensitive matching may not.
