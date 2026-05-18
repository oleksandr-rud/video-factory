# Remotion Production Spec

## Purpose

This spec defines how the Video Factory uses Remotion for deterministic generated clips and final video assembly. Remotion work is split into two agents because short reusable clips and full timeline renders have different contracts, validation surfaces, and failure modes.

## Remotion App Setup

The repo has a shared Remotion app at `remotion/`. It is the default execution target for deterministic clips, post-production timelines, preview stills, render release candidates, and local validation. A project-specific Remotion app may be created only when the shared app cannot satisfy incompatible dependency, licensing, or isolation requirements.

Track the app with `codex/contracts/remotion-project.schema.json`. The contract must record the app root, package manager, Remotion version, composition registry, dependency policy, commands, public asset policy, and QA status.

Reusable Remotion components are tracked separately with `codex/contracts/remotion-template.schema.json`. The shared app keeps a code registry at `remotion/src/templateRegistry.tsx` and shared template contracts under `remotion/templates/`; project-specific template contracts should live under `channels/<channel-slug>/projects/<project-slug>/remotion/templates/`.

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

The Clip Builder returns `codex/contracts/remotion-clip-package.schema.json` for scene instances and `codex/contracts/remotion-template.schema.json` when it selects, creates, revises, or promotes reusable templates. Its output can also be wrapped as a `clip-candidate` when Visual Producer needs to compare it against stock, AI video, or user media.

### Remotion Video Producer

Use for full 1-10 minute videos:

- Scene timeline assembly
- Captions, subtitles, and lower thirds
- Voiceover, music, and SFX timing
- Timeline sync plans that align scenario text, narration, captions, and selected visuals
- Transitions between approved scene assets
- Visual debugging for alignment, dense-region overlap, text fit, safe areas, motion readability, and broken animation repair
- Render release candidates and technical render QA

The Video Producer returns `codex/contracts/timeline-sync-plan.schema.json` before assembly and `codex/contracts/render-package.schema.json` for delivery. It consumes Remotion clip packages instead of treating every scene as custom timeline code.

If the Video Producer discovers that a missing lower third, source card, caption style, transition, overlay, or other reusable template is needed, it returns a handoff recommendation. The Director turns that into a Remotion Clip Builder handoff; the Video Producer does not read Clip Builder-only template skills.

## Animation Baseline

Every generated Remotion clip should follow these primitives unless the project already has a stronger local pattern:

- Use `useCurrentFrame()` and `useVideoConfig()` to derive frame, fps, dimensions, and duration.
- Use `interpolate()` for direct frame-to-value mapping such as opacity, scale, position, blur, and color mix values.
- Use `spring()` for natural entrance, exit, and emphasis motion.
- Use `AbsoluteFill` for full-frame layers and predictable composition sizing.
- Use `Sequence`, `Series`, and `TransitionSeries` for timeline structure rather than ad hoc frame offsets.
- Use deterministic `random(seed)` or fixed data; never use `Math.random()` for rendered output.
- Use local assets through repo paths or `staticFile()`; do not depend on remote assets at render time.

## Visual Debugging Baseline

Remotion work must include a visual debugging pass whenever code, props, templates, captions, source cards, lower thirds, VFX, transitions, or dense visual layouts change.

Use a staged evidence loop:

- Start with static checks: lint/typecheck/build where available.
- Render stills for representative frames: scene entry, settled/midpoint, scene exit, transition boundaries, caption-heavy frames, peak-density frames, peak-motion frames, and any reported failure timestamp.
- Use Remotion Studio or a local preview page through Browser when available for fast scrubbing, screenshots, console/runtime errors, visible loading states, and bounding-box inspection.
- Run per-scene sampled-frame analysis: 2 frames per second by default and 3 frames per second for dense, text-heavy, fast-motion, transition-heavy, source-card, caption-heavy, UI/product, or previously failed scenes.
- Treat Remotion previews as HTML/CSS/SVG/React when layers are DOM-backed: inspect bounding boxes, computed styles, transforms, opacity, z-index, overflow, fonts, and safe-area intersections with Browser automation.
- Treat video, images, canvas, WebGL, and OffthreadVideo internals as pixel evidence: inspect screenshots, stills, and sampled frames because their internal content is not exposed as useful DOM structure.
- Use short low-scale renders for motion problems before spending time on a full render.
- Analyze preview artifacts directly. An agent must inspect stills, screenshots, sampled frames, or short preview videos and write visual/motion observations before the preview can count as QA evidence.
- Keep final render evidence reproducible with exact commands, output paths, frame numbers, and manifest entries.

Visual debugging must check:

