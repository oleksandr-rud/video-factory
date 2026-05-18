---
name: style-system-extraction
description: Extract reusable channel style rules from references and brand materials, including color, typography, captions, layout, motion, audio, thumbnails, intros, outros, and reusable assets. Use when channel-level rules should guide many videos without dictating every clip.
---

# Style System Extraction

Workflow:

1. Identify stable visual tokens: colors, contrast, typography, caption style, logo behavior, safe areas, and thumbnail style.
2. Identify stable motion tokens: intro energy, transitions, zooms, kinetic type, UI motion, data animation, and B-roll motion.
3. Identify stable audio tokens: narrator persona, voice traits, pace, accent/language policy, music mood, SFX density, pauses, ambience, and loudness concerns.
4. Identify reusable assets and Remotion template candidates: intro/outro, lower thirds, source-card layout, quote style, map/chart style, CTA, disclaimers, caption style, overlays, and transitions; record media asset ids when assets are local or captured.
5. When an existing shared Remotion template appears to fit, record its stable template id and contract path from `remotion/src/templateRegistry.tsx`, `remotion/templates/`, or project-specific contracts under `channels/<channel-slug>/projects/<project-slug>/remotion/templates/`.
6. Mark each rule as:
   - `mandatory`: needed for channel recognition or compliance.
   - `preferred`: should usually apply.
   - `flexible`: can vary by episode.
   - `avoid`: creates redundancy, rights risk, or brand mismatch.
7. Keep exact clip choices out of the style system unless they are reusable assets or reusable template instances.

Template rules:

- Use shared Remotion template ids only for generic reusable primitives that fit the channel style without forcing the channel into the shared template's defaults.
- Prefer project/channel template contracts over shared contracts when the visual identity, safe areas, aspect ratio, or dependency needs differ.
- Do not implement templates in Channel Intelligence. Return reusable template candidates and style constraints; the Director routes implementation to Remotion Clip Builder.

Return style tokens and rules for `codex/contracts/channel-format.schema.json` and durable channel defaults for `codex/contracts/channel-profile.schema.json` when a channel folder is in scope.
