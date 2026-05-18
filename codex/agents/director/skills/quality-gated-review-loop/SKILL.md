---
name: quality-gated-review-loop
description: Orchestrate an evaluator-optimizer review loop for rendered videos, routing Video Critic findings back to production agents until quality gates pass, approval is needed, or revision limits are reached. Use after a render candidate exists and before release-candidate approval.
---

# Quality Gated Review Loop

Use this after `autonomous-production-run` reaches a render candidate. The Director owns loop state and routing; Video Critic owns evaluation; production agents own fixes.

## Loop State

Track each loop in `codex/contracts/production-run.schema.json` under `review_loops[]`:

- loop id and iteration number
- render package path and critique report path
- quality gate status: `pass`, `fail`, `needs_approval`, or `blocked`
- invalidated artifacts, preserved artifacts, and rerun scope
- routed revision actions and owning agents
- next action and stop reason

When rerun dependencies are no longer obvious from a single finding, also update `production-run.invalidation_graph` with artifact nodes, dependency edges, and invalidation events. Use the graph to make stale artifacts, preserved artifacts, owner agents, and rerun scope auditable without reconstructing the decision from prose.

## Inputs To Critic

Every critic handoff must include:

- user request and acceptance criteria
- producer criteria artifact matching `codex/contracts/producer-criteria.schema.json`: rules, instructions, restrictions, quality bars, scene criteria, revision policy, and provider constraints that production agents were supposed to apply
- scenario, scene artifact sync report, channel format, reference analysis, visual pack, voiceover package, timeline sync plan, render package, captions, and final video path
- previous critique reports and attempted fixes when iteration > 1
- explicit pass/fail gates and score thresholds

## Review Loop

1. Prepare or update the render package and review assets.
2. Ask Video Critic to run `scene-by-scene-gate-review`, `artifact-consistency-audit`, `multimodal-video-critique`, and `revision-prioritization`. Prefer approved hybrid critique, meaning direct video plus sampled frame stills, when provider limits and media policy allow it; use direct-video-only if frame extraction fails, and use the sampled-frame multimodal fallback when direct video is unavailable.
3. Validate the critique report against `codex/contracts/critique-report.schema.json`.
4. Decide:
   - If all gates pass, mark render package as `approved`, update production run QA to `pass`, record the critique report, and stop.
   - If any blocker exists, route required fixes unless the blocker is rights, approval, missing source, or impossible technical dependency.
   - If major findings exist in gate categories, route fixes unless the configured gate allows them.
   - If only accepted minor findings/notes remain, the Director may approve RC with residual risks.
5. Dispatch revision handoffs by owner agent. Include the exact finding ids, scene ids, timestamps, evidence, producer criteria, previous failed fix attempts, and expected output artifacts.
   - Use `codex/agents/director/references/artifact-problem-routing.md` to map each finding to the correct owner, target skills, output contract, invalidation scope, and definition of done.
   - Do not dispatch a repair to the agent that merely observed the problem unless that agent also owns the affected artifact.
6. Re-render downstream artifacts after fixes, then run Video Critic again.

## Revision Dependency Rules

Record `invalidated_artifacts`, `preserved_artifacts`, and `rerun_scope` in the production run ledger before dispatching fixes.

Also add an `invalidation_graph.events[]` entry when any of these are true:

- more than one owner agent must rerun work
- a change invalidates both media and Remotion artifacts
- a template change affects multiple clip packages
- a channel/source/scenario change invalidates artifacts across more than one phase
- a previous critique iteration is being preserved as evidence while newer artifacts supersede it

- Channel profile, channel/source/reference findings: rerun Channel Intelligence, update channel profile/channel format and producer criteria if needed, then rerun affected Creative Producer, Visual Producer, specialist, Remotion Video Producer, render, and Critic work.
- Scenario, narration, claim, or scene-boundary findings: rerun Creative Producer, update producer criteria scene checks if needed, then rerun affected Visual Producer, InVideo AI Generator or Remotion Clip Builder, Remotion Video Producer, render, and Critic work.
- Voiceover, pronunciation, caption, or timestamp findings: rerun Creative Producer voice/TTS artifacts when needed, then timeline sync, Remotion Video Producer render, and Critic work.
- Visual route, candidate, rights, or continuity findings: rerun Visual Producer for affected scenes, then the required InVideo AI Generator or Remotion Clip Builder handoffs, then Remotion Video Producer, render, and Critic work.
- AI generation prompt/output findings: rerun InVideo AI Generator for affected scenes, then Remotion Video Producer, render, and Critic work.
- Scene artifact sync, stale props, orphaned scene id, duplicate scene pack, or route/template/media conflict findings: run `scene-artifact-sync`, rerun the owning upstream agent for failed rows, then rerun downstream dependents.
- Remotion component, overlay, short-clip, or props findings: rerun Remotion Clip Builder for affected scenes, then scene artifact sync, Remotion Video Producer, render, and Critic work.
- Timeline, subtitles, audio mix, transition, layout alignment, dense-region overlap, motion readability, export, or technical render findings: rerun Remotion Video Producer visual debugging/render work, then Critic work only unless the defect belongs inside a Remotion Clip Builder-owned clip/template.
- Critic evidence gaps: rerun `prepare-multimodal-review-package` or request missing inputs before changing production artifacts.

Graph event fields should include `trigger`, source critique finding or change id when available, affected artifacts, preserved artifacts, rerun scope, owner agents, created timestamp, and notes. Mark any affected node status as `stale` or `invalidated` before dispatching the owner handoff.

When findings are mixed or ambiguous, normalize them into the finding shape from `artifact-problem-routing.md` before creating handoffs. Prefer one owner-scoped handoff per artifact owner over one broad handoff that asks a specialist to coordinate unrelated repairs.

## Default Gate Policy

Use stricter gates when the user supplies them. Otherwise:

- no unresolved blocker findings
- no unresolved major findings in story, factual, rights, sync, subtitles, audio, platform, or technical categories
- overall score >= 8
- story_clarity, visual_relevance, subtitle_sync, platform_fit, and factual_alignment >= 7
- every required scene has a scene review
- scene artifact sync has no unwaived stale props, orphaned scene ids, duplicate scene packs, or route/template/media conflicts
- every required production criterion is `pass`, `not_applicable`, or explicitly waived by Director/user

## Stop Conditions

Stop and report instead of looping when:

- max review iterations is reached; default 3
- the same blocker appears in two consecutive critique reports after attempted fixes
- a fix needs paid generation, licensed media, voice/model spend, or user approval
- the critic cannot inspect enough evidence to make a gate decision
- the user changes the brief enough to invalidate the scenario or channel format

Do not let the same producer and same critic silently optimize each other forever. Preserve all critique reports so the Director can see whether quality is actually improving.
