---
name: style-system-extraction
description: Extract reusable channel style rules from references and brand materials, including color, typography, captions, layout, motion, audio, thumbnails, intros, outros, and reusable assets. Use when channel-level rules should guide many videos without dictating every clip.
---

# Style System Extraction

Workflow:

1. Identify stable visual tokens: colors, contrast, typography, caption style, logo behavior, safe areas, and thumbnail style.
2. Identify stable motion tokens: intro energy, transitions, zooms, kinetic type, UI motion, data animation, and B-roll motion.
3. Identify stable audio tokens: voice direction, music mood, SFX density, pauses, ambience, and loudness concerns.
4. Identify reusable assets and templates: intro/outro, lower thirds, source-card layout, quote style, map/chart style, CTA, disclaimers.
5. Mark each rule as:
   - `mandatory`: needed for channel recognition or compliance.
   - `preferred`: should usually apply.
   - `flexible`: can vary by episode.
   - `avoid`: creates redundancy, rights risk, or brand mismatch.
6. Keep exact clip choices out of the style system unless they are reusable assets.

Return style tokens and rules for `codex/contracts/channel-format.schema.json`.
