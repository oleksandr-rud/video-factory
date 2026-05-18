---
name: clip-candidate-ranking
description: Score and rank scene visual candidates from stock providers, Remotion-generated visuals, AI video generation, user-supplied media, approved web images, screenshots, and source-card recreations with evidence-backed primary/fallback/rejected decisions. Use when choosing primary and fallback clips per scene before timeline sync or downstream handoff.
---

# Clip Candidate Ranking

Rank candidates as a production decision, not a taste note. Do not select a primary candidate with unresolved rights, missing technical fit, or unknown provenance unless the Director has explicitly accepted that risk.

## Inputs

- Scenario scene ids, scene indexes, narration, visual intent, neighboring scene context, and platform specs
- Scene visual pack with scene pack ids, scenario scene fingerprints, prop requirements, route requirements, fallback needs, constraints, and handoff recommendations
- Validated clip candidates matching `codex/contracts/clip-candidate.schema.json`
- Visual validation output when available
- Channel format, reference analysis, producer criteria, rights policy, and budget policy
- Media asset manifest path and media asset ids when candidates have local files or Remotion public projections

## Workflow

1. Group candidates by `scene_id`; report a blocker for any scene with no candidate set.
2. Confirm each candidate has `candidate_id`, `scene_id`, scene lineage (`scene_index`, `scene_pack_id`, `scene_visual_pack_id`, `scenario_scene_fingerprint`), `route`, `status`, `scores`, provenance, rights notes, and technical metadata or explicit unknowns.
3. Score each candidate from 0 to 10 for:
   - `semantic_fit`
   - `continuity_fit`
   - `technical_fit`
   - `rights_fit`
   - `editability`
4. Calculate `scores.total` using these weights unless producer criteria override them:
   - semantic fit: 35 percent
   - continuity fit: 20 percent
   - technical fit: 20 percent
   - rights fit: 15 percent
   - editability: 10 percent
5. Apply hard blockers before rank ordering:
   - rights blocker: unknown, unapproved, or incompatible license for intended use
   - technical blocker: missing required local path, unusable aspect ratio, duration mismatch, missing Remotion `staticFile()` path when needed, severe quality issue
   - continuity blocker: violates scenario meaning, breaks adjacent scene continuity, or conflicts with channel format
   - web-source blocker: `approved_web_image` lacks manifest approval or `source_card_recreation` lacks claim/evidence refs
6. Select one primary and at least one fallback per scene when possible.
7. If no primary can be selected, set the scene result to `blocked` or `needs_approval` and return a `no_primary_selected` blocker.
8. Preserve rejected candidates with rejection reasons; do not delete useful evidence.
9. Return downstream handoff recommendations only when specialist feasibility is still required.

## Required Output

Update each affected `codex/contracts/clip-candidate.schema.json` item:

- scene lineage fields: `scene_index`, `source_scenario_path`, `source_scene_visual_pack_path`, `scene_visual_pack_id`, `scene_pack_id`, and `scenario_scene_fingerprint`
- `scores.semantic_fit`
- `scores.continuity_fit`
- `scores.technical_fit`
- `scores.rights_fit`
- `scores.editability`
- `scores.total`
- `status`
- `rejection_reason` when rejected
- `evidence_refs` when ranking depends on source/reference/media evidence