- alignment against the project grid, safe areas, source-card regions, captions, lower thirds, CTAs, logos, products, UI details, and foreground subjects
- dense-region readability when multiple text/visual targets compete in the same third of the frame
- unintended overlap between blocks, captions, overlays, source evidence, and key visuals
- text fit for long words, source titles, translations, numbers, and dynamic captions
- motion quality: no CSS animations, timers, wall-clock behavior, unseeded randomness, unbounded interpolation drift, accidental spring overshoot, text jitter, or occluding transitions
- render production risks: font loading, asset loading, local `staticFile()` projection, media decode route, alpha edges, compression artifacts, GPU-heavy effects, cache/concurrency/SIGKILL risk, and browser/render differences

Classify overlaps as `intended_layering`, `acceptable_tightness`, `minor_collision`, `major_collision`, or `blocker_collision`. A blocker collision hides captions, source evidence, product/UI details, faces, legal/rights disclosures, or the scene's primary reading target.

Repair policy:

- Use targeted edits for isolated z-index, position, crop, scale, timing, easing, font-size, line-break, or delay problems.
- Replace the animation route when the current route is nondeterministic, visually ugly after bounded repair, too dense to read, dependent on unsupported CSS/browser behavior, or too brittle for full-render production.
- Preserve public props, composition ids, template contracts, and clip package APIs unless the repair cannot be made safely.
- If Remotion Video Producer finds a defect inside a Clip Builder-owned reusable clip or template, it must return a Director handoff recommendation rather than editing that template directly.

## Remotion-Only Stack Rule

Use Remotion templates, examples, and packages before generic UI/component libraries. Preferred sources include official Remotion templates, `@remotion/captions`, `@remotion/transitions`, `@remotion/light-leaks`, `@remotion/motion-blur`, `@remotion/noise`, `@remotion/shapes`, `@remotion/paths`, `@remotion/rounded-text-box`, `@remotion/lottie`, `@remotion/rive`, `@remotion/three`, `@remotion/skia`, `@remotion/media-utils`, and `@remotion/renderer`.

Paid Remotion Pro templates, paid providers, licensed stock, or external generation calls require Director approval before spend or download.

## Reusable Template Requirements

A Remotion template is reusable only when it has:

- stable `template_id`, `composition_id`, component path, and version
- documented props contract and default props
- category, aspect ratio support, safe-area behavior, alpha/export behavior, and usage rules
- dependencies and license notes
- preview/render commands or a documented blocker
- QA status and findings
- one or more scene-specific clip packages when instantiated in a project

Local reusable template categories include lower thirds, source cards, caption blocks, transitions, overlays, data callouts, device/UI mockups, audio visualizers, openers, title cards, thumbnails, scene shells, and VFX.

Templates are optional primitives, not a required implementation path. A Remotion clip may use no templates, one template, multiple template layers, or a hybrid of template layers and bespoke code. Use bespoke Remotion when the scene needs complex procedural VFX, custom 3D, custom Canvas/WebGL, unique art direction, or a one-off visual that would become harder to maintain as a template.

Do not hardcode one-off scene copy, claims, or media inside reusable templates. Put those values in props and record each use in a Remotion clip package.

## Clip Package Requirements

A clip package must identify:

- `clip_id`, `scene_id`, project/channel ids, `composition_id`, duration, fps, dimensions, and aspect ratio
- `template_id`, `template_contract_path`, instance props, or `template_instances[]` when the clip is template-backed
- `bespoke_vfx_notes` when templates were considered but skipped for a complex custom effect
- Component/source paths and asset paths
- Media asset manifest path, source asset ids, output asset ids, and Remotion app/contract path
- Template or package dependencies
- Props schema or props path
- Preview stills or review outputs when available
- Render commands attempted and whether they completed
- QA status and findings for timing, framing, alignment, dense-region overlap, alpha, text fit, safe areas, motion quality, determinism, and asset availability

## Full Render Package Requirements

A render package must identify:

- `render_id`, `scenario_id`, project/channel ids, `composition_id`, Remotion app/contract path, timeline path, timeline sync plan path, voiceover package path, duration, fps, dimensions, and aspect ratio
- Source clip package ids or candidate ids used per scene
- Media asset manifest path, source asset ids, output asset ids where available, and evidence refs for source-backed render decisions
- Captions/subtitle artifacts and burned-in versus sidecar subtitle policy
- Audio mix source paths and QA notes
- Render commands, preview commands, output files, and delivery variants
- Visual debugging evidence for representative stills/screenshots, dense frames, overlap classification, text fit, safe areas, and motion readability when risk is present
- Agent preview analysis for stills, screenshots, sampled frames, or short preview videos; preview generation alone is not validation
- Per-scene 2-3 fps sampled-frame coverage, plus DOM/CSS analysis reports for inspectable Remotion layers when Browser preview is available
- QA status and findings for timeline continuity, audio sync, subtitle fit, layout alignment, dense-region overlap, motion quality, render health, rights, and blockers

