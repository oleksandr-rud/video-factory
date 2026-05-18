---
name: remotion-template-library
description: Create, update, select, or promote reusable Remotion templates for Video Factory clips. Use when a scene can reuse an existing lower third, caption, source card, transition, overlay, opener, data callout, mockup, thumbnail, or other parameterized Remotion component, or when a finished clip should become a reusable template.
---

# Remotion Template Library

Use this before creating bespoke Remotion code when a reusable pattern might fit. Do not use it to force a template onto a one-off or complex VFX scene. A template is a parameterized Remotion component with a stable composition id, documented props, preview evidence, and a contract matching `codex/contracts/remotion-template.schema.json`.

## Inputs

- Scene visual pack entry, channel format, producer criteria, and any `template_hint`
- Existing Remotion project contract and template registry paths
- Media asset manifest and approved local assets
- Budget/license policy
- Required output contract: usually `codex/contracts/remotion-template.schema.json` for reusable templates and `codex/contracts/remotion-clip-package.schema.json` for scene-specific instances

## Workflow

1. Inspect the shared Remotion app registry, usually `remotion/src/templateRegistry.tsx`, shared contracts under `remotion/templates/`, and any project template contracts under `channels/<channel-slug>/projects/<project-slug>/remotion/templates/`.
2. Select an existing template when it satisfies the scene purpose, aspect ratio, safe-area requirements, alpha needs, dependency policy, and producer criteria.
3. If no existing template fits, design a new template with:
   - stable `template_id` and preview `composition_id`
   - component path under `remotion/src/templates/<category>/`
   - typed props and documented default props
   - deterministic frame math
   - local assets through props and `staticFile()` only when needed
   - safe-area and alpha behavior notes
4. Use `remotion-stack-selection` before adding dependencies or official templates.
5. Implement the reusable component in the shared `remotion/` app unless the Director provided an approved project-specific app.
6. Register template preview compositions in `remotion/src/templateRegistry.tsx` and the Remotion project contract `composition_registry` as `composition_type: "template"`.
7. Write or update a template contract matching `codex/contracts/remotion-template.schema.json`.
8. For a scene-specific use, write a Remotion clip package that references the template via `template_id`, `template_contract_path`, props, render commands, previews, and QA. For layered uses, populate `template_instances[]`.
9. Promote a finished clip into a template only when it is parameterized, reusable beyond one scene, validated, and does not encode one-off project copy as fixed code.

## Reusable Template Categories

- `lower_third`: names, source labels, chapter labels, speaker IDs
- `source_card`: evidence cards, claim receipts, article/video/source citations, and redrawn web-source visuals that cite `claim_ledger[]` / `web_pages[]` evidence
- `caption`: reusable caption blocks, emphasis captions, word-safe caption styles
- `transition`: deterministic wipes, flashes, light leaks, section breaks
- `overlay`: vignettes, grain, glows, focus masks, transparent VFX
- `data_callout`: numeric reveals, comparison chips, simple charts
- `product_mockup` or `phone_mockup`: device/UI presentation shells
- `audio_visualizer`: waveform or spectrum patterns
- `opener`, `title_card`, `thumbnail`, `still`, `scene_shell`, `vfx`, or `other` as needed

## Rules

- Prefer reusing an approved template over generating a new bespoke component.
- Prefer bespoke Remotion code when the visual request is a complex VFX sequence, shader-like effect, custom 3D shot, or unique art direction that does not map cleanly to a reusable template.
- Do not mutate a reusable template in a way that breaks existing clip packages; create a new version or scene-specific instance instead.
- Keep reusable copy and media as props, not hardcoded component internals.
- For parsed web content, keep exact source claim text, source title, URL, date, and evidence refs in props or clip package metadata; use copied page images only when the media manifest records approved reuse.
- Record template ids in the clip package, project index, and run ledger when used.
- Mark paid/pro templates, unclear licenses, remote render-time assets, or new external services as approval blockers.
- Video Producer may consume template-backed clip packages but must not edit this skill's outputs directly; it should request a Director handoff back to Remotion Clip Builder for new or revised templates.

## Required Output

Return either a selected-template decision or a new/updated template contract:

```json
{
  "status": "selected | implemented | needs_approval | blocked",
  "template_id": "string",
  "template_contract_path": "string",
  "template_instances": [
    {
      "template_id": "string",
      "template_contract_path": "string",
      "layer_name": "string"
    }
  ],
  "composition_id": "string",
  "component_paths": ["string"],
  "registry_paths": ["string"],
  "instance_clip_package_path": "string",
  "props_required_for_instance": ["string"],
  "validation": {
    "registry_updated": true,
    "remotion_project_contract_updated": true,
    "preview_attempted": true,
    "clip_package_written": true
  },
  "blockers": ["string"],
  "next_recommended_step": "string"
}
```

## Definition Of Done

- Template has a stable id, composition id, component path, props contract, usage rules, dependencies, safe-area/alpha notes, and QA status.
- The shared Remotion app registry and Remotion project contract point to it.
- A scene instance has a Remotion clip package referencing the template contract.
- The Video Producer can consume the resulting clip package without reading Clip Builder-only skills.

## Media Manifest Policy

If this skill consumes, creates, validates, previews, renders, mirrors, or defers template media dependencies, local assets, preview stills, rendered template instances, thumbnails, transparent overlays, or reusable Remotion outputs, update the media asset manifest or return `manifest_actions[]`.

Each manifest action must include `action`, `asset_id`, `canonical_path`, `remotion_public_path` and `static_file_path` when relevant, `rights_state`, `technical_metadata_state`, and `reason`.

Use `deferred` for templates that declare future assets, missing public projections, preview renders not yet generated, or template instances that will be rendered later. Template contracts and registry entries must not replace manifest provenance for real media files.
