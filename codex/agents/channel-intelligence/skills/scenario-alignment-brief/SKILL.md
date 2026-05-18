---
name: scenario-alignment-brief
description: Compare a scenario against source materials, reference analysis, and channel format rules. Use to identify missing evidence, off-format structure, weak hooks, redundant angles, visual gaps, and downstream guidance before production.
---

# Scenario Alignment Brief

Act as the pre-production gate between evidence, channel format, and downstream spend. Return scene-level findings that the Director can route without interpretation.

## Inputs

- Scenario contract path and scene list
- Producer criteria and acceptance gates when available
- Reference analysis package with `source_ledger[]`, `claim_ledger[]`, `reference_beats[]`, `web_pages[]`, visual evidence candidates, confidence, and evidence gaps
- Channel profile and channel format package, including anti-redundancy, style tokens, and VFX rules
- Media asset manifest for approved/deferred source images, screenshots, audio, video, and references
- Existing visual pack, voiceover package, or critique findings when reviewing a revision

## Workflow

1. Check each scene against channel promise, audience, content pillars, tone, pacing, episode structure, hook/payoff logic, and producer criteria.
2. Separate content alignment from visual-format alignment. If supplied references mismatch the target topic/channel/project content, mark their facts as `not_applicable` or `unsupported` for script claims, but keep their scene decomposition and whole-video summary available as visual-format evidence.
3. Map factual claims, implied claims, source mentions, on-screen text, and scene purpose to `claim_ledger[]`, source ids, evidence refs, or explicit user-provided facts.
4. Classify evidence coverage as `supported`, `partial`, `needs_review`, `unsupported`, or `not_applicable`.
5. Check visual producibility: every scene needs an approved visual route, a source-card path, a Remotion path, an AI-generation route, approved media, a reference-video visual-format plan, or a clear Visual Producer research need.
6. Check style/format alignment without forcing copied reference execution. Flag any scene that risks imitating a reference too closely.
7. When the reference is visually solid but content-mismatched, route the finding to Visual Producer or Remotion Clip Builder as a target-content substitution task, not as a reason to discard the reference.
8. Check novelty: the hook, angle, proof, examples, visual proof, and payoff must satisfy channel-format `must_vary` and anti-redundancy rules.
9. Route each finding to the owner that can fix it: `creative-producer`, `visual-producer`, `channel-intelligence`, `invideo-ai-generator`, `remotion-clip-builder`, `remotion-video-producer`, `video-critic`, or `director`.
10. Return `block` only for issues that should stop production spending or downstream rendering.

## Required Output

Return:

```json
{
  "status": "pass | needs_revision | blocked | needs_approval",
  "scenario_id": "string",
  "alignment_summary": {
    "source_coverage": "pass | partial | fail | unknown",
    "channel_fit": "pass | partial | fail | unknown",
    "visual_producibility": "pass | partial | fail | unknown",
    "novelty": "pass | partial | fail | unknown",
    "approval_readiness": "ready | needs_approval | blocked"
  },
  "scene_findings": [
    {
      "finding_id": "string",
      "scene_id": "string",
      "severity": "blocker | major | minor | note",
      "category": "source_gap | unsupported_claim | weak_hook | weak_payoff | off_format | visual_gap | style_risk | redundancy_risk | rights_or_approval | production_risk",
      "claim_or_rule_ref": "string",
      "evidence_coverage": "supported | partial | needs_review | unsupported | not_applicable",
      "channel_fit": "pass | partial | fail | unknown",
      "visual_proof_state": "ready | needs_visual_plan | needs_source_card | needs_approval | blocked | not_applicable",
      "reference_use_policy": "content_and_visual | visual_format_only | content_only | do_not_use | not_applicable",
      "description": "string",
      "recommendation": "string",
      "owner_agent": "creative-producer | visual-producer | channel-intelligence | invideo-ai-generator | remotion-clip-builder | remotion-video-producer | video-critic | director",
      "disposition": "pass | needs_revision | block | needs_approval",
      "evidence_refs": ["string"]
    }
  ],
  "required_changes": [
    {
      "owner_agent": "string",
      "scene_id": "string",
      "change": "string",
      "blocks_downstream": false
    }
  ],
  "next_recommended_step": "string"
}
```

## Contract Fields Populated

- `scenario.schema.json`: reviewed fields only; this skill does not rewrite the scenario unless explicitly assigned
- `reference-analysis.schema.json`: consumes `claim_ledger[]`, `reference_beats[]`, `downstream_guidance`, and `invalidation_impact[]`
- `channel-format.schema.json`: consumes narrative, visual, audio, and anti-redundancy rules
- `scene-visual-pack.schema.json`: may recommend visual pack revisions, but Visual Producer owns updates
- `agent-handoff.schema.json`: only as Director-facing handoff recommendations

## Status Policy

- Return `pass` when all scenes have adequate source grounding, channel fit, novelty, and visual producibility.
- Return `needs_revision` when fixes are local to scenario wording, scene purpose, visual intent, hook/payoff, or source mapping.
- Return `needs_approval` when a scene depends on unapproved media, licensed assets, direct source/page imagery, paid provider work, or user waiver.
- Return `blocked` when unsupported claims, rights issues, imitation risk, or missing evidence should stop downstream production.
- Do not return `blocked` solely because a visually useful reference has mismatched content. Block only if the mismatch causes unsupported target claims, rights risk, direct copying, or no viable substitution path.

## Evidence Required

Every factual or inferential scene beat must cite a source id, claim id, evidence ref, producer-criteria rule, or explicit user/Director instruction. If evidence is missing, mark `evidence_coverage: unsupported` or `needs_review`; do not hide it in prose.

## Media Manifest Policy

This skill normally validates rather than creates media. If it consumes or checks local source images, screenshots, reference frames, audio, generated clips, or approved user media, update the media asset manifest or return `manifest_actions[]` with `validated` or `deferred`.

Use `deferred` when a scene depends on source imagery or media that has not been captured, approved, downloaded, or manifest-tracked.

## Approval And Stop Conditions

Stop before production if blocker findings involve unsupported claims, rights-sensitive media, direct reference imitation, or paid/provider work. Route approval-sensitive findings to the Director instead of asking downstream agents to resolve them informally.

## Definition Of Done

- Every scene has a pass, revision, approval, or block disposition.
- Claims and visual proof needs are mapped to evidence or marked missing.
- Owner routing is explicit for each required change.
- The Director can create targeted handoffs directly from the findings.

## Handoff Summary Shape

Return:

```json
{
  "status": "pass | needs_revision | blocked | needs_approval",
  "artifact_paths": ["string"],
  "changed_files": ["string"],
  "populated_contracts": ["codex/contracts/scenario.schema.json", "codex/contracts/reference-analysis.schema.json"],
  "manifest_actions": [
    {
      "action": "validated | deferred | not_applicable",
      "asset_id": "string",
      "reason": "string"
    }
  ],
  "validation_performed": ["source coverage", "channel fit", "visual producibility", "novelty", "approval readiness"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
