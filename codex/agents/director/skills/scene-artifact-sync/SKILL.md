---
name: scene-artifact-sync
description: Validate and repair routing for scenario scenes, visual scene packs, Remotion props, clip packages, AI generation packages, selected candidates, and timeline sync plans so every downstream artifact stays one-to-one with stable scene ids and current source inputs.
---

# Scene Artifact Sync

Use this after scenario creation, after visual pack generation, before specialist handoffs, before timeline sync, and after any user change that touches scenes, narration, visual intent, route selection, props, templates, or selected media. This is a Director-owned gate because it crosses agent boundaries.

The purpose is to stop drift. Scenario scenes are the identity source. Visual packs, visual candidates, Remotion props, clip packages, AI generation packages, and timeline sync plans must derive from those scene ids instead of creating new hidden scene structures.

## Inputs

- Scenario artifact path and current scenario object
- Scene visual pack path and object when available
- Clip candidate ranking and selected visual candidates when available
- Remotion clip package paths and props paths when available
- AI video generation package paths when available
- Timeline sync plan path when available
- Voiceover package and caption artifacts when timing matters
- Producer criteria, channel format, media asset manifest, Remotion project contract, and project index
- Change request or critique finding when this is a repair pass

## Workflow

1. When artifacts already exist as JSON files, prefer the helper script:
   - Use the artifact flags the script supports; omit flags for downstream artifacts that do not exist yet.
   - Typical command: `python codex/agents/director/skills/scene-artifact-sync/scripts/build_scene_artifact_sync_report.py --scenario <scenario.json> --visual-pack <scene-visual-pack.json> --clip-candidates <clip-candidates.json> --remotion-clip-package <clip-package.json> --ai-video-generation-package <ai-package.json> --timeline-sync-plan <timeline-sync-plan.json> --output <scene-artifact-sync.json>`.
   - If some downstream artifacts do not exist yet, omit those optional flags and treat the result as a phase-appropriate partial pass.
2. Build the authoritative scenario scene index:
   - `scene_id`
   - `scene_index`
   - `start_seconds`, `end_seconds`, and duration
   - script/narration text
   - `onscreen_text`
   - `visual_intent`
   - `reference_use_policy`, `target_content_substitution`, and `source_ids`
   - a lightweight `scene_fingerprint` made from scene id, timing, script, on-screen text, visual intent, source ids, and format notes
3. Validate scene ids:
   - scene ids are unique in scenario
   - visual pack has exactly one scene pack for every scenario scene
   - no extra scene packs exist without an explicit `orphaned_by_change` status
   - candidate selections, Remotion clip packages, AI generation packages, voiceover entries, caption ranges, and timeline sync scenes use known scenario scene ids
4. Validate ordering and timing:
   - visual pack scene order follows scenario order
   - scene pack timing mirrors scenario timing unless a recorded timing adjustment exists
   - timeline sync frame ranges preserve scene order and cover the expected duration without accidental gaps or overlaps
   - voiceover/caption ranges map to the same scene ids
5. Validate visual pack lineage:
   - `scene_visual_pack.scenario_id` matches scenario
   - `source_scenario_path`, `source_scenario_hash`, or equivalent lineage fields are current when present
   - every scene pack records its `scene_index`, scenario timing, scene fingerprint, and scenario-derived prop requirements
   - route decisions, candidate requirements, template hints, source ids, and Remotion briefs cite scenario fields or evidence refs
6. Validate prop lineage:
   - every Remotion props file or inline props summary identifies `scenario_id`, `scene_id`, `scene_visual_pack_id`, and source artifact paths
   - props values for narration/on-screen text/source ids/claim ids/media ids/staticFile paths match the current scenario and scene visual pack
   - props do not contain stale scene copy, old visual goals, old template ids, or unselected media from a previous scene version
   - reusable template props are instance-specific; do not mutate template defaults to carry one scene's values
7. Validate specialist package alignment:
   - every Remotion clip package has the same scene id as the scene pack that requested it
   - every AI generation package has the same scene id as the scene pack that requested it
   - selected visual candidates are selected by Visual Producer, not helper-selected downstream, unless repair mode and Director review are explicit
   - fallback packages remain marked fallback and cannot silently replace the primary route
