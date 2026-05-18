---
name: style-system-extraction
description: Extract reusable channel style rules from references and brand materials, including color, typography, captions, layout, motion, audio, thumbnails, intros, outros, and reusable assets. Use when channel-level rules should guide many videos without dictating every clip.
---

# Style System Extraction

Extract a tokenized style system from evidence. Do not copy a reference video's exact execution, shot order, music bed, choreography, article layout, or page imagery unless rights and reuse are explicitly approved.

## Inputs

- Channel profile and durable channel path when available
- Reference analysis package, including `source_ledger[]`, `claim_ledger[]`, `reference_beats[]`, `web_pages[]`, deterministic artifact paths, confidence notes, and evidence gaps
- Media asset manifest when local brand assets, frames, screenshots, audio references, reusable visual assets, or template media exist
- Existing channel format and Remotion template registry/contract paths when updating a format
- Producer criteria, platform target, aspect ratio, and user/Director style constraints

## Workflow

1. Read only the supplied evidence artifacts. Mark any unsupported style inference as `model_inferred` or `human_inferred`; do not promote it as deterministic.
2. Extract stable visual tokens: colors, contrast, typography, layout density, framing, source-card style, logo behavior, safe areas, thumbnail conventions, and caption treatment.
3. Extract motion/VFX tokens: intro energy, transitions, zooms, kinetic type, UI/data animation, B-roll motion, allowed/preferred/avoided effects, alpha/export expectations, render-heavy techniques, fallback expectations, and per-channel VFX extensions.
4. Extract audio tokens: narrator persona, voice traits, pace, accent/language policy, music mood, SFX density, pauses, ambience, and loudness concerns.
5. Identify reusable assets and Remotion template candidates: intro/outro, lower thirds, source-card layout, quote style, maps/charts, CTA, disclaimers, overlays, transitions, caption style, recurring VFX motifs, and template contract paths.
6. Assign each token a policy level:
   - `mandatory`: required for recognition, accessibility, compliance, or producer criteria.
   - `preferred`: should usually apply, but can bend for scene needs.
   - `flexible`: safe variation zone.
   - `avoid`: creates redundancy, rights risk, accessibility risk, or brand mismatch.
7. Assign each token an inheritance priority: `explicit_user`, `producer_criteria`, `channel_profile`, `channel_format`, `reference_analysis`, `single_reference`, or `experimental`.
8. Add a do-not-copy boundary for every reference-derived token. Separate abstract reusable rules from non-reusable execution details.
9. Record evidence refs, source ids, asset ids, template ids, confidence, and rights state for every important token.
10. Return reusable template candidates only as constraints. Do not implement templates; the Director routes implementation to Remotion Clip Builder.

## Required Output

