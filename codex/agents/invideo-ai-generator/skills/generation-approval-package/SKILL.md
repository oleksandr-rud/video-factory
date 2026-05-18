---
name: generation-approval-package
description: Prepare approval packets for InVideo AI and paid AI video generation, including model, prompt, duration, aspect ratio, resolution, generation count, credit/cost estimate, and approval status. Use before spending credits or triggering generation.
---

# Generation Approval Package

Workflow:

1. Collect model route, quality mode, prompt, negative constraints, reference assets, duration, aspect ratio, resolution, and number of variants.
2. Estimate credits/cost from current provider UI or known plan data when available.
3. Mark approval state:
   - `pending` before Director approval.
   - `approved` only after explicit approval.
   - `rejected` when Director denies or budget blocks the run.
4. Record exactly what the generation dialog will submit: prompt, model, duration, aspect ratio, quality mode, reference assets, and expected outputs.
5. If approval is missing, return a package with status `needs_approval`; do not run generation.

Return an approval-ready generation package matching `codex/contracts/ai-video-generation-package.schema.json`.
