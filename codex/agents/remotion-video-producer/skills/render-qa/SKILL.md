---
name: render-qa
description: Inspect a video preview, VFX clip, subtitle track, render release candidate, or final render for technical correctness against scenario, voiceover, selected visual candidates, manifest coverage, template contracts, rights notes, and export requirements. Use for technical render QA before independent Video Critic release review.
---

# Render QA

This is a technical QA gate only. It does not approve final viewer-facing release quality. Video Critic and Director own release approval or waiver decisions.

Run `../remotion-visual-debugging/SKILL.md` first when timeline code changed, the render includes dense overlays/captions/source cards, a preview looks visually wrong, or a user/critic report names alignment, overlap, readability, or motion defects.

## Inputs

- Render package matching `codex/contracts/render-package.schema.json`
- Rendered video, preview video, subtitle files, caption JSON, audio outputs, thumbnails, metadata, and QA reports
- Scenario, voiceover package, timeline sync plan, selected visual candidates, Remotion clip packages, and Remotion template contracts
- Remotion project contract, channel format, producer criteria, platform/export requirements, rights notes, and approval records
- Media asset manifest with source, parsed web, approved web image/screenshot, generated, Remotion public projection, render, subtitle, thumbnail, and review assets
- Render logs, ffprobe/metadata output, screenshot/frame evidence, or Remotion preview evidence when available

## Workflow

1. Confirm render identity: `render_id`, `scenario_id`, `composition_id`, render status, output paths, render commands, and version/RC notes.
2. Verify render health: output file exists, command completed or failure is recorded, file is playable/probeable, no missing assets or broken paths.
3. Check duration and scene timing against scenario and timeline sync plan.
4. Check selected visual candidate usage by scene. Flag any unapproved helper-selected or untraceable visual source.
5. Check audio sync, voiceover presence, silence, clipping, loudness notes, pronunciation blockers, and audio mix paths.
6. Check caption sync, caption artifact presence, safe area, burned-in/separate subtitle requirements, and text legibility.
7. Check visual debugging coverage: per-scene 2-3 fps sampled frames, browser DOM/CSS analysis where available, representative stills/screenshots, short renders, agent preview analysis, layout alignment, dense-region collisions, text fit, safe areas, crop risk, motion quality, deterministic animation, asset/font loading, and render performance risks. A preview artifact without agent analysis is `partial` at best. Missing per-scene sampling is `fail` unless there is an approved Director waiver or a blocker.
8. Check VFX, transitions, alpha/export behavior, template contracts, template props, safe areas, deterministic motion, and VFX hardening evidence.
9. Check export settings: platform, aspect ratio, width, height, fps, codec, alpha codec when relevant, delivery variants, and metadata.
10. Check rights and approvals for stock media, approved web images/screenshots, source-card recreated page material, generated clips, music, voices, logos, likeness, paid templates, and external provider use.
11. Check media manifest coverage for every source, web snapshot/source report/web image/screenshot, local Remotion projection, render output, subtitle/caption output, thumbnail, metadata file, preview still/screenshot, debug report, and review-prep artifact.
12. Update render package `qa` and `known_blockers`; do not set release approval.

## Required Output

Update `codex/contracts/render-package.schema.json`:

- `status`
- `outputs[]`
- `output_asset_ids`
- `render_commands[]`
- `subtitles`
- `audio_mix`
- `performance_summary`
- `rights_notes`
- `evidence_refs`
- `known_blockers`
- `qa.status`
- `qa.summary`
- `qa.findings[]`

