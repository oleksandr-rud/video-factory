---
name: pexels-video-search
description: Search Pexels stock videos as a secondary/free fallback provider, normalize candidates, preserve attribution and rate-limit evidence, and guard local file downloads with scoped approval. Use when Freepik is unavailable, unsuitable, or needs fallback coverage for scene-level visual search.
---

# Pexels Video Search

Pexels is a secondary provider-specific implementation of `provider-clip-search`. Treat it as candidate discovery until a candidate passes rights, attribution, technical, and final-use checks.

Read `../../references/video-search-providers.md` before using Pexels.

## Inputs

- Scenario scene ids and visual goals
- Query groups from `visual-research-queries`
- Candidate requirements from the visual pack
- Project path, run id, candidate output directory, provider clip output directory, and media asset manifest path
- Pexels API availability, rate-limit state, license policy, attribution policy, and final-use policy
- Director approval scope for API search, file download, and final use

## Workflow

1. Select Pexels as a secondary stock route when Freepik/Magnific is unavailable, returns weak matches, or a free stock fallback is preferable.
2. Convert each scene query into a concise search term plus optional `orientation`, `size`, and `locale` notes.
3. Dry-run first: run `../../scripts/search_pexels_videos.py` without `--execute` to write the request plan. This does not call the API.
4. Execute search only when Pexels API search is approved:
   ```powershell
   python codex/agents/visual-producer/scripts/search_pexels_videos.py --term "<query>" --scene-id "<scene-id>" --output "<search-results-path>" --candidate-dir "<project>/visuals/candidates" --execute --approved-api-search
   ```
   `--approved` is accepted as a legacy alias for API search only.
5. Store normalized search artifacts:
   - raw/search payload: `visuals/candidates/search-results/pexels/<scene-id>-<query-slug>-<run-id>.json`
   - individual candidates when `--candidate-dir` is passed: `visuals/candidates/<scene-id>/<candidate-id>.json`
6. Preserve Pexels metadata: video id, page URL, thumbnail/image URL, duration, dimensions, user/creator, creator URL, `video_files[]`, selected video file, `video_pictures[]`, request URL, and rate-limit headers.
7. Set candidate route/status:
   - `route: stock_clip`
   - `provider: pexels`
   - `status: proposed` after search when license and preview metadata are present
   - `status: needs_approval` when final-use, likeness/logo, attribution, or file download scope is unclear
8. Pre-check candidates before file download:
   - semantic fit
   - duration/aspect/resolution fit
   - preview and crop risk
   - Pexels license restrictions: no misleading endorsement, no offensive bad-light use of identifiable people, no unmodified resale, no stock/wallpaper redistribution, no trademark/service-mark use
   - Pexels API attribution/link-back requirement and creator credit where possible
   - continuity and safe-area risk
9. Save downloaded files only when file download/storage is approved:
   ```powershell
   python codex/agents/visual-producer/scripts/search_pexels_videos.py --term "<query>" --scene-id "<scene-id>" --output "<search-results-path>" --candidate-dir "<project>/visuals/candidates" --execute --approved-api-search --save-downloads --approved-file-download --download-video-id "<pexels-video-id>" --download-dir "<project>/source-media/provider-clips/pexels/<candidate-id>"
   ```
   The Pexels API search response already contains `video_files[].link`; there is no separate download-link retrieval endpoint. API-search approval must account for these direct file URLs being present in search output.
10. After download, update the candidate `local_path`, `status: downloaded`, and media manifest entry before ranking or timeline use.

## Required Output