## Timeline Sync Requirements

A timeline sync plan must identify:

- scene ids, narration text, start/end seconds, and start/end frames
- selected visual candidate, source media asset, `staticFile()` path, or Remotion clip package per scene
- template id and template contract path, or template layer list, for template-backed scene visuals
- voiceover package scene entries, audio paths, and generated duration when available
- caption JSON/SRT paths and timing ranges
- overlay, lower-third, CTA, and transition notes
- QA findings for drift, missing audio, missing captions, missing visuals, and safe-area conflicts

## QA Gates

Clip QA passes only when the component renders or has a clearly documented blocker, timing is deterministic, text fits, assets resolve locally, and alpha/output expectations are verified.

Clip visual QA also requires representative frame evidence for dense, text-heavy, source-card, lower-third, UI/product, caption, or VFX-heavy clips. Any major or blocker overlap must be fixed, replaced, or returned as a blocked handoff with evidence.

Complex VFX QA additionally requires a quality/performance hardening pass. The clip package should record `vfx_profile` when the clip uses WebGL, Three, Skia, Canvas, media-heavy layers, large CSS filters/shadows/gradients, transparent export, many DOM nodes, particles, or bespoke procedural animation.

VFX hardening checks:

- deterministic frame mapping: `useCurrentFrame()`, `useVideoConfig()`, seeded randomness, no CSS animations, no timers, no render-order assumptions
- visual quality: representative stills for entry/peak/exit frames, text fit, safe areas, alpha edges, blend/mask behavior, compression artifact risk, and subpixel jitter
- performance: GPU-heavy effects, particle/geometry counts, blur/shadow/filter cost, memoization of expensive calculations, media decode route, cache/concurrency risk, and fallback plan
- render strategy: low-scale preview first, stills for changed frames, verbose logs or `npx remotion benchmark` when speed matters, and explicit alpha codec choices

Full-video QA passes only when the timeline sync plan exists, the timeline is assembled in order, captions and audio sync are checked, outputs match platform requirements, and rights/blockers are recorded in the render package.

Full-video visual debugging passes only when every scene has 2-3 fps sampled-frame analysis, Browser has inspected DOM/CSS/SVG layers when available, pixel-only layers have screenshot/still/frame evidence, the agent has analyzed those preview artifacts, layout alignment is checked, dense-region overlaps are classified, text fit and safe areas are checked, broken or ugly motion is fixed or routed, and render-production risks are recorded.

Remotion setup QA passes only when dependencies install, `npm run lint` passes or has a documented blocker, at least one still or preview render is attempted for changed compositions, and required media assets resolve through the manifest.

## Director Run Implementation

When the Director prompt runs, reusable templates enter the pipeline this way:

1. Director decomposes the request, resolves `remotion/remotion-project.json`, and notes `remotion/src/templateRegistry.tsx` plus any project template contract paths.
2. Channel Intelligence may put reusable template ids or desired reusable assets into the channel format.
3. Visual Producer expresses scene-level `template_hint`, `template_id`, `template_ids`, or reusable template requirements in the scene visual pack only when templates fit the scene. Complex VFX requests can explicitly allow bespoke VFX.
4. Director converts those hints into a Remotion Clip Builder handoff that includes `remotion-template-library`, the Remotion project contract, the template registry path, producer criteria, channel format, and the requested output contracts.
5. Remotion Clip Builder either selects one or more existing templates, implements a new reusable template, combines template layers with bespoke VFX, or writes a fully bespoke Remotion clip. Reusable templates are registered under `remotion/src/templateRegistry.tsx`; every scene-specific result still gets a `remotion-clip-package`.
6. Director validates the returned template and clip packages, updates the project index and production run ledger, then passes only the clip package paths and template contract paths downstream.
7. Remotion Video Producer consumes the clip packages and timeline sync plan; if a needed template is missing or invalid, it recommends a new Clip Builder handoff instead of editing template internals.
8. Remotion Video Producer runs visual debugging before render QA whenever the timeline changed, frames are dense, multiple overlay systems share the screen, or prior feedback names alignment, overlap, readability, or animation defects.
9. Render QA and Video Critic evaluate the final render with template provenance visible through clip packages and render package source references.

## Uncovered Skill Gaps

The scan found four gaps in the previous agent skills:

