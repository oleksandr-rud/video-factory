---
name: remotion-visual-debugging
description: Debug Remotion compositions, previews, clips, and render candidates for layout alignment, dense-region collisions, overlapping blocks, ugly or broken motion, text fit, safe-area conflicts, and production render risks using stills, browser/Studio previews, metadata, and targeted repairs.
---

# Remotion Visual Debugging

Use this before render QA when a Remotion composition has changed, a scene is visually dense, captions/lower thirds/source cards overlap other visuals, motion feels broken, or a rendered preview exposes layout or animation defects. This skill is technical and visual QA; Video Critic still owns independent release critique.

Preview capture is not enough. The agent must inspect and analyze preview artifacts directly, then record visual observations and pass/fail findings. Do not mark a preview as passing only because Studio opened, a still rendered, or a short render file exists.

Load the built-in `remotion:remotion-best-practices` skill before code changes. Read its `measuring-text`, `measuring-dom-nodes`, `animations`, `timing`, `assets`, `videos`, `transitions`, and `ffmpeg` rules as needed. Use the built-in `browser:browser` skill for local Remotion Studio or preview pages when a browser preview is available.

## Inputs

- Remotion app root, project contract, composition id, dimensions, fps, duration, and render commands
- Timeline source, timeline sync plan, render package, input props, and selected scene/frame ranges
- Scenario, producer criteria, channel format, platform safe areas, captions/subtitles, lower thirds, overlays, source cards, and visual candidates
- Remotion clip packages, template contracts, VFX profiles, media asset manifest, render logs, preview stills, short renders, or screenshots
- Known failure report from the Director, user, render QA, or Video Critic

## Workflow

1. Establish the debug target:
   - composition id, app root, props path, fps, dimensions, aspect ratio, duration frames, scene ids, and changed files
   - expected layer stack: background, selected visual, generated clip, VFX, source card, lower third, captions, CTA, watermark, foreground
   - current failure type: compile, missing asset, text overflow, visual overlap, dense region, unsafe crop, bad motion, flicker, jank, alpha edge, audio/caption sync, render performance, or unknown
2. Build a per-scene sampling plan:
   - sample every scene, not only the full RC as one unit
   - use 2 frames per second by default for each scene (`sample_interval_frames = fps / 2`)
   - use 3 frames per second for dense, text-heavy, fast-motion, transition-heavy, source-card, caption-heavy, UI/product, or previously failed scenes (`sample_interval_frames = fps / 3`)
   - always include scene starts, scene midpoints, scene ends, transition boundaries, caption-heavy frames, peak text density, peak VFX intensity, and any frames named by a failure report
   - if the scene is too long for full 2-3 fps inspection within the current run budget, return `blocked` or `needs_approval` unless the Director explicitly accepts a reduced sampling waiver
3. Run the cheapest deterministic checks first:
   - package lint/typecheck/build command when available
   - `npx remotion still <composition-id> <path> --frame=<frame> --scale=0.25` for quick layout evidence
   - short low-scale render for motion issues, such as `npx remotion render <composition-id> <path> --frames=<start>-<end> --scale=0.25`
   - metadata/probe checks for media-backed failures
4. Use browser preview when practical:
   - start Studio or use the preview URL from the Remotion project contract
   - open it with Browser, scrub or navigate to target frames, and capture screenshots for layout defects
   - inspect console/runtime errors, visible loading states, failed assets, font fallbacks, and viewport scaling
   - when debug attributes exist, collect bounding boxes with browser JavaScript for nodes marked with `data-vf-role`, `data-scene-id`, `data-layer`, `data-safe-area`, or project-equivalent markers
   - treat Remotion preview as inspectable HTML/CSS/SVG/React where the layer is DOM-backed: collect bounding boxes, computed styles, transforms, opacity, z-index, overflow, font metrics, and safe-area intersections
   - treat raster/video/canvas/WebGL/OffthreadVideo contents as pixel evidence: inspect screenshots/sampled frames because their internal content is not meaningfully exposed as DOM boxes
   - combine both views when a scene mixes DOM overlays over video/canvas backgrounds: DOM/CSS analysis for overlays, pixel analysis for visual media
