---
name: source-corpus-ingestion
description: Build a normalized source ledger from user requests, scenario files, reference videos, URLs, blogs, web pages, channel data, brand assets, and best-practice specs. Use before deep reference analysis or channel format synthesis.
---

# Source Corpus Ingestion

## Workflow

1. Inventory every supplied source: user notes, scenario, local files, URLs, reference videos, transcripts, screenshots, channel data, brand assets, and best-practice specs.
2. Classify each source as `reference_video`, `local_video`, `webpage`, `blog`, `channel_data`, `best_practice`, `brand_asset`, or `user_note`.
3. Record path or URL, title, owner/source, rights notes, date if known, media asset id when local media exists, and why it matters.
4. Mark which sources are reusable channel-level evidence versus one-off episode evidence.
5. For each reference video or local video, determine whether the deeper reference-analysis route has enough local evidence: video file, transcript, screenshots, thumbnail, or approved direct-video observation.
6. Identify missing assets needed for deeper analysis: transcript, screenshots, video file, thumbnail, channel analytics, brand tokens, product source material, or rights details.
7. When local media or captured artifacts are present, add or update entries in `codex/contracts/media-asset-manifest.schema.json`.
8. For durable channel/project work, choose repo-relative artifact destinations before reference breakdown starts:
   - channel-level references: `channels/<channel-slug>/references/`
   - project-specific reference analysis: `channels/<channel-slug>/projects/<project-slug>/source-media/reference-analysis/<source-id>/`
   - project-specific reference videos: `channels/<channel-slug>/projects/<project-slug>/source-media/reference-videos/`
9. Preserve whether each source is channel-level reusable evidence, project-only evidence, or a one-off citation for a single scenario.

## Required Output

Return a source ledger compatible with `codex/contracts/reference-analysis.schema.json`, including:

- stable `source_id`
- `kind`
- original path or URL
- local path when available
- title/owner/date when known
- rights notes and confidence
- asset id or deferred manifest note for local media
- captured artifact paths for transcripts, thumbnails, screenshots, probe output, scene JSON, keyframes, OCR, or model observations
- missing evidence needed before production reliance

## Definition Of Done

- Every supplied source is represented once with a stable id.
- Local media sources are either entered in the media asset manifest or explicitly deferred with a reason.
- The reference-video breakdown step can run without inventing paths, ids, rights state, or project folders.
