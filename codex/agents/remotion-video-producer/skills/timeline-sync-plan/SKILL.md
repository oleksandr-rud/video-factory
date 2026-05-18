---
name: timeline-sync-plan
description: Build a frame-accurate timeline sync plan that aligns scenario text, voiceover audio, subtitles, Visual Producer-selected candidates, Remotion clips, transitions, and safe-area overlays. Use before Remotion full-video assembly when narration, captions, and visuals must stay synchronized by scene id without letting timeline tooling make hidden creative selections.
---

# Timeline Sync Plan

Load `subtitle-caption-pipeline` and the built-in `remotion:remotion-best-practices` skill when implementing or validating Remotion code. The output must match `codex/contracts/timeline-sync-plan.schema.json` and preserve Visual Producer candidate authority.

## Inputs

- Scenario artifact with stable `scene_id`, narration, timing, on-screen text, and scene notes
- Voiceover package with audio paths, duration, timestamp alignment, caption paths, and TTS status
- Caption JSON/SRT artifacts and safe-area requirements
- Scene visual pack and clip candidates selected by Visual Producer
- Clip candidate ranking summary when available, including primary/fallback decisions
- Remotion clip packages, template contracts, and VFX hardening evidence for selected deterministic clips
- Media asset manifest path and asset ids for local source, generated, Remotion public, caption, and audio files
- Remotion project contract, channel format, producer criteria, export settings, and platform specs

## Workflow

1. Read the scenario, voiceover package, caption artifacts, visual pack, Visual Producer-selected clip candidates, Remotion clip packages, referenced Remotion template contracts, media asset manifest, Remotion project contract, channel format, producer criteria, and export settings.
2. Build one authoritative scene timeline:
   - scene id
   - narration text
   - audio path and duration
   - caption JSON/SRT path and caption time range
   - selected visual candidate, media asset id, `staticFile()` path, or Remotion clip package
   - `selection_authority`, `selection_decision_id`, `selection_status`, `helper_selected`, and `director_review_required`
   - template id/contract path or template layer list when the selected clip package is template-backed
   - VFX rule refs, complexity, performance notes, and fallback expectations from any Remotion clip package `vfx_profile`
   - frame start/end at the target fps
   - overlay, lower-third, CTA, and transition notes
3. Use `../../scripts/build_timeline_sync_plan.py` to create the first JSON plan when the inputs are already structured. Run it in default strict mode unless the Director explicitly requests repair-mode fallback selection with `--allow-repair-default`.
4. Adjust scene timing only when audio duration, captions, or selected clip lengths require it. Preserve scene ids and record any drift from the original scenario timing.
5. Treat Visual Producer selection as authoritative. Do not rank candidate visuals inside timeline sync except in repair mode, and mark any helper-selected visual as `repair_default`.
6. Hand the plan to `remotion-post-production` as the source of truth for `<Sequence>`, `<Series>`, audio placement, captions, and visual layers.
7. QA the plan for missing assets, stale manifest references, scene order, timing drift, caption coverage, selected visual coverage, safe-area conflicts, helper-selected visuals, and duration mismatch.

## Required Output

Return a timeline sync plan with:

```json
{
  "timeline_sync_id": "string",
  "scenario_id": "string",
  "voiceover_id": "string",
  "scene_visual_pack_id": "string",
  "media_asset_manifest_path": "string",
  "remotion_project_contract_path": "string",
  "fps": 30,
  "width": 1080,
  "height": 1920,
  "duration_seconds": 0,
  "scenes": [
    {
      "scene_id": "string",
      "start_seconds": 0,
      "end_seconds": 0,
      "start_frame": 0,
      "end_frame": 0,
      "narration_text": "string",
      "visual_source": {
        "candidate_id": "string",
        "route": "remotion_generated | ai_video_generation | stock_clip | user_supplied_media | approved_web_image | source_card_recreation | unassigned",
        "media_asset_id": "string",
        "remotion_static_file_path": "string",
        "remotion_clip_package_path": "string",
        "ai_video_generation_package_path": "string",
        "selection_authority": "visual-producer | timeline_helper_repair | unknown",
        "selection_decision_id": "string",
        "selection_status": "approved_primary | approved_fallback | missing_selection | repair_default",
        "helper_selected": false,
        "director_review_required": false
      },
      "audio": {
        "voiceover_path": "string",
        "start_seconds": 0,
        "end_seconds": 0,
        "duration_seconds": 0
      },
      "captions": {
        "caption_json_path": "string",
        "srt_path": "string",
        "start_ms": 0,
        "end_ms": 0,
        "safe_area_notes": "string"
      },
      "transition_in": "string",
      "transition_out": "string",
      "sync_notes": "string"
    }
  ],
  "manifest_actions": [],
  "qa": {
    "status": "pass | fail | partial | not_run",
    "summary": "string",
    "findings": []
  }
}
```

## Contract Fields Populated

