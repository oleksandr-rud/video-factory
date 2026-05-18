---
name: channel-profile-management
description: Create, update, and validate persistent Video Factory channel folders under channels/<channel-slug>, including channel-profile.json, brand assets, color palette, formats, rules, references, audio voice profile, project registry, governance metadata, and paths used by production contracts. Use when a run names a channel, creates a new channel, updates channel branding, creates a channel project, or needs channel-level defaults for many videos.
---

# Channel Profile Management

Use this before `channel-format-synthesis` when a channel is named or when reusable channel identity is needed. Preserve existing channel state unless the user, supplied evidence, or approved source artifacts explicitly update it.

## Inputs

- User/Director channel request, channel slug/name, project slug, domain, audience, platforms, language, timezone, and durable-channel intent
- Existing `channels/<channel-slug>/channel-profile.json` when present
- Existing project registry, channel formats, rules, references, brand assets, audio assets, and media asset manifests
- Source/reference evidence, brand guidelines, producer criteria, and media asset manifest paths when available
- Budget, rights, and approval policy for brand/media asset copying or external provider work

## Folder Layout

Create or update this structure when a durable project exists:

```text
channels/<channel-slug>/
  channel-profile.json
  brand/
    color-palette.json
    logos/
    typography/
    imagery/
  formats/
  references/
    source-ledger.json
    reference-videos/
    evidence/
  rules/
    production-rules.md
    voice-and-tone.md
    rights-and-approvals.md
  assets/
    visual/
    audio/
    remotion/
  projects/
    <project-slug>/
      project.json
      production-run.json
      producer-criteria.json
      media-asset-manifest.json
      scenario/
      voiceover/
      visuals/
        candidates/
      source-media/
        reference-videos/
        reference-analysis/
        web-content/
        loaded-videos/
        provider-clips/
        generated-clips/
      remotion/
        props/
        clips/
        timeline/
        public-projection/
      renders/
        previews/
        rc/
        final/
      reviews/
        assets/
        evidence/
      runs/
      delivery/
```

## Workflow

1. Resolve the channel slug, channel name, domain, audience, platforms, language defaults, root path, and whether this is a durable channel or one-off project.
2. For new channel/project workspaces, use `../../scripts/scaffold_channel_project.py <channel-slug> <project-slug>` when a project slug is available; run with `--dry-run` first for risky paths. The script writes repo-relative contract paths and creates the shared Remotion public projection directory for the project.
3. Create or update `channels/<channel-slug>/channel-profile.json` matching `codex/contracts/channel-profile.schema.json`.
4. Capture brand identity: promise, values, positioning, personality, approved/avoid vocabulary, logos, colors, typography, imagery, thumbnail, caption, and motion rules.
5. Capture content strategy: content pillars, format registry paths, hero/hub/hygiene mix, upload schedule, anti-redundancy rules, and novelty requirements.
6. Capture audio identity: narrator persona, voice traits, must-avoid traits, accent/language policy, pace range, energy profile, pronunciation defaults, provider voice refs, reference audio, continuity policy, and rights notes.
   - If the channel has an exact recurring provider voice, record it under `audio_identity.voice_profile.provider_voice_refs[]` with `provider`, `voice_id`, `voice_name`, `selection_policy: "exact_required"`, usage such as `primary_narrator`, target language/accent or language code, model preference when known, rights state, and continuity notes.
   - Use `selection_policy: "preferred"` only when the voice is a strong preference that can be replaced by a better or more available candidate.
   - Use `selection_policy: "fallback"` for backup voices and `blocked` for deprecated or rights-blocked voices.
7. Capture governance: approval rules, rights rules, sensitive topics, owner notes, last reviewed timestamp, and change log.
8. When the user starts a durable video deliverable, create or update `channels/<channel-slug>/projects/<project-slug>/project.json` matching `codex/contracts/video-project.schema.json`.
9. Create or update `channels/<channel-slug>/projects/<project-slug>/media-asset-manifest.json` matching `codex/contracts/media-asset-manifest.schema.json` when reference videos, user media, provider clips, generated clips, Remotion outputs, review frames, or evidence files are in scope.
10. Compute a channel/profile delta. Record changed fields, unchanged inherited fields, missing assets, approval blockers, and downstream invalidation impact.
11. Write channel format artifacts into `channels/<channel-slug>/formats/` only when `channel-format-synthesis` owns the format update; this skill records paths and invalidation, not format-rule synthesis.

## Required Output

