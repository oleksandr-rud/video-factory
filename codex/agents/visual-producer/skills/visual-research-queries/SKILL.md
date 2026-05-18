---
name: visual-research-queries
description: Generate and refine search queries for scene-level visual research across stock providers, internal footage, web references, and AI generation prompts. Use when a scene needs visual candidates.
---

# Visual Research Queries

Build search-query sets that preserve why each query exists, which evidence shaped it, and when to stop searching. Do not collapse visual research into one generic keyword list.

This skill is part of the required visual research gate for deliverable videos and channel-format/producer-criteria work. Even when provider API search, downloads, or paid generation are not approved, the query research must still preserve planned routes, evidence refs, rejected-query logic, stop criteria, and deferred approval actions so channel format requirements are grounded in actual scene needs.

## Inputs

- Scenario scene ids, narration, on-screen text, duration, and visual intent
- Visual pack draft or candidate requirements when available
- Producer criteria, channel profile, channel format, and platform constraints
- Reference analysis, especially `overall_summary`, `scene_decomposition[]`, `reference_beats[]`, `reference_videos[]`, `web_pages[].visual_evidence_candidates`, `claim_ledger[]`, and `evidence_refs[]`
- Media asset manifest with approved source/user/web assets and deferred image/screenshot candidates
- Provider availability, language/locale, budget policy, and Director approval state

## Workflow

1. Extract concrete nouns, actions, locations, mood, camera angle, motion, time period, audience context, and domain terms for each scene.
2. Read source-backed visual evidence before inventing new terms. Prefer source ids, reference beat ids, scene-decomposition notes, evidence refs, and approved media asset ids over unsupported imagery.
3. When reference videos were divided into beats/scenes, map query groups to the relevant `reference_beats[]` or `scene_decomposition[]` entries. Keep the top-level `overall_summary` in the query rationale so a query does not overfit one isolated reference beat.
   - If reference content mismatches the target channel/project, derive search intent from the reference's visual mechanics and replace subject/topic terms with target-content terms from the scenario, claim ledger, channel/project brief, and producer criteria.
4. Build query groups by route:
   - `stock_clip`: concise provider-search terms, not full cinematic prompts
   - `ai_video_generation`: prompt-intent phrases and reference constraints, not provider-final prompts
   - `remotion_generated`: component/template keywords, data-card needs, UI/mockup needs, or VFX requirements
   - `approved_web_image`: only approved media-manifest assets
   - `source_card_recreation`: claim/source terms to redraw or cite without copying page material
   - `user_supplied_media`: asset ids, filenames, and selection notes
5. For stock routes, create broad, narrow, and fallback queries. Record provider priority: Freepik/Magnific primary when account/licensing is available; Pexels secondary/free fallback unless the Director explicitly chooses it first.
6. Add provider filters when useful: orientation, aspect ratio, resolution, duration, language/locale, people/no-people, and safe-area notes.
7. Add negative criteria for unsuitable clips, including copyright, brand/celebrity, misleading endorsement, irrelevant geography, AI artifacts, watermarks, unreadable text, and unsafe likeness context.
8. Avoid copyrighted characters, brand names, celebrity names, logos, and restricted locations unless supplied and authorized.
9. Preserve rejected queries with reasons when they are too broad, too copyrighted, source-inaccurate, provider-hostile, redundant, or likely to retrieve unusable media.
10. Define stop criteria per scene: enough high-fit candidates, no safe provider route, approval needed, fallback route preferred, or specialist handoff needed.
11. Summarize format/criteria implications for the visual pack: route constraints, source-card needs, template/VFX requirements, provider limitations, and visual requirements that should be promoted into channel format or producer criteria.

## Required Output

Return this structure or embed it in `scene-visual-pack.schema.json` fields:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "query_groups": [
    {
      "scene_id": "string",
      "route": "stock_clip | ai_video_generation | remotion_generated | user_supplied_media | approved_web_image | source_card_recreation",
      "reference_beat_ids": ["string"],
      "scene_decomposition_refs": ["string"],
      "overall_reference_summary_ref": "string",
      "reference_use_policy": "content_and_visual | visual_format_only | content_only | do_not_use | not_applicable",
      "target_content_substitution": "string",
      "provider_priority": ["freepik", "pexels"],
      "queries": [
        {
          "query": "string",
          "purpose": "broad | narrow | fallback | reference_match | source_recreation",
          "provider_filters": {},
          "evidence_refs": ["string"],
          "negative_criteria": ["string"],
          "expected_candidate_count": "low | medium | high | unknown"
        }
      ],
      "rejected_queries": [
        {
          "query": "string",
          "reason": "string"
        }
      ],
      "search_stop_criteria": ["string"],
      "approvals_needed": ["api_search | file_download | final_use | source_image_use"],
      "format_requirement_implications": ["string"]
    }
  ],
  "next_recommended_step": "string"
}
```

## Contract Fields Populated

- `scene-visual-pack.schema.json`: `scene_packs[].search_queries`, `routes`, `candidate_requirements`, `reference_beat_ids`, `scene_decomposition`, `reference_materials`, `evidence_refs`, `source_asset_ids`, and `handoff_recommendations[]` when a specialist route is needed
- `clip-candidate.schema.json`: not created here; provider skills create candidate files after search
- `media-asset-manifest.schema.json`: not changed unless this skill records deferred manifest actions for source/user/web assets

## Status Policy

- Return `complete` when each scene has route-grouped queries, rejected-query reasons, stop criteria, and format/criteria implications or an explicit `not_applicable` reason.
- Return `needs_approval` when the next search requires provider API use, source image/screenshot use, licensed media, or rights-sensitive search terms.
- Return `blocked` when no allowed route can produce a usable visual and no fallback route is viable.
- Return `needs_revision` when scene goals, source grounding, platform constraints, or provider scope are too vague.

## Evidence Required

Each query group must cite at least one of:

- scene id and scenario field
- reference-analysis evidence id/source id
- reference-analysis beat id or scene-decomposition reference when reference video parsing shaped the query
- media asset id
- channel-format rule
- producer-criteria rule
- user-supplied constraint

If a query has no evidence, mark it as exploratory and keep it lower priority than source-backed queries.

## Media Manifest Policy

Do not treat remote page images, screenshots, provider previews, or direct video URLs as usable assets. Return `manifest_actions[]` with `deferred` when a query depends on media that still needs approval, download, local capture, or Remotion public projection.

## Approval And Stop Conditions

Stop before using provider APIs, downloading files, using page images/screenshots, or searching restricted brand/celebrity/likeness terms without Director approval. Escalate to the Director when the best query depends on paid/credited APIs, licensed assets, or unclear rights.

## Definition Of Done

- Every scene has route-grouped query options or a blocker.
- Provider-specific query terms are concise and searchable.
- Freepik/Pexels priority is explicit for stock routes.
- Rejected queries and search stop criteria are recorded.
- Evidence refs and approval needs are visible to provider skills and ranking.

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
      "action": "deferred | not_applicable",
      "asset_id": "string",
      "reason": "string"
    }
  ],
  "validation_performed": ["scene extraction", "source evidence check", "route grouping", "provider priority", "rejected-query review"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
