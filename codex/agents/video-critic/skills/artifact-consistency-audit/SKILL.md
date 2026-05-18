---
name: artifact-consistency-audit
description: Audit final video artifacts for contract, provenance, media manifest, timing, caption, voiceover, visual candidate, rights, and platform consistency with critique-report-shaped findings. Use before or alongside multimodal critique to catch errors a visual model may miss.
---

# Artifact Consistency Audit

Use this to catch contract and provenance failures before release review. This skill audits artifacts and returns findings; it does not edit production artifacts directly.

## Inputs

- Render package and final/preview video path
- Scenario, producer criteria, channel format, reference analysis, and source evidence
- Timeline sync plan, voiceover package, caption JSON/SRT, subtitle policy, and audio mix notes
- Scene visual pack, clip candidates, AI video generation packages, Remotion clip packages, and Remotion template contracts
- Media asset manifest with source, generated, rendered, subtitle, thumbnail, review, and delivery assets
- Render QA result, review package, sampled frames, and platform/delivery requirements when available

## Workflow

1. Verify identity consistency across render, scenario, timeline sync, voiceover, visual pack, media manifest, and critique inputs.
2. Check scene order, scene ids, timing ranges, frame ranges, duration, platform, aspect ratio, fps, width, and height.
3. Check timeline sync coverage: every scene has visual, audio, caption, transition/safe-area data or an explicit blocker.
4. Check captions and voice:
   - caption JSON/SRT exists where required
   - voiceover package scene ids match scenario scene ids
   - caption timing maps to scene timing
   - pronunciation/timing blockers are recorded
5. Check visual provenance:
   - selected clip candidates or Remotion clip packages are traceable
   - stock, AI-generated, user-supplied, approved web image, source-card recreation, and Remotion-generated routes are correctly labeled
   - helper-selected visuals are flagged unless Director-approved
   - source/output asset ids, local paths, and Remotion static paths exist where required
   - `approved_web_image` routes have manifest-backed rights approval and local/render-visible paths
   - `source_card_recreation` routes preserve source ids, claim ids, and evidence refs instead of copying article/page material without approval
6. Check Remotion template and VFX provenance:
   - template ids and contract paths exist
   - template-backed instances respect safe-area/props contracts
   - VFX rule refs and hardening evidence are traceable when required
7. Check media asset manifest coverage for loaded media, web snapshots, source reports, web images, screenshots, generated clips, renders, subtitles, thumbnails, review frames, and metadata files.
8. Check rights and approvals for paid generation, licensed media, voices, music, likeness, logos, screenshots, paid templates, and external critique.
9. Return critique-report-shaped findings with owner mapping and blocks-delivery flags.

## Required Output

Populate or update the artifact-audit portion of `codex/contracts/critique-report.schema.json`:

- `inputs`
- `findings[]`
- `limitations[]`
- `qa.status`
- `qa.summary`
- `qa.residual_risks[]`

Return this audit summary:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "critique_id": "string",
  "render_id": "string",
  "audit_status": "pass | fail | partial | unknown",
  "artifact_checks": [
    {
      "check_id": "string",
      "category": "identity | timing | captions | voiceover | visuals | remotion | manifest | rights | platform | technical",
      "status": "pass | fail | partial | unknown | needs_approval",
      "evidence": "string",
      "blocking_reasons": ["string"]
    }
  ],
  "findings": [
    {
      "finding_id": "string",
      "severity": "blocker | major | minor | note",
      "category": "story | hook | pacing | visual | audio | subtitles | sync | brand | platform | factual | rights | technical | accessibility | engagement | redundancy | other",
      "scene_id": "string",
      "timestamp_seconds": 0,
      "artifact_path": "string",
      "evidence": "string",
      "description": "string",
      "recommendation": "string",
      "owner_agent": "director | channel-intelligence | creative-producer | visual-producer | invideo-ai-generator | remotion-clip-builder | remotion-video-producer | video-critic",
      "blocks_delivery": true
    }
  ],
  "limitations": ["string"],
  "next_recommended_step": "string"
}
```

## Contract Fields Populated

- `critique-report.schema.json`: `inputs`, `findings`, `limitations`, `qa`
- `media-asset-manifest.schema.json`: not edited by this skill, but missing or stale entries are reported as findings
- `production-run.schema.json`: not edited directly; Director uses findings to route reruns and stale-artifact state

## Status Policy

- Return `complete` when the audit ran and all findings/limitations are captured, even if the audit fails.
- Return `needs_approval` when unresolved approval, rights, paid provider, likeness, voice, or waiver decisions block delivery.
- Return `blocked` when required artifacts are missing so the audit cannot establish render provenance or release risk.
- Return `needs_revision` when artifacts contradict each other and the owning production agent must repair them before critique.
- Audit `qa.status` is `pass` only when no blocker/major provenance, rights, sync, or manifest issues remain.

## Evidence Required

Every finding must include concrete evidence from at least one of:

- artifact path
- schema field/value
- scene id
- timestamp or frame range
- media asset id
- source id/evidence ref
- caption or voiceover path
- render output or metadata path
- approval record or rights note
- template or Remotion clip package path

If evidence is missing, record a limitation and, when release risk is affected, a finding.

## Media Manifest Policy

This skill usually audits rather than writes manifest entries. Return `manifest_actions[]`:

- `not_applicable` when no media artifact was created or modified
- `deferred` when a missing manifest entry must be created by the owning production agent
- `updated` only if the audit explicitly writes an audit/report asset into the manifest under Director-approved workflow

Missing manifest coverage for any real media file, generated clip, render, subtitle, thumbnail, review frame, or Remotion public projection must be a finding when it affects provenance, rights, technical validation, or reproducibility.

## Approval And Stop Conditions

Stop and return `needs_approval` when release depends on unapproved paid generation, licensed media, voice/likeness use, paid templates, external critique, or user waiver.

Stop and return `blocked` when:

- render package or scenario is missing
- final video path is missing when required for delivery audit
- scene ids cannot be reconciled across core artifacts
- selected visuals cannot be traced to candidates or clip packages
- rights/provenance gaps prevent safe release judgment
- manifest absence makes media lineage unverifiable

## Definition Of Done

- Core artifacts are checked for identity, timing, caption, voiceover, visual, Remotion, manifest, rights, and platform consistency.
- Findings use the critique report finding shape and include owner mapping.
- Every blocker has a recommended owner and action.
- Limitations are explicit and do not hide release risk.
- Director can route fixes without reading unstructured audit prose.

## Handoff Summary Shape

Return:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "artifact_paths": ["string"],
  "changed_files": ["string"],
  "populated_contracts": ["codex/contracts/critique-report.schema.json"],
  "manifest_actions": [
    {
      "action": "created | updated | not_applicable | deferred",
      "asset_id": "string",
      "reason": "string"
    }
  ],
  "validation_performed": ["identity consistency", "scene timing", "caption coverage", "voiceover linkage", "visual provenance", "Remotion template provenance", "manifest coverage", "rights approval audit", "platform delivery check"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
