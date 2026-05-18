---
name: generated-clip-qa
description: QA AI-generated video clips from InVideo or related models and convert acceptable outputs into clip candidates. Use after generation to inspect prompt adherence, visual artifacts, continuity, audio, rights, technical metadata, and editability.
---

# Generated Clip QA

Check:

- Prompt adherence and scene semantic fit
- Subject identity, product/brand accuracy, and reference asset use
- Motion plausibility, camera movement, physics, hands/faces, flicker, and temporal consistency
- Audio, dialogue, ambience, music, and lip sync when generated
- Aspect ratio, duration, resolution, fps, looping, and local file availability
- Media asset manifest entry, source/output asset ids, and Remotion `staticFile()` path when the generated clip is downloaded for editing
- Text, logos, watermarks, and unwanted subtitles
- Rights, approval state, provider terms, and credit/cost record
- Editability for Remotion Video Producer: clean start/end frames, safe crop, no baked-in issues that block captions or transitions

Return QA findings and update:

- `codex/contracts/ai-video-generation-package.schema.json`
- `codex/contracts/clip-candidate.schema.json`
- `codex/contracts/media-asset-manifest.schema.json` when local generated files, thumbnails, metadata, or QA reports exist

Reject or mark `needs_approval` for clips with unresolved rights, brand, or technical blockers.
