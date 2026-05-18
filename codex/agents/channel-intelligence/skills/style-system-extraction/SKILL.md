---
name: style-system-extraction
description: Extract reusable channel style rules from references and brand materials, including color, typography, captions, layout, motion, audio, thumbnails, intros, outros, and reusable assets. Use when channel-level rules should guide many videos without dictating every clip.
---

# Style System Extraction

Workflow:

1. Read the reference analysis package, including `processing_runs[]`, deterministic artifact paths, `reference_videos[]`, `web_pages[]`, `claim_ledger[]`, confidence notes, and evidence gaps.
2. Identify stable visual tokens from evidence: colors, contrast, typography, caption style, logo behavior, safe areas, and thumbnail style.
3. Identify stable motion and VFX tokens: intro energy, transitions, zooms, kinetic type, UI motion, data animation, B-roll motion, allowed/preferred/avoided effects, alpha/export expectations, render-heavy techniques, and fallback expectations.
4. Identify stable audio tokens: narrator persona, voice traits, pace, accent/language policy, music mood, SFX density, pauses, ambience, and loudness concerns.
5. Identify reusable assets and Remotion template candidates: intro/outro, lower thirds, source-card layout, quote style, map/chart style, CTA, disclaimers, caption style, overlays, transitions, and recurring VFX motifs; record media asset ids when assets are local or captured.
6. Treat parsed page images, screenshots, quotes, and article layouts as evidence for source-card or redrawn graphic style unless rights approval allows direct reuse.
7. When an existing shared Remotion template appears to fit, record its stable template id and contract path from `remotion/src/templateRegistry.tsx`, `remotion/templates/`, or project-specific contracts under `channels/<channel-slug>/projects/<project-slug>/remotion/templates/`.
8. Mark each rule as deterministic evidence-backed, model-inferred, or human/instruction-inferred when confidence differs.
9. Mark each rule as:
   - `mandatory`: needed for channel recognition or compliance.
   - `preferred`: should usually apply.
   - `flexible`: can vary by episode.
   - `avoid`: creates redundancy, rights risk, or brand mismatch.
10. Keep exact clip choices and page image choices out of the style system unless they are reusable assets or reusable template instances with manifest-backed rights.

Template rules:

- Use shared Remotion template ids only for generic reusable primitives that fit the channel style without forcing the channel into the shared template's defaults.
- Prefer project/channel template contracts over shared contracts when the visual identity, safe areas, aspect ratio, or dependency needs differ.
- Do not implement templates in Channel Intelligence. Return reusable template candidates and style constraints; the Director routes implementation to Remotion Clip Builder.
- When a channel has VFX expectations that extend shared Remotion hardening rules, return them as channel-format inputs for `visual_system.vfx_rules`: base rule refs, allowed/preferred/avoided effects, quality/performance/determinism rules, hardening triggers, benchmark requirements, and fallback requirements.

Return style tokens and rules for `codex/contracts/channel-format.schema.json` and durable channel defaults for `codex/contracts/channel-profile.schema.json` when a channel folder is in scope.

## Media Manifest Policy

If this skill consumes, validates, or promotes a local brand asset, reference frame, screenshot, audio reference, reusable visual asset, or Remotion template media dependency, update the media asset manifest or return `manifest_actions[]`.

Each manifest action must include `action`, `asset_id`, `canonical_path`, `remotion_public_path` and `static_file_path` when relevant, `rights_state`, `technical_metadata_state`, and `reason`.

Use `deferred` for style tokens inferred from media that is not yet captured, approved, or manifest-tracked. Do not promote a reusable asset or template media dependency into channel format without either a manifest entry or an explicit deferred manifest action.