Return:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "channel_profile_path": "channels/<channel-slug>/channel-profile.json",
  "project_path": "channels/<channel-slug>/projects/<project-slug>/project.json",
  "media_asset_manifest_path": "channels/<channel-slug>/projects/<project-slug>/media-asset-manifest.json",
  "channel_profile_delta": {
    "channel_profile_id": "string",
    "channel_slug": "string",
    "version": "string",
    "changed_fields": [
      {
        "field_path": "metadata.name",
        "old_value_summary": "string",
        "new_value_summary": "string",
        "reason": "user_instruction | source_evidence | scaffold | governance_update | correction"
      }
    ],
    "unchanged_inherited_fields": ["string"],
    "missing_assets": ["string"],
    "approval_blockers": ["string"]
  },
  "project_scaffold_result": {
    "created": false,
    "updated": false,
    "dry_run_performed": false,
    "paths_created_or_confirmed": ["string"]
  },
  "downstream_invalidation": [
    {
      "change": "string",
      "affected_artifacts": ["channel_format | producer_criteria | scenario | voiceover_package | scene_visual_pack | ai_video_generation_package | remotion_clip_package | timeline_sync_plan | render_package | critique_report"],
      "owner_agent": "string",
      "required_action": "string"
    }
  ],
  "qa_summary": {
    "status": "pass | partial | fail | not_run",
    "checks": ["schema shape", "repo-relative paths", "project registry", "manifest path", "missing assets", "invalidation impact"],
    "risks": ["string"]
  },
  "next_recommended_step": "string"
}
```

## Contract Fields Populated

- `channel-profile.schema.json`: all required profile fields, folder layout, reference management, projects, evidence, and QA
- `video-project.schema.json`: project index and project artifact paths when a durable project is in scope
- `media-asset-manifest.schema.json`: initial manifest or manifest actions for channel/project assets
- `production-run.schema.json`: artifact paths, blockers, approvals, and invalidation impact when a run ledger exists
- `channel-format.schema.json`: only records existing format paths; format synthesis belongs to `channel-format-synthesis`

## Status Policy

- Return `complete` when profile/project paths are resolved, required contract fields are present, deltas are recorded, and downstream invalidation is clear.
- Return `needs_approval` when brand/media assets, voice references, copyrighted materials, paid/provider assets, or rights-sensitive profile changes require approval.
- Return `blocked` when the channel/project path is unsafe, required durable identity is missing, rights block use of required assets, or the scaffold cannot be created.
- Return `needs_revision` when channel identity fields are contradictory, too vague for reuse, or missing enough data that downstream format/scenario/voice work would be unreliable.

## Evidence Required

Every changed durable profile field must cite a user/Director instruction, supplied source, existing channel artifact, governance note, or scaffold action. Missing brand assets, audio references, logos, fonts, and media must be listed instead of invented.

## Media Manifest Policy

If this skill creates, consumes, validates, copies, mirrors, or defers any brand image, logo, typography file, reference media, audio asset, Remotion asset, project media folder, or evidence sidecar, update the project media asset manifest or return `manifest_actions[]`.

Each manifest action must include `action`, `asset_id`, `canonical_path`, `remotion_public_path` and `static_file_path` when relevant, `rights_state`, `technical_metadata_state`, `evidence_refs`, and `reason`.

Use `deferred` when an expected brand or media asset is missing, pending approval, or intentionally left outside the manifest. Do not let downstream agents infer media rights or canonical paths from the channel profile alone.

## Approval And Stop Conditions

Stop before copying, mirroring, or promoting brand assets, reference media, copyrighted materials, voice references, logos, fonts, or paid/provider assets without Director approval. Stop if a channel profile change would invalidate active downstream artifacts and the Director has not accepted the rerun scope.

## Definition Of Done

- Channel profile validates structurally against the profile contract.
- Project index and media manifest paths are created or explicitly deferred when a durable project exists.
- Changed fields, inherited fields, missing assets, approval blockers, and downstream invalidation are explicit.
- All paths are repo-relative POSIX strings.
- Downstream agents can inherit channel defaults without relying on conversation memory.

## Handoff Summary Shape

Return:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "artifact_paths": ["string"],
  "changed_files": ["string"],
  "populated_contracts": ["codex/contracts/channel-profile.schema.json", "codex/contracts/video-project.schema.json", "codex/contracts/media-asset-manifest.schema.json"],
  "manifest_actions": [
    {
      "action": "created | updated | consumed | validated | mirrored_to_remotion_public | deferred | not_applicable",
      "asset_id": "string",
      "canonical_path": "string",
      "remotion_public_path": "string",
      "static_file_path": "string",
      "rights_state": "approved | needs_approval | blocked | unknown",
      "technical_metadata_state": "present | missing | partial | not_applicable",
      "evidence_refs": ["string"],
      "reason": "string"
    }
  ],
  "validation_performed": ["schema shape", "folder layout", "project registry", "manifest path", "profile delta", "downstream invalidation"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