- `timeline-sync-plan.schema.json`: `timeline_sync_id`, `scenario_id`, project/channel paths when available, `media_asset_manifest_path`, `remotion_project_contract_path`, `voiceover_id`, `scene_visual_pack_id`, `fps`, `width`, `height`, `duration_seconds`, `scenes[]`, and `qa`
- `timeline-sync-plan.schema.json` scene objects: `visual_source`, `audio`, `captions`, transition fields, and sync notes
- `media-asset-manifest.schema.json`: consumed or deferred entries for local visuals, Remotion public projections, voiceover audio, captions, subtitles, thumbnails, and metadata when touched
- `agent-handoff.schema.json`: Director-facing repair recommendations only when another agent must fix missing visuals, audio, captions, or assets

## Status Policy

- Return `pass` only when every scene has Visual Producer-selected visual coverage, usable audio timing, caption timing or an approved no-caption exception, valid frame ranges, and no helper-selected visual.
- Return `partial` when repair-mode fallback was used, fallback visual selection is used instead of primary, caption/audio coverage is incomplete but repairable, or non-blocking timing drift needs review.
- Return `fail` when any scene lacks selected visual coverage in strict mode, depends on remote media without Director approval, has unusable audio/caption timing, references missing required assets, or has a selected visual with blocking rights/technical status.
- Return `not_run` only when required inputs are missing before timeline construction starts.

- Use voiceover duration and caption timestamps as stronger timing evidence than estimated script duration.
- Keep captions, lower thirds, product/UI details, logos, and CTA text from occupying the same safe area.
- Mark the plan failed in strict mode if any scene has no Visual Producer-selected candidate.
- Mark the plan partial if repair mode selects a `repair_default` visual; this is not render-ready until the Director reviews it.
- Mark a plan partial if any scene has no audio path after approved TTS generation or no caption timing source.
- Mark a plan partial if a template-backed clip references a missing template contract or a template with failed QA.
- Mark a plan partial if a complex VFX clip has failed or missing hardening evidence and the scene depends on that effect.
- Mark a plan partial if channel-format VFX rules require hardening, benchmark evidence, alpha/export behavior, or fallback coverage that is missing from the relevant clip package.
- Do not use remote media paths for final render unless the Director explicitly accepts that risk.

## Evidence Required

For every scene, cite or preserve:

- scenario scene id and narration source
- audio path, duration source, caption path, and timestamp source
- selected `candidate_id` plus Visual Producer decision evidence
- media asset id, local path, Remotion `staticFile()` path, or Remotion clip package path when media is used
- for `approved_web_image`, the manifest entry must show rights approval and a local/render-visible path before final render
- for `source_card_recreation`, preserve source ids, claim/evidence refs, and source-card/template contract paths
- template contract paths and VFX hardening evidence for template-backed or VFX-heavy clips
- timing drift reason when scene duration changes from scenario estimates
- safe-area notes for captions, lower thirds, UI details, logos, and CTAs

Missing evidence must become a QA finding; do not bury it in prose.

## Media Manifest Policy

If this skill consumes, validates, mirrors, or defers any real media artifact, return `manifest_actions[]`:

```json
{
  "action": "created | updated | consumed | validated | mirrored_to_remotion_public | deferred | not_applicable",
  "asset_id": "string",
  "canonical_path": "string",
  "remotion_public_path": "string",
  "static_file_path": "string",
  "rights_state": "approved | needs_approval | blocked | unknown",
  "technical_metadata_state": "present | missing | partial",
  "reason": "string"
}
```

Use `consumed` for selected candidate media, voiceover audio, caption files, and Remotion clip outputs already in the manifest. Use `deferred` when a needed local file or asset id is missing. Use `not_applicable` only when no media artifact exists yet.

## Approval And Stop Conditions

Stop and return `fail` or `not_run` when:

- the scenario has no stable scene ids
- strict mode has no Visual Producer-selected candidate for any required scene
- a selected candidate has unresolved rights or technical blockers
- required local media is missing from the manifest and no Director waiver exists
- audio or caption timing cannot be aligned to the scene
- a template-backed clip lacks a required template contract

Only use repair mode when the Director explicitly accepts `--allow-repair-default`. Repair-mode output must require Director review before rendering.

## Definition Of Done

- Every scene has frame-accurate start/end values and synchronized audio/caption ranges.
- Every visual source identifies its candidate, route, authority, decision id when available, status, and review requirement.
- Timeline sync did not silently rank visuals; any helper choice is marked `repair_default`.
- Every local media artifact touched is covered by `manifest_actions[]`.
- QA findings are structured enough for Director rerouting.
- `remotion-post-production` can build the full composition from the plan without rereading candidate-ranking prose.

## Handoff Summary Shape

Return:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "artifact_paths": ["string"],
  "changed_files": ["string"],
  "populated_contracts": ["codex/contracts/timeline-sync-plan.schema.json"],
  "manifest_actions": [
    {
      "action": "created | updated | consumed | validated | mirrored_to_remotion_public | deferred | not_applicable",
      "asset_id": "string",
      "reason": "string"
    }
  ],
  "validation_performed": ["scene order", "frame ranges", "voice timing", "caption timing", "visual authority", "asset coverage", "safe areas"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
