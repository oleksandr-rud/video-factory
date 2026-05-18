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
8. For a scene-specific use, write a Remotion clip package that references the template via `template_id`, `template_contract_path`, scene lineage, `props_sync`, props, render commands, previews, and QA. For layered uses, populate `template_instances[]`.
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

## Contract Fields Populated

- `remotion-template.schema.json`: template id, version, status, category, owner, component paths, composition id, props contract, usage rules, dependencies, source, previews, render commands, known instances, and QA
- `remotion-project.schema.json`: `template_registry_paths`, `template_contract_paths`, and `composition_registry[]` entries for template preview compositions
- `remotion-clip-package.schema.json`: scene lineage, `props_sync`, `template_id`, `template_contract_path`, `template_instances[]`, instance props, component paths, render commands, preview frames, output asset ids, and QA for scene-specific use
- `media-asset-manifest.schema.json`: template media dependencies, preview stills, rendered template instances, thumbnails, transparent overlays, and deferred asset needs
- `video-project.schema.json` and `production-run.schema.json`: template contract paths and changed artifact references when available

## Status Policy

- Return `selected` when an existing template satisfies the scene purpose, producer criteria, aspect ratio, safe areas, alpha needs, dependency policy, and manifest requirements.
- Return `implemented` when a new or revised template is registered, contract-backed, project-contract-aligned, and ready for scene instances.
- Return `needs_approval` when the template uses paid/pro templates, licensed assets, unclear licenses, new external dependencies, direct source screenshots, or provider media outside approved scope.
- Return `blocked` when no template fits, required assets are unavailable, the registry/project contract cannot be aligned, or a breaking template change would invalidate existing clip packages.
- Return `needs_revision` when props, usage rules, registry entries, preview evidence, project contract entries, or clip package references are incomplete.

## Evidence Required

Every selected, created, revised, or promoted template must cite the scene brief, channel format rule, producer criteria rule, existing registry entry, source clip package, media asset id, or explicit Director instruction that justifies the template decision. Every registry/project/clip-package update must list the exact file path changed or deferred.

## Approval And Stop Conditions

Stop before using paid/pro templates, licensed media, unapproved source screenshots, new external services, or new dependencies without Director approval. Stop before mutating an existing template in a breaking way; create a new template version or scene-specific instance instead. Stop if `remotion-project.schema.json`, the template registry, the template contract, and any clip package references cannot be kept aligned in the same handoff.

## Definition Of Done

- Template has a stable id, composition id, component path, props contract, usage rules, dependencies, safe-area/alpha notes, and QA status.
- The shared Remotion app registry and Remotion project contract point to it.
- A scene instance has a Remotion clip package referencing the template contract.
- The Video Producer can consume the resulting clip package without reading Clip Builder-only skills.

## Media Manifest Policy

If this skill consumes, creates, validates, previews, renders, mirrors, or defers template media dependencies, local assets, preview stills, rendered template instances, thumbnails, transparent overlays, or reusable Remotion outputs, update the media asset manifest or return `manifest_actions[]`.

Each manifest action must include `action`, `asset_id`, `canonical_path`, `remotion_public_path` and `static_file_path` when relevant, `rights_state`, `technical_metadata_state`, `evidence_refs`, and `reason`.

Use `deferred` for templates that declare future assets, missing public projections, preview renders not yet generated, or template instances that will be rendered later. Template contracts and registry entries must not replace manifest provenance for real media files.

## Handoff Summary Shape

Return:

```json
{
  "status": "selected | implemented | needs_approval | blocked | needs_revision",
  "artifact_paths": ["string"],
  "changed_files": ["string"],
  "populated_contracts": [
    "codex/contracts/remotion-template.schema.json",
    "codex/contracts/remotion-project.schema.json",
    "codex/contracts/remotion-clip-package.schema.json"
  ],
  "template_alignment": {
    "template_contract_path": "string",
    "template_registry_path": "string",
    "remotion_project_contract_path": "string",
    "instance_clip_package_path": "string",
    "registry_updated": false,
    "project_contract_updated": false,
    "clip_package_references_template": false
  },
  "manifest_actions": [
    {
      "action": "created | updated | consumed | validated | mirrored_to_remotion_public | deferred | not_applicable",
      "asset_id": "string",
      "canonical_path": "string",
      "remotion_public_path": "string",
      "static_file_path": "string",
      "rights_state": "approved | needs_approval | blocked | unknown",
      "technical_metadata_state": "present | missing | partial | not_applicable",
      "evidence_refs": ["string"],
      "reason": "string"
    }
  ],
  "validation_performed": ["template fit", "scene lineage", "props sync", "props contract", "registry alignment", "project contract alignment", "clip package reference", "manifest coverage"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
