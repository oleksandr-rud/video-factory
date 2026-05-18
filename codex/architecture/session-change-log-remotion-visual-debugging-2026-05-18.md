# Session Change Log: Remotion Visual Debugging And QA

Date: 2026-05-18

Workspace: `C:\Users\oleks\Documents\video factory`

Purpose: Compact all changes made in this session into one durable file. This file was created after scanning git status, git diff summaries, targeted hunks, contract validation, and the new skill content.

## Git Evidence

Commands used as evidence:

- `git status --short`
- `git diff --name-status`
- `git diff --stat`
- `git diff --numstat`
- targeted `git diff --unified=0 -- <paths>`
- `git diff --check`
- JSON parse of every `codex/contracts/*.json`

Evidence summary before this compaction file was added:

- 17 tracked files modified.
- 1 new untracked skill folder/file added.
- Tracked diff stat: 185 insertions, 28 deletions across 17 files.
- New skill file: `codex/agents/remotion-video-producer/skills/remotion-visual-debugging/SKILL.md`, 180 lines, 1,912 words, 14,337 characters.
- `git diff --check` reported no whitespace errors. It only reported Git line-ending warnings that LF will be replaced by CRLF when Git touches the files.
- All JSON contract files under `codex/contracts/` parsed successfully with `ConvertFrom-Json`.

This compaction file itself is an additional new file created after the evidence scan:

- `codex/architecture/session-change-log-remotion-visual-debugging-2026-05-18.md`

## Changed Path Map

