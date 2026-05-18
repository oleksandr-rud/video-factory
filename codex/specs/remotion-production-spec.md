# Remotion Production Spec

## Purpose

This spec defines how the Video Factory uses Remotion for deterministic generated clips and final video assembly. Remotion work is split into two agents because short reusable clips and full timeline renders have different contracts, validation surfaces, and failure modes.

## Remotion App Setup

The repo has a shared Remotion app at `remotion/`. It is the default execution target for deterministic clips, post-production timelines, preview stills, render release candidates, and local validation. A project-specific Remotion app may be created only when the shared app cannot satisfy incompatible dependency, licensing, or isolation requirements.

Track the app with `codex/contracts/remotion-project.schema.json`. The contract must record the app root, package manager, Remotion version, composition registry, dependency policy, commands, public asset policy, and QA status.

Use this public asset rule:

- Canonical source media stays in `channels/<channel-slug>/projects/<project-slug>/source-media/` and generated/rendered media stays in the project artifact folders.
- Media needed by Remotion is copied or mirrored under `remotion/public/channels/<channel-slug>/projects/<project-slug>/...`.
- Every copied/mirrored asset must be recorded in `codex/contracts/media-asset-manifest.schema.json` with `canonical_path`, `remotion_public_path`, and `static_file_path`.
- Final renders must use local assets through `staticFile()` or local repo paths; remote render-time media requires explicit Director approval.

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

- `clip_id`, `scene_id`, project/channel ids, `composition_id`, duration, fps, dimensions, and aspect ratio
- Component/source paths and asset paths
- Media asset manifest path, source asset ids, output asset ids, and Remotion app/contract path
- Template or package dependencies
- Props schema or props path
- Preview stills or review outputs when available
- Render commands attempted and whether they completed
- QA status and findings for timing, framing, alpha, text fit, determinism, and asset availability

## Full Render Package Requirements

A render package must identify:

- `render_id`, `scenario_id`, project/channel ids, `composition_id`, Remotion app/contract path, timeline path, timeline sync plan path, voiceover package path, duration, fps, dimensions, and aspect ratio
- Source clip package ids or candidate ids used per scene
- Media asset manifest path, source asset ids, output asset ids where available, and evidence refs for source-backed render decisions
- Captions/subtitle artifacts and burned-in versus sidecar subtitle policy
- Audio mix source paths and QA notes
- Render commands, preview commands, output files, and delivery variants
- QA status and findings for timeline continuity, audio sync, subtitle fit, render health, rights, and blockers

## Timeline Sync Requirements

A timeline sync plan must identify:

- scene ids, narration text, start/end seconds, and start/end frames
- selected visual candidate, source media asset, `staticFile()` path, or Remotion clip package per scene
- voiceover package scene entries, audio paths, and generated duration when available
- caption JSON/SRT paths and timing ranges
- overlay, lower-third, CTA, and transition notes
- QA findings for drift, missing audio, missing captions, missing visuals, and safe-area conflicts

## QA Gates

Clip QA passes only when the component renders or has a clearly documented blocker, timing is deterministic, text fits, assets resolve locally, and alpha/output expectations are verified.

Full-video QA passes only when the timeline sync plan exists, the timeline is assembled in order, captions and audio sync are checked, outputs match platform requirements, and rights/blockers are recorded in the render package.

Remotion setup QA passes only when dependencies install, `npm run lint` passes or has a documented blocker, at least one still or preview render is attempted for changed compositions, and required media assets resolve through the manifest.

## Uncovered Skill Gaps

The scan found four gaps in the previous agent skills:

- The Remotion skills had animation guidance, but no explicit baseline tying clip generation to frame primitives such as current frame, video config, interpolation, springs, and full-frame layers.
- The VFX and generated-component skills produced useful implementation notes, but did not require a formal clip package artifact.
- The full-video render package did not track source Remotion clip packages, which made final timeline provenance weak.
- There was no explicit timeline sync contract tying scenario text, generated voiceover alignment, captions, and selected visuals together.
- There was no explicit Remotion app/setup contract, so commands, dependencies, public asset rules, and composition registry were implicit.
- There was no project media manifest, so loaded reference videos, source clips, generated clips, rendered clips, and review evidence could not be traced consistently.
- One agent owned both low-level component/VFX generation and full timeline render QA, which encouraged oversized prompts and mixed definitions of done.

Those gaps are now covered by `remotion-project.schema.json`, `media-asset-manifest.schema.json`, `remotion-clip-package.schema.json`, `voiceover-package.schema.json`, `timeline-sync-plan.schema.json`, the `source_clip_packages` and source asset fields in the render package, and the split between Remotion Clip Builder and Remotion Video Producer.

## Evidence From Current Research

The RemotionTemplates animation intro reinforced that basic Remotion animation is built from frame-aware React components: current frame, video config, `interpolate()`, `spring()`, and `AbsoluteFill`. That exposes a gap in the previous agent model: the old Remotion agent mixed low-level reusable animation/component generation with full timeline assembly and render QA. Those are different production loops, so they now have separate owners. Source: https://remotiontemplates.dev/articles/remotion-animations-intro

The official Remotion AI SaaS template and system-prompt docs support the same validation posture: generated Remotion code needs structured prompts, sanitation, compile/runtime correction, and local preview or render checks. Sources: https://www.remotion.dev/docs/ai/ai-saas-template and https://www.remotion.dev/docs/ai/system-prompt

The current Remotion setup and asset docs support the shared-app/public-projection design: projects can be created with `npx create-video@latest`, videos can render through Studio or CLI, local assets should be loaded from the app `public/` folder with `staticFile()`, and render-time sidecars can be emitted with `<Artifact>`. Sources: https://www.remotion.dev/docs, https://www.remotion.dev/docs/render, https://www.remotion.dev/docs/staticfile, and https://www.remotion.dev/docs/artifact
