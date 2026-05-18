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
