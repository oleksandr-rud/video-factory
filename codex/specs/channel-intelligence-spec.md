# Channel Intelligence Spec

## Purpose

Channel Intelligence is the upstream research and channel-management layer for Video Factory. It manages persistent `channels/<channel-slug>` folders, analyzes reference videos, source pages, blogs, channel data, brand materials, and best-practice specs, then produces reusable channel rules that support many videos without defining every clip.

## Why This Is Not Visual Producer

Visual Producer should decide scene-level visual routes and candidates. It should not carry the full weight of studying reference videos, source material, channel identity, content pillars, and anti-redundancy policy. That strategic work affects Creative Producer, Visual Producer, InVideo AI Generator, Remotion Clip Builder, and Remotion Video Producer, so it belongs in a separate agent.

## Recommended Agent Structure

Use one agent, not a group of micro-agents:

- `channel-intelligence`: owns channel profile management, source ingestion, reference video breakdown, web/source synthesis, channel format synthesis, style extraction, scenario alignment, and redundancy audit.

Split into multiple agents only if the project later has heavy batch workloads such as hundreds of reference videos, continuous channel analytics ingestion, or a separate research team reviewing claims.

## Outputs

Channel Intelligence returns three durable artifacts:

- `channels/<channel-slug>/channel-profile.json` using `codex/contracts/channel-profile.schema.json`: durable channel metadata, brand identity, visual identity, audio identity, content strategy, governance, project registry, assets, references, and folder paths.
- `channels/<channel-slug>/projects/<project-slug>/project.json` using `codex/contracts/video-project.schema.json`: durable project metadata, deliverables, artifact paths, render candidates, run history, and delivery state.
- `channels/<channel-slug>/projects/<project-slug>/media-asset-manifest.json` using `codex/contracts/media-asset-manifest.schema.json`: loaded reference videos, user-supplied media, provider clips, generated clips, Remotion previews/renders, review frames, rights state, technical metadata, and evidence refs.
- `codex/contracts/reference-analysis.schema.json`: evidence ledger, source summaries, timecoded reference video breakdowns, extracted patterns, source claims, visual evidence opportunities, risks, and downstream guidance.
- `codex/contracts/channel-format.schema.json`: channel promise, audience, content pillars, hero/hub/hygiene mix, narrative system, visual system, audio system, technical defaults, reusable assets, and anti-redundancy rules.

## Channel Folder Standard

Durable channels live under `channels/<channel-slug>` and follow `codex/specs/channel-management-spec.md`. Durable deliverables live under `channels/<channel-slug>/projects/<project-slug>`. Channel profile fields are inherited by project files, channel format packages, and downstream production artifacts.

Persist channel and project contract paths as repo-relative POSIX strings. Local tools can resolve those strings against the repo root, but generated JSON should not contain machine-specific absolute paths.

## Deep Reference Video Analysis

Analyze reference videos for:

- hook and story structure
- transcript rhythm and sentence style
- average shot length and pacing changes
- shot size, camera movement, framing, B-roll categories, screenshots, graphics, captions, and transitions
- color, typography, overlays, thumbnail/opening-frame patterns, and source-card behavior
- narrator persona, voice traits, accent/language policy, music, SFX, silence, and mix density
- reusable execution patterns versus one-off moments that should not be copied

## Channel Format Synthesis

The channel format should define:

- what must stay consistent for recognition
- what should vary to keep each episode distinct
- recurring intro/outro, caption, source-card, thumbnail, and CTA rules
- content pillars and video themes
- technical defaults such as aspect ratios, durations, and export assumptions
- anti-redundancy rules that prevent mass-produced or repetitive videos

## Voice Direction Inheritance

Creative Producer should not invent the voice from scratch when a channel exists. Channel Intelligence owns the channel-level audio identity. Creative Producer inherits it through this order: explicit user/Director override, producer criteria, scenario tone, channel profile audio identity, channel format audio system, reference evidence, then provider inventory.

## Anti-Redundancy Standard

Every video should have at least one clear novelty angle: new evidence, a new story question, a new visual metaphor, a new source set, a new case study, or a new payoff. Reusing the channel format is healthy; repeating the same topic angle, wording, B-roll, generated prompts, edit rhythm, or source paraphrase is a production risk.

## Evidence Used

YouTube's channel branding guidance treats channel identity as more than visuals: it asks creators to clarify uniqueness, values, community, and consistency across online/offline branding. Source: https://support.google.com/youtube/answer/12950272

YouTube's channel branding docs define concrete channel assets that should be tracked in a persistent channel folder: profile picture, banner image, and video watermark. Source: https://support.google.com/youtube/answer/10456525

YouTube's channel layout docs show that channel management also includes home tab, channel trailer, featured video, and sections. Source: https://support.google.com/youtube/answer/3219384

Purdue's brand guidelines show a broader brand-system pattern: strategy, messaging map, visual identity, voice and tone, logos, templates, photography, video, editorial style, and analytics resources. Source: https://marcom.purdue.edu/our-brand/

Hunter's voice and tone guidelines show why channel voice should be captured as reusable rules: domain confidence, customer sensitivity, active voice, and personality constraints. Source: https://www.hunter.com/en-int/media-center/brand-guidelines/voice--tone/

YouTube's brand playbook for brands uses hero, hub, and hygiene content to separate big tent-pole content, recurring episodic formats, and always-on search content. Source: https://think.storage.googleapis.com/docs/creator-playbook-for-brands_research-studies.pdf

YouTube monetization guidance emphasizes original, authentic, non-repetitive content and says reviewers may examine the channel theme, most viewed videos, newest videos, watch-time-heavy videos, metadata, and About section. Source: https://support.google.com/youtube/answer/1311392

Video reference tools such as ShotBook and Video to Prompt show a real workflow need for breaking references into technique, structure, camera, pacing, lighting, and prompt-ready language rather than saving vague inspiration. Sources: https://shotbook.art/ and https://vidtoprompt.net/
