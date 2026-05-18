# Project Artifact Structure Spec

## Purpose

This spec defines how Video Factory stores durable project workspaces, loaded source media, Remotion-visible assets, rendered clips, render release candidates, review evidence, and run ledgers.

## Core Decision

Use three levels of state:

- Channel: `channels/<channel-slug>/` stores reusable brand, format, voice, governance, references, and project registry.
- Project: `channels/<channel-slug>/projects/<project-slug>/` stores one durable video deliverable and all source/artifact state needed to revise it.
- Run: `channels/<channel-slug>/projects/<project-slug>/runs/<run-id>/` stores one execution attempt, review loop state, approvals, and rerun history.

Do not put top-level runs directly under the channel. Runs are attempts; projects are deliverables.

Contract path values should be repo-relative POSIX strings such as `channels/<channel-slug>/projects/<project-slug>/project.json`, even on Windows. Tool commands may resolve them to absolute filesystem paths at execution time, but persisted JSON artifacts should remain portable.

## Project Folder Standard

```text
channels/<channel-slug>/projects/<project-slug>/
  project.json
  production-run.json
  producer-criteria.json
  media-asset-manifest.json
  scenario/
  voiceover/
  visuals/
    candidates/
      search-results/
      <scene-id>/
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
    <run-id>/
      scene-artifact-sync.json
      context/
  delivery/
```

Store context compaction snapshots under:

```text
channels/<channel-slug>/projects/<project-slug>/runs/<run-id>/context/context-snapshot-<timestamp>.json
```

The production run ledger remains the entry point. Snapshot files are optional detailed sidecars; `production-run.context_state` must contain the compact working set and reload list needed to continue the next phase.

Use `codex/examples/*.template.json` as minimal fixtures for new channel/project artifacts. Replace placeholder channel/project/request ids and paths before writing them into `channels/<channel-slug>/` or `channels/<channel-slug>/projects/<project-slug>/`.

## Remotion Public Projection

The shared Remotion app lives at `remotion/`. Its `public/` folder is the render-visible projection, not the source of truth for media ownership.

For each project, the render-visible projection target is:

```text
remotion/public/channels/<channel-slug>/projects/<project-slug>/
```

Use this rule:

1. Keep canonical user/source/provider/generated media under the project folder.
2. Copy or mirror render-needed media into `remotion/public/channels/<channel-slug>/projects/<project-slug>/...`.
3. Record each asset in `media-asset-manifest.json` with `canonical_path`, `remotion_public_path`, and `static_file_path`.
4. Use the `static_file_path` value in Remotion code through `staticFile()`.
5. Do not render from remote media URLs unless the Director records an explicit approval and risk note.

## Visual Candidate Storage

Store candidate records before downloading provider media:

```text
channels/<channel-slug>/projects/<project-slug>/visuals/candidates/search-results/<provider>/<scene-id>-<query-slug>-<run-id>.json
channels/<channel-slug>/projects/<project-slug>/visuals/candidates/<scene-id>/<candidate-id>.json
```

Search result JSON is discovery evidence. Individual candidate JSON files are the durable candidate records and should match `codex/contracts/clip-candidate.schema.json`.

Store downloaded provider media separately:

```text
channels/<channel-slug>/projects/<project-slug>/source-media/provider-clips/<provider>/<candidate-id>/<filename>
```

Provider media is usable in Remotion only after it is tracked in `media-asset-manifest.json` and, when needed for render, mirrored into the Remotion public projection with `static_file_path` recorded.

## Reference Analysis Storage

Store project-specific reference media and deterministic analysis sidecars before downstream production:

```text
channels/<channel-slug>/projects/<project-slug>/source-media/reference-videos/<source-id>/<filename>
channels/<channel-slug>/projects/<project-slug>/source-media/reference-analysis/<source-id>/probe.json
channels/<channel-slug>/projects/<project-slug>/source-media/reference-analysis/<source-id>/scenes.json
channels/<channel-slug>/projects/<project-slug>/source-media/reference-analysis/<source-id>/frame-samples.json
channels/<channel-slug>/projects/<project-slug>/source-media/reference-analysis/<source-id>/keyframes/
channels/<channel-slug>/projects/<project-slug>/source-media/reference-analysis/<source-id>/ocr.json
```

The reference analysis JSON may live under the project, channel references folder, or run artifact folder, but persisted paths should remain repo-relative. Deterministic sidecars should be entered in `media-asset-manifest.json` or explicitly listed as deferred manifest entries.

## Web Content Source Storage

Store supplied direct web/article/blog/news links as one source folder per URL. Do not crawl the site unless the Director explicitly expands the scope.

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

