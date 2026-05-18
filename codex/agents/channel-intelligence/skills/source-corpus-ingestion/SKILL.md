---
name: source-corpus-ingestion
description: Build a normalized source ledger from user requests, scenario files, reference videos, URLs, blogs, web pages, channel data, brand assets, and best-practice specs. Use before deep reference analysis or channel format synthesis.
---

# Source Corpus Ingestion

Workflow:

1. Inventory every supplied source: user notes, scenario, local files, URLs, reference videos, transcripts, screenshots, channel data, brand assets, and best-practice specs.
2. Classify each source as `reference_video`, `local_video`, `webpage`, `blog`, `channel_data`, `best_practice`, `brand_asset`, or `user_note`.
3. Record path or URL, title, owner/source, rights notes, date if known, media asset id when local media exists, and why it matters.
4. Mark which sources are reusable channel-level evidence versus one-off episode evidence.
5. Identify missing assets needed for deeper analysis: transcript, screenshots, video file, thumbnail, channel analytics, brand tokens, or product source material.
6. When local media or captured artifacts are present, add or update entries in `codex/contracts/media-asset-manifest.schema.json`.

Return a source ledger compatible with `codex/contracts/reference-analysis.schema.json`.
