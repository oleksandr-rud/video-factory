---
name: vfx-quality-performance-hardening
description: Harden Remotion VFX clips for visual quality, deterministic rendering, render speed, memory use, GPU risk, media decode choices, alpha/export settings, and fallback routes. Use for complex VFX, WebGL/Three/Skia/Canvas effects, heavy gradients/blur/shadows, media-heavy clips, transparent overlays, or any clip that may slow or destabilize rendering.
---

# VFX Quality And Performance Hardening

Use this before finalizing complex VFX or after a preview/render exposes quality, timing, memory, flicker, or speed problems. This skill does not replace creative judgment; it records the technical tradeoffs needed for a VFX clip to render reliably.

When Studio or a preview page is available, use the built-in `browser:browser` skill for fast frame scrubbing, screenshots, console inspection, and visual confirmation. Browser preview supplements still renders; it does not replace renderable evidence for final handoff. The agent must analyze captured preview artifacts; screenshot or preview generation alone is not a pass.

For short clips and template previews, sample the full clip at 2 frames per second by default and 3 frames per second for dense, caption/source-card-heavy, fast-motion, transition-heavy, or previously failed clips. Browser automation should inspect DOM/CSS/SVG layers where available; video, image, canvas, WebGL, and OffthreadVideo internals are treated as pixel evidence from screenshots or sampled frames.

## Inputs

- Scene visual pack entry, producer criteria, and channel format
- Remotion scene plan, template decisions, and stack decision
- Current Remotion project contract, app commands, and dependency versions
- Media asset manifest, source asset ids, and any `staticFile()` paths
- Target output: clip package, transparent overlay, full-render layer, preview still, or review clip

## Workflow

1. Read the channel format's `visual_system.vfx_rules` when available. Treat it as a channel/project extension of this skill's local rules: apply stricter channel limits, record any allowed relaxations or exceptions, and copy applicable refs into the clip package `vfx_rule_refs`.
2. Classify VFX complexity:
   - `simple_css_svg`: transforms, opacity, SVG paths, basic masks
   - `dom_heavy`: many nodes, shadows, text effects, filters
   - `canvas`: 2D Canvas or pixel work
   - `webgl`: light leaks, shaders, starbursts, Mapbox, raw WebGL
   - `three`: React Three Fiber through `@remotion/three`
   - `skia`: React Native Skia
   - `media_heavy`: video textures, multiple video layers, image sequences
   - `hybrid`: several of the above
3. Check determinism:
   - all motion is derived from `useCurrentFrame()` and `useVideoConfig()`
   - no CSS animations, timers, `Date.now()`, live randomness, `useFrame()`, or render-order assumptions
   - seeded randomness only, with seed recorded in props
4. Check visual quality:
   - text fit and safe areas at representative frames
   - alignment of repeated blocks, source cards, lower thirds, captions, CTAs, logos, product/UI details, and foreground elements
   - dense-region readability: flag frames where multiple important reading targets compete in the same third of the frame
   - unintended overlap between blocks, captions, visual subjects, source evidence, and VFX overlays; classify intended layering separately from collisions
   - alpha edges, blend modes, masks, and transparent export path
   - color/contrast and artifact risk after compression
   - subpixel jitter on text or thin lines
   - overlays do not obscure captions, CTA, source cards, or product/UI details
5. Check performance risk:
   - avoid unnecessary GPU-heavy CSS such as large blur, drop-shadow, radial gradients, and huge box shadows
   - pre-render static or nearly-static GPU-heavy backgrounds to images when possible
   - use memoization for expensive JS calculations and stable arrays/paths
   - cap particle counts, geometry counts, blur radii, shadow layers, and canvas dimensions
   - prefer local assets and avoid render-time network fetches
6. Check media/render choices:
   - use current Remotion media guidance for video tags; record whether `<Video>` from `@remotion/media`, `<OffthreadVideo>`, or a texture helper is selected and why
   - use `staticFile()` paths for final renders
   - tune alpha export: transparent ProRes for editorial import, transparent WebM/VP9 for browser playback, or opaque H.264 when no alpha is needed
   - benchmark or lower scale before full-res renders for risky VFX
7. Check render stability:
   - attempt stills at representative frames including entry, peak motion, exit, and any alpha edge
   - use browser/Studio screenshots for quick alignment and motion debugging when available, especially for dense scenes, then analyze those screenshots directly
   - attempt a low-scale motion preview for complex VFX
   - for short preview videos, inspect the video directly when possible or sample frames across the segment at 2-3 fps and analyze the frame sequence
   - collect DOM bounding boxes, computed styles, transforms, opacity, z-index, overflow, and safe-area intersections for inspectable layers
   - use verbose render logs or `npx remotion benchmark` when render speed matters
   - lower concurrency or cache size if memory/SIGKILL risk appears
8. Record a fallback:
   - simpler CSS/SVG route
   - pre-rendered image/video background
   - lower particle/geometry count
   - opaque export instead of alpha
   - static still or reduced-motion variant
   - replacement animation route when the current motion is nondeterministic, ugly, unreadable, or remains broken after targeted timing/layout repairs

## Required Output

Return a hardening summary that can be copied into `remotion-clip-package.vfx_profile`:

```json
{
  "complexity": "simple_css_svg | dom_heavy | canvas | webgl | three | skia | media_heavy | hybrid",
  "quality_risks": ["string"],
  "performance_risks": ["string"],
  "determinism_checks": ["string"],
  "layout_debug_checks": ["string"],
  "agent_preview_analysis": {
    "artifacts_analyzed": ["string"],
    "sampling_fps": 2,
    "sampled_frames": [0],
    "dom_css_analysis_paths": ["string"],
    "visual_observations": ["string"],
    "motion_observations": ["string"],
    "pass_decision": "pass | fail | partial | unknown"
  },
  "vfx_rule_refs": ["string"],
  "render_checks": [
    {
      "purpose": "still | preview | benchmark | full_render",
      "command": "string",
      "completed": false,
      "notes": "string"
    }
  ],
  "optimization_notes": ["string"],
  "animation_repair_or_replacement": "string",
  "fallback_plan": "string",
  "status": "pass | partial | fail | not_run"
}
```

## Definition Of Done

- Complex VFX has explicit quality and performance risk notes.
- Representative stills or preview renders are attempted, or a blocker explains why not.
- Alignment, overlap, dense-region readability, text fit, safe areas, and motion readability are checked for representative frames.
- Full clip preview coverage uses 2-3 fps sampling unless an explicit blocker or Director waiver is recorded.
- DOM/CSS/SVG layers are inspected as browser elements when available; pixel-only layers are checked with screenshots or sampled frames.
- Preview artifacts are inspected and summarized by the agent; preview existence alone is not accepted as QA.
- GPU/media/alpha choices are recorded.
- A fallback exists when the chosen effect is render-heavy or fragile.
- Findings are copied into the Remotion clip package and made available to Remotion Video Producer render QA.
