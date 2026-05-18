---
name: autonomous-production-run
description: Run the full Video Factory pipeline autonomously from request to delivery, tracking artifacts, handoffs, approvals, blockers, QA, and post-run user change requests. Use when the Director should keep working until the video package is complete or blocked by approval, rights, budget, missing assets, or an impossible technical dependency.
---

# Autonomous Production Run

Use this after `decompose-video-request` when the user wants a full run, `/goal`-style autonomous execution, or a post-run change/update.

## Run Loop

1. Create or resolve the channel profile under `channels/<channel-slug>/channel-profile.json` when a durable channel is in scope; store its repo-relative POSIX path in `channel_profile_path`.
2. Create or update the video project under `channels/<channel-slug>/projects/<project-slug>/project.json` when a durable deliverable is in scope; store its path in `project_path`.
3. Create or update the media asset manifest under the project folder when source videos, reference videos, web content captures, generated clips, rendered clips, subtitles, review frames, or other media assets are in scope; store its path in `media_asset_manifest_path`.
4. Create or resolve the Remotion app contract matching `codex/contracts/remotion-project.schema.json`; default to the shared `remotion/` app and store the repo-relative contract path in `remotion_project_contract_path`. When reusable Remotion components are in scope, also resolve the app template registry path and any project template contract paths matching `codex/contracts/remotion-template.schema.json`.
5. Create or update a run ledger matching `codex/contracts/production-run.schema.json` inside the project folder. Initialize `context_state` so the run can resume from files after context compaction.
6. Create or update the producer criteria artifact matching `codex/contracts/producer-criteria.schema.json`; store its path in `producer_criteria_path`.
7. Load `AGENTS.md`, the target agent `AGENT.md`, and only the skill files named in each handoff. On resume, first read the production run ledger and the files listed in `context_state.artifacts_to_reload_next`.
8. Build each handoff using `codex/contracts/agent-handoff.schema.json`.
   - A production agent's `handoff_recommendations[]` are not executable work by themselves. Convert them into Director-owned handoffs before downstream agents run.
   - Only name skills that belong to the target agent's folder or explicitly approved built-in skills.
   - Include the project path in downstream handoff inputs once it exists.
   - Include the media asset manifest path, Remotion project contract path, and relevant Remotion template registry/contract paths in downstream handoff inputs once they exist.
   - Include the channel profile path in downstream handoff inputs once it exists.
   - Include the channel format path in downstream handoff inputs once it exists, especially when `visual_system.vfx_rules` extends shared VFX rules.
   - Include the producer criteria path in downstream handoff inputs once it exists.
9. Execute phases in dependency order:
   - Channel profile management before channel format synthesis when a durable channel exists.
   - Media asset manifest creation before reference-video analysis, web content synthesis, visual candidate selection, Remotion clip building, render packaging, or final critique when media files are in scope.
   - Channel Intelligence before scenario and visual planning when references, channel data, web sources, or redundancy concerns exist.
   - Creative Producer before Visual Producer; if voiceover is in scope, produce the voiceover package before final timeline assembly.
   - Visual Producer before InVideo AI Generator and Remotion Clip Builder.
   - Existing Remotion template selection before bespoke Remotion clip implementation only when `template_hint`, reusable channel assets, overlays, lower thirds, caption styles, source cards, or repeated motion patterns are in scope and the template fits the producer criteria. Complex VFX may combine multiple templates or use bespoke Remotion code.
   - InVideo AI Generator and Remotion Clip Builder before Remotion Video Producer.
   - Timeline sync plan before full Remotion assembly and render QA when narration, captions, and visuals must align.
   - Render QA before Video Critic.
   - Video Critic after a render candidate exists and before final delivery when the run targets a deliverable video.
   - Quality gated review loop after the first critique if findings do not pass release-candidate gates.
10. Parallelize only independent work. Do not run a downstream agent before its required input artifact exists.
11. After each handoff, validate that the returned artifact matches its output contract, update the media asset manifest, project index, and run ledger, and send one targeted repair handoff if required fields or QA evidence are missing.
12. Run `context-compaction` after each phase boundary, long handoff, review-loop iteration, user change, or large research/tool-output step. Keep the active working set limited to the current phase, next handoff, approvals, blockers, and `context_state.artifacts_to_reload_next`.
13. Continue until complete, blocked, waiting for approval, or release-candidate gates pass.

## Context Growth Policy

Use `context-compaction` as the durable memory boundary for autonomous work.

- Persist important state in `production-run.context_state`, not in conversation memory.
- Keep raw research, render logs, review frames, transcripts, provider responses, and full critique responses on disk; keep only paths and relevant ids in active context.
- After compaction or resume, read `AGENTS.md`, Director `AGENT.md`, the production run ledger, and only the files listed in `context_state.artifacts_to_reload_next`.
- Before delegating, refresh the reload list with the exact target `AGENT.md`, local skills, input contracts, producer criteria, budget policy, and stop conditions needed by that handoff.
- Mark the run ledger `stale` or `blocked` if the compaction summary points to missing, superseded, or invalidated artifacts.

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
- producer criteria path when available
- channel profile path when available
- channel format path when available
- project path when available
- media asset manifest path when available
- Remotion project contract path when available
- Remotion template registry and template contract paths when relevant
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
   - channel format / VFX rule extensions
   - source media / loaded assets
   - scenario/script/voice
   - voiceover/captions/timestamps
   - visual route/candidates
   - AI generation prompt/output
   - Remotion clip/component
   - timeline/subtitles/audio/render
   - critique/revision plan
   - delivery metadata only
   - channel profile only
3. Preserve stable ids when possible. Change scene ids only when scene boundaries or order change.
4. Re-run only affected agents and downstream dependents.
   - Channel/source/reference changes can invalidate producer criteria, scenario, visual plan, specialist clips, timeline, render, and critique.
   - Channel profile changes can invalidate channel format, producer criteria, scenario voice direction, visuals, Remotion styles, timeline, render, and critique.
   - Channel format changes, including `visual_system.vfx_rules`, can invalidate producer criteria, visual pack constraints, Remotion clip packages, timeline/render QA, and critique.
   - Scenario or narration changes invalidate scene-level voice, visuals, specialist clips, timeline, render, and critique.
   - Voiceover, caption, or timestamp changes invalidate timeline sync, render, and critique.
   - Visual route or candidate changes invalidate affected specialist clips, timeline, render, and critique.
   - AI generation output changes invalidate affected clip candidates, timeline, render, and critique.
   - Remotion clip/component changes invalidate timeline, render, and critique.
   - Remotion template changes invalidate every clip package that references that template, then timeline, render, and critique.
   - Source media or Remotion public projection changes invalidate affected visual candidates, clips, timeline sync, render, and critique.
   - Timeline, subtitle, audio mix, transition, or export changes invalidate render and critique only.
5. Update artifact versions and QA.
6. Return a concise diff: what changed, what was regenerated, what stayed valid, and any residual blocker.

Do not restart the whole pipeline unless the request changes the channel format, core topic, or scenario structure enough to invalidate downstream artifacts.

Use `quality-gated-review-loop` when a render candidate exists and the video should not be considered complete until the critic's release-candidate gates pass or the user explicitly accepts residual risks.
