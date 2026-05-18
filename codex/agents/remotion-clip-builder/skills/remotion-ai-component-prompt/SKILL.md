---
name: remotion-ai-component-prompt
description: Design prompts and guardrails for generating Remotion-only motion graphics components from natural language. Use when Codex or another LLM should create a self-contained Remotion component, choose targeted edits versus full replacement, sanitize generated code, recover from compile errors, or adapt the official Prompt to Motion Graphics SaaS workflow for local Codex work.
---

# Remotion AI Component Prompt

Use this for text-to-motion-graphics work. It borrows workflow ideas from Remotion's Prompt to Motion Graphics SaaS template, but this repo uses Codex with filesystem access, so generated components should be written into the project and validated with local preview/render checks.

Before generating a new component, use `../remotion-template-library/SKILL.md` when an existing reusable template might satisfy the brief. Generated code that is meant to be reused must also produce a template contract matching `codex/contracts/remotion-template.schema.json`.

## Prompt Contract

Ask for a Remotion component package, not a website component:

- A single named React/TypeScript export for the component.
- A `template_id` and template contract path if the component should be reusable beyond one scene.
- A clear composition id suggestion.
- Props shape for scene copy, colors, assets, duration, seed, and feature flags.
- Props and notes should reference media asset ids plus Remotion `staticFile()` paths, not only loose local filenames.
- Uses Remotion APIs: `useCurrentFrame()`, `useVideoConfig()`, `AbsoluteFill`, `Sequence`, `Series`, `interpolate()`, `spring()`, `random(seed)`, `staticFile()`, and approved `@remotion/*` packages.
- Uses Remotion-native templates/packages only. Do not import generic web component libraries.
- Uses deterministic frame math. Do not use `Math.random()`, wall-clock time, browser storage, fetch-at-render-time remote data, or live network assets.
- Outputs code without markdown fences when the code is being consumed programmatically.

## Generation Workflow

1. Decide whether this is a targeted edit or full replacement:
   - Targeted edit: same composition intent, fix one behavior, timing issue, copy change, asset swap, or styling change.
   - Full replacement: new visual concept, broken architecture, wrong scene language, or unsalvageable generated code.
2. Provide the generator:
   - scenario/scene id
   - target duration and fps
   - aspect ratio and dimensions
   - required text/captions
   - allowed Remotion packages
   - media asset ids and local `staticFile()` asset paths
   - style references in words
   - explicit forbidden dependencies
3. Request structured output when possible:
   - `component_name`
   - `template_id` and `template_contract` when reusable
   - `composition_id`
   - `dependencies`
   - `code`
   - `props_schema`
   - `preview_frames`
   - `notes`
4. Sanitize output before writing:
   - strip markdown fences
   - reject unexpected imports
   - reject remote runtime assets unless explicitly approved
   - reject nondeterministic APIs
   - reject missing named export
5. Validate:
   - TypeScript/build check when available
   - Remotion still frame at representative frames
   - Studio/browser preview for motion
   - full render when feasible
6. Self-correct:
   - feed compile/runtime errors back into a targeted repair prompt
   - keep the same component API unless the error requires changing it
   - stop after repeated failures and fall back to a simpler Remotion-native route

## Image Handling

- Attached image references should be treated as visual targets to recreate in code or as local assets, depending on the Director brief.
- URL strings in a prompt should only be embedded as media if rights and network/render policy allow it; prefer downloading or placing approved assets under `public/`.

## Minimal Prompt Template

```text
Generate a Remotion-only TypeScript component for scene <scene_id>.
Goal: <visual goal>.
Duration: <seconds> seconds at <fps> fps, <width>x<height>.
Allowed packages: <core remotion and approved @remotion/* packages>.
Assets: <media asset ids and local public/staticFile paths>.
Rules: named export <ComponentName>; deterministic frame math; no generic web component libraries; no Math.random; no remote runtime fetches; code only.
Return structured fields: component_name, template_id, composition_id, dependencies, code, props_schema, preview_frames, remotion_template_contract, notes.
```
