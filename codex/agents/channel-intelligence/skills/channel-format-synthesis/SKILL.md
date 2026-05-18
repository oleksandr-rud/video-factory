---
name: channel-format-synthesis
description: Create or update a reusable channel format package from reference analysis, source content, best-practice specs, and channel data. Use when the production needs consistent channel format rules, themes, colors, video structure, recurring materials, and reusable constraints across many videos.
---

# Channel Format Synthesis

Create a versioned, evidence-backed channel format. Preserve channel consistency while defining explicit variation rules so future videos do not become repetitive or stale.

## Inputs

- Channel profile, channel root path, existing channel formats, and recent project history when available
- Reference analysis package with `source_ledger[]`, `claim_ledger[]`, `reference_beats[]`, `downstream_guidance`, evidence gaps, and confidence notes
- Style tokens or style-system extraction output
- Media asset manifest and reusable asset/template ids
- Producer criteria, platform targets, target duration range, audience, and explicit user/Director strategy
- Performance or audience evidence when available: topic fit, viewer retention notes, CTR/watch-time notes, comments, or prior run critique findings

## Workflow

1. Read the channel profile, reference analysis, style tokens, source ledger, and media manifest. Do not promote rules with missing evidence as durable defaults.
2. Define the channel promise, audience, content pillars, video themes, platform targets, and content mix.
3. Define reusable narrative rules: hook families, episode structure, pacing bands, proof style, transitions between ideas, CTA behavior, and payoff expectations.
4. Define reusable visual/audio systems from style tokens and channel defaults, including caption, layout, source-card, thumbnail, motion, audio, and VFX rules.
5. Populate `visual_system.reusable_assets`, `visual_system.reusable_template_ids`, and `visual_system.remotion_template_contract_paths` only when assets/templates are manifest-backed or explicitly deferred.
6. Populate `visual_system.vfx_rules` as per-channel extensions to shared VFX hardening rules. Include base rule refs, allowed/preferred/avoided effects, quality/performance/determinism rules, alpha/export behavior, media decode rules, transition limits, safe-area constraints, hardening triggers, benchmark requirements, fallback requirements, and explicit overrides.
7. Split rules into `must_reuse`, `must_vary`, and `experimental` groups:
   - `must_reuse`: identity-preserving elements needed for recognition or compliance.
   - `must_vary`: episode-level elements that must change to avoid redundancy.
   - `experimental`: rules that need more audience evidence before becoming durable defaults.
8. Add anti-redundancy thresholds and flex zones for unique angle, examples, visual moments, data, references, opening pattern, proof order, and CTA wording.
9. Add a freshness policy. Define when the format becomes stale or needs review: old evidence, declining intro hold, declining watch time, repeated redundancy flags, topic decay, changed platform strategy, conflicting new references, or user/Director override.
10. Attach evidence ids, source ids, asset ids, template ids, template contract paths, VFX rule refs, confidence, and evidence mode for important rules.

## Required Output

Return a package matching `codex/contracts/channel-format.schema.json` and include this companion summary:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "channel_format_path": "string",
  "format_summary": {
    "channel_format_id": "string",
    "version": "string",
    "status": "draft | active | needs_review | deprecated",
    "format_type": "channel_default | project_variant | experimental",
    "source_analysis_ids": ["string"],
    "confidence": "high | medium | low | unknown"
  },
  "rule_groups": {
    "must_reuse": [
      {
        "rule_id": "string",
        "rule": "string",
        "evidence_refs": ["string"],
        "confidence": "high | medium | low | unknown"
      }
    ],
    "must_vary": [
      {
        "rule_id": "string",
        "dimension": "angle | hook | example | visual | proof | source | CTA | edit_rhythm | thumbnail | caption | voice",
        "rule": "string",
        "minimum_variation": "string"
      }
    ],
    "experimental": [
      {
        "rule_id": "string",
        "rule": "string",
        "evidence_needed": "string"
      }
    ]
  },
  "freshness_policy": {
    "review_after": "string",
    "staleness_triggers": ["string"],
    "downgrade_to_needs_review_when": ["string"]
  },
  "anti_redundancy_thresholds": {
    "max_reused_hook_similarity": "string",
    "max_reused_visual_motif_count": 0,
    "minimum_novelty_dimensions": 0
  },
  "downstream_invalidation": [
    {
      "change": "string",
      "affected_artifacts": ["scenario | voiceover_package | scene_visual_pack | ai_video_generation_package | remotion_clip_package | timeline_sync_plan | render_package | critique_report"],
      "owner_agent": "string"
    }
  ],
  "next_recommended_step": "string"
}
```

## Contract Fields Populated

- `channel-format.schema.json`: all required fields plus `visual_system`, `audio_system`, `technical_defaults`, `anti_redundancy`, `evidence`, and `channel_asset_paths`
- `channel-profile.schema.json`: only durable channel defaults or current active format refs when requested
- `media-asset-manifest.schema.json`: manifest entries or `manifest_actions[]` for reusable media and deferred assets
- `remotion-template.schema.json`: referenced template contract paths only; implementation stays with Remotion Clip Builder

## Status Policy

- Return `complete` when a versioned format has evidence-backed rules, freshness policy, anti-redundancy thresholds, and downstream invalidation.
- Return `needs_approval` when format activation depends on licensed assets, user-owned brand materials, paid provider outputs, direct screenshot reuse, or a user waiver.
- Return `blocked` when there is not enough evidence to create even an experimental format or when format rules would require protected copying.
- Return `needs_revision` when source/reference/style inputs conflict, freshness evidence is too old, or required channel profile data is missing.

## Evidence Required

Every durable `must_reuse`, `must_vary`, anti-redundancy, template, asset, voice, caption, thumbnail, or VFX rule must include evidence refs, source ids, explicit user/Director instruction, or producer-criteria rule. If audience evidence is missing, mark `format_type: experimental` or `status: needs_review`.

## Media Manifest Policy

If this skill references, promotes, validates, or defers reusable media assets, brand assets, audio identity assets, Remotion template media, source cards, overlays, thumbnail assets, or reference-derived examples, update the media asset manifest or return `manifest_actions[]`.

Each manifest action must include `action`, `asset_id`, `canonical_path`, `remotion_public_path` and `static_file_path` when relevant, `rights_state`, `technical_metadata_state`, and `reason`.

Use `deferred` for format rules that need a future asset, template, public projection, rights approval, or metadata probe. Channel format must not become the only record of a media asset's identity, rights, or render-visible path.

## Approval And Stop Conditions

Stop before activating a format that depends on unapproved licensed assets, copied references, direct article/page imagery, voice likeness, paid provider output, or unclear rights. Return `needs_revision` when a format would make future videos too repetitive because `must_vary` rules or freshness triggers are missing.

## Definition Of Done

- The channel format is versioned and points to source/channel/project paths.
- Durable rules have evidence, confidence, and lifecycle policy.
- `must_reuse`, `must_vary`, and experimental rules are separated.
- Anti-redundancy thresholds and freshness triggers are explicit.
- Downstream invalidation impact is routable by the Director.

## Handoff Summary Shape

Return:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "artifact_paths": ["string"],
  "changed_files": ["string"],
  "populated_contracts": ["codex/contracts/channel-format.schema.json"],
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
  "validation_performed": ["evidence coverage", "version/freshness review", "must-vary review", "anti-redundancy threshold check", "manifest check"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
