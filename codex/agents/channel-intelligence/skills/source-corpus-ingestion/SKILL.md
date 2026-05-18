---
name: source-corpus-ingestion
description: Build a normalized, evidence-backed source ledger from user requests, scenario files, reference videos, URLs, blogs, web pages, channel data, brand assets, and best-practice specs. Use before reference analysis, channel format synthesis, scenario work, visual planning, or any production step that depends on source provenance or media manifest coverage.
---

# Source Corpus Ingestion

Create the source ledger before downstream agents depend on web pages, files, reference videos, screenshots, transcripts, brand assets, or channel data. Do not treat a supplied source as production-ready until rights, reusable scope, evidence coverage, and manifest handling are explicit.

## Inputs

- User request, Director brief, producer criteria, and project/channel paths
- Supplied URLs, blogs, web pages, uploaded/local files, transcripts, screenshots, thumbnails, reference videos, brand assets, channel data, best-practice specs, and user notes
- Existing channel profile, project index, source ledger, reference analysis, and media asset manifest when available
- Media handling, web access, paid/cloud analysis, download, and rights approval state
- Intended scope: reusable channel evidence, project-only evidence, or one-off scenario citation

## Workflow

1. Inventory every supplied source: user notes, scenario, local files, URLs, reference videos, transcripts, screenshots, channel data, brand assets, and best-practice specs.
2. Classify each source as `reference_video`, `local_video`, `webpage`, `blog`, `channel_data`, `best_practice`, `brand_asset`, or `user_note`.
   - Treat YouTube, Vimeo, or other watch-page URLs supplied as video references as `reference_video` sources, not generic web pages, when the requested use is visual, pacing, edit, or channel-format analysis.
   - Preserve the original watch URL as `path_or_url`/`source_url`, but do not treat it as local analysis evidence until it has a downloaded local video, transcript, thumbnail, screenshots, or approved direct-video observation.
3. Assign a stable `source_id` and record `kind`, `path_or_url`, local path, title, owner, date, rights state, confidence, and why the source matters.
4. Mark `reusable_scope` as `global_channel`, `project_only`, `scene_only`, `critique_only`, `do_not_use`, or `unknown`.
   - If a reference video's topic, product, audience, or factual content differs from the target channel/project, do not downgrade it automatically. Mark its content/claims as non-authoritative for the target brief, but keep it as `style_reference`, `visual_format_reference`, `edit_rhythm_reference`, or `composition_reference` when the user supplied it for visuals, pacing, layout, or format.
   - Record the mismatch explicitly in `why_it_matters`, `missing_assets`, `findings.evidence_gaps[]`, or `downstream_guidance` so Creative Producer avoids copying its facts while Channel Intelligence and Visual Producer still decompose its visuals.
5. For each local media file or captured artifact, resolve or create a media asset id and decide the manifest action.
6. For each reference video or local video, determine whether deeper reference analysis has enough local evidence: video file, transcript, screenshots, thumbnail, probe data, scene JSON, OCR, or approved direct-video observation.
7. Identify missing assets needed for deeper analysis: transcript, screenshots, video file, thumbnail, channel analytics, brand tokens, product source material, technical metadata, or rights details.
   - For YouTube reference videos, mark `video file`, `info json`, `thumbnail`, and `subtitles/transcript` as missing until an approved `yt-dlp` capture or user-supplied local file exists.
   - Stop for Director approval before external video download, transcript download, thumbnail download, or upload/pass-through to a paid/cloud model.
8. Mark unsupported, inaccessible, duplicate, stale, rights-blocked, or low-confidence sources instead of deleting them.
9. For durable channel/project work, choose repo-relative artifact destinations before reference breakdown starts:
   - channel-level references: `channels/<channel-slug>/references/`
   - project-specific reference analysis: `channels/<channel-slug>/projects/<project-slug>/source-media/reference-analysis/<source-id>/`
   - project-specific reference videos: `channels/<channel-slug>/projects/<project-slug>/source-media/reference-videos/`
   - project-specific web/article/blog/news captures: `channels/<channel-slug>/projects/<project-slug>/source-media/web-content/<source-id>/`
10. Return downstream guidance that says which sources are safe to use for script claims, visual style, voice/tone, reference breakdown, and final critique.
11. Build the evidence graph fields that downstream agents can consume directly: `source_ledger[]`, `claim_ledger[]`, `downstream_guidance`, and `invalidation_impact[]`.

