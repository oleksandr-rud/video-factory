---
name: redundancy-risk-audit
description: Audit a planned video, scenario, reference package, or channel format for repetitive, mass-produced, reused-content, or over-templated risks. Use before production to keep channel consistency without making redundant videos.
---

# Redundancy Risk Audit

Score redundancy risk with evidence. Preserve healthy channel consistency while blocking low-novelty, over-templated, copied, or insufficiently transformed plans.

## Inputs

- Scenario, channel format, channel profile, reference analysis, and recent project/video artifacts
- Producer criteria, platform policy constraints, and user/Director novelty requirements
- Style-system tokens, anti-redundancy rules, `must_reuse`/`must_vary` rules, and freshness policy when available
- Media asset manifest for reused footage, generated clips, thumbnails, screenshots, captions, and audio assets
- Existing visual pack, AI generation packages, Remotion clip packages, title/thumbnail notes, or critique findings when auditing later stages

## Workflow

1. Compare the planned video against channel format rules, recent/reference videos, source materials, and previous project artifacts.
2. Identify repeated elements: openings, topic angle, hook wording, proof order, B-roll, AI prompts, Remotion templates, captions, thumbnails, voice posture, edit rhythm, CTA, claims, and source transformation pattern.
3. Separate healthy consistency from unhealthy sameness:
   - Healthy: recognizable voice, colors, captions, structure, source handling, and accessibility defaults.
   - Risky: same topic angle, wording, generated visuals, edit rhythm, proof order, source paraphrase, or template with no new payoff.
4. Score each risk factor with evidence and classify as `none`, `low`, `medium`, `high`, or `blocker`.
5. Require novelty in several dimensions: angle, evidence, visual metaphor, example, source, proof order, payoff, title/thumbnail, scene structure, or production method.
6. Check whether the channel-format freshness policy is stale or whether repeated redundancy flags should downgrade the format to `needs_review`.
7. Recommend concrete changes before downstream production. Do not solve creative revisions here; route owners and required changes.
8. Define waiver requirements when the Director/user may accept a risk; mark non-waivable blockers separately.

## Required Output

Return:

```json
{
  "status": "pass | caution | needs_revision | blocked | needs_approval",
  "audit_id": "string",
  "overall_redundancy_score": 0,
  "risk_level": "none | low | medium | high | blocker",
  "minimum_novelty_result": "pass | partial | fail | unknown",
  "risk_factors": [
    {
      "factor_id": "string",
      "category": "hook | topic_angle | structure | visual_motif | b_roll | ai_prompt | remotion_template | captions | thumbnail | voice | edit_rhythm | CTA | claim | source_transformation | policy",
      "score": 0,
      "risk_level": "none | low | medium | high | blocker",
      "evidence": "string",
      "evidence_refs": ["string"],
      "healthy_consistency": false,
      "required_change": "string"
    }
  ],
  "novelty_requirements": [
    {
      "dimension": "angle | evidence | visual_metaphor | example | source | proof_order | payoff | title_thumbnail | scene_structure | production_method",
      "current_state": "new | partially_new | repeated | unknown",
      "required_change": "string"
    }
  ],
  "waiver_policy": {
    "waiver_allowed": false,
    "waiver_reason_required": "string",
    "non_waivable_blockers": ["string"]
  },
  "owner_recommendations": [
    {
      "owner_agent": "creative-producer | visual-producer | channel-intelligence | invideo-ai-generator | remotion-clip-builder | remotion-video-producer | director",
      "artifact": "string",
      "required_change": "string",
      "blocks_downstream": false
    }
  ],
  "next_recommended_step": "string"
}
```

## Contract Fields Populated

- `channel-format.schema.json`: `anti_redundancy`, freshness review notes, and rules that should be updated
- `scenario.schema.json`: reviewed `novelty_angle`, `source_alignment_notes`, scene `redundancy_notes`, and visual intent
- `scene-visual-pack.schema.json`: reviewed route/template/reused media risks; Visual Producer owns updates
- `media-asset-manifest.schema.json`: validated or deferred manifest actions for reused assets
- `agent-handoff.schema.json`: only as Director-facing owner recommendations

## Status Policy

- Return `pass` when score and factors show healthy consistency with enough novelty.
- Return `caution` when risks are visible but do not block production if owner recommendations are addressed.
- Return `needs_revision` when novelty, transformation, source handling, or template variation is insufficient but fixable.
- Return `needs_approval` when the only viable path depends on licensed source reuse, copied reference material, paid provider work, or a user waiver.
- Return `blocked` when the plan is mass-produced, insufficiently transformed, rights-sensitive, or too repetitive for the intended platform/channel.

## Evidence Required

Every score above `low` must cite recent/reference project artifacts, channel-format rules, media asset ids, source ids, critique findings, or explicit user/Director rules. If prior project history is unavailable, mark comparison confidence as `unknown` and avoid overclaiming.

## Media Manifest Policy

If the audit compares reused clips, generated variants, thumbnails, screenshots, audio, captions, or Remotion template media, update the media asset manifest or return `manifest_actions[]` with `validated` or `deferred`.

Use `deferred` when repeated media is suspected but not yet manifest-tracked or when a reused asset needs rights verification before production.

## Approval And Stop Conditions

Return `needs_approval` when the only viable fix requires a waiver, licensed reuse, copied reference material, paid provider work, or rights-sensitive transformation. Stop and route to the Director when the audit finds material that is too repetitive, insufficiently transformed, or rights-sensitive for the intended channel.

## Definition Of Done

- Redundancy is scored with factor-level evidence.
- Healthy consistency and unhealthy sameness are separated.
- Minimum novelty requirements are pass/fail checked.
- Required changes are owner-routable.
- Waiver policy and non-waivable blockers are explicit.

## Handoff Summary Shape

Return:

```json
{
  "status": "pass | caution | needs_revision | blocked | needs_approval",
  "artifact_paths": ["string"],
  "changed_files": ["string"],
  "populated_contracts": ["codex/contracts/channel-format.schema.json", "codex/contracts/scenario.schema.json"],
  "manifest_actions": [
    {
      "action": "validated | deferred | not_applicable",
      "asset_id": "string",
      "reason": "string"
    }
  ],
  "validation_performed": ["recent-project comparison", "risk scoring", "minimum novelty check", "policy risk review", "waiver policy check"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
