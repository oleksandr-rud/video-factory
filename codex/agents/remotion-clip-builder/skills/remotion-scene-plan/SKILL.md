---
name: remotion-scene-plan
description: Plan deterministic Remotion-generated visuals for 5-20 second scenes or overlays, including layout, components, props, timing, transitions, VFX hooks, and asset needs. Use when a scene is better built with React motion graphics than searched or AI-generated footage.
---

# Remotion Scene Plan

Produce a deterministic implementation plan before coding. Treat this as a low-freedom skill: vague composition ids, frame math, props, or assets should block implementation rather than drift into guesswork.

## Inputs

- Visual Producer scene pack, selected route, visual goal, candidate requirements, source ids, evidence refs, and `remotion_scene_brief`
- Scenario scene with start/end seconds, narration, on-screen text, source alignment, and visual intent
- Director scene artifact sync report when available
- Producer criteria, channel profile, channel format, `visual_system.vfx_rules`, and reusable template hints
- Remotion project contract, template registry, existing template contracts, and shared `remotion/` app constraints
- Media asset manifest with approved source/user/web assets and Remotion public projection paths
- Target platform, aspect ratio, resolution, fps, duration, and safe-area rules

## Workflow

1. Consider `../remotion-template-library/SKILL.md` and the Remotion app template registry before planning a bespoke component when the scene has a reusable pattern, channel reusable asset, or `template_hint`.
2. Verify scene identity before planning props:
   - the scenario scene id, visual scene pack scene id, selected candidate scene id, and sync report scene id must match
   - `scene_index`, scenario timing, `scenario_scene_fingerprint`, `scene_pack_id`, and `scene_visual_pack_id` must be present
   - return `needs_revision` if the visual pack is missing the scene, has duplicate scene packs, has stale fingerprints, or does not expose `prop_requirements`
3. Derive the props schema from the current matching scenario scene plus the current matching scene pack. Do not use old prompt memory, generated component defaults, or another scene's props as truth.
4. Decide the implementation mode: `no_template`, `single_template`, `layered_templates`, `bespoke_component`, `bespoke_vfx`, or `hybrid`.
5. Define the composition id, component path, duration in frames, width, height, fps, and expected output kind.
6. Build a frame timing map. Frame ranges must cover the planned duration without gaps or accidental overlaps unless an overlap is intentional and named.
7. Define a serializable props schema for copy, colors, source ids, claim ids, evidence refs, media asset ids, `staticFile()` paths, safe-area settings, timing, scene duration, and the lineage fields: `scenario_id`, `scenario_path`, `scene_visual_pack_id`, `scene_visual_pack_path`, `scene_pack_id`, `scene_id`, `scene_index`, and `scenario_scene_fingerprint`.
8. For `source_card_recreation`, include claim ids, source title/URL/date, evidence refs, and approved image/screenshot asset ids as props or clip package metadata. Redraw source cards unless direct reuse is approved.
9. Define layout and responsive rules: text fitting, long-word behavior, caption-safe area, lower-third conflicts, platform UI safe areas, and mobile/desktop preview constraints.
10. Define dense-region and overlap rules: intended layer overlaps, forbidden collisions, maximum simultaneous reading targets, subject-preservation zones, source-card/caption/lower-third priority, and the frames most likely to become crowded.
11. Define VFX, transitions, audio-reactive hooks, subtitle-safe areas, alpha/export expectations, motion readability criteria, and fallback behavior. Apply `channel_format.visual_system.vfx_rules`.
12. Choose only necessary libraries; if dependency choice is uncertain, read `../remotion-stack-selection/SKILL.md`.
13. Trigger `../vfx-quality-performance-hardening/SKILL.md` when the scene is media-heavy, GPU-heavy, transparent, reusable, complex VFX, WebGL/Three/Skia, dense, overlap-prone, or channel-format rules require it.
14. Check assets before coding: every source media dependency needs a manifest id, canonical path, rights state, and Remotion public/staticFile projection or an explicit deferred action.
15. Define preview and validation commands: Studio/browser route, still render, short render, typecheck/build command, screenshot review, 2-3 fps sampled-frame inspection, browser DOM/CSS/SVG inspection for inspectable layers, pixel analysis for video/canvas/WebGL/raster layers, dense-frame inspection, and any performance check.
16. Define the expected `remotion-clip-package.schema.json` fields, including scenario/visual-pack lineage, `props_sync`, template ids/contracts, template instances for layered use, output asset ids, `vfx_rule_refs`, `vfx_profile`, QA, and manifest actions.
17. If the planned component should be reusable beyond the current scene, define the expected `remotion-template.schema.json` fields and return a Director-facing recommendation to run template-library work.

## Required Output