```text
C:\Users\oleks\Documents\video factory
|-- AGENTS.md
|-- codex
|   |-- agents
|   |   |-- director
|   |   |   `-- skills
|   |   |       |-- autonomous-production-run/SKILL.md
|   |   |       `-- quality-gated-review-loop/SKILL.md
|   |   |-- remotion-clip-builder
|   |   |   |-- AGENT.md
|   |   |   `-- skills
|   |   |       |-- remotion-ai-component-prompt/SKILL.md
|   |   |       |-- remotion-scene-plan/SKILL.md
|   |   |       |-- remotion-vfx-clip/SKILL.md
|   |   |       `-- vfx-quality-performance-hardening/SKILL.md
|   |   `-- remotion-video-producer
|   |       |-- AGENT.md
|   |       `-- skills
|   |           |-- remotion-post-production/SKILL.md
|   |           |-- remotion-visual-debugging/SKILL.md
|   |           |-- render-qa/SKILL.md
|   |           `-- render-release-candidate/SKILL.md
|   |-- architecture
|   |   |-- research-synthesis.md
|   |   `-- session-change-log-remotion-visual-debugging-2026-05-18.md
|   |-- contracts
|   |   |-- media-asset-manifest.schema.json
|   |   |-- remotion-clip-package.schema.json
|   |   `-- render-package.schema.json
|   `-- specs
|       `-- remotion-production-spec.md
```

## Step-by-Step Change Summary

### Step 1: Research And Gap Identification

Files read or checked before editing:

- `AGENTS.md`
- `codex/architecture/research-synthesis.md`
- `codex/specs/remotion-production-spec.md`
- Remotion Clip Builder agent and skills
- Remotion Video Producer agent and skills
- Director run/review-loop skills
- Render and clip package contracts
- Built-in Remotion skill at `C:\Users\oleks\.codex\plugins\cache\openai-curated\remotion\dc902811\skills\remotion\SKILL.md`
- Built-in Remotion rule files for measuring text, measuring DOM nodes, animations, and timing

Research findings applied:

- Remotion Studio supports browser preview and frame scrubbing.
- Remotion CLI and renderer support stills, frame sequences, short renders, and full renders.
- Remotion preview is React/HTML/CSS/SVG in a browser where layers are DOM-backed.
- Video, image, canvas, WebGL, and OffthreadVideo internals are pixel-only evidence, so they require screenshots, stills, or sampled frames.
- Existing repo rules covered render health and VFX performance, but did not require a formal per-scene visual debugging pass, active preview analysis, DOM/CSS inspection, or 2-3 fps scene sampling.

### Step 2: Added New Remotion Visual Debugging Skill

Path:

- `codex/agents/remotion-video-producer/skills/remotion-visual-debugging/SKILL.md`

Change:

- Added a new 180-line local skill.
- Defines when to run visual debugging before render QA.
- Requires loading built-in Remotion best practices and relevant rules as needed.
- Allows `browser:browser` for local Remotion Studio or preview pages.
- States that preview capture is not enough: the agent must inspect and analyze artifacts.
- Establishes debug inputs: Remotion app root, project contract, composition id, timeline source, timeline sync plan, render package, props, scene ranges, producer criteria, channel format, captions, lower thirds, overlays, source cards, visual candidates, clip packages, templates, VFX profiles, manifest, logs, stills, renders, screenshots, and failure reports.
- Adds a per-scene sampling plan:
  - every scene is sampled
  - 2 frames per second by default
  - 3 frames per second for dense, text-heavy, fast-motion, transition-heavy, source-card, caption-heavy, UI/product, or previously failed scenes
  - always include scene starts, midpoints, ends, transition boundaries, caption-heavy frames, peak text density, peak VFX intensity, and reported failure frames
  - return `blocked` or `needs_approval` if full 2-3 fps inspection is too expensive and no Director waiver exists
- Adds browser preview workflow:
  - open Studio or preview URL
  - scrub/navigate to target frames
  - capture screenshots
  - inspect console/runtime errors, loading states, failed assets, font fallbacks, and viewport scaling
  - collect bounding boxes and browser data for `data-vf-role`, `data-scene-id`, `data-layer`, `data-safe-area`, or equivalent markers
- Defines HTML/CSS/DOM versus pixel analysis split:
  - DOM-backed layers: inspect bounding boxes, computed styles, transforms, opacity, z-index, overflow, font metrics, and safe-area intersections
  - raster/video/canvas/WebGL/OffthreadVideo layers: inspect as screenshots, stills, or sampled frames
  - mixed scenes: DOM/CSS analysis for overlays plus pixel analysis for visual media
- Adds agent preview analysis:
  - inspect every still and screenshot
  - inspect preview videos directly when possible, or sample frames
  - inspect 2-3 fps per-scene sample sets
  - compare adjacent frames around transitions and fast motion
  - record visible, hidden, crowded, poor-motion, and post-repair observations
  - write a `preview_analysis` artifact or QA entry for multi-artifact passes
- Adds layout alignment checks:
  - safe areas
  - grid alignment
  - source cards
  - lower thirds
  - captions
  - CTAs
  - logos
  - visual subject preservation
  - long words, dynamic values, translated captions, and source titles
- Adds dense-region and overlap checks:
  - classify overlaps as `intended_layering`, `acceptable_tightness`, `minor_collision`, `major_collision`, or `blocker_collision`
  - record timestamp/frame, scene id, layers, bounding boxes, evidence paths
  - flag competing reading targets and caption coverage over key details
  - prefer moving, scaling, delaying, simplifying, or hiding nonessential layers over unreadably shrinking text
- Adds motion quality and determinism checks:
  - use `useCurrentFrame()` and `useVideoConfig()`
  - avoid CSS animations, timers, wall-clock time, render-order assumptions, and unseeded randomness
  - clamp interpolation where values should not drift
  - check springs/easing for overshoot, bounce, jitter, and occlusion
  - ensure entries, holds, exits, and transitions are readable
- Adds repair/replacement policy:
  - targeted edit for isolated timing/easing/scale/z-index/text-fit/asset issues
  - replace animation when nondeterministic, still ugly after two targeted repairs, brittle, too dense, or dependent on unsupported CSS/browser behavior
  - preserve public props/composition ids/template contracts/clip package APIs unless unsafe
  - hand off to Clip Builder if the defect belongs inside a Clip Builder-owned reusable clip/template
- Adds production render risk checks:
  - `staticFile()` or approved repo paths
  - font loading before measurement
  - media decode route
  - alpha/blend/mask/compression risk
  - GPU-heavy effects, DOM count, blur/shadow/filter cost, image sequences, cache, concurrency, SIGKILL risk, and render time
- Defines required output with:
  - `scene_sampling_plan`
  - `frames_checked`
  - `browser_preview`
  - `browser_dom_css_analysis`
  - `agent_preview_analysis`
  - category results for preview analysis, sampling coverage, DOM/CSS analysis, layout, dense overlap, text fit, safe area, motion, determinism, assets/fonts, and performance risk
  - findings with severity, scene id, frame, timestamp, category, description, repair route, and fix status
  - commands/previews and next step
- Updates status policy, media manifest policy, and definition of done.

### Step 3: Updated Top-Level Agent Instructions

Path:

- `AGENTS.md`

Changes:

- Expanded Remotion Video Producer pipeline output from technical render QA only to include `visual debugging evidence`.
- Added instruction to use `codex/agents/remotion-video-producer/skills/remotion-visual-debugging/SKILL.md` before render QA when scenes changed, frames are dense, overlays/captions/source cards share screen space, or feedback names alignment/overlap/readability/crop/animation defects.
- Added requirement that final QA preserve reproducible still/render/screenshot evidence plus agent-written preview analysis.
- Added explicit rule that preview generation alone is not a pass.
- Added per-scene sampling requirement:
  - 2 fps by default
  - 3 fps for dense/high-motion/problem scenes
- Added browser DOM/CSS/SVG inspection for inspectable Remotion layers.
- Added pixel analysis for video/canvas/WebGL/raster layers.

### Step 4: Updated Director Orchestration

Path:

- `codex/agents/director/skills/autonomous-production-run/SKILL.md`

Changes:

- Inserted Remotion visual debugging before render QA in the phase dependency order.
- Required per-scene sampled-frame analysis at 2 fps by default and 3 fps for dense/high-motion/problem scenes.
- Required browser DOM/CSS/SVG inspection for inspectable Remotion layers when available.
- Updated post-run invalidation rules so timeline, subtitle, audio mix, transition, layout, animation, or export changes invalidate visual debugging, render, and critique.

Path:

- `codex/agents/director/skills/quality-gated-review-loop/SKILL.md`

Changes:

- Updated revision routing for timeline/subtitle/audio/transition/export/technical render findings.
- Added layout alignment, dense-region overlap, and motion readability as findings that rerun Remotion Video Producer visual debugging/render work.
- Added exception: if the defect belongs inside a Remotion Clip Builder-owned clip/template, route it there instead.

### Step 5: Updated Remotion Video Producer Agent

Path:

- `codex/agents/remotion-video-producer/AGENT.md`

Changes:

- Added `skills/remotion-visual-debugging/SKILL.md` to the callable local skill list.
- Added built-in `browser:browser` when a local Remotion Studio or preview page is available.
- Added handoff rule: if visual debugging finds a defect inside a Clip Builder-owned clip/template, return a Director handoff recommendation with scene id, frame/timestamp, evidence paths, failing layer, expected repair, and definition of done.
- Added output expectation for visual debugging evidence covering layout alignment, dense-region overlap, text fit, safe areas, motion quality, and browser/Studio screenshots.
- Added rules to run visual debugging before technical render QA when timeline code changed, the frame is dense, captions/lower thirds/source cards overlap key visuals, motion looks broken, or critique/user feedback names a visual defect.
- Added targeted repair versus animation replacement policy.

### Step 6: Updated Remotion Video Producer Skills

Path:

- `codex/agents/remotion-video-producer/skills/remotion-post-production/SKILL.md`

Changes:

- Added a workflow step to run `../remotion-visual-debugging/SKILL.md` before render QA when timeline has changed, dense overlays are present, captions combine with lower thirds/source cards, or motion/VFX could obscure key visuals.
- Required preview files, stills, and browser screenshots to be inspected and summarized as findings, not merely attached.
- Required each scene to have 2-3 fps sampled-frame analysis.
- Required browser automation to inspect DOM/CSS/SVG layers when Remotion preview exposes them.
- Updated definition of done:
  - every scene has sampled-frame visual analysis at 2-3 fps plus DOM/CSS browser analysis for inspectable layers, or an explicit Director waiver/blocker
  - dense frames have visual debug evidence and agent preview analysis for alignment, overlap, text fit, safe areas, and motion readability

Path:

- `codex/agents/remotion-video-producer/skills/render-qa/SKILL.md`

Changes:

- Added requirement to run `../remotion-visual-debugging/SKILL.md` first when timeline code changed, render includes dense overlays/captions/source cards, preview looks wrong, or user/critic feedback names alignment/overlap/readability/motion defects.
- Replaced the previous VFX-first step with a visual debugging coverage gate before VFX/export/rights/manifest checks.
- Required visual debugging coverage to include:
  - per-scene 2-3 fps sampled frames
  - browser DOM/CSS analysis where available
  - representative stills/screenshots
  - short renders
  - agent preview analysis
  - layout alignment
  - dense-region collisions
  - text fit
  - safe areas
  - crop risk
  - motion quality
  - deterministic animation
  - asset/font loading
  - render performance risks
- Added rule that preview artifact without agent analysis is `partial` at best.
- Added rule that missing per-scene sampling is `fail` unless there is an approved Director waiver or blocker.
- Added QA category results:
  - `agent_preview_analysis`
  - `per_scene_sampling_coverage`
  - `browser_dom_css_analysis`
  - `layout_alignment`
  - `dense_region_overlap`
  - `text_fit`
  - `motion_quality`
  - `browser_preview_evidence`
- Added evidence types:
  - visual debugging report
  - preview still
  - browser screenshot
  - bounding-box inspection output
  - preview analysis report
  - browser DOM/CSS analysis report with bounding boxes and computed styles
- Added media manifest coverage items:
  - preview still
  - browser screenshot
  - short visual debug render
  - debug report
  - preview analysis report
  - browser DOM/CSS analysis report

Path:

- `codex/agents/remotion-video-producer/skills/render-release-candidate/SKILL.md`

Changes:

- Added visual debugging to light validation before full render.
- Required agent analysis of generated preview artifacts.
- Added explicit statement that preview generation alone is not validation.
- Required per-scene 2-3 fps sampled-frame analysis plus browser DOM/CSS inspection for inspectable layers.
- Updated VFX-heavy performance summary language to visually dense or motion-heavy renders, including agent preview analysis, layout/overlap evidence, and browser screenshots.
- Updated `previewed` status policy so it requires analyzed preview artifacts and 2-3 fps scene sampling coverage or a recorded waiver/blocker.

### Step 7: Updated Remotion Clip Builder Agent

Path:

- `codex/agents/remotion-clip-builder/AGENT.md`

Changes:

- Added built-in `browser:browser` for local Studio/preview-based clip layout and motion debugging.
- Added output expectation for layout and motion debug notes covering alignment, dense-region overlap, safe-area conflicts, unreadable text, and broken/ugly animation routes.
- Added rule for dense clips, source cards, captions, lower thirds, UI/product shots, and generated animation repairs to check representative stills or browser/Studio previews for alignment, overlap, safe areas, and motion readability before handoff.
- Added targeted fix versus animation replacement policy for clip work.

### Step 8: Updated Remotion Clip Builder Skills

Path:

- `codex/agents/remotion-clip-builder/skills/remotion-ai-component-prompt/SKILL.md`

Changes:

- Added bounded targeted repair rule for generated components that look broken, crowded, misaligned, or ugly in preview.
- Added replacement rule when generated code remains nondeterministic, unreadable, or brittle after repairs.
- Added debug affordance guidance: stable `data-vf-role`, `data-scene-id`, or `data-layer` attributes on major layers when practical.
- Replaced one-frame validation with still frames at entry, settled, peak-density, peak-motion, and exit frames.
- Added 2-3 fps sampled-frame coverage for generated clip or scene.
- Added browser DOM/CSS/SVG inspection for inspectable layers.
- Added screenshot/pixel analysis for video/canvas/WebGL/raster layers.
- Added dense-region, overlap, text-fit, and safe-area inspection.
- Added agent-written preview analysis from stills, screenshots, sampled frames, or preview video.
- Updated fallback from simpler Remotion-native route to simpler deterministic Remotion-native route or replacement animation.

Path:

- `codex/agents/remotion-clip-builder/skills/remotion-scene-plan/SKILL.md`

Changes:

- Inserted dense-region and overlap planning before VFX planning.
- Required planned rules for:
  - intended layer overlaps
  - forbidden collisions
  - maximum simultaneous reading targets
  - subject-preservation zones
  - source-card/caption/lower-third priority
  - frames most likely to become crowded
- Added motion readability criteria to VFX/fallback planning.
- Expanded VFX hardening trigger to dense and overlap-prone scenes.
- Expanded preview/validation commands to include:
  - Studio/browser route
  - 2-3 fps sampled-frame inspection
  - browser DOM/CSS/SVG inspection for inspectable layers
  - pixel analysis for video/canvas/WebGL/raster layers
  - dense-frame inspection
- Added output fields:
  - `dense_region_rules`
  - `overlap_policy`
  - `preview_plan.sampling_fps`
  - `preview_plan.browser_dom_css_analysis`
  - `validation_summary.layout_overlap_risk`
- Added definition of done that dense-frame and overlap risks are known before implementation starts.
- Added `dense-region/overlap risk` to validation performed list.

Path:

- `codex/agents/remotion-clip-builder/skills/remotion-vfx-clip/SKILL.md`

Changes:

- Replaced minimal preview checks with:
  - still frames for entry, settled, peak-motion, and exit states
  - 2-3 fps sampled-frame coverage across the clip
  - browser/Studio screenshots for fast alignment review
  - one motion preview or full render for complex VFX
- Required the agent to inspect preview artifacts and record preview-analysis findings before accepting a clip.
- Added browser automation inspection for DOM/CSS/SVG layers.
- Added screenshot/sampled-frame pixel analysis for video, image, canvas, WebGL, and OffthreadVideo content.
- Added definition of done checks for:
  - dense frames checked for alignment, unintended overlap, source-card/caption/lower-third conflicts, and readable motion
  - preview artifacts analyzed by the agent and summarized in QA or `vfx_profile.agent_preview_analysis`
  - full clip preview coverage at 2-3 fps unless blocker or Director waiver exists
  - broken/ugly motion repaired, replaced with simpler deterministic route, or blocked with evidence

Path:

- `codex/agents/remotion-clip-builder/skills/vfx-quality-performance-hardening/SKILL.md`

Changes:

- Added Browser/Studio preview guidance for frame scrubbing, screenshots, console inspection, and visual confirmation.
- Stated Browser preview supplements still renders and does not replace renderable evidence.
- Required agent analysis of captured preview artifacts.
- Stated screenshot or preview generation alone is not a pass.
- Added full-clip sampling policy:
  - 2 fps by default
  - 3 fps for dense, caption/source-card-heavy, fast-motion, transition-heavy, or previously failed clips
- Added DOM/CSS/SVG versus pixel evidence rule:
  - browser automation inspects DOM/CSS/SVG layers
  - video/image/canvas/WebGL/OffthreadVideo internals are pixel evidence from screenshots or sampled frames
- Added visual quality checks:
  - alignment of repeated blocks, source cards, lower thirds, captions, CTAs, logos, product/UI details, foreground elements
  - dense-region readability
  - unintended overlap between blocks/captions/subjects/source evidence/VFX overlays
- Added render stability checks:
  - use browser/Studio screenshots for dense scenes and analyze them directly
  - sample short preview videos at 2-3 fps
  - collect DOM bounding boxes, computed styles, transforms, opacity, z-index, overflow, and safe-area intersections for inspectable layers
- Added fallback route for replacement animation when current motion is nondeterministic, ugly, unreadable, or still broken after targeted repairs.
- Extended required output with:
  - `layout_debug_checks`
  - `agent_preview_analysis`
  - `agent_preview_analysis.sampling_fps`
  - `agent_preview_analysis.sampled_frames`
  - `agent_preview_analysis.dom_css_analysis_paths`
  - visual and motion observations
  - pass decision
  - `animation_repair_or_replacement`
- Extended definition of done with alignment, overlap, dense-region readability, text fit, safe areas, motion readability, 2-3 fps coverage, DOM/CSS/SVG inspection, pixel-only screenshot/frame checks, and agent preview analysis.

### Step 9: Updated Contracts

Path:

- `codex/contracts/media-asset-manifest.schema.json`

Changes:

- Added media asset kind `preview_analysis`.
- Added media asset kind `dom_css_analysis`.

Path:

- `codex/contracts/remotion-clip-package.schema.json`

Changes:

- Added `vfx_profile.layout_debug_checks`.
- Added `vfx_profile.agent_preview_analysis` object with:
  - `artifacts_analyzed`
  - `visual_observations`
  - `motion_observations`
  - `pass_decision`
- Added `vfx_profile.animation_repair_or_replacement`.
- Expanded output kind enum:
  - added `debug_screenshot`
  - added `preview_analysis`
  - added `dom_css_analysis`
  - added `debug_report`
- Expanded QA finding fields:
  - `frame`
  - `category`
  - `evidence_path`
  - `recommendation`

Path:

- `codex/contracts/render-package.schema.json`

Changes:

- Expanded output kind enum:
  - added `short_preview`
  - added `still`
  - added `debug_screenshot`
  - added `preview_analysis`
  - added `dom_css_analysis`
  - added `debug_report`
- Expanded QA finding fields:
  - `frame`
  - `category`
  - `evidence_path`
  - `recommendation`

### Step 10: Updated Research And Production Spec

Path:

- `codex/architecture/research-synthesis.md`

Changes:

- Added new section `Remotion Visual Debugging Findings`.
- Recorded that repo needs a visual debugging lane in addition to render health checks.
- Captured research basis:
  - Remotion Studio supports browser preview
  - CLI/renderer paths support still frames and frame sequences
  - Remotion animation docs require frame-driven animation with `useCurrentFrame()`
  - Remotion flickering troubleshooting highlights nondeterminism, asset loading, font loading, media tag, concurrency, and memory risk
  - Remotion layout-utils supports text measurement/fitting
  - Playwright supports screenshots, visual comparisons, and page JavaScript evaluation
- Recorded local decision:
  - add `remotion-visual-debugging` under Remotion Video Producer
  - wire it before render QA for changed/risky scenes
  - update Clip Builder VFX/generation skills for alignment, overlap, dense-region, and animation replacement checks
  - preview artifacts must be analyzed by the agent
  - preview generation only creates evidence, not a pass
  - each scene gets sampled-frame analysis at 2 fps by default or 3 fps for dense/high-motion/problem scenes
  - browser automation inspects DOM/CSS/SVG where Remotion exposes it
  - video/canvas/WebGL/raster content remains pixel evidence from screenshots and sampled frames

Path:

- `codex/specs/remotion-production-spec.md`

Changes:

- Added Visual Debugging to Remotion Video Producer responsibilities.
- Added full `Visual Debugging Baseline` section.
- Required visual debugging whenever code, props, templates, captions, source cards, lower thirds, VFX, transitions, or dense layouts change.
- Added staged evidence loop:
  - static checks
  - representative stills
  - Browser/Studio preview
  - per-scene sampled-frame analysis at 2 fps default and 3 fps for dense/high-risk scenes
  - DOM/CSS/SVG inspection for DOM-backed layers
  - pixel evidence for video/images/canvas/WebGL/OffthreadVideo
  - short low-scale renders for motion issues
  - agent preview analysis
  - reproducible final evidence
- Added visual debugging check categories:
  - alignment
  - dense-region readability
  - unintended overlap
  - text fit
  - motion quality
  - render production risks
- Added overlap classification names and blocker definition.
- Added repair policy:
  - targeted edits for isolated defects
  - replacement for nondeterministic, ugly, too-dense, unsupported, or brittle routes
  - preserve public APIs unless unsafe
  - route Clip Builder-owned template/clip defects back through Director
- Expanded clip package requirements for alignment, dense-region overlap, safe areas, motion quality, and determinism.
- Expanded full render package requirements with visual debugging evidence, agent preview analysis, per-scene 2-3 fps coverage, DOM/CSS reports, and updated QA findings.
- Added Clip visual QA gate for dense/text-heavy/source-card/lower-third/UI/product/caption/VFX-heavy clips.
- Added full-video visual debugging QA gate requiring every scene to have 2-3 fps analysis, Browser DOM/CSS/SVG inspection when available, pixel evidence for pixel-only layers, preview artifact analysis, overlap classification, text/safe-area checks, repair/routing of bad motion, and render-production risk recording.
- Updated Director run implementation to place Remotion visual debugging before render QA.
- Added previous uncovered gap: no explicit visual debugging gate for alignment, dense-region overlaps, browser/Studio preview evidence, and broken animation replacement before render QA.
- Updated gap coverage statement to include `remotion-visual-debugging`.
- Added evidence from current Remotion debugging docs for the new visual debug lane.

### Step 11: Validation

Validation performed:

- Ran `git diff --check`.
  - Result: no whitespace errors.
  - Note: Git reported line-ending warnings that LF will be replaced by CRLF when Git touches the edited files.
- Parsed every JSON schema in `codex/contracts/*.json` with `ConvertFrom-Json`.
  - Result: all contracts parsed successfully.
- Did not run Remotion preview/render.
  - Reason: this session changed instructions, contracts, specs, and agent skill docs, not Remotion app implementation code.

## Final Changed Files List

Files modified before this compaction artifact:

1. `AGENTS.md`
2. `codex/agents/director/skills/autonomous-production-run/SKILL.md`
3. `codex/agents/director/skills/quality-gated-review-loop/SKILL.md`
4. `codex/agents/remotion-clip-builder/AGENT.md`
5. `codex/agents/remotion-clip-builder/skills/remotion-ai-component-prompt/SKILL.md`
6. `codex/agents/remotion-clip-builder/skills/remotion-scene-plan/SKILL.md`
7. `codex/agents/remotion-clip-builder/skills/remotion-vfx-clip/SKILL.md`
8. `codex/agents/remotion-clip-builder/skills/vfx-quality-performance-hardening/SKILL.md`
9. `codex/agents/remotion-video-producer/AGENT.md`
10. `codex/agents/remotion-video-producer/skills/remotion-post-production/SKILL.md`
11. `codex/agents/remotion-video-producer/skills/render-qa/SKILL.md`
12. `codex/agents/remotion-video-producer/skills/render-release-candidate/SKILL.md`
13. `codex/architecture/research-synthesis.md`
14. `codex/contracts/media-asset-manifest.schema.json`
15. `codex/contracts/remotion-clip-package.schema.json`
16. `codex/contracts/render-package.schema.json`
17. `codex/specs/remotion-production-spec.md`
18. `codex/agents/remotion-video-producer/skills/remotion-visual-debugging/SKILL.md`

Compaction artifact added at the end of the session:

19. `codex/architecture/session-change-log-remotion-visual-debugging-2026-05-18.md`

## Follow-Up: Scene, Props, And Visual Pack Sync Hardening

This follow-up was added after the visual debugging compaction when the next issue was identified: scenario scenes, visual scene packs, Remotion props, selected candidates, AI packages, clip packages, and timeline sync could drift because `scene_id` alone was not a strong enough lineage contract.

### Sync Design Change

- Scenario scenes are now the identity source for downstream artifacts.
- Director owns a new `scene-artifact-sync` gate and report contract.
- Visual Producer must produce exactly one current scene pack per scenario scene.
- Scene packs must preserve `scene_index`, scenario timing, scenario fingerprints, and downstream `prop_requirements`.
- InVideo AI Generator and Remotion Clip Builder must consume the current scenario scene plus matching scene pack instead of old memory or generated defaults.
- Remotion clip packages must record scenario/visual-pack lineage and `props_sync`.
- Timeline sync must consume the scene artifact sync report and current props/packages before render work.
- Render QA and Video Critic now treat stale props, stale scene packs, orphaned scene ids, duplicate scene packs, and route/template/media conflicts as delivery blockers unless waived.

### New Files Added

1. `codex/agents/director/skills/scene-artifact-sync/SKILL.md`
2. `codex/agents/director/skills/scene-artifact-sync/scripts/build_scene_artifact_sync_report.py`
3. `codex/contracts/scene-artifact-sync.schema.json`

### Existing Files Updated For Sync

1. `AGENTS.md`
2. `codex/agents/channel-intelligence/scripts/analyze_reference_video.py`
3. `codex/agents/channel-intelligence/scripts/parse_web_content.py`
4. `codex/agents/channel-intelligence/skills/channel-format-synthesis/SKILL.md`
5. `codex/agents/channel-intelligence/skills/channel-profile-management/SKILL.md`
6. `codex/agents/channel-intelligence/skills/reference-video-breakdown/SKILL.md`
7. `codex/agents/channel-intelligence/skills/source-corpus-ingestion/SKILL.md`
8. `codex/agents/channel-intelligence/skills/style-system-extraction/SKILL.md`
9. `codex/agents/director/AGENT.md`
10. `codex/agents/director/skills/autonomous-production-run/SKILL.md`
11. `codex/agents/director/skills/producer-criteria-prompt/SKILL.md`
12. `codex/agents/director/skills/quality-gated-review-loop/SKILL.md`
13. `codex/agents/invideo-ai-generator/AGENT.md`
14. `codex/agents/invideo-ai-generator/skills/ai-video-prompt-builder/SKILL.md`
15. `codex/agents/invideo-ai-generator/skills/generated-clip-qa/SKILL.md`
16. `codex/agents/remotion-clip-builder/AGENT.md`
17. `codex/agents/remotion-clip-builder/skills/remotion-ai-component-prompt/SKILL.md`
18. `codex/agents/remotion-clip-builder/skills/remotion-scene-plan/SKILL.md`
19. `codex/agents/remotion-clip-builder/skills/remotion-stack-selection/SKILL.md`
20. `codex/agents/remotion-clip-builder/skills/remotion-template-library/SKILL.md`
21. `codex/agents/remotion-clip-builder/skills/remotion-vfx-clip/SKILL.md`
22. `codex/agents/remotion-video-producer/AGENT.md`
23. `codex/agents/remotion-video-producer/scripts/build_timeline_sync_plan.py`
24. `codex/agents/remotion-video-producer/skills/render-qa/SKILL.md`
25. `codex/agents/remotion-video-producer/skills/render-release-candidate/SKILL.md`
26. `codex/agents/remotion-video-producer/skills/timeline-sync-plan/SKILL.md`
27. `codex/agents/video-critic/AGENT.md`
28. `codex/agents/video-critic/scripts/prepare_video_review_assets.py`
29. `codex/agents/video-critic/skills/artifact-consistency-audit/SKILL.md`
30. `codex/agents/video-critic/skills/prepare-multimodal-review-package/SKILL.md`
31. `codex/agents/visual-producer/AGENT.md`
32. `codex/agents/visual-producer/skills/clip-candidate-ranking/SKILL.md`
33. `codex/agents/visual-producer/skills/visual-pack-plan/SKILL.md`
34. `codex/agents/visual-producer/skills/visual-validation/SKILL.md`
35. `codex/architecture/agent-responsibility-map.md`
36. `codex/architecture/research-synthesis.md`
37. `codex/contracts/agent-handoff.schema.json`
38. `codex/contracts/ai-video-generation-package.schema.json`
39. `codex/contracts/clip-candidate.schema.json`
40. `codex/contracts/critique-report.schema.json`
41. `codex/contracts/producer-criteria.schema.json`
42. `codex/contracts/production-run.schema.json`
43. `codex/contracts/reference-analysis.schema.json`
44. `codex/contracts/remotion-clip-package.schema.json`
45. `codex/contracts/render-package.schema.json`
46. `codex/contracts/scene-visual-pack.schema.json`
47. `codex/contracts/timeline-sync-plan.schema.json`
48. `codex/contracts/video-project.schema.json`
49. `codex/specs/agent-system-integrated-spec.md`
50. `codex/specs/orchestrator-agent-architecture-spec.md`
51. `codex/specs/project-artifact-structure-spec.md`
52. `codex/specs/remotion-production-spec.md`
53. `codex/specs/video-critique-spec.md`
54. `codex/architecture/session-change-log-remotion-visual-debugging-2026-05-18.md`

### Sync Validation Notes

- `codex/agents/director/skills/scene-artifact-sync/scripts/build_scene_artifact_sync_report.py` creates a JSON report from scenario, visual pack, candidate, AI package, Remotion clip package, and timeline sync artifacts.
- `codex/agents/remotion-video-producer/scripts/build_timeline_sync_plan.py` now requires `--visual-pack` and `--scene-artifact-sync`, carries scene lineage into each timeline scene, and marks failing sync rows as blockers.
- `codex/agents/video-critic/scripts/prepare_video_review_assets.py` now accepts `--scene-artifact-sync` so critic evidence packages can carry the sync report path.
