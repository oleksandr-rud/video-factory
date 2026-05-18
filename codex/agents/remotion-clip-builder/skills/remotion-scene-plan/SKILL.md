---
name: remotion-scene-plan
description: Plan deterministic Remotion-generated visuals for 5-20 second scenes or overlays, including layout, components, props, timing, transitions, VFX hooks, and asset needs. Use when a scene is better built with React motion graphics than searched or AI-generated footage.
---

# Remotion Scene Plan

1. Map scene visual goal to a standalone Remotion component, composition id, and clip duration.
2. Define props for copy, colors, assets, and scene duration.
3. Define frame ranges for animation beats.
4. Specify text safe areas and responsive layout rules.
5. Identify needed VFX, subtitle-safe areas, audio-reactive hooks, and transition handles.
6. Choose only necessary libraries; if uncertain, read `../remotion-stack-selection/SKILL.md`.
7. Add render validation command or preview check.
8. Define the fields needed for `codex/contracts/remotion-clip-package.schema.json`.

Return implementation-ready clip notes or code changes when assigned, plus the expected Remotion clip package fields.
