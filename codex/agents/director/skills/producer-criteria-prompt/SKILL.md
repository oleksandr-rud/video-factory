---
name: producer-criteria-prompt
description: Create or update the first-class producer criteria artifact for a Video Factory run, including acceptance criteria, hard quality gates, scene-specific review rules, provider restrictions, and revision policy. Use before production handoffs and before Video Critic review loops.
---

# Producer Criteria Prompt

Use this after `decompose-video-request` and before production handoffs. The artifact is the binding review contract for producers, the Video Critic, and the Director.

## Workflow

1. Create a JSON artifact matching `codex/contracts/producer-criteria.schema.json`.
2. Convert the user request, channel format, source constraints, platform requirements, budget policy, and known approvals into discrete criteria.
3. Separate:
   - acceptance criteria: what the finished video must accomplish
   - hard gates: failures that block release unless fixed or waived
   - required rules: instructions all producers must follow
   - forbidden rules: things producers must avoid
   - style rules: preferred channel and brand behavior
   - provider constraints: limits for TTS, AI generation, stock, Remotion templates, paid APIs, and licensed assets
   - scene criteria: per-scene checks keyed by `scene_id`
4. Set default review thresholds unless the user provides stricter gates:
   - `overall_min`: 8
   - `category_min`: 7
   - `max_major_findings`: 0 for story, factual, rights, sync, subtitles, audio, platform, and technical categories
   - `allow_minor_findings`: true only when they do not violate a hard gate
5. Record the revision policy:
   - max review iterations, default 3
   - rerun only affected artifacts when possible
   - stop when the same blocker repeats after an attempted fix

## Rules

- Treat this artifact as versioned run state. Update it when the user changes requirements; do not silently rewrite it after production has started.
- Keep criteria testable. Avoid vague gates such as "make it better"; rewrite them as observable checks.
- Preserve scene ids. If the scenario is not ready yet, create global criteria first and update `scene_criteria[]` after the scenario exists.
- Include rights, budget, and approval gates even when no paid work is currently planned.
- Pass the criteria path in every downstream handoff once it exists.
