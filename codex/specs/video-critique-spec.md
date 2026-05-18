# Video Critique Spec

## Purpose

The Video Critic gives the pipeline an independent final review pass. It validates the actual rendered output, not just the production contracts, and returns revision guidance that the Director can route back to the owning agents.

## Why This Is A Separate Agent

The Remotion Video Producer already owns assembly and render QA. A separate critic is useful only at the final gate because it should not share the producer's assumptions. It reviews the video as a viewer, compares it against the scenario and channel format, checks artifacts for consistency, and prioritizes fixes without editing files itself.

## Multimodal Review Route

Use sampled frames plus artifact text as the default model input:

- final video path
- ffprobe metadata
- representative frame samples
- scenario and timeline sync plan
- captions/subtitles and voiceover package
- render package and QA notes
- reference analysis and channel format when available

Direct video-file input should only be used if the chosen provider explicitly supports it. For OpenAI, use Responses API image inputs with extracted frames unless newer approved docs and tooling are wired.

## Required Output

The critic returns `codex/contracts/critique-report.schema.json` with:

- model/provider notes and approval state
- reviewed input paths
- timestamped observations
- category scores
- findings with severity, category, evidence, recommendation, timestamp, and owner agent
- prioritized revision plan
- limitations and residual risks

## Review Loop Pattern

Use an evaluator-optimizer loop:

1. Producer agents create or revise the render candidate.
2. Video Critic evaluates the actual render against the producer criteria artifact, scenario, channel format, artifacts, and sampled video frames.
3. Director reads the critique report and gate decision.
4. If gates fail, Director dispatches targeted handoffs to the owning agents with exact findings, scene ids, timestamps, criteria, and expected artifacts.
5. Downstream agents regenerate only affected artifacts, Remotion Video Producer renders a new candidate, and Video Critic reviews again.
6. The loop stops only when gates pass, a user waiver is recorded, an approval/blocker is hit, the same blocker repeats, or max iterations is reached.

The loop state lives in `production-run.schema.json` under `review_loops[]`. Do not hide failed critique reports; each iteration is evidence for whether the system is improving or gaming the review.

## Scene-Level Gate Review

The critic must produce `scene_reviews[]` for every scenario scene. Each scene review compares the final video against:

- scene purpose and narration
- producer rules and restrictions
- selected visual route and expected visual intent
- source/factual alignment
- voiceover, captions, and sync
- channel style and anti-redundancy
- platform safe areas and readability

Every production criterion should be marked `pass`, `fail`, `waived`, `not_applicable`, or `unknown`. Missing evidence is not a pass.

## Default Release Gates

Use user-supplied gates first. Otherwise a render can become release candidate only when:

- no unresolved blocker findings
- no unresolved major findings in story, factual, rights, sync, subtitles, audio, platform, or technical categories
- overall score is at least 8
- story clarity, visual relevance, subtitle sync, platform fit, and factual alignment are at least 7
- every required scene has a scene review
- every required production criterion passes, is not applicable, or is explicitly waived

## QA Standard

A critique report is useful only when it distinguishes:

- delivery blockers
- major viewer-experience defects
- minor polish issues
- optional notes or experiments

It must map each actionable finding to a responsible agent or Director decision.

## Evidence Used

Anthropic describes the evaluator-optimizer workflow as one model generating while another evaluates and provides feedback in a loop, and says it fits when criteria are clear and iterative refinement adds value. Source: https://www.anthropic.com/engineering/building-effective-agents

LangGraph documents the same pattern as a generator node, evaluator node, and conditional edge that either accepts or routes feedback back to generation. Source: https://docs.langchain.com/oss/python/langgraph/workflows-agents

Agent evaluation guidance emphasizes rubrics, graders, traces, and outcomes rather than only final text. Anthropic also notes that video-editing agent evals can be framed around "don't break things, do what I asked, and do it well." Source: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents

Self-Refine and Reflexion support iterative feedback as a useful pattern, but reward-hacking research shows why this project keeps the critic independent, records every iteration, uses explicit gates, and stops on repeated blockers instead of optimizing judge scores forever. Sources: https://arxiv.org/abs/2303.17651, https://arxiv.org/abs/2303.11366, and https://arxiv.org/abs/2407.04549
