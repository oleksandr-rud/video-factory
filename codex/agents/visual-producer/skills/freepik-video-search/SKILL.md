---
name: freepik-video-search
description: Search Freepik/Magnific stock videos, normalize candidates, store candidate artifacts, and guard download-link/file-download steps with scoped approvals. Use when Freepik is an approved or likely stock provider for scene-level visual search and downloadable clips.
---

# Freepik Video Search

Freepik/Magnific is a provider-specific implementation of `provider-clip-search`. Treat it as discovery until a candidate passes pre-download checks and the Director approves the next action.

Read `../../references/video-search-providers.md` before using Freepik/Magnific.

## Inputs

- Scenario scene ids and visual goals
- Query groups from `visual-research-queries`
- Candidate requirements from the visual pack
- Project path, run id, candidate output directory, provider clip output directory, and media asset manifest path
- Budget, account/API availability, provider quota, license policy, and attribution policy
- Director approval scope for API search, download-link retrieval, file download, and final use

## Workflow

1. Select Freepik only when stock footage is a practical route for the scene.
2. Convert each scene query into a concise search term plus filter/order/language notes.
3. Dry-run first: run `../../scripts/search_freepik_videos.py` without `--execute` to write the request plan. This does not call the API.
4. Execute search only when provider API search is approved:
   ```powershell
   python codex/agents/visual-producer/scripts/search_freepik_videos.py --term "<query>" --scene-id "<scene-id>" --output "<search-results-path>" --execute --approved-api-search
   ```
   `--approved` is accepted as a legacy alias for API search only.
5. Normalize search results into candidate files:
   - raw/search payload: `visuals/candidates/search-results/freepik/<scene-id>-<query-slug>-<run-id>.json`
   - individual candidates: `visuals/candidates/<scene-id>/<candidate-id>.json`
6. Preserve Freepik metadata: video id, page URL, name, duration, quality, premium flag, fps, aspect ratio, author, previews, thumbnails, tags, AI-generated flag, item subtype, query, and request URL.
7. Set candidate route/status:
   - `route: stock_clip`
   - `provider: freepik`
   - `status: needs_approval` until rights/download/final-use approval is resolved
8. Pre-check candidates before download-link retrieval:
   - semantic fit
   - duration/aspect/quality fit
   - preview/watermark limitations
   - premium/credit/quota risk
   - license and attribution notes
   - safe-area/crop risk
9. Request download links only when approved:
   ```powershell
   python codex/agents/visual-producer/scripts/search_freepik_videos.py --term "<query>" --scene-id "<scene-id>" --output "<search-results-path>" --execute --approved-api-search --request-download-links --approved-download-links
   ```
10. Save downloaded files only when file download/storage is approved:
   ```powershell
   python codex/agents/visual-producer/scripts/search_freepik_videos.py --term "<query>" --scene-id "<scene-id>" --output "<search-results-path>" --execute --approved-api-search --request-download-links --approved-download-links --save-downloads --approved-file-download --download-dir "<project>/source-media/provider-clips/freepik/<candidate-id>"
   ```
11. After download, update the candidate `local_path`, `status: downloaded`, and media manifest entry before ranking or timeline use.

## Required Output

Return:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "provider": "freepik",
  "search_results_path": "string",
  "candidate_paths": ["string"],
  "downloaded_asset_paths": ["string"],
  "scene_results": [
    {
      "scene_id": "string",
      "query": "string",
      "candidate_ids": ["string"],
      "rejected_candidate_ids": ["string"],
      "approvals_needed": ["api_search | download_link | file_download | final_use"],
      "pre_download_checks": [
        {
          "candidate_id": "string",
          "freepik_video_id": "string",
          "semantic_fit": "pass | fail | partial | unknown",
          "technical_fit": "pass | fail | partial | unknown",
          "rights_fit": "pass | fail | needs_approval | unknown",
          "preview_fit": "pass | fail | partial | unknown",
          "recommendation": "validate | reject | request_download_link_approval | request_file_download_approval | search_more"
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
- `provider: freepik`
- `source_url`
- `preview_url`
- `prompt_or_query`
- `license_summary`
- `cost_estimate`
- `technical.duration_seconds`
- `technical.fps` when available
- `scores` initialized or updated
- `status`
- `rejection_reason` when rejected

## Contract Fields Populated

- `clip-candidate.schema.json`: candidate files under `visuals/candidates/<scene-id>/`
- `video-project.schema.json`: `artifacts.clip_candidate_paths[]` when the project index is updated
- `media-asset-manifest.schema.json`: only for local previews, metadata files, downloaded clips, or Remotion public projections

## Status Policy

- Return `complete` when dry-run/search/normalization completed and next approval or validation step is explicit.
- Return `needs_approval` when API search, download-link retrieval, file download, premium/credit use, or final-use approval is needed.
- Return `blocked` when approved execution lacks credentials, provider terms are unclear, quota risk cannot be bounded, or no candidate can satisfy scene requirements.
- Return `needs_revision` when query inputs or scene requirements are too vague for reliable search.
- Keep candidates as `needs_approval` until final rights/download state is clear; only `visual-validation` and `clip-candidate-ranking` may promote to selected/approved use.

## Evidence Required

Preserve:

- Freepik/Magnific video id
- Freepik page URL
- preview or thumbnail URL
- query and request URL
- duration, quality, premium flag, fps, aspect ratio, author, tags, and AI-generated flag when available
- download response metadata when requested
- filename, signed URL or URL, and local path when downloaded
- license/attribution notes and approval id when available

## Media Manifest Policy

Do not create manifest entries for remote-only candidates unless a local preview/metadata artifact is written.

When a file is downloaded, create or update an asset:

```json
{
  "kind": "stock_clip",
  "origin": "provider",
  "status": "loaded",
  "canonical_path": "channels/<channel-slug>/projects/<project-slug>/source-media/provider-clips/freepik/<candidate-id>/<filename>",
  "provider": "freepik",
  "provider_asset_id": "string",
  "rights": {
    "license_summary": "string",
    "usage_allowed": true,
    "approval_required": true
  },
  "technical": {},
  "related_scene_ids": ["string"],
  "related_contract_paths": ["channels/<channel-slug>/projects/<project-slug>/visuals/candidates/<scene-id>/<candidate-id>.json"]
}
```

Return `manifest_actions[]` with `created`, `updated`, `deferred`, or `not_applicable`.

## Approval And Stop Conditions

Stop before API search unless the Director approved Freepik/Magnific API use for the scoped project/scenes.

Stop before download-link retrieval unless the Director approved download-link/license retrieval.

Stop before file download unless the Director approved local download/storage.

Stop before final use if license, attribution, premium/credit, AI-generated status, likeness/logo, or source rights are unclear.

## Definition Of Done

- Dry-run or executed search output is stored.
- Normalized candidate files exist under `visuals/candidates/`.
- Downloaded files, if any, exist only under `source-media/provider-clips/freepik/`.
- Candidates preserve Freepik metadata, license summary, cost/quota risk, preview evidence, and technical metadata or unknown markers.
- Download-link and file-download actions are guarded by separate approval scope.
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
  "validation_performed": ["dry-run request plan", "Freepik search", "candidate normalization", "pre-download checks", "download approval check"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
