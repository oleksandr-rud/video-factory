---
name: producer-criteria-prompt
description: Create or update the first-class producer criteria artifact for a Video Factory run, including acceptance criteria, hard quality gates, scene-specific review rules, provider restrictions, and revision policy. Use before production handoffs and before Video Critic review loops.
---

# Producer Criteria Prompt

Use this after `decompose-video-request` and before production handoffs. The artifact is the binding review contract for producers, the Video Critic, and the Director.

## Workflow

1. Create a JSON artifact matching `codex/contracts/producer-criteria.schema.json`.
2. Convert the user request, channel profile, channel format, media asset manifest, Remotion setup constraints, source constraints, platform requirements, budget policy, known approvals, and Visual Producer research artifacts into discrete criteria.
3. Separate:
   - acceptance criteria: what the finished video must accomplish
   - hard gates: failures that block release unless fixed or waived
   - required rules: instructions all producers must follow
   - forbidden rules: things producers must avoid
   - style rules: preferred channel and brand behavior
   - provider constraints: limits for TTS, AI generation, stock, Remotion templates, paid APIs, and licensed assets
   - template constraints: allowed reusable template ids, required template contract paths, project/channel override rules, safe-area restrictions, and whether shared templates may be used directly
   - VFX constraints: channel-format VFX rule extensions, required hardening triggers, alpha/export rules, benchmark requirements, fallback expectations, and scene-level VFX restrictions
   - media constraints: allowed source assets, required local media, Remotion `staticFile()` requirements, remote-asset restrictions, and evidence refs
   - visual research constraints: required scene visual pack path, scene artifact sync path when available, visual research query coverage, primary/fallback route coverage, target-content substitution rules, reference beat/decomposition refs, required source-card/Remotion/AI/stock route evidence, provider search/download approval gates, and deferred fallback policy
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
- Preserve visual research as a binding input. For deliverable videos, criteria are draft until the scene visual pack and visual research query groups exist or are explicitly blocked/deferred with approval notes.
- Include a hard scene-sync gate: stale props, stale scene packs, duplicate scene packs, orphaned scene ids, or route/template/media conflicts block render/release unless explicitly waived.
- Include rights, budget, and approval gates even when no paid work is currently planned.
- Include channel brand, voice, color, format, and governance gates when a channel profile exists.
- Include Remotion template governance when reusable templates are in scope: project/channel contracts override shared contracts, shared templates are base primitives, and breaking changes to reusable template props require a new version or scene-specific instance.
- Include channel-format VFX extensions when present. Copy binding items from `visual_system.vfx_rules` into `vfx_constraints`, hard gates, style rules, or scene criteria rather than relying on the Remotion skills to infer channel intent.
- After Visual Producer completes research, update hard gates and scene criteria with concrete visual requirements: selected route, fallback route, evidence refs, reference material refs, safe areas, source-card rules, target-content substitution, template hints, VFX requirements, and approval blockers. Do not let downstream generation/rendering proceed against stale draft visual criteria.
- Pass the criteria path in every downstream handoff once it exists.