- The Remotion skills had animation guidance, but no explicit baseline tying clip generation to frame primitives such as current frame, video config, interpolation, springs, and full-frame layers.
- The VFX and generated-component skills produced useful implementation notes, but did not require a formal clip package artifact.
- The full-video render package did not track source Remotion clip packages, which made final timeline provenance weak.
- There was no explicit timeline sync contract tying scenario text, generated voiceover alignment, captions, and selected visuals together.
- There was no explicit Remotion app/setup contract, so commands, dependencies, public asset rules, and composition registry were implicit.
- There was no project media manifest, so loaded reference videos, source clips, generated clips, rendered clips, and review evidence could not be traced consistently.
- One agent owned both low-level component/VFX generation and full timeline render QA, which encouraged oversized prompts and mixed definitions of done.
- There was no explicit visual debugging gate for alignment, dense-region overlaps, browser/Studio preview evidence, and broken animation replacement before render QA.

Those gaps are now covered by `remotion-project.schema.json`, `media-asset-manifest.schema.json`, `remotion-clip-package.schema.json`, `voiceover-package.schema.json`, `timeline-sync-plan.schema.json`, the `source_clip_packages` and source asset fields in the render package, the split between Remotion Clip Builder and Remotion Video Producer, and `codex/agents/remotion-video-producer/skills/remotion-visual-debugging/SKILL.md`.

## Evidence From Current Research

The RemotionTemplates animation intro reinforced that basic Remotion animation is built from frame-aware React components: current frame, video config, `interpolate()`, `spring()`, and `AbsoluteFill`. That exposes a gap in the previous agent model: the old Remotion agent mixed low-level reusable animation/component generation with full timeline assembly and render QA. Those are different production loops, so they now have separate owners. Source: https://remotiontemplates.dev/articles/remotion-animations-intro

The official Remotion AI SaaS template and system-prompt docs support the same validation posture: generated Remotion code needs structured prompts, sanitation, compile/runtime correction, and local preview or render checks. Sources: https://www.remotion.dev/docs/ai/ai-saas-template and https://www.remotion.dev/docs/ai/system-prompt

The current Remotion setup and asset docs support the shared-app/public-projection design: projects can be created with `npx create-video@latest`, videos can render through Studio or CLI, local assets should be loaded from the app `public/` folder with `staticFile()`, and render-time sidecars can be emitted with `<Artifact>`. Sources: https://www.remotion.dev/docs, https://www.remotion.dev/docs/render, https://www.remotion.dev/docs/staticfile, and https://www.remotion.dev/docs/artifact

The current Remotion debugging docs support a formal visual debug lane: Studio previews run in the browser, CLI still renders can capture exact frames, `@remotion/renderer` can render stills or frame sequences, layout-utils can measure and fit text, frame-driven animation avoids flicker, and troubleshooting docs identify nondeterminism, asset loading, font loading, concurrency, and memory/SIGKILL as production failure modes. Sources: https://www.remotion.dev/docs/studio, https://www.remotion.dev/docs/cli/still, https://www.remotion.dev/docs/renderer, https://www.remotion.dev/docs/layout-utils, https://www.remotion.dev/docs/animating-properties, and https://www.remotion.dev/docs/flickering

Remotion's current performance docs also define the VFX hardening surface. Concurrency should be benchmarked because too much or too little concurrency can slow rendering; GPU-heavy content includes WebGL, Canvas, gradients, blur, shadows, and similar effects; slow JavaScript should be measured and memoized; transparent videos need PNG image format, which is slower than JPEG; and lower-resolution preview renders can be used through `--scale`. Remotion also recommends verbose render logs and `npx remotion benchmark` for measuring speed. Sources: https://www.remotion.dev/docs/performance and https://www.remotion.dev/docs/cli/benchmark

GPU and media docs refine the implementation choices: headless Chromium disables GPU by default, cloud environments may lack GPU, `<Html5Video>` and `<OffthreadVideo>` are not GPU-accelerated, `@remotion/media` can be the better render-time video tag, and `@remotion/three` should use `ThreeCanvas` plus frame-derived animation rather than render-loop animation. Sources: https://www.remotion.dev/docs/gpu, https://www.remotion.dev/docs/video-tags, https://www.remotion.dev/docs/offthreadvideo, and https://www.remotion.dev/docs/three

Troubleshooting docs reinforce failure modes that should become QA checks: flickering often comes from non-deterministic or order-dependent animation, SIGKILL commonly indicates memory pressure where lower cache/concurrency can help, and font loading should be scoped to needed weights/subsets to avoid render timeouts. Sources: https://www.remotion.dev/docs/flickering, https://www.remotion.dev/docs/troubleshooting/sigkill, and https://www.remotion.dev/docs/troubleshooting/font-loading-errors
