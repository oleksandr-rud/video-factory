---
name: visual-pack-plan
description: Create a per-scene visual pack plan that lists visual goals, routes, search queries, AI video route briefs, Remotion briefs, technical requirements, and fallback options. Use after the scenario is stable.
---

# Visual Pack Plan

1. Read every scene in the scenario, plus any reference analysis, channel format package, and media asset manifest.
2. For each scene, define visual goal, mood, subject, motion, and continuity needs.
3. Pull source-backed options from `reference-analysis.web_pages[].visual_evidence_candidates`, `reference_videos[]`, `claim_ledger[]`, and approved media manifest assets.
4. Select candidate routes: `remotion_generated`, `ai_video_generation`, `stock_clip`, `user_supplied_media`, `approved_web_image`, or `source_card_recreation`.
5. Write provider search queries and AI generation route briefs where applicable.
6. Add technical requirements: aspect ratio, minimum resolution, duration, people/product needs, required source asset ids, Remotion `staticFile()` needs, and brand safety notes.
7. Use web page images/screenshots only when approved in the manifest. If not approved, plan source cards, redrawn diagrams, UI abstractions, or motion-graphic recreations instead.
8. Apply reusable channel rules while keeping scene-specific visual choices flexible. When the channel format has `visual_system.vfx_rules`, copy applicable VFX constraints into `vfx_requirements`, add `vfx_rule_refs`, and mention hardening or benchmark expectations in Remotion handoff recommendations.
9. When the channel format provides `reusable_template_ids` or `remotion_template_contract_paths`, map suitable scenes to `template_hint`, `template_id`, `template_ids`, `template_contract_path`, `template_contract_paths`, and `reusable_template_requirements` in the visual pack.
10. Prefer a project/channel template contract over a shared template contract when the scene's format, safe areas, aspect ratio, or style requirements differ.
11. Include one practical fallback route for every important scene.
12. For any route that needs downstream specialist execution, add `handoff_recommendations[]` instead of reading another agent's skills:
   - `invideo-ai-generator` for AI video model feasibility, provider-ready prompts, generation approval, variants, generation, or generated clip QA.
   - `remotion-clip-builder` for deterministic 5-20 second Remotion clips, reusable template selection/creation, component templates, motion graphics, or VFX overlays.
13. For template-backed Remotion recommendations, include the template id/contract path or arrays of template ids/contract paths when known. Otherwise include category and constraints such as lower third, source card, caption, transition, overlay, data callout, mockup, safe areas, alpha, dimensions, and duration.
14. Do not force template reuse. If a scene needs complex VFX, a custom procedural component, or a one-off art direction, set `allow_bespoke_vfx` in `reusable_template_requirements` and request Remotion Clip Builder implementation.
15. Keep handoff recommendations implementation-neutral: state the scene need, required inputs, constraints, output contract, approval notes, and definition of done. Let the Director create the actual `agent-handoff`.

Return a visual pack matching `codex/contracts/scene-visual-pack.schema.json`, including project/channel fields, source asset ids, and evidence refs when available.
