---
name: render-qa
description: Inspect a video preview, VFX clip, subtitle track, render release candidate, or final render against the scenario, voiceover, selected visual candidates, rights notes, and export requirements. Use for technical render QA, Remotion preview checks, timing validation, export validation, and delivery-readiness evidence before independent Video Critic release review.
---

# Render QA

Check:

- Duration and scene timing
- Script, captions, and on-screen text
- Voiceover sync, clipping, silence, and pronunciation
- Visual continuity and candidate usage
- VFX timing, alpha/export behavior, and transition continuity
- Template provenance, template contract availability, and whether template-backed instances respect their props/safe-area contracts
- Missing assets or broken media paths
- Media asset manifest coverage for source clips, Remotion public projection paths, outputs, subtitles, and review-prep artifacts
- Aspect ratio, resolution, FPS, and export format
- Subtitle artifact presence when separate `.srt` export is required
- Rights, attribution, and approval notes

This skill does not approve release-candidate gates. It produces technical QA evidence for the Video Critic and Director.

Return pass/fail, findings by scene or timestamp, fixes made, and residual risk.
