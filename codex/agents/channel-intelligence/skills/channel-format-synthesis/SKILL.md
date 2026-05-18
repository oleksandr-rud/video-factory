---
name: channel-format-synthesis
description: Create or update a reusable channel format package from reference analysis, source content, best-practice specs, and channel data. Use when the production needs consistent channel format rules, themes, colors, video structure, recurring materials, and reusable constraints across many videos.
---

# Channel Format Synthesis

Workflow:

1. Read the channel profile, reference analysis package, source ledger, and media asset manifest when media evidence exists.
2. Define the channel promise, audience, content pillars, video themes, and platform targets.
3. Define reusable narrative patterns: hook types, episode structure, pacing bands, proof style, transitions between ideas, and CTA behavior.
4. Define reusable visual/audio systems from style extraction and channel profile defaults.
5. Populate `visual_system.reusable_assets`, `visual_system.reusable_template_ids`, and `visual_system.remotion_template_contract_paths` when reusable Remotion templates should be allowed for the channel format.
6. Prefer project/channel template contracts over shared template contracts when the channel format requires different colors, typography, safe areas, aspect ratios, motion behavior, or dependencies.
7. Define flex zones where each episode should vary: unique angle, examples, visual moments, data, references, opening pattern, and CTA wording.
8. Add anti-redundancy rules and channel-level "avoid" patterns.
9. Attach evidence ids, source asset ids, template ids, template contract paths, and confidence notes for important rules.

Template routing:

- Use shared contracts under `remotion/templates/` only as base primitives.
- Use project/channel contracts under `channels/<channel-slug>/projects/<project-slug>/remotion/templates/` for format-specific variants.
- If a needed template does not exist, record the desired reusable pattern and constraints, but do not implement it. The Director should route that to Remotion Clip Builder with `remotion-template-library`.

Return a channel format package matching `codex/contracts/channel-format.schema.json`, with `channel_profile_id`, `channel_slug`, and `channel_root_path` when a persistent channel exists.
