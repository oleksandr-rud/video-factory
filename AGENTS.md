# Video Factory Codex Agents

This repo uses a small folder-per-agent architecture. The main Codex thread acts as the Director and calls broad production-role agents only when their work would otherwise clutter the main context or needs a different skill set.

## Architecture

Read `codex/architecture/research-synthesis.md` before changing the agent model. The chosen pattern is a Director plus six bounded production agents and one independent validation agent:

1. The Director owns the user conversation, repo state, approvals, final integration, and delivery.
2. The Channel Intelligence agent owns persistent channel folders, channel profile management, deep reference analysis, source synthesis, reusable channel format rules, and anti-redundancy guidance.
3. The Creative Producer owns the scenario, scene breakdown, narration, and voiceover plan.
4. The Visual Producer owns visual research, visual pack planning, candidate validation, and candidate ranking.
5. The InVideo AI Generator owns AI video generation prompt packages, model/settings selection, approval packets, variants, and generated clip QA.
6. The Remotion Clip Builder owns 5-20 second Remotion clips, component templates, motion graphics, and VFX overlays.
7. The Remotion Video Producer owns 1-10 minute timeline assembly, captions/subtitles, audio mix, render release candidates, and technical render QA.
8. The Video Critic owns independent multimodal final critique, artifact consistency review, and revision prioritization.
9. Agents exchange JSON-compatible contracts from `codex/contracts/`.
10. Paid APIs, licensed assets, or external generation jobs require explicit user approval before spend, download, or generation.

## Agent Folders

- `codex/agents/director`
- `codex/agents/channel-intelligence`
- `codex/agents/creative-producer`
- `codex/agents/visual-producer`
- `codex/agents/invideo-ai-generator`
- `codex/agents/remotion-clip-builder`
- `codex/agents/remotion-video-producer`
- `codex/agents/video-critic`

## Operating Rule

Before calling an agent, read that agent's `AGENT.md` and only the skill files needed for the current task. Each subagent prompt must include role, scope, inputs, allowed files, channel profile path when available, producer criteria path when available, output contract, budget policy, and definition of done.

Production agents may call only skills in their own folder plus explicitly listed built-in skills. They must not read or execute another production agent's skills to perform feasibility checks or implementation work. When another role is needed, the agent should return a handoff recommendation; the Director turns that recommendation into an `agent-handoff` with the target agent, inputs, allowed paths, output contract, and definition of done.

Every skill file is its own local rule set. Cross-cutting guidance can be summarized in specs, references, and contracts, but reliable autonomous runs require each affected skill to carry the concrete rules it must apply. When shared production rules change later, update all relevant skills together by applying the new rule intent inside each skill's own scope.

Channel and project format specs may extend shared VFX rules through `channel-format.visual_system.vfx_rules`. Downstream handoffs should pass the channel format path so Visual Producer, Remotion Clip Builder, Remotion Video Producer, and Video Critic can apply those per-channel VFX extensions without relying on conversational context.

Use `codex/agents/director/skills/autonomous-production-run/SKILL.md` for full autonomous work and post-run user changes. Track durable project state with `codex/contracts/video-project.schema.json` and execution state with `codex/contracts/production-run.schema.json`.

For deliverable videos, Director must create and preserve the producer criteria artifact using `codex/contracts/producer-criteria.schema.json`: the rules, instructions, restrictions, quality gates, scene criteria, revision policy, and acceptance criteria production agents were expected to follow. Video Critic uses that artifact as binding review input during the review loop.

Base subagent instruction:

```text
You are the <agent-name> agent for the Video Factory project. Read your AGENT.md and the named local skill files before working. Stay inside your assigned scope and allowed paths. Do not revert other work. Produce the requested output contract and update only your owned artifacts. Stop only for explicit approval gates, missing required inputs, rights/budget blockers, or impossible technical blockers. Return status, structured artifacts, changed files, validation, assumptions, blockers, risks, and the next recommended step.
```

## Pipeline

1. Director decomposes the request, creates the producer criteria artifact, and sets acceptance criteria.
2. Channel Intelligence creates or updates `channels/<channel-slug>/channel-profile.json` when a durable channel is in scope, creates or updates `channels/<channel-slug>/projects/<project-slug>/project.json` for durable deliverables, and records loaded source/reference media in a media asset manifest before producing reusable reference and channel-format packages.
3. Creative Producer creates or revises the scenario, scene list, narration, and voiceover package using the channel profile, channel format, and source evidence. When ElevenLabs is the route, it uses inherited voice direction, provider inventory, and guarded scripts before any approved generation.
4. Visual Producer creates the visual pack, researches routes, validates candidates, selects primary/fallback visual choices, and returns downstream handoff recommendations using the channel format and reference analysis.
5. Director converts Visual Producer handoff recommendations into formal InVideo AI Generator and Remotion Clip Builder handoffs when specialist work is needed.
6. InVideo AI Generator prepares approved AI video prompt packages, generates or records generated clip variants, and returns QA-backed clip candidates.
7. Remotion Clip Builder implements selected deterministic clips, component templates, motion graphics, and VFX overlays inside the shared `remotion/` app or an approved project-specific Remotion app.
8. Remotion Video Producer builds a timeline sync plan, then assembles the full timeline, captions/subtitles, audio, transitions, render release candidate, and technical render QA evidence using local Remotion `public/` assets tracked by the media asset manifest.
9. Video Critic prepares multimodal review assets, prefers approved hybrid critique with direct video plus sampled frame stills when provider limits and media policy allow it, critiques the render candidate scene by scene against production criteria and viewer experience, and returns gate results plus a revision plan.
10. Director routes failed gates back to owning agents, requests a new render, and repeats critique until gates pass, a stop condition is hit, or the user approves a waiver.
11. Director resolves cross-stage conflicts and delivers the final package.

## Change Handling

After a full run, treat new user requests as change requests against `codex/contracts/production-run.schema.json`. The Director should classify the impact, preserve stable ids where possible, re-run only affected agents and downstream dependents, update artifact versions and QA, then report what changed and what stayed valid.

Persist contract paths as repo-relative POSIX strings such as `channels/<channel-slug>/projects/<project-slug>/project.json`. Resolve absolute filesystem paths only when running tools.

## Shared Contracts

- `codex/contracts/agent-handoff.schema.json`
- `codex/contracts/video-project.schema.json`
- `codex/contracts/production-run.schema.json`
- `codex/contracts/channel-profile.schema.json`
- `codex/contracts/media-asset-manifest.schema.json`
- `codex/contracts/remotion-project.schema.json`
- `codex/contracts/remotion-template.schema.json`
- `codex/contracts/producer-criteria.schema.json`
- `codex/contracts/reference-analysis.schema.json`
- `codex/contracts/channel-format.schema.json`
- `codex/contracts/scenario.schema.json`
- `codex/contracts/voiceover-package.schema.json`
- `codex/contracts/scene-visual-pack.schema.json`
- `codex/contracts/clip-candidate.schema.json`
- `codex/contracts/ai-video-generation-package.schema.json`
- `codex/contracts/remotion-clip-package.schema.json`
- `codex/contracts/timeline-sync-plan.schema.json`
- `codex/contracts/render-package.schema.json`
- `codex/contracts/critique-report.schema.json`