Default capture should save raw HTML, extracted text/metadata, image URL candidates, claim candidates, evidence annotations, and a report. Image files and screenshots are local media artifacts: download or capture them only when the Director has recorded approval and then add them to `media-asset-manifest.json` as `web_image` or `screenshot` assets.

For 10-20 supplied links, process each URL as an independent one-page source with a stable `source_id`; merge the resulting `web_pages[]`, `claim_ledger[]`, image manifests, and source reports into the project reference analysis rather than storing one large untraceable scrape.

## Contract Map

- `channel-profile.schema.json`: durable channel identity, brand, content, visual/audio defaults, governance, and project registry. Minimal fixture: `codex/examples/channel-profile.template.json`.
- `video-project.schema.json`: durable project index, folder layout, deliverables, artifact paths, Remotion setup, current run/render state. Minimal fixture: `codex/examples/video-project.template.json`.
- `production-run.schema.json`: one execution attempt, handoffs, approvals, blockers, review loops, invalidation/rerun graph, and compact context/resume state. Minimal fixture: `codex/examples/production-run.template.json`.
- `agent-handoff.schema.json`: Director-owned executable handoff with owner, scope, inputs, allowed paths, skills, output contract, budget policy, and stop conditions. Repair fixture: `codex/examples/agent-handoff.artifact-repair.template.json`.
- `producer-criteria.schema.json`: binding production criteria, hard gates, scene criteria, thresholds, and revision policy. Minimal fixture: `codex/examples/producer-criteria.template.json`.
- `media-asset-manifest.schema.json`: loaded videos, provider clips, generated clips, rendered clips, subtitles, review frames, technical metadata, rights state, and evidence refs. Minimal fixture: `codex/examples/media-asset-manifest.template.json`.
- `remotion-project.schema.json`: Remotion app root, package manager, composition registry, commands, dependency policy, and public asset policy. Minimal fixture: `codex/examples/remotion-project.template.json`.
- `remotion-template.schema.json`: reusable Remotion template contract, props, previews, usage, registry alignment, and QA. Minimal fixture: `codex/examples/remotion-template.template.json`.
- `reference-analysis.schema.json`: source ledger and timecoded evidence distilled for production.
- `scene-artifact-sync.schema.json`: Director-owned cross-artifact scene lineage report for scenario scenes, visual scene packs, props, candidates, AI packages, Remotion clip packages, and timeline sync.
- `clip-candidate.schema.json`, `ai-video-generation-package.schema.json`, `remotion-clip-package.schema.json`, `timeline-sync-plan.schema.json`, and `render-package.schema.json`: media-producing contracts that must point back to project, channel, media manifest, current scenario scene lineage, and source/output asset ids when available.

## Evidence Rules

- Every source-backed claim, reference-derived style rule, downloaded/provider clip, AI-generated clip, Remotion render, and review frame should have an asset id or evidence ref.
- Missing rights, missing local paths, or missing technical metadata are not blockers for early planning, but they must be blockers before render release-candidate approval.
- Keep failed or superseded assets in the manifest unless rights require deletion; mark status instead of deleting provenance.

## Research Basis

LangChain Deep Agents uses planning, subagents, filesystem tools, persistent memory, permissions, and human-in-the-loop controls as harness capabilities for complex tasks. That supports keeping project state in inspectable files rather than packing all context into prompts. Source: https://docs.langchain.com/oss/python/deepagents/overview

LangChain's subagent guidance recommends specialized subagents for context isolation and clear descriptions, while warning against subagents for simple tasks. This supports the current Director plus bounded production-agent model. Source: https://docs.langchain.com/oss/python/deepagents/subagents

OpenAI Agents SDK handoffs support explicit delegation and custom handoff input schemas. This maps to the local `agent-handoff` contract and argues for typed paths instead of informal cross-agent messages. Source: https://openai.github.io/openai-agents-python/handoffs/

Remotion's current setup docs use `npx create-video@latest`, Remotion Studio, and CLI rendering as the basic workflow. Source: https://www.remotion.dev/docs

Remotion requires assets in a project `public/` folder to be loaded through `staticFile()`, and the `public/` folder must sit next to the `package.json` containing the Remotion dependency. Source: https://www.remotion.dev/docs/staticfile

Remotion render docs support Studio, CLI, server-side rendering, Lambda, GitHub Actions, Cloud Run, and variants such as audio-only, still images, image sequences, GIFs, and transparent videos. Source: https://www.remotion.dev/docs/render

Remotion's `<Artifact>` can emit extra files during rendering, including thumbnails. This supports tracking render sidecars and evidence files as first-class artifacts. Source: https://www.remotion.dev/docs/artifact
