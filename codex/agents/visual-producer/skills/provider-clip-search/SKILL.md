---
name: provider-clip-search
description: Search, normalize, store, and pre-validate stock/provider video clip candidates before download or licensing. Use with Freepik/Magnific, Pexels, Pixabay, Shutterstock, internal libraries, or another approved content provider when scene-level stock candidates need rights, technical metadata, manifest policy, and approval gates.
---

# Provider Clip Search

Provider search is candidate discovery. A remote preview or search result is not a production asset until rights, technical fit, approval state, local storage, and manifest coverage are resolved.

Read `../../references/video-search-providers.md` when using Freepik/Magnific, Pexels, or another provider with documented API/search behavior.

## Inputs

- Scenario scene ids, visual goals, duration/aspect requirements, platform, and adjacent-scene context
- Query groups from `visual-research-queries`
- Scene visual pack candidate requirements and route priorities
- Project path, media asset manifest path, and candidate output directory
- Provider availability, credentials, rate limits, license policy, and budget policy
- Director approval state for provider API search, download-link/license retrieval, file download, and final use

## Workflow

1. Select providers based on scene need, route fit, rights policy, budget, account availability, and expected download quality.
   - Prefer Freepik/Magnific as the primary stock-video provider when an approved account/license route exists.
   - Use Pexels as a secondary/free fallback when Freepik is unavailable, unsuitable, or needs broader B-roll coverage.
2. Prepare exact dry-run search terms before any API call. Dry-run planning does not need provider approval.
3. Run provider API search only when the Director has approved the provider/search scope.
4. Normalize raw results into candidate records shaped like `codex/contracts/clip-candidate.schema.json`.
5. Store normalized candidates before download:
   - candidate batch or raw provider response: `channels/<channel-slug>/projects/<project-slug>/visuals/candidates/search-results/<provider>/<scene-id>-<query-slug>-<run-id>.json`
   - individual candidate records: `channels/<channel-slug>/projects/<project-slug>/visuals/candidates/<scene-id>/<candidate-id>.json`
6. Keep actual downloaded provider media separate:
   - `channels/<channel-slug>/projects/<project-slug>/source-media/provider-clips/<provider>/<candidate-id>/<filename>`
7. Pre-check each candidate before requesting a download link:
   - scene semantic fit
   - duration/aspect/quality fit
   - preview/watermark limitations
   - license summary and premium/credit risk
   - attribution requirements
   - continuity and safe-area risk
8. Set status:
   - `proposed` for non-paid, non-downloaded candidates with clear preview metadata but no final approval yet
   - `needs_approval` for paid/licensed/uncertain candidates, required download links, or required file downloads
   - `rejected` for unusable or rights-blocked candidates
   - `downloaded` only after approved file download and manifest update
9. Send candidates to `visual-validation`, then `clip-candidate-ranking`. Do not skip validation because provider metadata looked complete.

## Approval Model

Use the fewest approvals that are safe. One Director approval can cover a batch if it names the provider, project, scenes, max spend/quota, and allowed action. Keep approvals separate when the action changes risk:

- API search approval: allows provider API calls and possible rate-limit/logging exposure.
- Download-link/license retrieval approval: may consume quota, reveal final asset intent, or create licensing obligations.
- File download approval: writes licensed/copyrighted media into the project.
- Final-use approval: confirms the selected asset can be used in the render under the intended rights/attribution terms.

Do not ask repeatedly for the same approved scope. Do stop when the next action exceeds that scope.

## Required Output

Return:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "provider": "string",
  "search_results_path": "string",
  "candidate_paths": ["string"],
  "scene_results": [
    {
      "scene_id": "string",
      "query": "string",
      "provider": "string",
      "candidate_ids": ["string"],
      "rejected_candidate_ids": ["string"],
      "approvals_needed": ["api_search | download_link | file_download | final_use"],
      "pre_download_checks": [
        {
          "candidate_id": "string",
          "semantic_fit": "pass | fail | partial | unknown",
          "technical_fit": "pass | fail | partial | unknown",
          "rights_fit": "pass | fail | needs_approval | unknown",
          "preview_fit": "pass | fail | partial | unknown",
          "recommendation": "validate | reject | request_approval | search_more"
        }
      ]
    }
  ],
  "next_recommended_step": "string"
}
```

Each candidate record must populate:

- `candidate_id`
- `scene_id`
- `project_id`, `project_path`, `channel_slug`, and `media_asset_manifest_path` when available
- `route: stock_clip`
- `provider`
- `source_url`
- `preview_url`
- `prompt_or_query`
- `license_summary`
- `cost_estimate`
- `technical`
- `scores` initialized or updated
- `status`
- `rejection_reason` when rejected

## Contract Fields Populated

- `clip-candidate.schema.json`: normalized candidate files under `visuals/candidates/`
- `video-project.schema.json`: `artifacts.clip_candidate_paths[]` should include stored candidate file paths when the project index is updated
- `media-asset-manifest.schema.json`: updated only after local media, preview captures, thumbnails, metadata files, or downloads exist

## Status Policy

- Return `complete` when candidate search/normalization completed and all next approvals/blockers are explicit.
- Return `needs_approval` when the next action is API execution, download-link retrieval, file download, paid/premium use, unclear license, or final-use approval.
- Return `blocked` when provider terms are incompatible, credentials are missing for an approved provider call, or no usable candidates can be found.
- Return `needs_revision` when scene requirements or query groups are too ambiguous to search safely.

## Evidence Required

Every candidate must preserve:

- provider name
- source URL or provider asset id
- preview URL or thumbnail URL when available
- query/prompt used
- duration/aspect/fps/resolution when available
- license summary and premium/credit state
- attribution/author when available
- technical unknowns and rights unknowns

Missing technical or rights evidence is allowed for early search, but it must keep the candidate out of `approved` status.

## Media Manifest Policy

Do not create media manifest entries for remote-only search results unless the project intentionally tracks remote previews as referenced assets.

Create or update manifest entries when:

- a provider clip is downloaded
- a preview or thumbnail is captured locally
- provider metadata/probe output is written as a project artifact
- a file is mirrored into Remotion public projection

Downloaded provider clips must use:

- `kind: stock_clip`
- `origin: provider`
- `canonical_path` under `source-media/provider-clips/`
- `provider`, `provider_asset_id`, rights state, approval state, technical metadata, related scene ids, related candidate path, and evidence refs

Return `manifest_actions[]` with `created`, `updated`, `deferred`, or `not_applicable`.

## Approval And Stop Conditions

Stop before any provider API call unless the Director approved provider search scope.

Stop before download-link or license retrieval unless the Director approved that action.

Stop before file download unless the Director approved local storage of the selected provider asset.

Stop before final timeline use when license, attribution, likeness/logo, premium/credit, or source rights remain unclear.

## Definition Of Done

- Search terms and provider choices are recorded.
- Candidate files are stored under `visuals/candidates/` before download.
- Actual media files, if any, are stored under `source-media/provider-clips/`.
- Every candidate has status, provenance, license summary, technical metadata or unknown markers, and pre-download check results.
- Download actions are impossible without the appropriate approval scope.
- Next step is clear: validate/rank, request approval, search more, or use fallback route.

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
  "validation_performed": ["provider selection", "query preparation", "candidate normalization", "pre-download rights check", "pre-download technical check"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