Return this QA summary:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "render_id": "string",
  "technical_gate": "pass | fail | partial | unknown",
  "release_approval": "not_applicable",
  "category_results": {
    "render_health": { "status": "pass | fail | partial | unknown", "evidence": "string" },
    "duration_match": { "status": "pass | fail | partial | unknown", "evidence": "string" },
    "scene_timing": { "status": "pass | fail | partial | unknown", "evidence": "string" },
    "asset_availability": { "status": "pass | fail | partial | unknown", "evidence": "string" },
    "audio_sync": { "status": "pass | fail | partial | unknown", "evidence": "string" },
    "caption_sync": { "status": "pass | fail | partial | unknown", "evidence": "string" },
    "caption_safe_area": { "status": "pass | fail | partial | unknown", "evidence": "string" },
    "agent_preview_analysis": { "status": "pass | fail | partial | unknown", "evidence": "string" },
    "per_scene_sampling_coverage": { "status": "pass | fail | partial | unknown", "evidence": "string" },
    "browser_dom_css_analysis": { "status": "pass | fail | partial | unknown", "evidence": "string" },
    "layout_alignment": { "status": "pass | fail | partial | unknown", "evidence": "string" },
    "dense_region_overlap": { "status": "pass | fail | partial | unknown", "evidence": "string" },
    "text_fit": { "status": "pass | fail | partial | unknown", "evidence": "string" },
    "motion_quality": { "status": "pass | fail | partial | unknown", "evidence": "string" },
    "browser_preview_evidence": { "status": "pass | fail | partial | unknown", "evidence": "string" },
    "visual_candidate_usage": { "status": "pass | fail | partial | unknown", "evidence": "string" },
    "export_settings": { "status": "pass | fail | partial | unknown", "evidence": "string" },
    "metadata_validation": { "status": "pass | fail | partial | unknown", "evidence": "string" },
    "rights_and_approvals": { "status": "pass | fail | needs_approval | unknown", "evidence": "string" },
    "manifest_coverage": { "status": "pass | fail | partial | unknown", "evidence": "string" }
  },
  "findings": [
    {
      "severity": "blocker | major | minor | note",
      "scene_id": "string",
      "timestamp_seconds": 0,
      "category": "string",
      "description": "string",
      "recommendation": "string",
      "fix_status": "string"
    }
  ],
  "next_recommended_step": "string"
}
```

## Contract Fields Populated

- `render-package.schema.json`: technical QA fields, outputs, commands, performance summary, rights notes, known blockers
- `media-asset-manifest.schema.json`: render/subtitle/thumbnail/metadata/review-prep coverage checks and any missing asset findings
- `critique-report.schema.json`: not populated directly; render QA evidence is handed to Video Critic as input

## Status Policy

- Return `complete` when technical QA is performed and render package QA is updated, even if QA fails.
- Return `needs_approval` when rights, paid media, voice, likeness, cloud review, or waiver decisions are needed.
- Return `blocked` when the render cannot be inspected, required outputs are missing, or a technical issue prevents reliable critique.
- Return `needs_revision` when timeline/render inputs are stale or contradictory.
- Set render package `qa.status` to `pass`, `partial`, `fail`, or `not_run`; never use this as final release approval.

## Evidence Required

Each QA result must cite at least one of:

- render output path
- render command/log
- ffprobe or metadata path
- screenshot/frame timestamp
- visual debugging report, preview still, browser screenshot, or bounding-box inspection output
- preview analysis report written after the agent inspected stills, screenshots, sampled frames, or short preview video
- browser DOM/CSS analysis report, including bounding boxes and computed styles for inspectable layers
- timeline sync scene/frame range
- caption JSON/SRT path
- voiceover/audio path
- clip candidate or Remotion clip package path
- template contract path
- web source report path, claim id, or evidence ref for source-card recreations
- media asset id
- approval/right note

Unknowns must be recorded as `unknown` or `partial`, not pass.

## Media Manifest Policy

For every real media artifact touched by render QA, verify or update `media-asset-manifest.schema.json`:

- rendered video or preview
- preview still, browser screenshot, short visual debug render, or debug report
- preview analysis report
- browser DOM/CSS analysis report
- subtitle SRT
- caption JSON
- audio output
- thumbnail
- metadata/probe output
- review-prep frame or package when already created
- Remotion public projection used by the render
- web snapshots, source reports, approved web images, or screenshots used by selected visuals

Return `manifest_actions[]` with `updated`, `created`, `deferred`, or `not_applicable`. Missing manifest entries that affect render reproducibility are technical QA findings.

## Approval And Stop Conditions

Stop and return `needs_approval` when QA discovers unapproved paid media, licensed downloads, paid templates, generated media, web image/screenshot reuse, voice/likeness risk, or release-waiver needs.

Stop and return `blocked` when:

- render output is missing or unreadable
- required subtitle/caption/audio artifacts are missing for the requested delivery
- selected visuals cannot be traced to approved candidates or clip packages
- manifest gaps prevent provenance or rights validation
- render inputs are stale relative to scenario, timeline sync, or voiceover

## Definition Of Done

- Render package QA is updated with category-backed findings.
- Every blocking technical issue has owner/fix guidance.
- Manifest coverage is checked for render, subtitles, captions, thumbnails, metadata, and Remotion public assets.
- Candidate/template provenance is traceable by scene.
- The result is ready for Video Critic input or clearly blocked.
- No final release approval is claimed.

## Handoff Summary Shape

Return:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "artifact_paths": ["string"],
  "changed_files": ["string"],
  "populated_contracts": ["codex/contracts/render-package.schema.json"],
  "manifest_actions": [
    {
      "action": "created | updated | not_applicable | deferred",
      "asset_id": "string",
      "reason": "string"
    }
  ],
  "validation_performed": ["render health", "duration match", "scene timing", "asset availability", "audio sync", "caption sync", "caption safe area", "visual candidate usage", "export settings", "metadata validation", "rights and approvals", "manifest coverage"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
