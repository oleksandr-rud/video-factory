---
name: visual-validation
description: Validate visual candidates with evidence-backed pass/fail states, rights and technical guardrails, continuity checks, editability notes, candidate score updates, blockers, and definition-of-done criteria. Use before candidates are ranked, selected, handed to Remotion, or accepted into a render candidate.
---

# Visual Validation

Visual validation is a safety gate, not a taste pass. Unknown rights, missing media, unverified provenance, or unusable technical metadata must not become `approved` by default.

## Inputs

- Scene visual pack and candidate requirements
- Clip candidates from stock, user media, Remotion, or AI generation
- Scenario scene list and neighboring scene context
- Channel format, brand rules, platform specs, rights policy, and budget policy
- Local file paths, source URLs, provider metadata, media asset manifest entries, or generation package paths

## Workflow

1. Verify candidate identity: `candidate_id`, `scene_id`, route, provider/source, local path or URL, media asset id when available, and provenance.
2. Check semantic fit against the scene purpose, narration, visual intent, and channel format.
3. Check technical fit: resolution, aspect ratio, crop risk, duration, fps, audio presence, start/end usability, Remotion `staticFile()` readiness when needed, and overlay safe areas.
4. Check rights fit: license summary, attribution, paid approval, likeness/logo concerns, watermark risk, and provider restrictions.
5. Check continuity with adjacent scenes and overall video visual language.
6. Check brand safety, sensitive content, factual/source alignment, and editability.
7. Update `clip-candidate` scores and status. Do not rank an item as primary unless rights and technical fit are pass or explicitly approved.

## Required Output

Update each affected `codex/contracts/clip-candidate.schema.json` item:

- `technical`
- `license_summary`
- `media_asset_id`
- `remotion_static_file_path`
- `scores.semantic_fit`
- `scores.continuity_fit`
- `scores.technical_fit`
- `scores.rights_fit`
- `scores.editability`
- `scores.total`
- `status`
- `rejection_reason` when rejected

Return this validation summary:

```json
{
  "status": "complete | needs_approval | blocked | needs_revision",
  "scenario_id": "string",
  "scene_results": [
    {
      "scene_id": "string",
      "candidate_results": [
        {
          "candidate_id": "string",
          "overall_status": "pass | fail | partial | unknown | needs_approval",
          "semantic_fit": { "status": "pass | fail | partial | unknown", "evidence": "string" },
          "technical_fit": { "status": "pass | fail | partial | unknown", "evidence": "string" },
          "rights_fit": { "status": "pass | fail | unknown | needs_approval", "evidence": "string" },
          "continuity_fit": { "status": "pass | fail | partial | unknown", "evidence": "string" },
          "brand_safety": { "status": "pass | fail | unknown", "evidence": "string" },
          "editability": { "status": "pass | fail | partial | unknown", "evidence": "string" },
          "recommendation": "select | fallback | reject | needs_approval | needs_specialist_review",
          "blocking_reasons": ["string"]
        }
      ]
    }
  ],
  "approvals_needed": ["string"],
  "fallback_gaps": ["string"],
  "next_recommended_step": "string"
}
```

## Status Policy

- Use `approved` only when semantic, technical, rights, continuity, and editability checks pass or explicit approval covers the risk.
- Use `needs_approval` for paid/licensed media, unclear but resolvable rights, likeness/logo concerns, or required downloads.
- Use `rejected` for unfixable rights, severe technical mismatch, misleading visuals, watermarks, or continuity failures that would damage the final render.
- Keep a fallback candidate or report the fallback gap before the Director proceeds to full assembly.

## Definition Of Done

- Every candidate has validation evidence, scores, status, and any rejection or approval reason.
- No candidate with unknown rights is silently promoted.
- Technical metadata is present or the candidate is marked unknown/blocked.
- Selected and fallback candidates are usable by Remotion Video Producer without redoing validation.