8. Decide sync status per scene:
   - `synced`: current and one-to-one
   - `missing_downstream`: scenario scene exists but visual pack, candidate, props, clip, AI package, voice/caption, or timeline data is missing
   - `stale_downstream`: downstream artifact fingerprint/path/hash does not match current scenario or visual pack
   - `orphaned_downstream`: downstream artifact references a scene id that is no longer in the scenario
   - `conflicting_routes`: visual pack, candidate, props, clip package, or timeline disagree about route/template/media
   - `needs_director_decision`: multiple valid repairs exist or a waiver/approval is needed
9. Produce repair routing, not hidden edits:
   - scenario/content mismatch: rerun Creative Producer then Visual Producer and downstream dependents
   - visual pack missing/stale: rerun Visual Producer for affected scene ids
   - Remotion props/clip stale: rerun Remotion Clip Builder for affected scene ids with current scenario scene and scene pack
   - AI package stale: rerun InVideo AI Generator for affected scene ids
   - selected media/candidate mismatch: rerun Visual Producer validation/ranking
   - timeline mismatch only: rerun Remotion Video Producer timeline sync
10. Update project/run state with the sync report path and invalidated artifacts. Do not let downstream work proceed while any required scene is `missing_downstream`, `stale_downstream`, `orphaned_downstream`, or `conflicting_routes` unless the Director records a waiver.

## Required Output

Return a sync report matching `codex/contracts/scene-artifact-sync.schema.json`. Store it under the project folder, for example `channels/<channel-slug>/projects/<project-slug>/runs/<run-id>/scene-artifact-sync.json`:

```json
{
  "sync_report_id": "string",
  "status": "pass | fail | partial | not_run",
  "scenario_id": "string",
  "scenario_path": "string",
  "scenario_hash": "string",
  "scene_visual_pack_id": "string",
  "scene_visual_pack_path": "string",
  "scene_visual_pack_hash": "string",
  "checked_artifacts": ["string"],
  "scene_index": [
    {
      "scene_id": "string",
      "scene_index": 0,
      "start_seconds": 0,
      "end_seconds": 0,
      "scene_fingerprint": "string",
      "scene_pack_id": "string",
      "scene_pack_fingerprint": "string",
      "sync_status": "synced | missing_downstream | stale_downstream | orphaned_downstream | conflicting_routes | needs_director_decision",
      "visual_pack_status": "pass | fail | partial | unknown",
      "props_status": "pass | fail | partial | unknown",
      "candidate_status": "pass | fail | partial | unknown",
      "clip_package_status": "pass | fail | partial | unknown",
      "ai_package_status": "pass | fail | partial | unknown",
      "timeline_status": "pass | fail | partial | unknown",
      "findings": ["string"],
      "repair_owner": "director | creative-producer | visual-producer | invideo-ai-generator | remotion-clip-builder | remotion-video-producer | none",
      "repair_action": "string"
    }
  ],
  "orphaned_artifacts": ["string"],
  "invalidated_artifacts": ["string"],
  "preserved_artifacts": ["string"],
  "handoff_recommendations": [],
  "next_recommended_step": "string"
}
```

## Status Policy

- Return `pass` only when every required scenario scene is one-to-one across available downstream artifacts and no stale/orphaned/conflicting route exists.
- Return `partial` when early phases do not yet have downstream artifacts, but all existing artifacts are current and the missing artifacts are expected next steps.
- Return `fail` when any required downstream artifact is stale, orphaned, extra, missing after its phase should have produced it, or route/props/media/template values conflict.
- Return `not_run` when no scenario artifact exists.

## Definition Of Done

- Every downstream artifact is traceable to a current scenario scene id.
- Visual pack scene packs are one-to-one with scenario scenes before specialist handoffs.
- Remotion props and clip packages are traceable to the current scene pack and current scenario scene.
- Timeline sync does not consume stale props, stale clip packages, helper-selected visuals, or orphaned scene ids.
- Repair routing is explicit and owned by the correct production agent.