Return:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "provider": "pexels",
  "search_results_path": "string",
  "candidate_paths": ["string"],
  "downloaded_asset_paths": ["string"],
  "scene_results": [
    {
      "scene_id": "string",
      "query": "string",
      "candidate_ids": ["string"],
      "rejected_candidate_ids": ["string"],
      "approvals_needed": ["api_search | file_download | final_use"],
      "pre_download_checks": [
        {
          "candidate_id": "string",
          "pexels_video_id": "string",
          "semantic_fit": "pass | fail | partial | unknown",
          "technical_fit": "pass | fail | partial | unknown",
          "rights_fit": "pass | fail | needs_approval | unknown",
          "preview_fit": "pass | fail | partial | unknown",
          "attribution_fit": "pass | fail | needs_approval | unknown",
          "recommendation": "validate | reject | request_file_download_approval | search_more"
        }
      ]
    }
  ],
  "next_recommended_step": "string"
}
```

Each normalized candidate must populate `codex/contracts/clip-candidate.schema.json` fields:

- `candidate_id`
- `scene_id`
- `project_id`, `project_path`, `channel_slug`, and `media_asset_manifest_path` when available
- `route: stock_clip`
- `provider: pexels`
- `source_url`
- `preview_url`
- `prompt_or_query`
- `license_summary`
- `cost_estimate`
- `technical.duration_seconds`
- `technical.width` and `technical.height` when available
- `scores` initialized or updated
- `status`
- `rejection_reason` when rejected

## Contract Fields Populated

- `clip-candidate.schema.json`: candidate files under `visuals/candidates/<scene-id>/`
- `video-project.schema.json`: `artifacts.clip_candidate_paths[]` when the project index is updated
- `media-asset-manifest.schema.json`: only for local previews, metadata files, downloaded clips, or Remotion public projections

## Status Policy

- Return `complete` when dry-run/search/normalization completed and next approval or validation step is explicit.
- Return `needs_approval` when API search, file download, final-use approval, attribution display, or rights-sensitive context approval is needed.
- Return `blocked` when approved execution lacks credentials, Pexels terms are incompatible with the intended use, quota risk cannot be bounded, or no candidate can satisfy scene requirements.
- Return `needs_revision` when query inputs or scene requirements are too vague for reliable search.
- Keep candidates out of `approved` status until `visual-validation` and `clip-candidate-ranking` validate them for final use.

## Evidence Required

Preserve:

- Pexels video id
- Pexels page URL
- preview image URL and video pictures
- query, request URL, and rate-limit headers when available
- duration, dimensions, selected video file metadata, available `video_files[]`, creator name, and creator URL
- local filename/path when downloaded
- license, attribution/link-back notes, rights restrictions, and approval id when available

## Media Manifest Policy

Do not create manifest entries for remote-only candidates unless a local preview/metadata artifact is written.

When a file is downloaded, create or update an asset:

```json
{
  "kind": "stock_clip",
  "origin": "provider",
  "status": "loaded",
  "canonical_path": "channels/<channel-slug>/projects/<project-slug>/source-media/provider-clips/pexels/<candidate-id>/<filename>",
  "provider": "pexels",
  "provider_asset_id": "string",
  "rights": {
    "license_summary": "string",
    "usage_allowed": true,
    "approval_required": true,
    "attribution_required": true
  },
  "technical": {},
  "related_scene_ids": ["string"],
  "related_contract_paths": ["channels/<channel-slug>/projects/<project-slug>/visuals/candidates/<scene-id>/<candidate-id>.json"]
}
```

Return `manifest_actions[]` with `created`, `updated`, `deferred`, or `not_applicable`.

## Approval And Stop Conditions

Stop before API search unless the Director approved Pexels API use for the scoped project/scenes.

Stop before file download unless the Director approved local download/storage.

Stop before final use if attribution/link-back handling, likeness/logo context, source rights, trademark implication, endorsement risk, or license fit is unclear.

Stop when Pexels rate-limit headers indicate the approved quota scope is exhausted or too close to exhaustion for the batch.

## Definition Of Done

- Dry-run or executed search output is stored.
- Normalized candidate files exist under `visuals/candidates/` when `--candidate-dir` is supplied.
- Downloaded files, if any, exist only under `source-media/provider-clips/pexels/`.
- Candidates preserve Pexels metadata, license summary, attribution/link-back notes, preview evidence, and technical metadata or unknown markers.
- File downloads are impossible without the appropriate approval scope.
- Manifest actions are reported for any local artifact.

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
  "validation_performed": ["dry-run request plan", "Pexels search", "candidate normalization", "pre-download checks", "file-download approval check"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
