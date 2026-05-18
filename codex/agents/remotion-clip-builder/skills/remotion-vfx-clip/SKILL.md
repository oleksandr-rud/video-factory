---
name: remotion-vfx-clip
description: Generate deterministic VFX clips and overlays in Remotion. Use when a scene needs kinetic typography, particles, light leaks, motion blur, starbursts, noise, Lottie overlays, 3D phone/product shots, transparent WebM/ProRes overlays, or audio-reactive visuals.
---

# Remotion VFX Clip

Load the built-in `remotion:remotion-best-practices` skill before implementation. Read its rule files only as needed: `animations`, `timing`, `transitions`, `light-leaks`, `transparent-videos`, `3d`, `lottie`, `audio-visualization`, `assets`, `fonts`, and `measuring-text`.

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
6. Define frame ranges, entry/exit timing, blend mode, z-index, safe areas, and alpha behavior.
7. Make props typed and deterministic: `durationInFrames`, colors, seed, intensity, text, audio path, and transparent mode.
8. Add preview checks: one still frame at a representative frame, one motion preview or full render for complex VFX.
9. For overlays, define both opaque and transparent render commands when needed.
10. Write or update a Remotion clip package matching `codex/contracts/remotion-clip-package.schema.json`, including template ids/contract paths or `template_instances[]` when relevant, project/channel fields, Remotion app path, media manifest path, source asset ids, and output asset ids when available.
11. If this VFX should be reusable, write or update a Remotion template contract matching `codex/contracts/remotion-template.schema.json`.

Definition of done:

- VFX clip has stable composition id or reusable component path.
- Reusable VFX has a stable `template_id`, template contract, and registry entry. Bespoke VFX records the reason templates were not used in `bespoke_vfx_notes`.
- It can render without network access.
- It fits the target aspect ratio and does not obscure required captions or CTA.
- Alpha/export settings are documented when transparency is required.
- It does not depend on generic web UI component libraries.
- It can be consumed by the Remotion Video Producer without hidden assumptions.
