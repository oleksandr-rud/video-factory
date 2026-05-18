---
name: visual-pack-plan
description: Create a per-scene visual pack plan that lists visual goals, routes, search queries, AI video route briefs, Remotion briefs, technical requirements, and fallback options. Use after the scenario is stable.
---

# Visual Pack Plan

Create the scene-level visual routing contract. This is a planning artifact, not provider execution and not Remotion implementation.

## Inputs

- Scenario contract with stable scene ids, narration, durations, and visual intent
- Producer criteria, channel profile, channel format, and platform delivery constraints
- Reference analysis, source corpus, claim ledger, and anti-redundancy guidance
- Media asset manifest with approved, deferred, and blocked source/user/provider/generated assets
- Visual research query groups when already prepared
- Remotion project contract, template registry path, and template contract paths when reusable components are in scope
- Budget, rights, provider availability, approval state, and fallback policy

## Workflow

1. Read every scene in the scenario, plus reference analysis, channel format, producer criteria, and the media asset manifest.
2. Build a scene-reference matrix before route selection. For each scenario scene, collect relevant `reference_beats[]`, `scene_decomposition[]`, `reference_videos[].beats[]`, `web_pages[].visual_evidence_candidates`, `claim_ledger[]`, `evidence_refs[]`, and manifest assets. Preserve both the scene-specific evidence and the top-level `overall_summary`/findings so downstream agents can compare scene detail against the full reference read.
3. For each scene, define visual goal, mood, subject, camera/motion, continuity needs, source grounding, viewer job, and the reference-material subset that shaped the route.
4. Pull source-backed options from `reference-analysis.web_pages[].visual_evidence_candidates`, `reference_videos[]`, `reference_beats[]`, `scene_decomposition[]`, `claim_ledger[]`, and approved manifest assets before proposing generic footage.
5. Select one or more routes: `remotion_generated`, `ai_video_generation`, `stock_clip`, `user_supplied_media`, `approved_web_image`, or `source_card_recreation`.
6. Add technical requirements: aspect ratio, minimum resolution, duration, fps if material, people/product needs, safe areas, source asset ids, Remotion `staticFile()` needs, and brand safety notes.
7. Use web page images/screenshots only when manifest rights are approved. If not approved, plan source cards, redrawn diagrams, UI abstractions, or motion-graphic recreations.
8. Apply channel rules without making every scene repetitive. Copy applicable `channel-format.visual_system.vfx_rules` into `vfx_requirements` and `vfx_rule_refs`.
9. Map reusable templates when suitable using `template_hint`, `template_id`, `template_ids`, `template_contract_path`, `template_contract_paths`, and `reusable_template_requirements`.
10. Prefer a project/channel template contract over a shared template contract when safe areas, aspect ratio, visual style, or props differ.
11. Add provider search queries and AI route briefs where applicable. Link them to evidence refs, `reference_beat_ids`, scene decomposition notes, and rejected-query logic from `visual-research-queries`.
12. Include at least one practical fallback route for every important scene.
13. For downstream specialist execution, add `handoff_recommendations[]` instead of reading another agent's skills:
    - `invideo-ai-generator` for AI video feasibility, model-ready prompts, generation approval, variants, generation, or generated clip QA
    - `remotion-clip-builder` for deterministic 5-20 second clips, reusable templates, component templates, motion graphics, source-card recreation, or VFX overlays
14. Keep handoff recommendations implementation-neutral. State need, required inputs, constraints, output contract, approval notes, and definition of done. Let the Director create the actual `agent-handoff`.
15. When recommending InVideo AI Generator or Remotion Clip Builder work, pass the scene-specific reference subset (`reference_beat_ids`, `reference_materials`, `reference_asset_paths`, evidence refs, source asset ids) plus the full `overall_reference_summary` path or object. This lets specialists analyze scene by scene without losing the full-reference context.

## Required Output