## Batch Source Policy

When the Director supplies several reference videos and 10-20 direct content links:

- Create one stable `source_id` per URL or video before analysis starts; do not let downstream agents invent ids.
- Treat reference videos and web content as different evidence modes that merge into the same `reference-analysis.schema.json` artifact.
- For YouTube/video-platform reference URLs, download or otherwise capture the media into `source-media/reference-videos/` only after approval, then run local reference-video breakdown on the downloaded file. Do not pass raw watch-page URLs downstream as if they were manifest-backed media.
- Process web links as one-page captures by default, not as open-ended crawls. Only follow extra links when the Director explicitly requests a crawl scope.
- Store every web page under `source-media/web-content/<source-id>/` with raw HTML, extracted text/metadata, image manifest, annotations, and a source report.
- Download page images or capture browser screenshots only after approval; otherwise catalog image URLs and mark the media manifest action as deferred.
- Keep per-source artifacts small and independent so one failed source does not invalidate the whole corpus.

## Required Output

Return or update a source ledger compatible with `codex/contracts/reference-analysis.schema.json`:

```json
{
  "analysis_id": "string",
  "status": "complete | partial | blocked",
  "project_id": "string",
  "project_path": "string",
  "channel_profile_path": "string",
  "media_asset_manifest_path": "string",
  "source_ledger": [
    {
      "source_id": "string",
      "kind": "reference_video | local_video | webpage | blog | channel_data | best_practice | brand_asset | user_note | other",
      "path_or_url": "string",
      "local_path": "string",
      "owner": "string",
      "rights_state": "approved | needs_approval | blocked | unknown",
      "reusable_scope": "global_channel | project_only | scene_only | critique_only | do_not_use | unknown",
      "why_it_matters": "string",
      "missing_assets": ["string"],
      "evidence_refs": [],
      "confidence": "high | medium | low | unknown"
    }
  ],
  "claim_ledger": [
    {
      "claim_id": "string",
      "claim": "string",
      "source_ids": ["string"],
      "support_state": "supported | contradicted | unsupported | needs_review",
      "allowed_use": "script_claim | visual_context | style_reference | critique_context | do_not_use",
      "risk": "none | factual | rights | policy | stale | unknown",
      "confidence": "high | medium | low | unknown"
    }
  ],
  "sources": [
    {
      "source_id": "string",
      "kind": "reference_video | local_video | webpage | blog | channel_data | best_practice | brand_asset | user_note | other",
      "path_or_url": "string",
      "local_path": "string",
      "title": "string",
      "owner": "string",
      "date": "string",
      "rights": {
        "state": "approved | needs_approval | blocked | unknown",
        "notes": "string",
        "usage_allowed": false,
        "approval_required": true
      },
      "reusable_scope": "global_channel | project_only | scene_only | critique_only | do_not_use | unknown",
      "why_it_matters": "string",
      "asset_id": "string",
      "captured_artifacts": [],
      "missing_assets": [],
      "evidence_refs": [],
      "confidence": "high | medium | low | unknown"
    }
  ],
  "findings": {
    "source_claims": [],
    "visual_evidence_opportunities": [],
    "rights_or_policy_risks": [],
    "evidence_gaps": [],
    "confidence_notes": []
  },
  "reference_beats": [],
  "evidence_refs": [],
  "downstream_guidance": {
    "creative_producer": ["string"],
    "visual_producer": ["string"],
    "invideo_ai_generator": ["string"],
    "remotion_clip_builder": ["string"],
    "remotion_video_producer": ["string"],
    "video_critic": ["string"]
  },
  "invalidation_impact": [
    {
      "impact_id": "string",
      "change_or_gap": "source_added | source_removed | rights_changed | evidence_added | claim_changed | reusable_scope_changed",
      "affected_artifacts": ["channel_profile | channel_format | producer_criteria | scenario | scene_artifact_sync | voiceover | visual_pack | clip_candidates | ai_generation | remotion_template | remotion_clip | timeline_sync | render | critique | delivery_metadata"],
      "reason": "string",
      "owner_agent": "channel-intelligence | creative-producer | visual-producer | invideo-ai-generator | remotion-clip-builder | remotion-video-producer | video-critic",
      "severity": "blocker | major | minor | note",
      "recommended_action": "string"
    }
  ],
  "manifest_actions": []
}
```

Each source must include:

