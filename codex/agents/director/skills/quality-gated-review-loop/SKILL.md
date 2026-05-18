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

## Inputs To Critic

Every critic handoff must include:

- user request and acceptance criteria
- producer criteria artifact matching `codex/contracts/producer-criteria.schema.json`: rules, instructions, restrictions, quality bars, scene criteria, revision policy, and provider constraints that production agents were supposed to apply
- scenario, channel format, reference analysis, visual pack, voiceover package, timeline sync plan, render package, captions, and final video path
- previous critique reports and attempted fixes when iteration > 1
- explicit pass/fail gates and score thresholds

## Review Loop

1. Prepare or update the render package and review assets.
2. Ask Video Critic to run `scene-by-scene-gate-review`, `artifact-consistency-audit`, `multimodal-video-critique`, and `revision-prioritization`.
3. Validate the critique report against `codex/contracts/critique-report.schema.json`.
4. Decide:
   - If all gates pass, mark render package as `approved`, update production run QA to `pass`, record the critique report, and stop.
   - If any blocker exists, route required fixes unless the blocker is rights, approval, missing source, or impossible technical dependency.
   - If major findings exist in gate categories, route fixes unless the configured gate allows them.
   - If only accepted minor findings/notes remain, the Director may approve RC with residual risks.
5. Dispatch revision handoffs by owner agent. Include the exact finding ids, scene ids, timestamps, evidence, producer criteria, previous failed fix attempts, and expected output artifacts.
6. Re-render downstream artifacts after fixes, then run Video Critic again.

## Revision Dependency Rules

Record `invalidated_artifacts`, `preserved_artifacts`, and `rerun_scope` in the production run ledger before dispatching fixes.

- Channel profile, channel/source/reference findings: rerun Channel Intelligence, update channel profile/channel format and producer criteria if needed, then rerun affected Creative Producer, Visual Producer, specialist, Remotion Video Producer, render, and Critic work.
- Scenario, narration, claim, or scene-boundary findings: rerun Creative Producer, update producer criteria scene checks if needed, then rerun affected Visual Producer, InVideo AI Generator or Remotion Clip Builder, Remotion Video Producer, render, and Critic work.
- Voiceover, pronunciation, caption, or timestamp findings: rerun Creative Producer voice/TTS artifacts when needed, then timeline sync, Remotion Video Producer render, and Critic work.
- Visual route, candidate, rights, or continuity findings: rerun Visual Producer for affected scenes, then the required InVideo AI Generator or Remotion Clip Builder handoffs, then Remotion Video Producer, render, and Critic work.
- AI generation prompt/output findings: rerun InVideo AI Generator for affected scenes, then Remotion Video Producer, render, and Critic work.
- Remotion component, overlay, or short-clip findings: rerun Remotion Clip Builder for affected scenes, then Remotion Video Producer, render, and Critic work.
- Timeline, subtitles, audio mix, transition, export, or technical render findings: rerun Remotion Video Producer, render, and Critic work only.
- Critic evidence gaps: rerun `prepare-multimodal-review-package` or request missing inputs before changing production artifacts.

## Default Gate Policy

Use stricter gates when the user supplies them. Otherwise:

- no unresolved blocker findings
- no unresolved major findings in story, factual, rights, sync, subtitles, audio, platform, or technical categories
- overall score >= 8
- story_clarity, visual_relevance, subtitle_sync, platform_fit, and factual_alignment >= 7
- every required scene has a scene review
- every required production criterion is `pass`, `not_applicable`, or explicitly waived by Director/user

## Stop Conditions

Stop and report instead of looping when:

- max review iterations is reached; default 3
- the same blocker appears in two consecutive critique reports after attempted fixes
- a fix needs paid generation, licensed media, voice/model spend, or user approval
- the critic cannot inspect enough evidence to make a gate decision
- the user changes the brief enough to invalidate the scenario or channel format

Do not let the same producer and same critic silently optimize each other forever. Preserve all critique reports so the Director can see whether quality is actually improving.