Return a visual pack matching `codex/contracts/scene-visual-pack.schema.json` and include:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "scene_visual_pack_path": "string",
  "scene_results": [
    {
      "scene_id": "string",
      "routes": ["stock_clip"],
      "primary_route": "string",
      "fallback_routes": ["string"],
      "source_asset_ids": ["string"],
      "reference_beat_ids": ["string"],
      "reference_materials": [],
      "scene_decomposition": {},
      "overall_reference_summary": {},
      "evidence_refs": ["string"],
      "candidate_requirements": {},
      "search_queries": ["string"],
      "ai_video_generation_brief": "string",
      "remotion_clip_brief": "string",
      "handoff_recommendation_ids": ["string"],
      "approval_needs": ["api_search | generation | file_download | final_use | source_image_use"],
      "blockers": ["string"]
    }
  ],
  "next_recommended_step": "string"
}
```

## Contract Fields Populated

- `scene-visual-pack.schema.json`: all project/channel fields, `scene_packs[]`, route decisions, candidate requirements, search queries, AI/Remotion briefs, template hints, reference beat ids, scene decomposition notes, reference materials, evidence refs, source asset ids, VFX requirements, and handoff recommendations
- `agent-handoff.schema.json`: not written here; `handoff_recommendations[]` provide Director routing input
- `media-asset-manifest.schema.json`: updated or deferred only for media dependencies and future local/public projection needs

## Status Policy

- Return `complete` when every scene has a route plan, candidate requirements, fallback, and explicit next step.
- Return `needs_approval` when the next useful action is provider API use, paid generation, licensed download, source image/screenshot use, or rights-sensitive final use.
- Return `blocked` when a scene cannot be visually satisfied under allowed routes, rights, or budget.
- Return `needs_revision` when scenario, channel format, source evidence, or producer criteria are too unstable to plan visuals.

## Evidence Required

Each important scene must preserve at least one of:

- scenario scene field
- source id or claim id
- reference-analysis evidence id
- reference-analysis beat id or scene-decomposition id when reference material shaped the scene
- media asset id
- channel-format rule id
- producer-criteria rule

Unsupported visual ideas are allowed only as exploratory fallbacks and must be marked lower confidence.

## Media Manifest Policy

If this skill consumes, references, requires, validates, or defers source media, approved web images, screenshots, provider clips, generated clips, Remotion assets, reusable template media, or public-projection needs, update the media asset manifest or return `manifest_actions[]`.

Each manifest action must include `action`, `asset_id`, `canonical_path`, `remotion_public_path` and `static_file_path` when relevant, `rights_state`, `technical_metadata_state`, `evidence_refs`, and `reason`.

Use `deferred` for planned-but-not-yet-created media, assets awaiting approval, source visuals that should be recreated instead of copied, or media that must later be mirrored into Remotion `public/`. Visual plans should pass asset ids and manifest status downstream, not just descriptive clip ideas.

## Approval And Stop Conditions

Stop before provider search execution, file downloads, paid/licensed media, AI generation, page screenshot/image reuse, real-person likeness use, trademark-sensitive use, or final-use approval unless the Director has recorded approval for the scoped project/scenes.

Do not create specialist handoffs that imply generation or download approval. Use `approval_notes` and `blocked_until` on the handoff recommendation.

## Definition Of Done

- Every scene has a visual goal, route set, candidate requirements, and primary/fallback logic.
- Source/evidence refs and manifest states are carried forward.
- Queries and AI/Remotion briefs are linked to the selected routes.
- Specialist handoff recommendations are Director-routable and contract-shaped.
- Approval needs and blockers are explicit before provider/generation work begins.

## Handoff Summary Shape

Return:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "artifact_paths": ["string"],
  "changed_files": ["string"],
  "populated_contracts": ["codex/contracts/scene-visual-pack.schema.json"],
  "manifest_actions": [
    {
      "action": "created | updated | not_applicable | deferred",
      "asset_id": "string",
      "reason": "string"
    }
  ],
  "validation_performed": ["scene route plan", "source evidence check", "fallback coverage", "handoff recommendation shape", "approval gate review"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
