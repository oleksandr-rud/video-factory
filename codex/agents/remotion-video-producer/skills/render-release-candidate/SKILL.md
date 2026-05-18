---
name: render-release-candidate
description: Produce a render release candidate package for a Remotion video. Use when an assembled composition needs render commands, output paths, subtitles, metadata, QA status, rights notes, known blockers, or fallback exports.
---

# Render Release Candidate

Use this after the Remotion composition is assembled and before final delivery.

Workflow:

1. Confirm composition id, Remotion app contract, media asset manifest, timeline path, source clip packages, fps, dimensions, duration, and target platform.
2. Run the lightest meaningful validation first:
   - still frame checks at representative scene frames
   - preview in Studio or browser when available
   - full render when dependencies and time allow
3. Render the release candidate with an explicit output path.
4. Emit subtitle artifacts when required:
   - burned-in captions inside the video
   - separate `.srt` file for platforms that support upload
5. Verify output metadata with Remotion, FFprobe, Mediabunny, or available repo tooling.
6. Run `../render-qa/SKILL.md` and attach results.
7. Write or update a render package matching `codex/contracts/render-package.schema.json`.
8. Add or update media asset manifest entries for the rendered video, subtitle sidecars, thumbnails, metadata, QA reports, and review-prep outputs.

Rules:

- Treat the RC as a package, not only a video file.
- Keep render commands reproducible.
- Mark the RC as blocked if full render, captions, audio, or license approval is missing.
- Include fallback export commands for transparent overlays, square/vertical crops, or no-caption versions when requested.
- The render package must carry project/channel fields, media asset manifest path, Remotion project contract path, source asset ids, and output media asset ids when available.
