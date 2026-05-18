---
name: autonomous-production-run
description: Run the full Video Factory pipeline autonomously from request to delivery, tracking artifacts, handoffs, approvals, blockers, QA, and post-run user change requests. Use when the Director should keep working until the video package is complete or blocked by approval, rights, budget, missing assets, or an impossible technical dependency.
---

# Autonomous Production Run

Use this after `decompose-video-request` when the user wants a full run, `/goal`-style autonomous execution, or a post-run change/update.

## Run Loop

1. Create or update a run ledger matching `codex/contracts/production-run.schema.json`.
2. Load `AGENTS.md`, the target agent `AGENT.md`, and only the skill files named in each handoff.
3. Build each handoff using `codex/contracts/agent-handoff.schema.json`.
   - A production agent's `handoff_recommendations[]` are not executable work by themselves. Convert them into Director-owned handoffs before downstream agents run.
   - Only name skills that belong to the target agent's folder or explicitly approved built-in skills.
4. Execute phases in dependency order:
   - Channel Intelligence before scenario and visual planning when references, channel data, web sources, or redundancy concerns exist.
   - Creative Producer before Visual Producer; if voiceover is in scope, produce the voiceover package before final timeline assembly.
   - Visual Producer before InVideo AI Generator and Remotion Clip Builder.
   - InVideo AI Generator and Remotion Clip Builder before Remotion Video Producer.
   - Timeline sync plan before full Remotion assembly and render QA when narration, captions, and visuals must align.
   - Render QA before Video Critic.
   - Video Critic after a render candidate exists and before final delivery when the run targets a deliverable video.
   - Quality gated review loop after the first critique if findings do not pass release-candidate gates.
5. Parallelize only independent work. Do not run a downstream agent before its required input artifact exists.
6. After each handoff, validate that the returned artifact matches its output contract, update the run ledger, and send one targeted repair handoff if required fields or QA evidence are missing.
7. Continue until complete, blocked, waiting for approval, or release-candidate gates pass.

## Approval Stops

Stop and ask the user only for:

- paid API spend, credit usage, licensed media, paid templates, or external generation jobs
- ElevenLabs or other TTS generation, voice design, forced alignment, or transcription that spends credits or uses a paid cloud endpoint
- multimodal model critique through a paid API or external provider
- waiving a quality gate that the critic marked as blocker or hard fail
- missing source assets that cannot be inferred safely
- rights or likeness concerns
- impossible technical blockers after one repair attempt
- ambiguous user intent that changes the product, not just implementation details

## Subagent Prompt Shape

Every subagent prompt must include:

- agent name and role
- exact `AGENT.md` path
- exact skill files to read
- objective
- inputs and artifact paths
- allowed paths
- output contract
- budget and approval policy
- definition of done
- stop conditions
- revision policy

Tell subagents to return: status, changed files, artifact paths, validation performed, assumptions, blockers, risks, and next recommended step.

Target agent skill files must be local to that agent unless they are explicitly listed built-in skills. If a worker reports that it needs another production agent's skill, stop that action and create a separate handoff to the owning agent.

## Post-Run User Changes

When the user changes or updates the request after a full run:

1. Add a `change_requests[]` entry to the production run ledger.
2. Classify impact:
   - channel/source/reference
   - scenario/script/voice
   - voiceover/captions/timestamps
   - visual route/candidates
   - AI generation prompt/output
   - Remotion clip/component
   - timeline/subtitles/audio/render
   - critique/revision plan
   - delivery metadata only
3. Preserve stable ids when possible. Change scene ids only when scene boundaries or order change.
4. Re-run only affected agents and downstream dependents.
5. Update artifact versions and QA.
6. Return a concise diff: what changed, what was regenerated, what stayed valid, and any residual blocker.

Do not restart the whole pipeline unless the request changes the channel format, core topic, or scenario structure enough to invalidate downstream artifacts.

Use `quality-gated-review-loop` when a render candidate exists and the video should not be considered complete until the critic's release-candidate gates pass or the user explicitly accepts residual risks.
