---
name: write-scenario
description: Write a timed video scenario with narration, on-screen text, scene purpose, visual intent, source alignment, channel-format fit, and claim-check notes. Use for scriptwriting, social video structure, explainer copy, product promo scripts, and scene-level planning.
---

# Write Scenario

1. Read the Director brief, reference analysis, channel format, and constraints.
2. When `reference-analysis.claim_ledger[]` or `web_pages[]` are present, use them as the source of factual claim options. Do not invent page facts from memory.
3. Treat `claim_ledger[].support_state=needs_review` or unknown confidence as a script limitation unless another supplied source supports the claim.
4. Choose a structure: hook, context, proof, payoff, CTA.
5. Draft scenes with timestamps and stable scene ids.
6. Keep narration compatible with target duration.
7. Mark factual claims that need verification and source ids when known.
8. Add initial visual intent without choosing footage. Refer to `web_pages[].visual_evidence_candidates` only as evidence or visual inspiration unless the manifest marks the image/screenshot approved.
9. Add a novelty angle so the episode follows the channel format without becoming repetitive.

Return JSON-compatible content matching `codex/contracts/scenario.schema.json`.