5. Analyze the preview artifacts as an agent:
   - visually inspect every generated still and browser screenshot
   - for preview videos or short renders, inspect the video directly when possible; otherwise sample frames across the segment and inspect those frames
   - inspect the 2-3 fps per-scene sample set and record skipped frames only with a reason
   - compare adjacent sampled frames around transitions or fast motion to catch jitter, popping, flicker, unreadable motion, and accidental occlusion
   - record what is visible, what is hidden, what is crowded, what moves poorly, and what changed after repairs
   - write a `preview_analysis` output artifact or QA entry when the pass covers more than one screenshot/still
6. Check layout alignment:
   - all required elements sit inside platform safe areas and channel-format safe zones
   - repeated elements align to the same grid or deliberate offsets
   - text blocks, source cards, lower thirds, captions, CTAs, and logos do not collide with each other or with the subject of the shot
   - long words, dynamic numbers, source titles, and translated captions fit their containers
   - crops preserve faces, products, UI details, source cards, and evidence-critical regions
7. Check dense regions and overlaps:
   - classify overlaps as `intended_layering`, `acceptable_tightness`, `minor_collision`, `major_collision`, or `blocker_collision`
   - record the timestamp/frame, scene id, layers involved, bounding boxes when available, and screenshot/still path
   - flag visual density when more than one important reading target competes in the same third of the frame, when captions cover key details, or when simultaneous animations make the frame hard to parse
   - prefer moving, scaling, delaying, simplifying, or temporarily hiding nonessential layers over shrinking text below readability
8. Check motion quality and determinism:
   - motion is driven by `useCurrentFrame()` and `useVideoConfig()`, not CSS animation, timers, wall-clock time, render order, or unseeded randomness
   - `interpolate()` ranges are clamped where the value must not drift past the intended range
   - springs and easing curves do not create accidental overshoot, bounce, jitter, or occlusion
   - entry, hold, exit, and transition timing gives viewers enough time to read dense information
   - motion blur, light leaks, particles, camera moves, and text effects support the edit instead of hiding content
9. Repair or replace bad animation:
   - use a targeted edit when the component concept is sound and the defect is timing, easing, scale, z-index, text fit, or asset choice
   - replace the animation route when it is nondeterministic, visibly ugly after two targeted repairs, architecturally brittle, too dense to read, or dependent on unsupported browser/CSS behavior
   - preserve public props, composition id, template contract, and clip package API unless the repair cannot be made safely
   - if the failing layer belongs to a reusable clip/template owned by Remotion Clip Builder, return a Director handoff recommendation instead of editing that agent's internals
10. Check production render risks:
   - local assets use `staticFile()` or approved repo paths; no unapproved remote render-time media
   - fonts are loaded before measurement; font weights/subsets are scoped to what is actually used
   - media tags and decode route are appropriate for frame-accurate rendering
   - alpha exports, blend modes, masks, and subpixel text/line movement survive compression
   - GPU-heavy effects, many DOM nodes, blur/shadow/filter cost, image sequence size, cache, concurrency, SIGKILL risk, and render time are recorded or mitigated
11. Re-run validation after every repair. A fix is not done until the failing frame range and one adjacent frame range pass the same still/browser/short-render checks that exposed the problem and the agent has analyzed the new preview artifacts.
12. Update the render package QA findings, render commands, performance summary, evidence refs, and media manifest actions for every generated still, screenshot, short render, metadata file, preview analysis, or debug report.

## Required Output

