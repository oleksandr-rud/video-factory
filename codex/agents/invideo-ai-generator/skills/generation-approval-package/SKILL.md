---
name: generation-approval-package
description: Prepare approval packets for InVideo AI and paid AI video generation, including model, prompt, duration, aspect ratio, resolution, generation count, credit/cost estimate, and approval status. Use before spending credits or triggering generation.
---

# Generation Approval Package

Workflow:

1. Collect model route, quality mode, prompt, negative constraints, reference assets, duration, aspect ratio, resolution, and number of variants.
2. Estimate credits/cost from current provider UI or known plan data when available.
3. Check parsed web reference assets: page images/screenshots must have media-manifest approval before they can be submitted as generation references.
4. Mark approval state:
   - `pending` before Director approval.
   - `approved` only after explicit approval.
   - `rejected` when Director denies or budget blocks the run.
5. Record exactly what the generation dialog will submit: prompt, model, duration, aspect ratio, quality mode, reference assets, expected outputs, and target media asset manifest path.
6. If approval is missing, return a package with status `needs_approval`; do not run generation.

Return an approval-ready generation package matching `codex/contracts/ai-video-generation-package.schema.json`.

## Media Manifest Policy

If this skill consumes, references, validates, or defers reference assets, seed images, source clips, generated-output placeholders, provider previews, or future downloaded generation files, update the media asset manifest or return `manifest_actions[]`.

Each manifest action must include `action`, `asset_id`, `canonical_path`, `rights_state`, `technical_metadata_state`, and `reason`; include `remotion_public_path` and `static_file_path` when approved outputs will be mirrored for Remotion.

Use `deferred` until generation is approved and actual files exist. The approval package must identify which source asset ids and future output asset ids will need manifest entries before downstream timeline work.
