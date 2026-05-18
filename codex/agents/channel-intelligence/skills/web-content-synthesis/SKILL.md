---
name: web-content-synthesis
description: Parse and synthesize supplied direct web pages, blogs, news posts, product pages, research notes, and source documents into claim evidence, image candidates, narrative opportunities, and source reports for a video scenario. Use when source content should inform the video without becoming a redundant page summary.
---

# Web Content Synthesis

Read `../../references/reference-analysis-dimensions.md` when source evidence needs structure.

## Inputs

- Source ids and URL classifications from `source-corpus-ingestion`
- Direct article/blog/news/product/source URLs, supplied HTML snapshots, screenshots, or user notes
- Project path, channel profile path, producer criteria path, media asset manifest path, and existing reference analysis when available
- Director approval state for external downloads, screenshots, paid/cloud parsing, login/paywall handling, and image reuse
- Intended use for each source: script claim, visual context, style reference, critique context, or do-not-use

## Workflow

1. Confirm every page has a stable `source_id`, `kind`, rights state, reusable scope, and destination:
   `channels/<channel-slug>/projects/<project-slug>/source-media/web-content/<source-id>/`.
2. Process direct content URLs as one-page captures by default. Do not crawl internal links, feeds, or related posts unless the Director explicitly expands the scope.
3. Use local deterministic capture first:
   ```powershell
   python codex/agents/channel-intelligence/scripts/parse_web_content.py `
     --url <source-url> `
     --source-id <source-id> `
     --work-dir <project-path>/source-media/web-content/<source-id> `
     --output <project-path>/source-media/web-content/<source-id>/reference-analysis.json `
     --media-asset-manifest <project-path>/media-asset-manifest.json `
     --update-media-asset-manifest
   ```
4. The local parser should create `raw.html`, `extracted.json`, `extracted.md`, `source-report.json`, `source-report.md`, `annotations.json`, and `images/image-manifest.json`.
5. If image files are needed, stop for approval before external download. After approval, run with:
   ```powershell
   python codex/agents/channel-intelligence/scripts/parse_web_content.py `
     --url <source-url> `
     --source-id <source-id> `
     --work-dir <project-path>/source-media/web-content/<source-id> `
     --output <project-path>/source-media/web-content/<source-id>/reference-analysis.json `
     --media-asset-manifest <project-path>/media-asset-manifest.json `
     --update-media-asset-manifest `
     --download-images `
     --approved-downloads
   ```
6. Use browser/Playwright screenshots only when static HTML extraction misses a key visual, chart, interactive state, or lazy-loaded image. Store screenshots under `source-media/web-content/<source-id>/screenshots/` and track them as `screenshot` assets.
7. Extract only video-useful claims, examples, entities, dates, product details, visual evidence, contradictions, and attribution requirements. Avoid turning the video into a page summary.
8. Separate source facts from interpretation:
   - source fact: directly supported by page text, metadata, image alt/caption, screenshot, or supplied note
   - interpretation: narrative angle, implication, visual metaphor, or production recommendation
   - unverified claim: needs another source or user approval before script use
9. Create or update `claim_ledger[]` for every claim that could affect script wording, source cards, visual choices, critique gates, or factual QA.
10. Create `visual_evidence_candidates[]` from page images, Open Graph/Twitter images, charts, screenshots, diagrams, quotes, UI states, maps, or product shots. Each candidate needs a URL or local path, evidence ref, rights note, and confidence.
11. Summarize narrative opportunities as angles, not recaps: contradiction, transformation, timeline, comparison, expert insight, user pain, surprising stat, or proof point.
12. Return downstream guidance for Creative Producer, Visual Producer, InVideo AI Generator, Remotion Clip Builder, Remotion Video Producer, and Video Critic.

## Storage Pattern

For every direct content source:

```text
channels/<channel-slug>/projects/<project-slug>/source-media/web-content/<source-id>/raw.html
channels/<channel-slug>/projects/<project-slug>/source-media/web-content/<source-id>/extracted.json
channels/<channel-slug>/projects/<project-slug>/source-media/web-content/<source-id>/extracted.md
channels/<channel-slug>/projects/<project-slug>/source-media/web-content/<source-id>/source-report.json
channels/<channel-slug>/projects/<project-slug>/source-media/web-content/<source-id>/source-report.md
channels/<channel-slug>/projects/<project-slug>/source-media/web-content/<source-id>/annotations.json
channels/<channel-slug>/projects/<project-slug>/source-media/web-content/<source-id>/images/image-manifest.json
channels/<channel-slug>/projects/<project-slug>/source-media/web-content/<source-id>/images/<source-id>-image-<nnn>-<checksum>.<ext>
channels/<channel-slug>/projects/<project-slug>/source-media/web-content/<source-id>/screenshots/full-page.png
```

The final project reference analysis may either merge these page fragments or reference their per-source `reference-analysis.json` paths. Keep persisted paths repo-relative POSIX strings.

## Required Output

Return or update `codex/contracts/reference-analysis.schema.json` with:

