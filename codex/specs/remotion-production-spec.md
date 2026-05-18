# Remotion Production Spec

## Purpose

This spec defines how the Video Factory uses Remotion for deterministic generated clips and final video assembly. Remotion work is split into two agents because short reusable clips and full timeline renders have different contracts, validation surfaces, and failure modes.

## Agent Split

### Remotion Clip Builder

Use for standalone 5-20 second artifacts:

- Scene motion graphics
- VFX overlays and transparent clips
- Reusable Remotion components
- AI-assisted component drafts
- Preview stills, low-resolution review clips, and clip metadata

The Clip Builder returns `codex/contracts/remotion-clip-package.schema.json`. Its output can also be wrapped as a `clip-candidate` when Visual Producer needs to compare it against stock, AI video, or user media.

### Remotion Video Producer

Use for full 1-10 minute videos:

- Scene timeline assembly
- Captions, subtitles, and lower thirds
- Voiceover, music, and SFX timing
- Timeline sync plans that align scenario text, narration, captions, and selected visuals
- Transitions between approved scene assets
- Render release candidates and technical render QA

The Video Producer returns `codex/contracts/timeline-sync-plan.schema.json` before assembly and `codex/contracts/render-package.schema.json` for delivery. It consumes Remotion clip packages instead of treating every scene as custom timeline code.

## Animation Baseline

Every generated Remotion clip should follow these primitives unless the project already has a stronger local pattern:

- Use `useCurrentFrame()` and `useVideoConfig()` to derive frame, fps, dimensions, and duration.
- Use `interpolate()` for direct frame-to-value mapping such as opacity, scale, position, blur, and color mix values.
- Use `spring()` for natural entrance, exit, and emphasis motion.
- Use `AbsoluteFill` for full-frame layers and predictable composition sizing.
- Use `Sequence`, `Series`, and `TransitionSeries` for timeline structure rather than ad hoc frame offsets.
- Use deterministic `random(seed)` or fixed data; never use `Math.random()` for rendered output.
- Use local assets through repo paths or `staticFile()`; do not depend on remote assets at render time.

## Remotion-Only Stack Rule

Use Remotion templates, examples, and packages before generic UI/component libraries. Preferred sources include official Remotion templates, `@remotion/captions`, `@remotion/transitions`, `@remotion/light-leaks`, `@remotion/motion-blur`, `@remotion/noise`, `@remotion/shapes`, `@remotion/paths`, `@remotion/rounded-text-box`, `@remotion/lottie`, `@remotion/rive`, `@remotion/three`, `@remotion/skia`, `@remotion/media-utils`, and `@remotion/renderer`.

Paid Remotion Pro templates, paid providers, licensed stock, or external generation calls require Director approval before spend or download.

## Clip Package Requirements

A clip package must identify:

- `clip_id`, `scene_id`, `composition_id`, duration, fps, dimensions, and aspect ratio
- Component/source paths and asset paths
- Template or package dependencies
- Props schema or props path
- Preview stills or review outputs when available
- Render commands attempted and whether they completed
- QA status and findings for timing, framing, alpha, text fit, determinism, and asset availability

## Full Render Package Requirements

A render package must identify:

- `render_id`, `scenario_id`, `composition_id`, timeline path, timeline sync plan path, voiceover package path, duration, fps, dimensions, and aspect ratio
- Source clip package ids or candidate ids used per scene
- Captions/subtitle artifacts and burned-in versus sidecar subtitle policy
- Audio mix source paths and QA notes
- Render commands, preview commands, output files, and delivery variants
- QA status and findings for timeline continuity, audio sync, subtitle fit, render health, rights, and blockers

## Timeline Sync Requirements

A timeline sync plan must identify:

- scene ids, narration text, start/end seconds, and start/end frames
- selected visual candidate or Remotion clip package per scene
- voiceover package scene entries, audio paths, and generated duration when available
- caption JSON/SRT paths and timing ranges
- overlay, lower-third, CTA, and transition notes
- QA findings for drift, missing audio, missing captions, missing visuals, and safe-area conflicts

## QA Gates

Clip QA passes only when the component renders or has a clearly documented blocker, timing is deterministic, text fits, assets resolve locally, and alpha/output expectations are verified.

Full-video QA passes only when the timeline sync plan exists, the timeline is assembled in order, captions and audio sync are checked, outputs match platform requirements, and rights/blockers are recorded in the render package.

## Uncovered Skill Gaps

The scan found four gaps in the previous agent skills:

- The Remotion skills had animation guidance, but no explicit baseline tying clip generation to frame primitives such as current frame, video config, interpolation, springs, and full-frame layers.
- The VFX and generated-component skills produced useful implementation notes, but did not require a formal clip package artifact.
- The full-video render package did not track source Remotion clip packages, which made final timeline provenance weak.
- There was no explicit timeline sync contract tying scenario text, generated voiceover alignment, captions, and selected visuals together.
- One agent owned both low-level component/VFX generation and full timeline render QA, which encouraged oversized prompts and mixed definitions of done.

Those gaps are now covered by `remotion-clip-package.schema.json`, `voiceover-package.schema.json`, `timeline-sync-plan.schema.json`, the `source_clip_packages` field in the render package, and the split between Remotion Clip Builder and Remotion Video Producer.

## Evidence From Current Research

The RemotionTemplates animation intro reinforced that basic Remotion animation is built from frame-aware React components: current frame, video config, `interpolate()`, `spring()`, and `AbsoluteFill`. That exposes a gap in the previous agent model: the old Remotion agent mixed low-level reusable animation/component generation with full timeline assembly and render QA. Those are different production loops, so they now have separate owners. Source: https://remotiontemplates.dev/articles/remotion-animations-intro

The official Remotion AI SaaS template and system-prompt docs support the same validation posture: generated Remotion code needs structured prompts, sanitation, compile/runtime correction, and local preview or render checks. Sources: https://www.remotion.dev/docs/ai/ai-saas-template and https://www.remotion.dev/docs/ai/system-prompt
