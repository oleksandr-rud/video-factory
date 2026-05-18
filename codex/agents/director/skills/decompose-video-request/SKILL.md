---
name: decompose-video-request
description: Convert a user's video request into a staged production plan and broad production-agent handoffs. Use when the Director needs to choose whether to call Channel Intelligence, Creative Producer, Visual Producer, InVideo AI Generator, Remotion Clip Builder, Remotion Video Producer, or Video Critic, define scene-level artifacts, set budget gates, and establish acceptance criteria.
---

# Decompose Video Request

1. Extract goal, audience, platform, duration, aspect ratio, tone, and source material.
2. Decide which broad production and validation agents are needed: Channel Intelligence, Creative Producer, Visual Producer, InVideo AI Generator, Remotion Clip Builder, Remotion Video Producer, Video Critic.
3. Create stable artifact paths for the production run ledger, producer criteria prompt, reference analysis, channel format, scenario, voiceover package, visual pack, candidates, AI video generation packages, Remotion clip packages, timeline sync plan, render packages, critique reports, and QA.
4. Define approval gates for paid APIs, licensed media, and generation jobs.
5. Build handoffs using `codex/contracts/agent-handoff.schema.json`.
6. Treat Visual Producer `handoff_recommendations[]` as routing input only. The Director decides whether to create downstream InVideo AI Generator or Remotion Clip Builder handoffs and names the target agent's local skills.

Return a plan with agents, dependencies, inputs, outputs, allowed paths, approval gates, and done criteria. Use `autonomous-production-run` when the user expects the Director to keep working until complete or blocked.
