---
name: remotion-stack-selection
description: Choose Remotion-native templates, packages, component primitives, and VFX helpers with dependency guardrails, version/license checks, fallback plans, rejected alternatives, and definition-of-done validation. Use before adding Remotion dependencies for subtitles, 3D, Lottie, Rive, Skia, transitions, motion blur, audio visualization, transparent overlays, captions, or render tooling.
---

# Remotion Stack Selection

Read `../../references/remotion-component-stack.md` before adding a dependency, template, or component primitive.

Treat dependency choice like production change control. Prefer small, reversible, local, Remotion-native choices. Do not add shared dependencies, paid templates, runtime network paths, or generic web UI libraries without a recorded reason and Director approval where required.

## Inputs

- Scene visual brief, target route, duration, fps, width, height, aspect ratio, alpha needs, and VFX requirements
- Existing Remotion project contract, app root, version, dependency list, and public asset policy
- Approved asset paths, template hints, package policy, and budget/license policy
- Required output contract: usually `codex/contracts/remotion-clip-package.schema.json`, or `codex/contracts/remotion-template.schema.json` when selecting or creating reusable templates

## Workflow

1. Check the reusable template registry only when a reusable pattern might fit. Bespoke Remotion code is acceptable for complex VFX, one-off scene language, or effects that would become worse if forced into a template.
2. Start with core Remotion primitives. Add packages only when they reduce real complexity or unlock required video functionality.
3. Check the current `remotion` package version before recommending `@remotion/*` dependencies. Keep Remotion packages on the same exact version.
4. Prefer local assets and deterministic rendering. Avoid runtime network dependencies.
5. Record rejected alternatives so future agents do not repeat the same dependency debate.
6. Mark paid/pro templates, unclear licenses, unsupported package versions, or risky shared dependencies as approval/blockers.
7. Define a fallback that works with core Remotion, CSS, SVG, Canvas, or simpler motion if the selected package fails.

Default choices:

1. Use core Remotion first: `AbsoluteFill`, `Sequence`, `Series`, `interpolate`, `spring`, `Audio`, `OffthreadVideo`, `Img`, `staticFile`, and typed props.
2. Choose an official Remotion template when a project shape already matches the job: Blank, Hello World, Prompt to Motion Graphics SaaS, 3D, Audiogram, Music Visualization, Prompt to Video, Skia, Overlay, Code Hike, Stargazer, TikTok, or render server templates.
3. Use `@remotion/captions` for caption parsing, TikTok-style pages, word highlighting, and `.srt` export.
4. Use `@remotion/transitions` for scene transitions and overlay transitions.
5. Use `@remotion/light-leaks`, `@remotion/motion-blur`, `@remotion/noise`, `@remotion/starburst`, `@remotion/shapes`, `@remotion/paths`, and `@remotion/rounded-text-box` for code-native VFX and motion graphics.
6. Use `@remotion/lottie` or `@remotion/rive` only for approved local animation assets.
7. Use `@remotion/three` for 3D scenes and `@remotion/skia` for Skia-heavy vector/canvas effects.
8. Use `@remotion/media-utils`, `@remotion/media`, Mediabunny, and `@remotion/renderer` for media metadata, audio visualization, decode checks, and render tooling.
9. Use `codex/contracts/media-asset-manifest.schema.json` to decide whether an asset is canonical source media, Remotion-public projection media, generated output, or review evidence.

Rules:

- Stay inside Remotion-native packages and official Remotion templates unless the Director explicitly approves an exception.
- Do not use generic HTML, dashboard, icon-pack, or website component libraries as the production component source.
- Do not add a dependency if CSS, SVG, Canvas, or core Remotion can do it clearly.
- Keep all Remotion packages on the same exact version as the project's `remotion` dependency.
- Avoid runtime network dependencies; place assets in `public/` or import them locally.
- Record each selected package, reason, license note, and fallback in the scene plan.

## Required Output

Return a stack decision before implementation:

```json
{
  "status": "complete | needs_approval | blocked",
  "decision_id": "string",
  "scene_id": "string",
  "component_scope": "short_clip | vfx_overlay | motion_graphic | template_component",
  "selected_primitives": [
    {
      "name": "string",
      "purpose": "string",
      "reason": "string"
    }
  ],
  "selected_packages": [
    {
      "package_name": "string",
      "required_version": "string",
      "reason": "string",
      "license_note": "string",
      "approval_required": false,
      "install_command": "string"
    }
  ],
  "template_source": {
    "name": "string",
    "url": "string",
    "license_summary": "string",
    "approval_required": false
  },
  "template_contract": {
    "template_id": "string",
    "path": "string",
    "reuse_mode": "selected_existing | create_new | promote_from_clip | not_applicable"
  },
  "rejected_options": [
    {
      "name": "string",
      "reason_rejected": "string"
    }
  ],
  "fallback_plan": {
    "approach": "string",
    "primitives": ["string"],
    "limitations": "string"
  },
  "validation": {
    "remotion_version_match": true,
    "no_runtime_network_dependency": true,
    "no_generic_web_component_library": true,
    "paid_package_approved": "true | false | not_applicable"
  },
  "blockers": ["string"],
  "next_recommended_step": "string"
}
```

When implementation proceeds, copy the selected dependency and template data into `remotion-clip-package.dependencies`, `remotion-clip-package.template_source`, `remotion-clip-package.template_id`, `remotion-clip-package.template_contract_path`, or `remotion-clip-package.template_instances[]` for multi-template clips. If a reusable template is created or changed, write `codex/contracts/remotion-template.schema.json` too.

## Definition Of Done

- Every selected dependency has reason, version, license note, approval state, and fallback.
- Core Remotion/CSS/SVG/Canvas has been considered before adding packages.
- Generic web component libraries are rejected unless explicitly approved.
- Paid/pro packages and unclear licenses are marked `needs_approval` or `blocked`.
- The Remotion Clip Builder can implement without redoing dependency research.