Return this summary and copy the useful parts into `render-package.qa.findings[]`, `performance_summary`, and `evidence_refs`:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "composition_id": "string",
  "debug_scope": "changed_frames | full_timeline | scene_subset | clip_preview",
  "scene_sampling_plan": [
    {
      "scene_id": "string",
      "start_frame": 0,
      "end_frame": 0,
      "sampling_fps": 2,
      "sample_interval_frames": 15,
      "sampled_frames": [0],
      "reduced_sampling_reason": "string"
    }
  ],
  "frames_checked": [
    {
      "scene_id": "string",
      "frame": 0,
      "timestamp_seconds": 0,
      "purpose": "entry | midpoint | exit | transition | peak_density | peak_motion | caption_heavy | reported_failure",
      "evidence_path": "string"
    }
  ],
  "browser_preview": {
    "used": false,
    "url_or_command": "string",
    "screenshots": ["string"],
    "console_or_runtime_findings": ["string"],
    "dom_css_analysis_paths": ["string"]
  },
  "browser_dom_css_analysis": {
    "used": false,
    "analyzable_layers": ["string"],
    "pixel_only_layers": ["string"],
    "bbox_findings": ["string"],
    "computed_style_findings": ["string"],
    "limitations": ["string"]
  },
  "agent_preview_analysis": {
    "required": true,
    "artifacts_analyzed": ["string"],
    "sampled_video_frames": [0],
    "visual_observations": ["string"],
    "motion_observations": ["string"],
    "pass_decision": "pass | fail | partial | unknown",
    "analysis_artifact_path": "string"
  },
  "category_results": {
    "agent_preview_analysis": { "status": "pass | fail | partial | unknown", "evidence": "string" },
    "per_scene_sampling_coverage": { "status": "pass | fail | partial | unknown", "evidence": "string" },
    "browser_dom_css_analysis": { "status": "pass | fail | partial | unknown", "evidence": "string" },
    "layout_alignment": { "status": "pass | fail | partial | unknown", "evidence": "string" },
    "dense_region_overlap": { "status": "pass | fail | partial | unknown", "evidence": "string" },
    "text_fit": { "status": "pass | fail | partial | unknown", "evidence": "string" },
    "safe_area": { "status": "pass | fail | partial | unknown", "evidence": "string" },
    "motion_quality": { "status": "pass | fail | partial | unknown", "evidence": "string" },
    "determinism": { "status": "pass | fail | partial | unknown", "evidence": "string" },
    "asset_and_font_loading": { "status": "pass | fail | partial | unknown", "evidence": "string" },
    "render_performance_risk": { "status": "pass | fail | partial | unknown", "evidence": "string" }
  },
  "findings": [
    {
      "severity": "blocker | major | minor | note",
      "scene_id": "string",
      "frame": 0,
      "timestamp_seconds": 0,
      "category": "layout_alignment | dense_region_overlap | text_fit | safe_area | motion_quality | determinism | asset_loading | performance",
      "description": "string",
      "repair": "targeted_edit | replace_animation | route_to_clip_builder | route_to_visual_producer | no_change",
      "fix_status": "fixed | deferred | needs_handoff | blocked"
    }
  ],
  "changed_files": ["string"],
  "commands_or_previews": [
    {
      "purpose": "lint | typecheck | still | short_render | browser_preview | metadata_probe",
      "command_or_url": "string",
      "completed": false,
      "notes": "string"
    }
  ],
  "next_recommended_step": "string"
}
```

## Status Policy

- Return `complete` when visual debugging ran, every scene has 2-3 fps sampling coverage or an approved waiver/blocker, browser DOM/CSS analysis was attempted where available, and all findings have either a fix, a structured handoff, or a recorded blocker.
- Return `needs_revision` when the timeline, props, clip package, template contract, or producer criteria contradict each other.
- Return `needs_approval` when the repair requires paid tools, licensed assets, unapproved web images/screenshots, paid render services, or waiver decisions.
- Return `blocked` when the composition cannot compile, preview, render a still, load required media, or expose enough evidence for reliable judgment.

## Media Manifest Policy

If this skill creates, validates, consumes, or defers preview stills, screenshots, short renders, preview analysis reports, DOM/CSS analysis reports, metadata probes, debug reports, thumbnails, or review evidence, update the media asset manifest or return `manifest_actions[]`.

Use `created` for new still/screenshot/preview artifacts, `validated` for existing evidence used in the debug pass, `deferred` for evidence that could not be generated, and `not_applicable` only when no media artifact was touched.

## Definition Of Done

- Representative stills or browser screenshots cover every changed or suspected frame range.
- Every scene has 2-3 fps sampled-frame analysis, unless the Director explicitly approves reduced sampling or the skill returns a blocker.
- Browser automation analyzes DOM/CSS/SVG layers when available and records pixel-only limits for video/canvas/WebGL/raster layers.
- Preview artifacts are actively analyzed by the agent; existence of a preview file or Studio session is not enough.
- Layout alignment, dense-region overlap, text fit, safe areas, motion quality, deterministic animation, asset/font loading, and render risk are explicitly pass/fail/partial/unknown.
- Broken or ugly motion is fixed, replaced, or routed to the owning agent with a concrete handoff recommendation.
- Dense frames are readable and do not hide captions, source evidence, product/UI details, or viewer-critical visuals.
- The render package records evidence, commands, findings, blockers, and next steps.
