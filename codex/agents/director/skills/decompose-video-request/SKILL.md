---
name: decompose-video-request
description: Convert a user's video request into a staged production plan and broad production-agent handoffs. Use when the Director needs to choose whether to call Channel Intelligence, Creative Producer, Visual Producer, InVideo AI Generator, Remotion Clip Builder, Remotion Video Producer, or Video Critic, define scene-level artifacts, set budget gates, and establish acceptance criteria.
---

# Decompose Video Request

1. Extract goal, audience, platform, duration, aspect ratio, tone, and source material.
2. Decide which broad production and validation agents are needed: Channel Intelligence, Creative Producer, Visual Producer, InVideo AI Generator, Remotion Clip Builder, Remotion Video Producer, Video Critic.
3. If the request names a durable channel, create or resolve `channels/<channel-slug>/channel-profile.json` through Channel Intelligence `channel-profile-management`.
4. If the request is a durable deliverable, create or resolve `channels/<channel-slug>/projects/<project-slug>/project.json` using `codex/contracts/video-project.schema.json`.
5. Create or resolve the shared Remotion app contract using `codex/contracts/remotion-project.schema.json`; default to the repo `remotion/` app unless a project-specific app is justified. If reusable Remotion components are likely, resolve the app template registry and reserve project template contract paths using `codex/contracts/remotion-template.schema.json`.
6. Create stable repo-relative POSIX artifact paths under the project folder for the production run ledger, channel profile, producer criteria artifact, media asset manifest, reference analysis, web content source reports, channel format, scenario, voiceover package, visual pack, candidates, source media, AI video generation packages, Remotion template contracts, Remotion clip packages, timeline sync plan, render packages, critique reports, review assets, and QA.
7. Run `producer-criteria-prompt` to create the first criteria artifact. Update scene-specific criteria after the scenario scene ids exist.
8. Define approval gates for paid APIs, licensed media, remote render-time assets, and generation jobs.
9. Build handoffs using `codex/contracts/agent-handoff.schema.json`; include project path, media asset manifest path, Remotion project contract path, Remotion template registry/contract paths, channel profile path, and producer criteria path when available.
10. Treat Visual Producer `handoff_recommendations[]` as routing input only. The Director decides whether to create downstream InVideo AI Generator or Remotion Clip Builder handoffs and names the target agent's local skills.

Return a plan with agents, dependencies, inputs, outputs, allowed paths, approval gates, and done criteria. Use `autonomous-production-run` when the user expects the Director to keep working until complete or blocked.
