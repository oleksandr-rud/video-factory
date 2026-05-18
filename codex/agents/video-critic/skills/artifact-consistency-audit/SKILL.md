---
name: artifact-consistency-audit
description: Audit final video artifacts for consistency across scenario, render package, timeline sync plan, captions, voiceover, visual candidates, rights notes, and platform requirements. Use before or alongside multimodal critique to catch contract and provenance errors.
---

# Artifact Consistency Audit

Use this to catch issues a visual model may miss.

## Checks

1. Scenario and render package:
   - scenario id matches
   - platform, duration, aspect ratio, fps, width, and height are plausible
   - scene order is preserved or intentionally revised
2. Timeline sync:
   - every scene has frame ranges
   - selected visuals exist or blockers are recorded
   - audio and captions reference stable paths
3. Captions and voice:
   - caption JSON/SRT exists where required
   - voiceover package scene ids match scenario scene ids
   - pronunciation or timing blockers are recorded
4. Visual provenance:
   - selected clip candidates or Remotion clip packages are traceable
   - stock, AI-generated, user-supplied, and Remotion-generated routes are correctly labeled
5. Rights and approvals:
   - paid generation, licensed media, voices, music, likeness, logos, and source screenshots have approval or blocker notes

Return findings in the critique report format and mark anything unverifiable as a limitation.
