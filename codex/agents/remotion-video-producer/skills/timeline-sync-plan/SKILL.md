---
name: timeline-sync-plan
description: Build a frame-accurate timeline sync plan that aligns scenario text, voiceover audio, subtitles, selected visual candidates, Remotion clips, transitions, and safe-area overlays. Use before Remotion full-video assembly when narration, captions, and visuals must stay synchronized by scene id.
---

# Timeline Sync Plan

Load `subtitle-caption-pipeline` and the built-in `remotion:remotion-best-practices` skill when implementing or validating Remotion code. The output is a plan matching `codex/contracts/timeline-sync-plan.schema.json`.

## Workflow

1. Read the scenario, voiceover package, caption artifacts, visual pack, approved clip candidates, Remotion clip packages, channel format, and export settings.
2. Build one authoritative scene timeline:
   - scene id
   - narration text
   - audio path and duration
   - caption JSON/SRT path and caption time range
   - selected visual candidate or Remotion clip package
   - frame start/end at the target fps
   - overlay, lower-third, CTA, and transition notes
3. Use `../../scripts/build_timeline_sync_plan.py` to create the first JSON plan when the inputs are already structured.
4. Adjust scene timing only when audio duration, captions, or selected clip lengths require it. Preserve scene ids and record any drift from the original scenario timing.
5. Hand the plan to `remotion-post-production` as the source of truth for `<Sequence>`, `<Series>`, audio placement, captions, and visual layers.
6. QA the plan for missing assets, scene order, timing drift, caption coverage, visual coverage, safe-area conflicts, and duration mismatch.

## Rules

- Use voiceover duration and caption timestamps as stronger timing evidence than estimated script duration.
- Keep captions, lower thirds, product/UI details, logos, and CTA text from occupying the same safe area.
- Mark a plan partial if any scene has no approved visual candidate, no audio path after approved TTS generation, or no caption timing source.
- Do not use remote media paths for final render unless the Director explicitly accepts that risk.
