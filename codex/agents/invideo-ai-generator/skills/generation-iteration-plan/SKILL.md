---
name: generation-iteration-plan
description: Plan AI video generation variants and rerolls with controlled prompt changes. Use when a scene needs 2-3 candidate clips, model comparisons, or targeted regeneration after QA failures.
---

# Generation Iteration Plan

Workflow:

1. Define the baseline prompt and target model/settings.
2. Plan 2-3 variants only when the budget allows:
   - camera variant
   - performance/action variant
   - lighting/style variant
   - model/quality variant
3. Change one meaningful variable at a time so QA can attribute improvements or failures.
4. Preserve version ids, prompts, negative constraints, settings, reference assets, and credit estimates.
5. After QA, decide whether to accept, reroll with a targeted fix, switch model, fall back to stock, or fall back to Remotion.

Return variant specs and stop conditions. Do not generate variants without approval.

## Media Manifest Policy

If this skill consumes, validates, compares, or defers generated variants, reference assets, provider previews, downloaded outputs, thumbnails, prompt sidecars, or QA evidence media, update the media asset manifest or return `manifest_actions[]`.

Each manifest action must include `action`, `asset_id`, `canonical_path`, `rights_state`, `technical_metadata_state`, and `reason`; include `remotion_public_path` and `static_file_path` when an accepted output will be mirrored for Remotion.

Use `deferred` for planned variants before generation approval, rerolls that may spend credits, provider outputs not yet downloaded, or files that still need QA before becoming timeline candidates.
