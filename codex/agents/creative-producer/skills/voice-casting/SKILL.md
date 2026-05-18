---
name: voice-casting
description: Select voice direction for a video scenario, including tone, gender or neutrality, language, accent, pace, energy, and pronunciation constraints. Use before TTS generation or human voiceover briefing.
---

# Voice Casting

Create a structured voice direction and risk artifact. Do not invent a provider voice here; pass the casting direction to provider-specific selection such as `elevenlabs-voice-selection`.

## Inputs

- Director/user instructions, producer criteria, scenario, scene voice notes, audience, platform, and target duration
- Channel profile audio identity, channel format `audio_system`, reference voice evidence, and prior voiceover package when updating
- Provider constraints when known: current model support, target language support, target accent labels, voice quality evidence, voice categories, inventory availability, and generation policy
- Pronunciation inputs: names, acronyms, numbers, technical terms, foreign-language words, and brand terms
- Rights/consent policy for cloned, branded, celebrity-like, real-person, or synthetic voices

## Workflow

1. Build the inheritance chain in priority order:
   - explicit user or Director override
   - producer criteria
   - scenario tone and scene voice notes
   - `channel-profile.audio_identity.voice_profile`
   - `channel-format.audio_system`
   - reference analysis voice evidence
   - provider inventory and availability
2. Classify the voice need: reusable narrator, episode-specific narrator, character-like performance, neutral/accessibility-first narration, regional/localized narration, or human voiceover brief.
3. Select voice attributes that support the video goal and channel continuity: narrator persona, authority level, warmth, energy, seriousness, humor, urgency, emotional distance, target language, target accent or neutral accent policy, age range when relevant, gender or neutral preference, pace, pauses, and scene-level energy.
   - If `provider_voice_refs[]` contains `selection_policy: "exact_required"` for the selected provider and no higher-priority user/Director override conflicts, treat that provider voice as the binding channel narrator instead of recasting the episode.
   - If an exact channel voice conflicts with language/accent, rights, or provider availability, return `needs_approval` or `blocked` rather than silently choosing a different voice.
4. Build a weighted suitability rubric before provider selection:
   - audience fit
   - domain credibility
   - scenario tone fit
   - channel continuity
   - platform pacing
   - pronunciation safety
   - accessibility/comprehension
   - rights/consent safety
   - provider availability
   - quality fit when ElevenLabs is in scope: prefer `eleven_v3` and high-quality voice evidence; use lower-latency models only when explicit constraints justify the tradeoff
   - target language/accent fit
5. Identify rejected styles and why they are wrong for this video.
6. Identify pronunciation risks and required pronunciation notes for provider payloads or human narration.
7. Stop for approval if the request implies cloning, celebrity-like imitation, branded/person-specific matching, real-person voice use, or paid generation.

## Required Output

Return this object and use it to populate `voiceover-package.schema.json`:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "voiceover_id": "string",
  "scenario_id": "string",
  "provider": "elevenlabs | openai_audio | human | other",
  "voice_direction": {
    "voice_need_type": "reusable_narrator | episode_specific_narrator | character_performance | neutral_accessibility | localized | human_brief",
    "inherited_from": [
      {
        "source": "user | director | producer_criteria | scenario | channel_profile | channel_format | reference_analysis | provider_inventory",
        "path": "string",
        "notes": "string"
      }
    ],
    "narrator_persona": "string",
    "authority_level": "low | medium | high",
    "emotional_distance": "close | balanced | detached",
    "voice_traits": ["string"],
    "must_avoid_traits": ["string"],
    "target_language": "string",
    "target_accent": "string",
    "language_code": "string",
    "accent_policy": "string",
    "gender_or_neutrality": "neutral | feminine | masculine | unspecified",
    "pace_wpm_range": "string",
    "pause_density": "low | medium | high",
    "energy_profile": "string",
    "accessibility_notes": ["string"],
    "selection_rubric": [
      {
        "criterion": "audience_fit | domain_credibility | tone_fit | channel_continuity | platform_pacing | pronunciation_safety | accessibility | rights_safety | provider_availability",
        "weight": 0,
        "notes": "string"
      }
    ],
    "selection_reason": "string",
    "provider_voice_refs": [
      {
        "provider": "elevenlabs",
        "voice_id": "string",
        "voice_name": "string",
        "selection_policy": "exact_required | preferred | fallback | blocked",
        "target_language": "string",
        "target_accent": "string",
        "rights_state": "approved | needs_approval | blocked | unknown"
      }
    ]
  },
  "rejected_styles": [
    {
      "style": "string",
      "reason": "string"
    }
  ],
  "pronunciation_notes": [
    {
      "term": "string",
      "preferred_pronunciation": "string",
      "risk": "name | acronym | number | technical | foreign_language | brand | other"
    }
  ],
  "rights_and_consent": {
    "risk_level": "none | low | medium | high | blocked",
    "requires_approval": false,
    "blocked_styles": ["voice_clone | celebrity_like | branded_person | real_person | unauthorized_accent_or_identity"],
    "notes": ["string"]
  },
  "next_recommended_step": "string"
}
```

## Contract Fields Populated

- `voiceover-package.schema.json`: `provider`, `status`, `voice_direction`, `generation_policy`, `pronunciation_notes`, `continuity_notes`, and voice-selection constraints
- `channel-format.schema.json`: consumes `audio_system`
- `channel-profile.schema.json`: consumes durable audio identity only
- `agent-handoff.schema.json`: only as a Director-facing recommendation to run provider-specific selection or TTS planning

## Status Policy

- Return `complete` when the voice direction is ready for provider selection or a human voiceover brief.
- Return `needs_approval` when matching depends on cloning, celebrity-like voice, branded/person-specific voice, real-person consent, paid generation, or sensitive identity traits.
- Return `blocked` when the requested voice direction is unsafe, unauthorized, discriminatory, impossible under provider limits, or conflicts with explicit channel/producer criteria.
- Return `needs_revision` when scenario tone, audience, language, accent policy, or channel audio identity is missing or contradictory.

## Evidence Required

Every inherited voice rule must cite the source artifact or explicit instruction that created it. Every selected or rejected style must have a rationale tied to audience, channel continuity, scenario tone, accessibility, rights, or provider constraints.

## Media Manifest Policy

This skill does not create audio. Return `manifest_actions[]` as `not_applicable` unless it validates existing voice reference audio or defers a future voice reference asset. Existing audio references must have manifest ids and rights state before they influence provider matching.

## Approval And Stop Conditions

Stop and return `needs_approval` before voice cloning, celebrity-like imitation, branded/person-specific voice matching, paid provider generation, or use of a real person's voice without explicit rights confirmation. Voice direction may be planned before approval; provider generation and rights-sensitive matching may not.

## Definition Of Done

- Voice direction is structured and provider-agnostic.
- Inheritance, rejected styles, suitability rubric, pronunciation notes, accessibility concerns, and rights/consent status are explicit.
- Provider-specific selection can rank real inventory without inventing a voice profile.
- Approval-sensitive voice use is stopped before provider work.

## Handoff Summary Shape

Return:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "artifact_paths": ["string"],
  "changed_files": ["string"],
  "populated_contracts": ["codex/contracts/voiceover-package.schema.json"],
  "manifest_actions": [
    {
      "action": "validated | deferred | not_applicable",
      "asset_id": "string",
      "reason": "string"
    }
  ],
  "validation_performed": ["inheritance chain", "suitability rubric", "pronunciation risk", "rights/consent check", "provider handoff readiness"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
