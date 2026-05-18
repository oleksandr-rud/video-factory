---
name: channel-profile-management
description: Create, update, and validate persistent Video Factory channel folders under channels/<channel-slug>, including channel-profile.json, brand assets, color palette, formats, rules, references, audio voice profile, project registry, governance metadata, and paths used by production contracts. Use when a run names a channel, creates a new channel, updates channel branding, creates a channel project, or needs channel-level defaults for many videos.
---

# Channel Profile Management

Use this before `channel-format-synthesis` when a channel is named or when a reusable channel identity is needed.

## Folder Layout

Create or update this structure:

```text
channels/<channel-slug>/
  channel-profile.json
  brand/
    color-palette.json
    logos/
    typography/
    imagery/
  formats/
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

Use lowercase hyphen-case for `<channel-slug>`. Do not create separate channel folders for one-off videos unless the user wants a durable channel.

## Workflow

1. Resolve the channel slug, channel name, domain, audience, platforms, language defaults, and root path.
2. For new channel/project workspaces, use `../../scripts/scaffold_channel_project.py <channel-slug> <project-slug>` when a project slug is available; run with `--dry-run` first for risky paths. The script writes repo-relative contract paths and creates the shared Remotion public projection directory for the project.
3. Create or update `channels/<channel-slug>/channel-profile.json` matching `codex/contracts/channel-profile.schema.json`.
4. Capture brand identity:
   - channel promise, values, positioning, personality, approved/avoid vocabulary
   - profile image, banner, watermark, logo rules, color palette, typography, imagery, thumbnails, caption style, motion rules
5. Capture content strategy:
   - content pillars, format registry, hero/hub/hygiene mix, upload schedule, anti-redundancy, novelty requirements
6. Capture audio identity:
   - narrator persona, voice traits, must-avoid traits, accent/language policy, pace range, energy profile, pronunciation defaults, provider voice refs, reference audio, continuity policy
7. Capture governance:
   - rights rules, approval rules, sensitive topics, owner notes, change log
8. When the user starts a durable video deliverable, create or update `channels/<channel-slug>/projects/<project-slug>/project.json` matching `codex/contracts/video-project.schema.json`.
9. Create or update `channels/<channel-slug>/projects/<project-slug>/media-asset-manifest.json` matching `codex/contracts/media-asset-manifest.schema.json` when reference videos, user media, provider clips, generated clips, Remotion outputs, review frames, or evidence files are in scope.
10. Write channel format artifacts into `channels/<channel-slug>/formats/` and point `channel-format.schema.json` fields back to the channel profile.

## Rules

- Preserve existing channel profile values unless the user or evidence clearly updates them.
- Persist JSON contract paths as repo-relative POSIX strings, even on Windows; resolve absolute paths only for tool execution.
- Mark unknown brand fields as missing assets or risks; do not invent logos, fonts, colors, or provider voice ids.
- Keep reusable channel rules separate from episode-specific choices.
- Keep project artifacts under `projects/<project-slug>`; reserve `runs/` for execution attempts inside a project.
- Keep canonical source media under the project folder; mirror into the Remotion `public/` tree only when a render needs a `staticFile()` path, and record canonical, Remotion public, and `staticFile()` paths in the media asset manifest.
- Store evidence for inferred rules and confidence level.
- When voice is in scope, expose `audio_identity.voice_profile` so Creative Producer can inherit voice direction before provider voice selection.
