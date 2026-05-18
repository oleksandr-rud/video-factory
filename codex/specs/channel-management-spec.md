# Channel Management Spec

## Purpose

Each durable content channel gets a persistent folder under `channels/<channel-slug>`. The folder stores brand, format, voice, asset, governance, reference defaults, and a project registry reused across many video projects.

## Why This Belongs To Channel Intelligence

This should not be a separate agent yet. Channel profile management is the durable state layer for the existing Channel Intelligence responsibility: reference analysis, brand extraction, channel format synthesis, style rules, and anti-redundancy. A separate Channel Manager agent would add orchestration overhead without a distinct production phase.

## Folder Contract

```text
channels/<channel-slug>/
  channel-profile.json
  brand/
    color-palette.json
    logos/
    typography/
    imagery/
  formats/
    <format-slug>.json
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
          search-results/
          <scene-id>/
      source-media/
        reference-videos/
        reference-analysis/
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

`channel-profile.json` must match `codex/contracts/channel-profile.schema.json`.

`projects/<project-slug>/project.json` must match `codex/contracts/video-project.schema.json`.

`projects/<project-slug>/media-asset-manifest.json` must match `codex/contracts/media-asset-manifest.schema.json` and is the local ledger for loaded reference videos, user media, provider clips, generated clips, Remotion previews, render outputs, subtitles, review frames, and evidence references.

Persist contract paths as repo-relative POSIX strings, for example `channels/<channel-slug>/projects/<project-slug>/project.json`. Agents and scripts can resolve those paths to absolute paths for shell commands, but should not write machine-specific absolute paths into channel/project JSON.

## Projects Versus Runs

Use projects, not top-level runs, under a channel.

- A project is the durable workspace for one video, short, episode, or campaign deliverable.
- A run is one execution attempt through the agent pipeline.
- A project can contain multiple runs when revisions, regenerations, or review-loop attempts happen.
- Render candidates live under `renders/`; historical execution ledgers live under `runs/`.
- Source media and rendered clips live under the project, then are copied or mirrored into the Remotion app `public/` tree only when Remotion must load them through `staticFile()`.
- Clip candidate records live under `visuals/candidates/`; downloaded provider media lives under `source-media/provider-clips/`. Do not treat provider search result JSON or preview URLs as downloaded production media.
- The project index should track both the project-local staging folder `remotion/public-projection/` and the actual Remotion-visible folder `remotion/public/channels/<channel-slug>/projects/<project-slug>/`.

## Production Linkage

- `channel-profile.schema.json` is the durable channel identity and asset registry.
- `video-project.schema.json` is the durable project workspace index for one deliverable under a channel.
- `media-asset-manifest.schema.json` is the project-local ledger for loaded media, generated/rendered assets, rights state, technical metadata, and evidence refs.
- `remotion-project.schema.json` describes the shared or project-specific Remotion app, composition registry, commands, dependencies, and public asset policy.
- `channel-format.schema.json` is a production-ready format package derived from the channel profile plus current references.
- Per-channel format files under `formats/` may extend shared VFX hardening rules through `visual_system.vfx_rules`; these extensions should be passed downstream by `channel_format_path` and copied into producer criteria or VFX rule refs when they affect a scene.
- `scenario.schema.json`, `voiceover-package.schema.json`, `producer-criteria.schema.json`, and `production-run.schema.json` carry channel profile ids/paths so every video can trace its inherited rules.
- Creative Producer inherits voice direction from `channel_profile.audio_identity.voice_profile` before choosing a provider voice.
- Visual Producer and Remotion agents inherit colors, typography, caption style, motion rules, thumbnail rules, VFX rule extensions, and asset paths from the channel profile through the channel format.

## Voice Inheritance

Use this priority order:

1. Explicit user request or Director override.
2. Producer criteria artifact.
3. Scenario tone and scene voice notes.
4. Channel profile `audio_identity.voice_profile`.
5. Channel format `audio_system`.
6. Reference analysis voice evidence.
7. Provider inventory and practical availability.

The selected voice should be scored against audience fit, domain authority, emotional tone, pace, language/accent, pronunciation risk, channel continuity, rights, and provider availability.

## Evidence Used

YouTube's branding guidance treats a channel brand as a recognizable message, values, community, visual consistency, and voice across profile picture, banner, and off-platform identity. Source: https://support.google.com/youtube/answer/12950272

YouTube's channel branding docs define platform assets that should be tracked: profile picture, banner, and video watermark, including banner safe-area constraints and watermark display behavior. Source: https://support.google.com/youtube/answer/10456525

YouTube's channel layout docs show that channel management also includes trailer, featured video, and sections, not only media files. Source: https://support.google.com/youtube/answer/3219384

Purdue's brand guidelines demonstrate the broader brand-system shape: strategy, messaging, visual identity, voice/tone, logos, templates, photography, video, editorial style, and analytics resources. Source: https://marcom.purdue.edu/our-brand/

Hunter's voice and tone guidelines show why voice is not just TTS selection: brand voice includes customer sensitivity, domain confidence, active voice, personality constraints, and use-case examples. Source: https://www.hunter.com/en-int/media-center/brand-guidelines/voice--tone/
