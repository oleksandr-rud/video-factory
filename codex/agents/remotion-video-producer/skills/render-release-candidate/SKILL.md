---
name: render-release-candidate
description: Produce an immutable, reproducible render release candidate package for a Remotion video. Use when an assembled composition needs RC versioning, exact render commands, input/output hashes, subtitles, metadata, technical QA status, rights notes, known blockers, or fallback exports.
---

# Render Release Candidate

Use this after the Remotion composition is assembled and before Video Critic review. Treat each RC as a build attestation: immutable after creation, reproducible from recorded inputs, and comparable to later RC versions.

## Inputs

- Scenario, producer criteria, channel format, and platform/export requirements
- Remotion project contract, app root, composition id, composition type, fps, dimensions, duration, and render settings
- Timeline source path and timeline sync plan path
- Input props path and props hash when props are externalized
- Voiceover package, caption JSON/SRT, music/SFX, source clip packages, source template contracts, and media asset manifest
- Source/output asset ids, web source report paths, approved web image/screenshot ids, rights approvals, budget approvals, and known waivers
- Existing RC packages when creating `rc2`, `rc3`, or later revisions
- Render logs, metadata probes, thumbnails, QA report paths, and critique report paths when already created

## Workflow

1. Assign the next immutable `rc_version` and `render_attempt_id`. Never mutate a previous RC; create a new version when any input, code, asset, setting, subtitle, or export changes.
2. Confirm the reproducibility envelope:
   - git commit or dirty worktree state
   - Remotion app root and project contract path/hash
   - composition id and render settings
   - input props path/hash
   - timeline source path/hash and timeline sync plan path/hash
   - media asset manifest path/hash
   - source clip package paths/hashes
   - template contract paths/hashes
   - web source reports, claim/evidence refs, and approved web image/screenshot asset ids when source-card or web-image routes are used
   - dependency versions and render environment
3. Run the lightest meaningful validation first:
   - representative still frame checks
   - Studio/browser preview when available
   - metadata/probe checks for source assets when relevant
   - full render only when dependencies, approvals, and time allow
4. Render the RC with an explicit output path, exact command, and captured log path.
5. Emit required sidecars: separate `.srt`, caption JSON, thumbnails, metadata probe, render log, QA report, and fallback exports when requested.
6. Verify output metadata with Remotion, FFprobe, Mediabunny, or available repo tooling.
7. Calculate or record output hashes for the video and sidecars whenever files exist.
8. For VFX-heavy renders, record render time, slowest frames, benchmark commands, VFX rule refs, alpha/export behavior, decode risk, and optimization notes in `performance_summary`.
9. Run `../render-qa/SKILL.md`; attach the technical QA report path and status.
10. Write a render package matching `codex/contracts/render-package.schema.json`, including the RC attestation fields even when they are stored as additional JSON properties.
11. Update or request updates to the media asset manifest for rendered video, subtitle sidecars, thumbnails, metadata, render logs, QA reports, review-prep outputs, and any consumed web snapshots/source reports/approved web images/screenshots.

## Required Output

Write a render package with:

```json
{
  "render_id": "project-rc1",
  "rc_version": "rc1",
  "render_attempt_id": "string",
  "scenario_id": "string",
  "composition_id": "string",
  "status": "planned | previewed | rendered | blocked | approved | rejected",
  "timeline_path": "string",
  "timeline_sync_plan_path": "string",
  "media_asset_manifest_path": "string",
  "remotion_project_contract_path": "string",
  "render_provenance": {
    "git_commit_or_worktree_state": "string",
    "input_props_path": "string",
    "input_props_hash": "sha256:string",
    "timeline_sync_plan_hash": "sha256:string",
    "media_asset_manifest_hash": "sha256:string",
    "source_clip_package_hashes": [],
    "template_contract_hashes": [],
    "render_environment": {},
    "dependency_versions": {}
  },
  "outputs": [
    {
      "kind": "video | preview_video | subtitle_srt | caption_json | thumbnail | metadata | qa_report | critique_report",
      "path": "string",
      "media_asset_id": "string",
      "static_file_path": "string",
      "sha256": "string"
    }
  ],
  "render_commands": [
    {
      "purpose": "preview | still_check | full_render | metadata_probe | fallback_export",
      "command": "string",
      "completed": true,
      "log_path": "string",
      "notes": "string"
    }
  ],
  "subtitles": {},
  "audio_mix": {},
  "performance_summary": {},
  "rights_notes": [],
  "known_blockers": [],
  "manifest_actions": [],
  "qa": {
    "status": "pass | fail | partial | not_run",
    "summary": "string",
    "findings": []
  }
}
```