Return:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "scene_id": "string",
  "scene_index": 0,
  "scene_pack_id": "string",
  "scene_visual_pack_id": "string",
  "source_scenario_path": "string",
  "source_scene_visual_pack_path": "string",
  "scenario_scene_fingerprint": "string",
  "remotion_scene_plan": {
    "plan_id": "string",
    "implementation_mode": "no_template | single_template | layered_templates | bespoke_component | bespoke_vfx | hybrid",
    "composition_id": "string",
    "component_path": "string",
    "duration_frames": 0,
    "fps": 30,
    "width": 1080,
    "height": 1920,
    "template_id": "string",
    "template_contract_path": "string",
    "props_sync": {
      "status": "synced | stale | partial | blocked | unknown",
      "props_path": "string",
      "prop_requirement_keys": ["string"],
      "missing_prop_keys": ["string"],
      "stale_prop_keys": ["string"]
    },
    "template_instances": [
      {
        "template_id": "string",
        "template_contract_path": "string",
        "layer_role": "background | source_card | overlay | transition | caption_support | foreground"
      }
    ],
    "props_schema": [
      {
        "prop": "string",
        "type": "string",
        "required": true,
        "source": "scenario | visual_pack | scene_artifact_sync | channel_format | media_manifest | producer_criteria | generated",
        "validation": "string"
      }
    ],
    "frame_timing_map": [
      {
        "beat_id": "string",
        "start_frame": 0,
        "end_frame": 0,
        "purpose": "string",
        "component_or_layer": "string",
        "transition_in": "string",
        "transition_out": "string"
      }
    ],
    "asset_requirements": [
      {
        "asset_id": "string",
        "canonical_path": "string",
        "static_file_path": "string",
        "rights_state": "approved | needs_approval | blocked | unknown",
        "required_for": "string"
      }
    ],
    "safe_area_rules": ["string"],
    "dense_region_rules": ["string"],
    "overlap_policy": ["string"],
    "vfx_rule_refs": ["string"],
    "vfx_hardening_required": false,
    "preview_plan": {
      "studio_url_or_command": "string",
      "still_command": "string",
      "short_render_command": "string",
      "sampling_fps": 2,
      "browser_dom_css_analysis": "string",
      "validation_steps": ["string"]
    }
  },
  "validation_summary": {
    "frame_math": "pass | fail | unknown",
    "props_complete": "pass | fail | unknown",
    "props_lineage": "pass | fail | unknown",
    "assets_ready": "pass | partial | fail | unknown",
    "template_fit": "pass | partial | fail | unknown",
    "layout_overlap_risk": "pass | partial | fail | unknown",
    "vfx_complexity": "simple | moderate | high | unknown"
  },
  "next_recommended_step": "string"
}
```

## Contract Fields Populated

- `remotion-clip-package.schema.json`: project/channel fields, scene id, scene index, scenario path/hash, scene visual pack path/id, scene pack id, scenario scene fingerprint, `props_sync`, composition id, component path, template ids/contracts, props, outputs, dependencies, `vfx_rule_refs`, `vfx_profile`, and QA expectations
- `remotion-template.schema.json`: only when recommending or defining a reusable template contract
- `remotion-project.schema.json`: consumes project commands, composition registry, public asset policy, and dependency constraints
- `scene-visual-pack.schema.json`: consumes Remotion route brief and template hints
- `media-asset-manifest.schema.json`: manifest entries or deferred actions for planned/consumed/rendered media

## Status Policy

- Return `complete` when the plan is implementation-ready and all required lineage fields, props, frame ranges, assets, templates, and validation commands are explicit.
- Return `needs_approval` when implementation depends on unapproved source images, licensed assets, paid tools, new dependencies, provider downloads, or rights-sensitive reference use.
- Return `blocked` when frame math cannot fit the scene, required assets are unavailable, the requested effect is not feasible in Remotion, or rights make the route unusable.
- Return `needs_revision` when scene ids, scene indexes, scenario fingerprints, visual-pack lineage, visual goals, props, template hints, source data, safe areas, or channel-format rules are contradictory, stale, or underspecified.

## Evidence Required

Every prop, asset, template, VFX rule, source-card detail, and timing decision must cite an input source: scenario scene, visual pack, scene artifact sync report, channel format, producer criteria, reference analysis, media manifest, Remotion project contract, or explicit Director instruction.

## Media Manifest Policy

If this skill consumes, creates, validates, renders, previews, mirrors, or defers source assets, Remotion public assets, template media, frame stills, clip outputs, transparent overlays, thumbnails, or preview evidence, update the media asset manifest or return `manifest_actions[]`.

Each manifest action must include `action`, `asset_id`, `canonical_path`, `remotion_public_path` and `static_file_path` when relevant, `rights_state`, `technical_metadata_state`, `evidence_refs`, and `reason`.

Use `deferred` for planned assets, missing `staticFile()` projections, preview renders that are not created yet, or clip outputs that will be written by `remotion-vfx-clip`. Remotion Video Producer should receive manifest-backed asset ids or explicit deferred actions.

## Approval And Stop Conditions

Stop before coding when required assets are missing, unapproved, outside allowed paths, or not projectable into Remotion `public/`. Stop before adding new dependencies, paid assets, licensed media, direct screenshot reuse, or complex VFX escalation without Director approval.

## Definition Of Done

- Composition id, dimensions, fps, duration frames, component path, and output kind are explicit.
- Frame timing map covers the full duration.
- Props schema is serializable, complete, and derived from the current scenario scene plus matching scene pack.
- The plan records `scene_index`, `scene_pack_id`, `scene_visual_pack_id`, source artifact paths, and `scenario_scene_fingerprint`.
- Asset needs are manifest-backed or deferred with blockers.
- Template/VFX decisions are routed to the right local skills.
- Preview and validation plan is executable by Remotion Clip Builder.
- Dense-frame and overlap risks are known before implementation starts.

## Handoff Summary Shape

Return:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "artifact_paths": ["string"],
  "changed_files": ["string"],
  "populated_contracts": ["codex/contracts/remotion-clip-package.schema.json", "codex/contracts/remotion-template.schema.json"],
  "manifest_actions": [
    {
      "action": "created | updated | consumed | validated | mirrored_to_remotion_public | deferred | not_applicable",
      "asset_id": "string",
      "canonical_path": "string",
      "remotion_public_path": "string",
      "static_file_path": "string",
      "rights_state": "approved | needs_approval | blocked | unknown",
      "technical_metadata_state": "present | missing | partial | not_applicable",
      "reason": "string"
    }
  ],
  "validation_performed": ["scene lineage", "template fit", "frame math", "props schema", "props lineage", "asset readiness", "safe-area check", "dense-region/overlap risk", "VFX hardening trigger check", "preview plan"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
