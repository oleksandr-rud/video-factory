---
name: remotion-vfx-clip
description: Generate deterministic VFX clips and overlays in Remotion. Use when a scene needs kinetic typography, particles, light leaks, motion blur, starbursts, noise, Lottie overlays, 3D phone/product shots, transparent WebM/ProRes overlays, or audio-reactive visuals.
---

# Remotion VFX Clip

Load the built-in `remotion:remotion-best-practices` skill before implementation. Read its rule files only as needed: `animations`, `timing`, `transitions`, `light-leaks`, `transparent-videos`, `3d`, `lottie`, `audio-visualization`, `assets`, `fonts`, and `measuring-text`.
For complex VFX, WebGL/Three/Skia/Canvas, media-heavy clips, transparent overlays, or any render speed/memory/flicker risk, also use `../vfx-quality-performance-hardening/SKILL.md`.

Workflow:

1. Define the clip purpose: scene insert, transition overlay, opener, lower third, caption emphasis, product/UI shot, data moment, or audio-reactive beat.
2. If the purpose matches a reusable pattern, use `../remotion-template-library/SKILL.md` to select, create, or promote a template. Skip template use when the requested VFX needs bespoke procedural animation, custom 3D, custom Canvas/WebGL, or one-off art direction.
3. If a clip is being generated from text by another LLM/Codex run, first use `../remotion-ai-component-prompt/SKILL.md`.
4. Pick the implementation route from Remotion-native options:
   - CSS/SVG: shapes, typography, glows, masks, overlays.
   - Remotion package: transitions, light leaks, motion blur, noise, shapes, paths, rounded text boxes, starburst.
   - Lottie or Rive: local animation assets with timing controlled by Remotion.
   - Remotion Three: 3D mockups, camera moves, product objects, spatial UI.
   - Remotion Skia: Skia-heavy vector/canvas effects.
   - Canvas/WebGL inside Remotion: procedural particles or shader-like effects when CSS/SVG is insufficient.
5. Resolve the Remotion app contract, template registry path, and media asset manifest. Use the shared `remotion/` app by default, and record source media asset ids plus `staticFile()` paths for any local media.
6. Read `channel_format_path` when available and apply `visual_system.vfx_rules` to effect selection, intensity limits, transition behavior, alpha/export choices, hardening triggers, benchmarks, and fallback requirements.
7. Define frame ranges, entry/exit timing, blend mode, z-index, safe areas, and alpha behavior.
8. Make props typed and deterministic: `durationInFrames`, colors, seed, intensity, text, audio path, and transparent mode.
9. Add preview checks: still frames for entry/settled/peak-motion/exit states, 2-3 fps sampled-frame coverage across the clip, browser/Studio screenshots when available for fast alignment review, and one motion preview or full render for complex VFX. The agent must inspect those artifacts and record preview-analysis findings before accepting the clip.
   - Use browser automation to inspect DOM/CSS/SVG layers where available.
   - Use screenshot/sampled-frame pixel analysis for video, image, canvas, WebGL, and OffthreadVideo content.
10. For overlays, define both opaque and transparent render commands when needed.
11. Run quality/performance hardening when the clip is complex, bespoke, GPU-heavy, media-heavy, transparent, intended for repeated reuse, or required by channel-format VFX rules.
12. Write or update a Remotion clip package matching `codex/contracts/remotion-clip-package.schema.json`, including template ids/contract paths or `template_instances[]` when relevant, project/channel fields, channel format path, Remotion app path, media manifest path, source asset ids, output asset ids, `vfx_rule_refs`, and `vfx_profile` when hardening was performed.
13. If this VFX should be reusable, write or update a Remotion template contract matching `codex/contracts/remotion-template.schema.json`.

Definition of done:

- VFX clip has stable composition id or reusable component path.
- Reusable VFX has a stable `template_id`, template contract, and registry entry. Bespoke VFX records the reason templates were not used in `bespoke_vfx_notes`.
- It can render without network access.
- It fits the target aspect ratio and does not obscure required captions or CTA.
- Dense frames have been checked for alignment, unintended overlap, source-card/caption/lower-third conflicts, and readable motion.
- Preview artifacts have been analyzed by the agent and summarized in QA or `vfx_profile.agent_preview_analysis`.
- Clip preview coverage samples the full clip at 2-3 fps unless an explicit blocker or Director waiver is recorded.
- Alpha/export settings are documented when transparency is required.
- It does not depend on generic web UI component libraries.
- VFX quality/performance risks and fallback plan are recorded for complex effects.
- Broken or ugly motion is repaired, replaced with a simpler deterministic route, or explicitly marked as blocked with evidence.
- It can be consumed by the Remotion Video Producer without hidden assumptions.

## Media Manifest Policy

If this skill consumes, creates, validates, renders, mirrors, or defers local media, Remotion public assets, generated clip outputs, transparent overlays, still previews, thumbnails, template assets, or QA evidence media, update the media asset manifest or return `manifest_actions[]`.

Each manifest action must include `action`, `asset_id`, `canonical_path`, `remotion_public_path` and `static_file_path` when relevant, `rights_state`, `technical_metadata_state`, `evidence_refs`, and `reason`.

Use `deferred` for planned renders, missing media probes, public projection work that has not happened yet, or outputs blocked by render failures. Clip packages must cite manifest-backed `source_asset_ids` and `output_asset_ids` when files exist.

## Approval And Stop Conditions

Stop and return `needs_approval` before using paid Remotion Pro templates, paid VFX assets, licensed stock, unapproved source images/screenshots, external generation tools, or remote render-time media. Stop and return `blocked` when required VFX cannot render locally, cannot meet alpha/export requirements, or would obscure required captions, source disclosures, or platform-safe areas.
