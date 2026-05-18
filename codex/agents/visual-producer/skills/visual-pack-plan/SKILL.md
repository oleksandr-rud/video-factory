---
name: visual-pack-plan
description: Create a per-scene visual pack plan that lists visual goals, routes, search queries, AI video route briefs, Remotion briefs, technical requirements, and fallback options. Use after the scenario is stable.
---

# Visual Pack Plan

1. Read every scene in the scenario, plus any reference analysis, channel format package, and media asset manifest.
2. For each scene, define visual goal, mood, subject, motion, and continuity needs.
3. Select candidate routes: `remotion_generated`, `ai_video_generation`, `stock_clip`, or `user_supplied_media`.
4. Write provider search queries and AI generation route briefs where applicable.
5. Add technical requirements: aspect ratio, minimum resolution, duration, people/product needs, required source asset ids, Remotion `staticFile()` needs, and brand safety notes.
6. Apply reusable channel rules while keeping scene-specific visual choices flexible.
7. Include one practical fallback route for every important scene.
8. For any route that needs downstream specialist execution, add `handoff_recommendations[]` instead of reading another agent's skills:
   - `invideo-ai-generator` for AI video model feasibility, provider-ready prompts, generation approval, variants, generation, or generated clip QA.
   - `remotion-clip-builder` for deterministic 5-20 second Remotion clips, component templates, motion graphics, or VFX overlays.
9. Keep handoff recommendations implementation-neutral: state the scene need, required inputs, constraints, output contract, approval notes, and definition of done. Let the Director create the actual `agent-handoff`.

Return a visual pack matching `codex/contracts/scene-visual-pack.schema.json`, including project/channel fields, source asset ids, and evidence refs when available.
