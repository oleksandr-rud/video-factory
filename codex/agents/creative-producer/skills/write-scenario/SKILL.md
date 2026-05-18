---
name: write-scenario
description: Write a timed video scenario with narration, on-screen text, scene purpose, visual intent, source alignment, channel-format fit, and claim-check notes. Use for scriptwriting, social video structure, explainer copy, product promo scripts, and scene-level planning.
---

# Write Scenario

Write a dual-layer scenario: story logic for the viewer and production logic for downstream agents. Keep scene ids stable after downstream work begins.

## Inputs

- Director production brief, producer criteria, target platform, aspect ratio, duration, audience, and acceptance gates
- Channel profile and channel format, including narrative system, voice/audio rules, anti-redundancy rules, and `must_reuse`/`must_vary` guidance when available
- Reference analysis with `source_ledger[]`, `claim_ledger[]`, `web_pages[]`, `reference_beats[]`, evidence refs, confidence notes, and source gaps
- Scenario alignment brief or redundancy audit findings when revising
- Media asset manifest for approved source/user/web assets and deferred visual evidence
- Existing scenario path when updating a version

## Workflow

1. Build a production-safe premise from the Director brief, channel promise, audience, source evidence, and producer criteria.
   - When supplied references are visually relevant but their topic/content mismatches the target project, use them only for format, pacing, scene logic, and visual rhythm. Do not import their facts, examples, audience promise, product claims, or subject matter unless those are independently supported by target sources or explicit Director instruction.
2. Select a structure appropriate to the platform and channel format: hook, context, proof, payoff, CTA, or an approved variant.
3. Define the novelty angle before drafting scenes. The angle must vary topic framing, proof, example, visual metaphor, source, payoff, or structure enough to satisfy anti-redundancy rules.
4. Use `claim_ledger[]`, `web_pages[]`, source ids, or explicit user-provided facts as factual inputs. Do not invent page facts from memory.
5. Treat `claim_ledger[].support_state=needs_review`, unknown confidence, or missing evidence as a limitation unless another supplied source supports the claim.
6. Draft scenes with stable `scene_id`, start/end seconds, purpose, narration/script, on-screen text, visual intent, voice notes, source ids, format notes, and redundancy notes.
7. Separate:
   - `must_say`: claims or message points that cannot be changed without invalidating the scenario.
   - `must_show`: visual proof or scene function needed for comprehension.
   - `flexible`: creative execution that downstream agents may vary.
8. Keep narration compatible with target duration and platform pacing. Flag duration pressure instead of silently cutting required claims.
9. Add visual intent without choosing footage. Refer to `web_pages[].visual_evidence_candidates` only as evidence or inspiration unless the manifest marks the image/screenshot approved. For mismatched-content reference videos, write visual intent as a substitution: preserve the reference's visual job and composition, but replace its subject matter with target-channel/project content.
10. Run a pre-handoff self-check for claim/source coverage, channel fit, novelty, duration budget, scene id stability, and downstream producibility.

## Required Output

Return JSON-compatible content matching `codex/contracts/scenario.schema.json` plus this production summary:

```json
{
  "status": "complete | needs_revision | blocked | needs_approval",
  "scenario_path": "string",
  "scenario_summary": {
    "scenario_id": "string",
    "title": "string",
    "duration_seconds": 0,
    "platform": "string",
    "aspect_ratio": "string",
    "novelty_angle": "string",
    "structure": ["hook", "context", "proof", "payoff", "CTA"]
  },
  "scene_production_logic": [
    {
      "scene_id": "string",
      "must_say": ["string"],
      "must_show": ["string"],
      "flexible_execution": ["string"],
      "source_ids": ["string"],
      "claim_ids": ["string"],
      "format_rules_applied": ["string"],
      "visual_intent": "string",
      "reference_use_policy": "content_and_visual | visual_format_only | content_only | do_not_use | not_applicable",
      "target_content_substitution": "string",
      "voice_notes": "string",
      "duration_pressure": "none | low | medium | high",
      "downstream_owner_hints": ["visual-producer | creative-producer | remotion-video-producer | video-critic"]
    }
  ],
  "claim_source_coverage": [
    {
      "claim_id": "string",
      "scene_id": "string",
      "support_state": "supported | partial | needs_review | unsupported | not_applicable",
      "source_ids": ["string"],
      "evidence_refs": ["string"],
      "script_action": "included | softened | excluded | needs_review"
    }
  ],
  "validation_summary": {
    "duration_fit": "pass | partial | fail",
    "source_grounding": "pass | partial | fail",
    "channel_format_fit": "pass | partial | fail",
    "novelty": "pass | partial | fail",
    "visual_producibility": "pass | partial | fail"
  },
  "next_recommended_step": "string"
}
```

## Contract Fields Populated

- `scenario.schema.json`: `scenario_id`, project/channel fields, title, audience, platform, aspect ratio, duration, tone, `must_include`, `must_avoid`, `source_alignment_notes`, `novelty_angle`, and `scenes[]`
- `reference-analysis.schema.json`: consumes `claim_ledger[]`, `source_ledger[]`, `web_pages[]`, and evidence refs
- `channel-format.schema.json`: consumes narrative, audio, visual, and anti-redundancy rules
- `media-asset-manifest.schema.json`: not modified unless this skill validates or defers source/user/web media referenced by the scenario

## Status Policy

- Return `complete` when the scenario is source-grounded, timed, channel-fit, production-feasible, and ready for scene breakdown or visual planning.
- Return `needs_revision` when duration, hook/payoff, channel fit, visual intent, source mapping, or novelty is weak but fixable.
- Return `needs_approval` when the scenario depends on unapproved source imagery, licensed assets, sensitive claims, user waiver, or paid provider work.
- Return `blocked` when required claims are unsupported, legally/rights-sensitive, contradictory, or impossible to fit in the requested duration without changing the brief.

## Evidence Required

Every factual or inferential claim must map to a `source_id`, `claim_id`, evidence ref, explicit user/Director instruction, or producer-criteria rule. Unknown claims must be softened, excluded, or marked `needs_review`; do not hide unsupported claims inside narration.

## Media Manifest Policy

This skill normally plans media but does not create it. Return `manifest_actions[]` with `deferred` when a scene depends on source imagery, screenshots, user media, audio, or approved web assets that are not yet manifest-tracked or approved for the intended use.

Do not mark page images, screenshots, provider previews, or reference clips as usable visuals unless the media manifest rights state allows that use.

## Approval And Stop Conditions

Stop before writing claims or scenes that require unapproved medical/legal/financial certainty, direct article/page copying, source image reuse, celebrity/brand/likeness use, or paid provider execution. Route approval-sensitive dependencies to the Director.

## Definition Of Done

- Scenario validates against the expected `scenario.schema.json` shape.
- Scene ids, timestamps, purposes, script, visual intent, voice notes, source ids, and format notes are present.
- Claim-source coverage and novelty angle are explicit.
- The scenario separates what downstream agents must preserve from what they may creatively vary.
- Handoff summary identifies blockers, assumptions, and next owner.

## Handoff Summary Shape

Return:

```json
{
  "status": "complete | needs_revision | blocked | needs_approval",
  "artifact_paths": ["string"],
  "changed_files": ["string"],
  "populated_contracts": ["codex/contracts/scenario.schema.json"],
  "manifest_actions": [
    {
      "action": "deferred | validated | not_applicable",
      "asset_id": "string",
      "reason": "string"
    }
  ],
  "validation_performed": ["schema shape", "claim-source coverage", "duration budget", "channel-format fit", "novelty check", "visual producibility"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
