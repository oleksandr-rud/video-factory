---
name: scene-by-scene-gate-review
description: Evaluate a rendered video scene by scene against the original production criteria, generation rules, restrictions, scenario, channel format, and quality gates. Use when the reviewer loop needs pass/fail gate decisions and actionable evidence for each scene before approving a release candidate.
---

# Scene By Scene Gate Review

Use this inside the review loop before final release-candidate approval. It extends `multimodal-video-critique` with explicit pass/fail gates.

## Inputs

Read all supplied criteria, not just the rendered video:

- user acceptance criteria
- producer criteria artifact with rules, instructions, restrictions, scene criteria, revision policy, and intended style constraints
- scenario and scene list
- channel format and reference analysis
- media asset manifest, visual pack, selected candidates, AI generation packages, Remotion clip packages
- voiceover package, captions, timeline sync plan, render package, sampled review frames, and hybrid/direct-video observations when approved
- previous critique reports and revision attempts if this is not the first review iteration

## Workflow

1. Normalize producer criteria into discrete checks:
   - required
   - forbidden
   - scoring threshold
   - stylistic preference
   - not applicable
2. Evaluate every scene against:
   - scenario purpose and narration
   - visual relevance and visible artifacts
   - audio/caption timing and readability
   - source/factual alignment
   - brand/channel style and anti-redundancy rules
   - platform and safe-area rules
   - any scene-specific production restrictions
3. Add a scene review for every scene id. Missing evidence is a finding, not a reason to silently pass.
4. Convert failures into findings with timestamp, scene id, evidence, recommendation, owner agent, and fix status.
5. Produce gate results:
   - `pass`: criterion is satisfied
   - `fail`: criterion is violated and must be fixed or waived
   - `waived`: Director/user accepted the risk
   - `not_applicable`: criterion does not apply to this scene or render
   - `unknown`: evidence is insufficient
6. Set overall status:
   - `approved` only if all hard gates pass
   - `needs_revision` if production agents can fix it
   - `needs_approval` if spend, rights, source material, or waiver is needed
   - `blocked` if the critic cannot inspect enough evidence or the same blocker persists

## Gate Discipline

- Do not pass a video because it is generally good if a hard rule failed.
- Do not fail a video for taste if the issue is outside the production criteria and not a viewer-experience defect.
- Compare against the actual final render, not the intended plan.
- If hybrid/direct-video evidence is unavailable and frame samples are insufficient, request more samples through `prepare-multimodal-review-package` before declaring pass.