```json
{
  "analysis_id": "string",
  "status": "complete | partial | blocked",
  "project_id": "string",
  "project_path": "string",
  "media_asset_manifest_path": "string",
  "sources": [],
  "source_ledger": [
    {
      "source_id": "string",
      "kind": "webpage | blog | best_practice | channel_data | other",
      "path_or_url": "string",
      "local_path": "string",
      "rights_state": "approved | needs_approval | blocked | unknown",
      "reusable_scope": "global_channel | project_only | scene_only | critique_only | do_not_use | unknown",
      "why_it_matters": "string",
      "missing_assets": ["string"],
      "evidence_refs": [],
      "confidence": "high | medium | low | unknown"
    }
  ],
  "web_pages": [
    {
      "page_id": "string",
      "source_id": "string",
      "url": "string",
      "final_url": "string",
      "captured_at": "string",
      "metadata": {
        "title": "string",
        "description": "string",
        "author": "string",
        "publisher": "string",
        "published_date": "string",
        "modified_date": "string",
        "canonical_url": "string"
      },
      "artifacts": {
        "raw_html_path": "string",
        "extracted_json_path": "string",
        "extracted_markdown_path": "string",
        "image_manifest_path": "string",
        "annotations_path": "string",
        "report_markdown_path": "string",
        "report_json_path": "string",
        "screenshot_path": "string"
      },
      "claim_candidates": [],
      "visual_evidence_candidates": [],
      "downloaded_images": [],
      "robots": {},
      "limitations": [],
      "confidence": "high | medium | low | unknown"
    }
  ],
  "claim_ledger": [
    {
      "claim_id": "string",
      "claim": "string",
      "source_ids": ["string"],
      "support_state": "supported | contradicted | unsupported | needs_review",
      "allowed_use": "script_claim_after_review | visual_context | critique_context | do_not_use",
      "risk": "none | factual | rights | policy | stale | unknown",
      "confidence": "high | medium | low | unknown",
      "evidence_refs": []
    }
  ],
  "reference_beats": [],
  "findings": {
    "source_claims": [],
    "visual_evidence_opportunities": [],
    "story_opportunities": [],
    "rights_or_policy_risks": [],
    "evidence_gaps": [],
    "confidence_notes": []
  },
  "evidence_refs": [],
  "downstream_guidance": {},
  "invalidation_impact": [],
  "manifest_actions": []
}
```

## Contract Fields Populated

- `reference-analysis.schema.json`: required fields `analysis_id`, `status`, `sources[]`, `source_ledger[]`, `claim_ledger[]`, `reference_beats[]`, `findings`, `downstream_guidance`, and `invalidation_impact[]`, plus `processing_runs[]`, `web_pages[]`, and `evidence_refs`
- `media-asset-manifest.schema.json`: `web_snapshot`, `source_report`, `web_image`, `screenshot`, and `metadata` entries when files are created or consumed
- `producer-criteria.schema.json`: no direct writes, but return source-use restrictions or acceptance criteria candidates when page evidence creates hard factual/rights gates

## Status Policy

- `complete`: each supplied page has raw/extracted/report artifacts, claim candidates or an explicit no-claims note, image candidate manifest, rights notes, and evidence refs.
- `partial`: static extraction works but some metadata, images, screenshots, claim support, rights, or dynamic content are missing.
- `blocked`: source is inaccessible, robots disallow applies, the page requires login/paywall handling not approved, rights block analysis, or no usable source evidence can be captured.
- Return handoff status `needs_approval` when the next useful step requires image download, screenshot capture, login/session handling, paid/cloud parsing, or licensed media use.

## Evidence Required

Every important claim, visual candidate, and recommendation must cite one or more of:

- `source_id`
- URL or canonical URL
- raw/extracted/report artifact path
- text `block_id` or annotation id
- local screenshot or image path
- image URL plus alt/title/caption metadata
- metadata field such as Open Graph, Twitter card, Schema.org/JSON-LD, author, publisher, or publication date
- confidence note and limitation when extraction is heuristic

Missing evidence must become `findings.evidence_gaps[]`; do not hide it in prose.

## Media Manifest Policy

When a local web artifact is created, consumed, validated, downloaded, captured, or deferred, return `manifest_actions[]`:

```json
{
  "action": "created | updated | consumed | validated | deferred | not_applicable",
  "asset_id": "string",
  "canonical_path": "string",
  "rights_state": "approved | needs_approval | blocked | unknown",
  "technical_metadata_state": "present | missing | partial",
  "reason": "string"
}
```

Use `deferred` for image downloads, screenshots, or dynamic captures that would be useful but lack approval.

## Approval And Stop Conditions

Stop and return `needs_approval` before:

- downloading page images or other external media files
- logging into a site, using cookies, bypassing bot protection, or accessing paywalled content
- sending page screenshots, media, or full text to a paid/cloud model
- using copied images or article text as final video media

Stop and return `blocked` when:

- the URL cannot be accessed or identified
- robots rules disallow the configured user agent
- provenance is unknown and the source would affect factual claims
- rights state blocks analysis or reuse
- extraction creates no usable evidence and no screenshot/browser fallback is approved

## Definition Of Done

- Every supplied direct page has one source folder, stable ids, and repo-relative artifact paths.
- Raw HTML, extracted text/metadata, image manifest, annotations, and source report are captured or explicitly blocked.
- `source_ledger[]`, `claim_ledger[]`, `reference_beats[]`, `invalidation_impact[]`, visual evidence candidates, source risks, and downstream guidance are populated or explicitly deferred.
- Image downloads/screenshots are either covered by approval and manifest entries or listed as deferred.
- Downstream agents can cite claims and visuals without re-parsing the original page.

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
      "action": "created | updated | consumed | validated | deferred | not_applicable",
      "asset_id": "string",
      "reason": "string"
    }
  ],
  "validation_performed": ["raw HTML capture", "metadata extraction", "claim candidate extraction", "image candidate scan", "rights review", "manifest action review"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