- stable `source_id`
- `kind`
- `path_or_url` and local path when available
- title, owner, date, rights state, reusable scope, and confidence
- `asset_id` or deferred manifest note for local media
- `captured_artifacts[]` for transcripts, thumbnails, screenshots, probe output, scene JSON, keyframes, OCR, or model observations
- `missing_assets[]` needed before production reliance
- `why_it_matters` and downstream usage notes

Every source-backed claim or candidate fact must either enter `claim_ledger[]` or be marked as not extracted yet in `findings.evidence_gaps[]`. Use `claim_ledger[]` for facts that may influence script claims, visual choices, critique gates, or source-card/citation content.

## Contract Fields Populated

- `reference-analysis.schema.json`: required fields `analysis_id`, `status`, `sources[]`, `source_ledger[]`, `claim_ledger[]`, `reference_beats[]`, `findings`, `downstream_guidance`, and `invalidation_impact[]`, plus `project_id`, `project_path`, `channel_profile_path`, `media_asset_manifest_path`, and `evidence_refs`
- Additional reference-analysis fields allowed by the contract: source-level `rights`, `reusable_scope`, `why_it_matters`, and `missing_assets`
- `media-asset-manifest.schema.json`: asset entries or deferred actions for local videos, images, transcripts, thumbnails, screenshots, probes, keyframes, OCR outputs, and other captured artifacts
- `channel-profile.schema.json` or project index only when the Director explicitly asks this skill to attach source ledger paths

## Status Policy

- Return `complete` when every supplied source has a stable id, classification, rights state, reusable scope, confidence, source-ledger entry, claim-ledger treatment, and manifest action when media exists.
- Return `partial` when some source metadata, rights, local copies, technical metadata, transcripts, screenshots, or manifest entries are missing but downstream work can proceed with limitations.
- Return `blocked` when required sources are inaccessible, rights prevent analysis, media handling is not approved, or source provenance is too weak for production use.
- Return handoff status `needs_approval` when the next useful step requires paid/cloud analysis, download, external media handling, or rights approval.

## Evidence Required

For every source, preserve at least one of:

- URL, local path, repo-relative artifact path, or media asset id
- supplied user note or Director brief field
- transcript, screenshot, thumbnail, probe JSON, scene JSON, keyframe, OCR, model observation, or citation artifact path
- source owner, publisher, provider id, or channel identifier
- evidence ref with confidence and reason

Missing evidence must be listed in `missing_assets[]` or `findings.evidence_gaps[]`.

## Media Manifest Policy

If this skill creates, consumes, validates, captures, mirrors, or defers any local media or sidecar artifact, return `manifest_actions[]`:

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

Use `created` for new local source or captured artifact entries, `updated` for rights/technical/evidence changes, `consumed` for existing manifest assets, `validated` when checking existing entries, `deferred` when a needed manifest entry cannot be written yet, and `not_applicable` only when no local media or captured artifact exists.

## Approval And Stop Conditions

Stop and return `needs_approval` before paid/cloud transcription, direct-video model analysis, external download, licensed media use, or sensitive media handling.

Stop and return `blocked` when:

- a required source cannot be accessed or identified
- rights state blocks analysis or reuse
- source provenance is unknown and the source would affect factual claims or selected media
- local media is required but missing
- manifest path is required for local media but absent and no Director waiver exists

## Definition Of Done

- Every supplied source is represented once with a stable id.
- Every source has owner/path, rights state, reusable scope, missing evidence, and confidence.
- `source_ledger[]`, `claim_ledger[]`, `reference_beats[]`, `downstream_guidance`, and `invalidation_impact[]` are populated or explicitly deferred.
- Local media and captured artifacts are either entered in the media asset manifest or explicitly deferred with a reason.
- The reference-video breakdown step can run without inventing paths, ids, rights state, or project folders.

## Handoff Summary Shape

Return:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "artifact_paths": ["string"],
  "changed_files": ["string"],
  "populated_contracts": ["codex/contracts/reference-analysis.schema.json", "codex/contracts/media-asset-manifest.schema.json"],
  "manifest_actions": [
    {
      "action": "created | updated | consumed | validated | mirrored_to_remotion_public | deferred | not_applicable",
      "asset_id": "string",
      "reason": "string"
    }
  ],
  "validation_performed": ["source inventory", "rights classification", "reusable scope classification", "missing evidence scan", "manifest action review"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
