---
name: decompose-video-request
description: Convert a user's video request into a staged production plan and broad production-agent handoffs. Use when the Director needs to choose whether to call Channel Intelligence, Creative Producer, Visual Producer, InVideo AI Generator, Remotion Clip Builder, Remotion Video Producer, or Video Critic, define scene-level artifacts, set budget gates, and establish acceptance criteria.
---

# Decompose Video Request

Convert the user request into a Director-owned production brief, artifact path map, and first handoff plan. This skill chooses routing; it does not perform specialist production work.

## Inputs

- User request, attached/source files, URLs, target platform, deadline, and explicit constraints
- Existing channel/project/run paths when resuming or changing a prior run
- Repo architecture rules, agent `AGENT.md` files, Director handoff skill map, and contract schemas
- Budget policy, provider preferences, credentials availability, and approval state
- Existing channel profile, source/reference analysis, producer criteria, media manifest, Remotion app contract, or render artifacts when available

## Workflow

1. Extract goal, audience, platform, duration, aspect ratio, language, tone, source material, deliverables, and success criteria.
2. Classify the request as analysis-only, planning, asset preparation, full autonomous production, revision, review, or delivery.
3. Decide which broad production and validation agents are needed: Channel Intelligence, Creative Producer, Visual Producer, InVideo AI Generator, Remotion Clip Builder, Remotion Video Producer, Video Critic.
   - Include Visual Producer for every deliverable video, channel-format build/update, reference-video-driven format, visual-format-only reference, reusable visual system, stock/media/generative route, Remotion visual route, or scene-level composition requirement. Do not classify it as optional just because provider search/download/generation needs approval.
4. If the request names a durable channel, create or resolve `channels/<channel-slug>/channel-profile.json` through Channel Intelligence `channel-profile-management`.
5. If the request is a durable deliverable, create or resolve `channels/<channel-slug>/projects/<project-slug>/project.json` using `codex/contracts/video-project.schema.json`.
6. Create or resolve the shared Remotion app contract using `codex/contracts/remotion-project.schema.json`; default to the repo `remotion/` app unless a project-specific app is justified.
7. If reusable Remotion components are likely, resolve the app template registry and reserve project template contract paths using `codex/contracts/remotion-template.schema.json`.
8. Create stable repo-relative POSIX artifact paths under the project folder for the run ledger, producer criteria, media manifest, reference analysis, source reports, channel format, scenario, voiceover package, visual pack, candidates, source media, AI generation packages, Remotion templates/clips, timeline sync plan, render packages, critique reports, review assets, and QA.
9. Run `producer-criteria-prompt` to create the first criteria artifact. Update scene-specific criteria after scenario scene ids exist, and update visual criteria again after Visual Producer returns the scene visual pack/research queries.
10. Define approval gates for paid APIs, licensed media, remote render-time assets, provider downloads, generation jobs, voice/TTS, external critique, likeness/logo use, and release waivers.
11. Build handoffs using `codex/contracts/agent-handoff.schema.json`; include project path, media asset manifest path, Remotion project contract path, Remotion template registry/contract paths, channel profile path, channel format path, and producer criteria path when available.
12. Treat Visual Producer `handoff_recommendations[]` as routing input only. The Director decides whether to create downstream InVideo AI Generator or Remotion Clip Builder handoffs and names the target agent's local skills.
13. Mark visual research as a non-skippable dependency in the plan when channel format, producer criteria, scene composition, template requirements, VFX requirements, source-card rules, or provider choices depend on reference/source visuals. The planned Visual Producer output must include `scene-visual-pack.schema.json` plus route/query research, fallback coverage, and approval/deferred actions.
14. Use `autonomous-production-run` when the user expects the Director to keep working until complete or blocked.

## Required Output

Return:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "production_brief": {
    "request_id": "string",
    "objective": "string",
    "audience": "string",
    "platform": "string",
    "duration_target": "string",
    "aspect_ratio": "string",
    "deliverables": ["string"],
    "acceptance_criteria": ["string"]
  },
  "artifact_paths": {
    "project_path": "string",
    "production_run_path": "string",
    "producer_criteria_path": "string",
    "media_asset_manifest_path": "string",
    "remotion_project_contract_path": "string"
  },
  "agent_plan": [
    {
      "agent": "channel-intelligence | creative-producer | visual-producer | invideo-ai-generator | remotion-clip-builder | remotion-video-producer | video-critic",
      "phase": "string",
      "depends_on": ["string"],
      "skills_to_read": ["string"],
      "output_contract": "string",
      "non_skippable": false,
      "approval_gates": ["string"],
      "definition_of_done": ["string"]
    }
  ],
  "initial_handoffs": ["string"],
  "approvals_needed": ["string"],
  "next_recommended_step": "string"
}
```

## Contract Fields Populated

- `agent-handoff.schema.json`: planned or created handoffs with role, scope, inputs, allowed paths, local skills, output contract, budget policy, and stop conditions
- `producer-criteria.schema.json`: created through `producer-criteria-prompt`
- `production-run.schema.json`: run objective, phase plan, approvals, blockers, handoffs, and context state when a durable run is in scope
- `video-project.schema.json`: project index when a durable deliverable is in scope
- `media-asset-manifest.schema.json`: created or resolved when media/source/generated/rendered assets are in scope

## Status Policy

- Return `complete` when the Director has a route plan, stable artifact paths, approval gates, and first handoffs or next local step.
- Return `needs_approval` when the next necessary action spends credits, uses paid APIs, downloads/licences media, uploads media externally, generates voice/video, performs paid critique, uses rights-sensitive material, or waives release gates.
- Return `blocked` when required source files, credentials, channel/project state, legal rights, or technical setup cannot be resolved.
- Return `needs_revision` when the user request is too vague to define objective, platform, deliverables, or acceptance criteria.

## Evidence Required

Preserve source request details, channel/project/run paths, contract paths, approval assumptions, chosen agent dependencies, and any explicit user constraints. Do not rely on conversation-only context for paths that downstream agents need.

## Media Manifest Policy

Create or resolve a media asset manifest path before any agent loads, downloads, generates, renders, samples, or reviews media. Early decomposition may return `manifest_actions[]` as `deferred`; later handoffs must pass the manifest path and require agents to update it or explain why they could not.

## Approval And Stop Conditions

Stop before calling a paid API, spending generation credits, downloading licensed assets, uploading media to providers, generating voice/video, using paid critique, using likeness/logo-sensitive assets, or waiving a failed gate without explicit user approval. Handoffs must carry budget policy and stop conditions, not just a task description.

## Definition Of Done

- Production brief and acceptance criteria are explicit.
- Durable artifact paths are repo-relative POSIX strings.
- Producer criteria path exists or is scheduled before production handoffs.
- Approval gates are named before any spend/download/generation.
- Agent plan respects ownership boundaries and Director-managed handoffs.

## Handoff Summary Shape

Return:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "artifact_paths": ["string"],
  "changed_files": ["string"],
  "populated_contracts": [
    "codex/contracts/agent-handoff.schema.json",
    "codex/contracts/production-run.schema.json",
    "codex/contracts/producer-criteria.schema.json"
  ],
  "manifest_actions": [
    {
      "action": "created | updated | not_applicable | deferred",
      "asset_id": "string",
      "reason": "string"
    }
  ],
  "validation_performed": ["request classification", "artifact path plan", "agent dependency plan", "approval gate review", "contract mapping"],
  "assumptions": ["string"],
  "blockers": ["string"],
  "risks": ["string"],
  "next_recommended_step": "string"
}
```
