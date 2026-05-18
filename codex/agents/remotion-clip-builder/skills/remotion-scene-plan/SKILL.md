---
name: remotion-scene-plan
description: Plan deterministic Remotion-generated visuals for 5-20 second scenes or overlays, including layout, components, props, timing, transitions, VFX hooks, and asset needs. Use when a scene is better built with React motion graphics than searched or AI-generated footage.
---

# Remotion Scene Plan

1. Consider `../remotion-template-library/SKILL.md` and the Remotion app template registry before planning a bespoke component when the scene has a reusable pattern, channel reusable asset, or `template_hint`.
2. Read `channel_format_path` when available. Apply `visual_system.vfx_rules` as per-channel extensions to VFX choices, hardening triggers, alpha/export behavior, safe areas, benchmark requirements, and fallback expectations.
3. Decide whether the scene should use no template, one template, multiple template layers, bespoke VFX, or a hybrid.
4. Map scene visual goal to a standalone Remotion component, template-backed instance, hybrid VFX component, composition id, and clip duration.
5. Define props for copy, colors, assets, source media asset ids, `staticFile()` paths, and scene duration.
6. Define frame ranges for animation beats.
7. Specify text safe areas and responsive layout rules.
8. Identify needed VFX, subtitle-safe areas, audio-reactive hooks, and transition handles.
9. Choose only necessary libraries; if uncertain, read `../remotion-stack-selection/SKILL.md`.
10. Identify whether `../vfx-quality-performance-hardening/SKILL.md` is required because the scene is complex, media-heavy, GPU-heavy, transparent, likely to be reused, or required by channel-format VFX rules.
11. Add render validation command or preview check.
12. Define the fields needed for `codex/contracts/remotion-clip-package.schema.json`, including `template_id`/`template_contract_path` for one-template cases or `template_instances[]` for layered template usage, plus project/channel fields, channel format path, media asset manifest path, Remotion project contract path, output asset ids, `vfx_rule_refs`, and `vfx_profile` when applicable.
13. If the planned component should be reusable beyond the current scene, also define the fields needed for `codex/contracts/remotion-template.schema.json`.

Return implementation-ready clip notes or code changes when assigned, plus the expected Remotion clip package fields.