## Contract Fields Populated

- `render-package.schema.json`: `render_id`, `scenario_id`, project/channel paths, `media_asset_manifest_path`, `remotion_project_contract_path`, `remotion_app_root_path`, `composition_id`, `timeline_path`, `timeline_sync_plan_path`, `voiceover_package_path`, `source_clip_packages`, `source_template_contracts`, `source_asset_ids`, `output_asset_ids`, export specs, `status`, `outputs`, `render_commands`, `subtitles`, `audio_mix`, `performance_summary`, `delivery_variants`, `rights_notes`, `evidence_refs`, `known_blockers`, and `qa`
- Additional render package properties: `rc_version`, `render_attempt_id`, `render_provenance`, hashes, log paths, and immutable version notes
- `media-asset-manifest.schema.json`: entries for render outputs, preview outputs, subtitles, captions, thumbnails, metadata probes, QA reports, critique sidecars, and delivery variants
- `production-run.schema.json` or project index when the Director records the RC path and review-loop state

## Status Policy

- Return `rendered` only when the full RC video exists, output metadata was probed, required sidecars are present or explicitly waived, output hashes are recorded, and technical render QA was run.
- Return `previewed` when still/preview validation exists but full render has not completed.
- Return `planned` when commands and paths are prepared but no render or preview exists.
- Return `blocked` when render execution, required assets, required approvals, caption/audio readiness, rights, or reproducibility evidence are missing.
- Do not set `approved` for final release. Video Critic plus Director own final release approval or waiver.

## Evidence Required

Every RC must preserve:

- RC version and render attempt id
- exact render command and working directory
- render log path or explicit reason no log exists
- source input paths and hashes for timeline, props, manifest, clip packages, and template contracts
- Remotion project contract path and dependency versions
- output paths, media asset ids, metadata probe paths, and hashes
- subtitle/caption paths and hashes when present
- thumbnail paths when generated
- technical QA report path and summary
- source-card claim ids/evidence refs or approved web image/screenshot asset ids when those routes appear in the timeline sync plan
- rights notes, waiver ids, and known blockers

Missing evidence must appear in `known_blockers` or `qa.findings`; do not treat it as implied by the render command.

## Media Manifest Policy

If this skill creates, validates, consumes, or defers any media or sidecar artifact, return `manifest_actions[]`:

```json
{
  "action": "created | updated | consumed | validated | mirrored_to_remotion_public | deferred | not_applicable",
  "asset_id": "string",
  "canonical_path": "string",
  "remotion_public_path": "string",
  "static_file_path": "string",
  "rights_state": "approved | needs_approval | blocked | unknown",
  "technical_metadata_state": "present | missing | partial",
  "reason": "string"
}
```

Use `created` for new RC video, subtitles, captions, thumbnails, metadata probes, QA reports, and delivery variants. Use `consumed` for source visual/audio assets. Use `deferred` when the file exists but the manifest cannot be updated in this handoff.

## Approval And Stop Conditions

Stop and return `blocked` before full render when:

- paid rendering, cloud rendering, licensed media, provider download, or external generation lacks Director approval
- required local source assets, source reports, `staticFile()` projections, or audio/caption files are missing
- timeline sync has failed QA or includes `helper_selected: true` without Director review
- timeline sync uses `approved_web_image` without manifest-backed rights approval, or `source_card_recreation` without claim/source evidence refs
- rights notes block delivery
- exact render command, output path, or reproducibility envelope cannot be recorded
- a previous RC would need mutation instead of creating a new version

Use fallback export commands only when requested or needed for delivery variants; do not create unapproved paid/cloud variants.

## Definition Of Done

- The RC package is more than an MP4: it includes outputs, sidecars, commands, logs, hashes, metadata, QA, rights notes, and blockers.
- A later agent can rerun or compare the RC from recorded inputs, versions, commands, and hashes.
- Previous RC versions remain immutable and traceable.
- Media manifest actions cover every rendered, consumed, or sidecar artifact.
- Technical render QA is attached, and final release judgment remains with Video Critic plus Director.

## Handoff Summary Shape

Return:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "artifact_paths": ["string"],
  "changed_files": ["string"],
  "populated_contracts": ["codex/contracts/render-package.schema.json"],
  "manifest_actions": [
    {
      "action": "created | updated | consumed | validated | mirrored_to_remotion_public | deferred | not_applicable",
      "asset_id": "string",
      "reason": "string"
    }
  ],
  "validation_performed": ["still checks", "preview", "full render", "metadata probe", "hash capture", "technical render QA"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