Return this ranking summary:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "scenario_id": "string",
  "scene_rankings": [
    {
      "scene_id": "string",
      "scene_index": 0,
      "scene_pack_id": "string",
      "scenario_scene_fingerprint": "string",
      "primary_candidate_id": "string",
      "fallback_candidate_ids": ["string"],
      "no_primary_selected": false,
      "coverage_status": "covered | fallback_only | missing_primary | missing_all",
      "candidate_decisions": [
        {
          "candidate_id": "string",
          "decision": "primary | fallback | rejected | needs_approval | needs_specialist_feasibility",
          "score_breakdown": {
            "semantic_fit": 0,
            "continuity_fit": 0,
            "technical_fit": 0,
            "rights_fit": 0,
            "editability": 0,
            "total": 0
          },
          "score_evidence": "string",
          "rights_blocker_state": "none | needs_approval | blocked | unknown",
          "technical_blocker_state": "none | needs_repair | blocked | unknown",
          "tie_break_reason": "string",
          "rejection_reason": "string"
        }
      ],
      "fallback_coverage": "strong | partial | missing",
      "blockers": ["string"]
    }
  ],
  "approvals_needed": ["string"],
  "handoff_recommendations": [
    {
      "target_agent": "invideo-ai-generator | remotion-clip-builder | remotion-video-producer",
      "reason": "string",
      "scene_id": "string"
    }
  ],
  "next_recommended_step": "string"
}
```

## Contract Fields Populated

- `clip-candidate.schema.json`: scene lineage, `scores`, `status`, `rejection_reason`, `evidence_refs`
- `scene-visual-pack.schema.json`: selected primary/fallback fields or scene notes when the current visual pack supports them
- `agent-handoff.schema.json`: only as a Director-facing handoff recommendation, never as an executable handoff

## Status Policy

- Return `complete` only when every scene has a primary candidate and fallback coverage or an explicit Director-approved exception.
- Return `needs_approval` when the best candidate depends on paid media, unclear rights, likeness/logo risk, provider download approval, or spend.
- Return `blocked` when a scene has no usable primary and no safe fallback route.
- Return `needs_revision` when scene intent, visual pack constraints, or candidate metadata is too ambiguous for fair ranking.
- Candidate status may become `approved` only when rights and technical blockers are clear or explicitly approved.

## Evidence Required

Each decision must cite at least one of:

- candidate metadata
- provider/source URL
- media asset id
- local path or Remotion `staticFile()` path
- validation finding
- scenario scene field
- scenario scene fingerprint or visual scene pack lineage
- reference/channel-format evidence ref
- producer criteria rule

Missing evidence must be called out as `unknown`, not treated as a pass.

## Media Manifest Policy

This skill usually consumes existing manifest entries rather than creating media. If ranking uses or validates a local media file, generated clip, downloaded preview, Remotion clip output, thumbnail, or Remotion public projection, return `manifest_actions[]`:

- `not_applicable` when no local media was created, consumed, or inspected
- `updated` when the ranking adds missing related scene ids, evidence refs, rights notes, or technical notes
- `deferred` when a needed manifest entry is missing and another owner must create it

## Approval And Stop Conditions

Stop and return `needs_approval` before selecting a paid/licensed candidate that lacks Director approval.

Stop and return `blocked` when:

- a scene has no candidate and no fallback route
- all candidates have unresolved rights blockers
- all candidates fail required technical constraints
- source provenance is missing for a candidate that would be used in the render
- a web image/screenshot candidate is not approved for reuse and no source-card recreation fallback exists
- specialist feasibility is required before any fair ranking can be made

## Definition Of Done

- Every scene has primary/fallback/rejected decisions or an explicit blocker.
- Every candidate decision includes scene lineage, score breakdown, score evidence, rights blocker state, and technical blocker state.
- Tie-breakers are explained when scores are close or route choice is non-obvious.
- No primary is selected with unknown rights or missing technical viability unless Director approval is recorded.
- The next owner can proceed without re-ranking from prose.

## Handoff Summary Shape

Return:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "artifact_paths": ["string"],
  "changed_files": ["string"],
  "populated_contracts": ["codex/contracts/clip-candidate.schema.json"],
  "manifest_actions": [
    {
      "action": "created | updated | not_applicable | deferred",
      "asset_id": "string",
      "reason": "string"
    }
  ],
  "validation_performed": ["scene lineage", "candidate grouping", "weighted scoring", "rights blocker check", "technical blocker check", "fallback coverage check"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
