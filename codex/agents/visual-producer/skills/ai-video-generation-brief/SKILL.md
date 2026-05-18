---
name: ai-video-generation-brief
description: Prepare route-level AI video generation briefs for scenes, including visual goal, prompt intent, constraints, references, aspect ratio, duration, fallback, and cost risk. Use when Visual Producer needs to decide whether to hand a scene to InVideo AI Generator or another approved provider.
---

# AI Video Generation Brief

For each scene:

1. Convert visual goal into a route brief, not a final provider prompt.
2. Add desired camera motion, subject action, lighting, environment, mood, and reference assets.
3. Add constraints and known unwanted artifacts for downstream prompt building.
4. Specify target aspect ratio, duration, resolution, keyframes or first/last frame needs, loop needs, and fallback route.
5. Estimate risk: identity drift, text rendering, physics, hand detail, brand mismatch, cost, rights, and editability.
6. If InVideo or another AI provider is the likely target, add a Director-facing `handoff_recommendations[]` entry for `invideo-ai-generator` instead of reading that agent's skills.
7. Include the recommended handoff objective, required scene inputs, approval notes, fallback route, output contract, and definition of done.

Return route briefs only unless execution is explicitly approved through the InVideo AI Generator.
