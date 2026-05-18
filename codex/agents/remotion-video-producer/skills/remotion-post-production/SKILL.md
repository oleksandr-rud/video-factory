---
name: remotion-post-production
description: Assemble a complete 1-10 minute Remotion video from scenario, voiceover, visual candidates, Remotion clip packages, subtitles, music, transitions, and export settings. Use for post-production editing, timeline assembly, audio mix, media normalization, render preparation, and final delivery packaging.
---

# Remotion Post Production

Load the built-in `remotion:remotion-best-practices` skill before implementation. Use its rules for sequencing, videos, audio, assets, transitions, trimming, subtitles, FFmpeg, silence detection, and render checks as needed.

Workflow:

1. Build or consume a single authoritative timeline sync plan from the scenario, voiceover package, captions, and selected visual candidates:
   - `fps`, `width`, `height`, `durationInFrames`
   - scene ids
   - frame start/end
   - selected visual candidate or Remotion clip package
   - narration/audio segment
   - captions/subtitles
   - VFX clip packages and transitions
2. Normalize media:
   - verify local paths
   - check duration, resolution, fps, and decode support
   - trim or loop clips deterministically
   - avoid live network assets during render
3. Assemble with Remotion timeline primitives:
   - use `Sequence` or `Series` for scenes
   - use `TransitionSeries` only where the transition is intentional
   - keep overlays, captions, lower thirds, and watermarks in predictable layers
4. Mix audio:
   - voiceover first
   - music ducked under voice
   - SFX only where they support motion or transitions
   - trim silence and avoid clipping
5. Add post polish:
   - captions/subtitles
   - light leaks or motion blur only where they serve the edit
   - Remotion-native component templates or packages for 3D, audiogram, TikTok captions, overlay, Skia, Code Hike, Lottie, Rive, shapes, paths, and transitions
   - safe-area CTA and platform-specific framing
   - color/contrast consistency
6. Prepare render commands for preview, release candidate, and optional transparent/VFX overlay exports.

Definition of done:

- Composition can be previewed or rendered locally.
- Timeline matches scenario duration.
- Captions, audio, visuals, source clip packages, and VFX align by scene id through `codex/contracts/timeline-sync-plan.schema.json`.
- Any template or package used is Remotion-native or explicitly approved as an exception.
- Render command and output path are written into the render package.
