---
name: scene-breakdown
description: Break or revise a script/scenario into contract-ready scenes with stable ids, contiguous timing, source linkage, voice notes, on-screen text, visual intent, downstream invalidation notes, and definition-of-done validation. Use when downstream visual, Remotion, voiceover, timeline, or critic work needs precise per-scene inputs.
---

# Scene Breakdown

Treat scene breakdown as a production contract. Ambiguity here amplifies downstream rework, so fail closed: mark unknown sources, timing gaps, or unstable scene boundaries instead of silently guessing.

## Inputs

- Director brief, target platform, aspect ratio, duration target, language, and audience
- Scenario draft, script, outline, source notes, reference analysis, and channel format rules
- Existing scenario artifact when revising
- Producer criteria when available
- Known downstream artifacts when scene ids may already be in use

## Workflow

1. Assign deterministic `scene_id` values. Reuse existing ids when revising unless scene order or boundaries genuinely change.
2. Create contiguous scene timing. Do not overlap scenes or leave unexplained gaps.
3. Keep each scene short enough for the platform and explicit enough for Visual Producer, voiceover, timeline sync, and critique.
4. Link factual claims and source-derived statements with `source_ids`; prefer `reference-analysis.claim_ledger[]` claim ids/evidence refs when available.
5. Mark unsupported, contradicted, needs-review, or low-confidence web claims in `source_alignment_notes` or scene notes instead of smoothing them into narration.
6. Preserve channel format without copying reference videos shot-for-shot or copying supplied article/page images without approval.
7. Record downstream invalidation risk whenever a scene id, timing, script, source claim, or visual intent changes after downstream work exists.

## Required Output

Populate or revise `codex/contracts/scenario.schema.json`:

- top level: `scenario_id`, `title`, `audience`, `platform`, `duration_seconds`, and optional project/channel/reference fields when supplied
- each scene: `scene_id`, `start_seconds`, `end_seconds`, `purpose`, `script`, `onscreen_text`, `visual_intent`, `voice_notes`, `source_ids`, `format_notes`, and `redundancy_notes`

Also return this handoff summary:

```json
{
  "status": "complete | needs_revision | blocked",
  "scenario_id": "string",
  "changed_scene_ids": ["string"],
  "new_scene_ids": ["string"],
  "removed_scene_ids": ["string"],
  "timing_validation": {
    "contiguous": true,
    "no_overlaps": true,
    "duration_matches_target": true
  },
  "source_validation": {
    "unsupported_claims": ["string"],
    "missing_source_ids": ["string"]
  },
  "downstream_invalidation": [
    {
      "artifact_type": "visual | voiceover | ai_generation | remotion_clip | timeline | render | critique",
      "reason": "string"
    }
  ],
  "assumptions": ["string"],
  "blockers": ["string"],
  "next_recommended_step": "string"
}
```

## Definition Of Done

- Every scene has stable id, order, start/end seconds, purpose, script, visual intent, and voice notes.
- Timing is contiguous, non-overlapping, and fits the duration target or explicitly explains the variance.
- Scene ids are preserved when downstream artifacts already exist, or invalidation is clearly reported.
- Claims are tied to sources or marked unsupported.
- Visual, voiceover, timeline, and critic agents can proceed without inventing missing scene intent.

## Stop Conditions

Stop with `blocked` when the source material is insufficient for required factual claims, the user request conflicts with platform/rights constraints, or a scene-id change would invalidate downstream work without Director approval.