Return this structure or embed it in the channel format/channel profile update:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "style_system_id": "string",
  "channel_slug": "string",
  "style_tokens": [
    {
      "token_id": "string",
      "category": "color | typography | layout | caption | motion | vfx | audio | thumbnail | source_card | template | reusable_asset | avoid",
      "name": "string",
      "rule": "string",
      "policy_level": "mandatory | preferred | flexible | avoid",
      "inheritance_priority": "explicit_user | producer_criteria | channel_profile | channel_format | reference_analysis | single_reference | experimental",
      "evidence_mode": "deterministic | model_inferred | human_inferred",
      "source_ids": ["string"],
      "evidence_refs": ["string"],
      "asset_ids": ["string"],
      "template_ids": ["string"],
      "template_contract_paths": ["string"],
      "rights_state": "approved | needs_approval | blocked | unknown | not_applicable",
      "confidence": "high | medium | low | unknown",
      "downstream_targets": ["channel-format-synthesis | write-scenario | visual-pack-plan | remotion-scene-plan | subtitle-caption-pipeline | video-critic"]
    }
  ],
  "do_not_copy_rules": [
    {
      "source_id": "string",
      "non_reusable_element": "string",
      "safe_abstraction": "string",
      "reason": "rights | redundancy | imitation | unknown"
    }
  ],
  "reusable_template_candidates": [
    {
      "candidate_id": "string",
      "pattern": "string",
      "template_id": "string",
      "template_contract_path": "string",
      "needed_if_missing": false,
      "constraints": ["string"]
    }
  ],
  "evidence_gaps": ["string"],
  "invalidation_impact": [
    {
      "change_or_gap": "string",
      "affected_artifacts": ["channel_format | scenario | scene_artifact_sync | visual_pack | remotion_clip | render_package | critique_report"],
      "recommended_action": "string"
    }
  ],
  "next_recommended_step": "string"
}
```

## Contract Fields Populated

- `channel-format.schema.json`: `visual_system`, `audio_system`, `anti_redundancy`, `evidence`, `channel_asset_paths`, and `visual_system.vfx_rules` inputs
- `channel-profile.schema.json`: durable defaults only when the channel folder is in scope
- `media-asset-manifest.schema.json`: manifest entries or `manifest_actions[]` for consumed, validated, promoted, or deferred media assets
- `remotion-template.schema.json`: only as referenced template contract paths or template candidates, never as implementation work

## Status Policy

- Return `complete` when reusable tokens, do-not-copy rules, evidence refs, confidence, and downstream targets are explicit.
- Return `needs_approval` when promoting a token depends on unapproved brand assets, source screenshots, music/audio references, provider media, or template media.
- Return `blocked` when style extraction would require copying a protected reference execution or there is too little evidence to separate style from imitation risk.
- Return `needs_revision` when reference evidence is inconsistent, missing required artifacts, or insufficient for channel-level reuse.

## Evidence Required

Every `mandatory`, `preferred`, `avoid`, reusable asset, or template token must include at least one evidence ref, source id, asset id, explicit user/Director instruction, or producer-criteria rule. If evidence comes from one reference only, mark `inheritance_priority: single_reference` and add a do-not-copy rule.

## Media Manifest Policy

If this skill consumes, validates, or promotes a local brand asset, reference frame, screenshot, audio reference, reusable visual asset, or Remotion template media dependency, update the media asset manifest or return `manifest_actions[]`.

Each manifest action must include `action`, `asset_id`, `canonical_path`, `remotion_public_path` and `static_file_path` when relevant, `rights_state`, `technical_metadata_state`, `evidence_refs`, and `reason`.

Use `deferred` for style tokens inferred from media that is not yet captured, approved, or manifest-tracked. Do not promote a reusable asset or template media dependency into channel format without either a manifest entry or an explicit deferred manifest action.

## Approval And Stop Conditions

Stop and return `needs_approval` before using unapproved screenshots, page images, copyrighted reference visuals, music/audio references, licensed assets, or source material as reusable channel assets. Stop and return `blocked` when the only way to express the style is to imitate a protected reference execution.

## Definition Of Done

- Style tokens are categorized, evidence-backed, confidence-scored, and policy-leveled.
- Do-not-copy boundaries exist for reference-derived tokens.
- Reusable assets/templates are tied to manifest ids or deferred manifest actions.
- Downstream targets and invalidation impact are explicit.
- The output can feed `channel-format-synthesis` without relying on conversational context.

## Handoff Summary Shape

Return:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "artifact_paths": ["string"],
  "changed_files": ["string"],
  "populated_contracts": ["codex/contracts/channel-format.schema.json", "codex/contracts/channel-profile.schema.json"],
  "manifest_actions": [
    {
      "action": "created | updated | consumed | validated | deferred | not_applicable",
      "asset_id": "string",
      "canonical_path": "string",
      "rights_state": "approved | needs_approval | blocked | unknown",
      "technical_metadata_state": "present | missing | partial | not_applicable",
      "reason": "string"
    }
  ],
  "validation_performed": ["evidence coverage", "do-not-copy review", "policy-level assignment", "manifest check", "downstream target check"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
