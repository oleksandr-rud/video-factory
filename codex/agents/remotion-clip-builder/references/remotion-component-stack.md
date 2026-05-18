# Remotion Component Stack Reference

Use this when choosing templates, packages, and component primitives for Remotion VFX, subtitles, or post-production.

Reusable local templates are tracked with `codex/contracts/remotion-template.schema.json` and registered in the Remotion app, usually `remotion/src/templateRegistry.tsx`. Check those local templates before importing external examples or adding new dependencies.

## Boundary

Use Remotion-native packages and official Remotion templates. Do not use generic web UI/component libraries as the production source for video components unless the Director explicitly approves an exception.

Avoid generic HTML, dashboard, icon-pack, chart, or website template libraries as the production component source.

Core CSS/SVG/Canvas inside Remotion is fine. The concern is importing web app component ecosystems as if they were motion-design templates.

## Built-In Remotion Skill Map

The installed `remotion:remotion-best-practices` skill includes local rule files for:

- `3d`: Three.js and React Three Fiber integration through Remotion.
- `animations`, `timing`, `text-animations`, `transitions`: frame-driven animation and scene cuts.
- `assets`, `images`, `videos`, `audio`, `fonts`: deterministic local media usage.
- `subtitles`, `import-srt-captions`, `transcribe-captions`, `display-captions`: caption pipeline.
- `audio-visualization`, `sfx`, `silence-detection`, `ffmpeg`: audio polish and diagnostics.
- `light-leaks`, `lottie`, `transparent-videos`, `gifs`, `charts`, `maps`: common VFX and specialty scene routes.

## Official Free Templates

Prefer official Remotion templates when starting a new project or a scene pattern matches directly:

- Blank: empty canvas.
- Hello World: simple animation playground.
- Prompt to Motion Graphics SaaS: app starter for AI-generated motion graphics, live preview, input validation, output sanitation, and compile-error self-correction. Use as a workflow reference for generated component prompts; do not treat it as the default Codex video-production path.
- JavaScript: plain JS starter.
- Next.js variants: video generation app shells; use only when building a render app, not a clip.
- React Router: video generation app shell.
- Render Server: Express render backend.
- Electron: desktop render app.
- 3D: Remotion + React Three Fiber starter.
- Stills: dynamic PNG/JPEG template.
- Audiogram: text and waveform visualization.
- Music Visualization: waveform/music visualizer.
- Prompt to Video: story with images and voiceover from a prompt.
- Skia: React Native Skia starter.
- Overlay: overlays for video editing software.
- Code Hike: code animation template.
- Stargazer: GitHub stars celebration video.
- TikTok: animated word-by-word captions.

Paid Remotion Pro templates such as Editor Starter, Watercolor Map, and Timeline require explicit Director approval.

## Remotion Packages

Caption and text:

- `@remotion/captions`: Parse SRT, manipulate captions, create TikTok-style caption pages, serialize SRT.
- `@remotion/rounded-text-box`: TikTok-like multiline rounded text-box SVG paths. MIT.
- `@remotion/animated-emoji`: Animated emoji components; emoji assets require CC BY 4.0 attribution.

Motion graphics and VFX:

- `@remotion/transitions`: `TransitionSeries`, transition timings, presentations.
- `@remotion/light-leaks`: WebGL light leak effects and transition overlays.
- `@remotion/motion-blur`: Motion blur and trail effects. MIT.
- `@remotion/noise`: Procedural 2D/3D/4D noise utilities. MIT.
- `@remotion/starburst`: WebGL retro starburst ray component.
- `@remotion/shapes`: SVG shape components and path generators. MIT.
- `@remotion/paths`: Dependency-free SVG path utilities and path interpolation. MIT.

Animation asset formats:

- `@remotion/lottie`: Local Lottie JSON playback in Remotion.
- `@remotion/rive`: Local Rive animation playback in Remotion.

3D, canvas, and rendering:

- `@remotion/three`: React Three Fiber integration through `ThreeCanvas` and video textures.
- `@remotion/skia`: React Native Skia integration through `SkiaCanvas`; use the Skia template for complex Skia scenes.
- `@remotion/media-utils`: Audio duration, audio data, waveform, spectrum, image/video metadata helpers.
- `@remotion/media`: New media primitives backed by WebCodecs/Mediabunny where suitable.
- `@remotion/renderer`: Node rendering APIs such as `renderMedia()`, metadata helpers, FFmpeg/FFprobe helpers, and silence detection.
- Mediabunny: preferred multimedia helper direction for media parsing, metadata, frame extraction, and decode checks.

Keep `remotion` and all `@remotion/*` packages on the same exact version.

## Selection Heuristics

- Existing local reusable template: use first when the scene needs a lower third, source card, caption block, transition, overlay, opener, callout, mockup, or visual shell already represented in the template registry.
- Fast short from scratch: Blank or Hello World template.
- Text-to-motion component generation: Prompt to Motion Graphics SaaS workflow ideas plus `../skills/remotion-ai-component-prompt/SKILL.md`.
- Word-by-word short captions: TikTok template plus `@remotion/captions` and `@remotion/rounded-text-box`.
- Music or podcast visual: Audiogram or Music Visualization template plus `@remotion/media-utils`.
- 3D product/mockup scene: 3D template or `@remotion/three`.
- Skia-heavy abstract VFX: Skia template or `@remotion/skia`.
- Transparent overlay pack: Overlay template plus transparent-video render settings.
- Code/demo animation: Code Hike template when code is the subject.
- Animated illustration asset: `@remotion/lottie` or `@remotion/rive` with local files.
- Procedural VFX: light leaks, starburst, noise, shapes, paths, motion blur.
- Media QA and metadata: Remotion renderer helpers or Mediabunny direction.

## Guardrails

- Avoid paid Remotion Pro packages unless the Director explicitly approves purchase.
- Avoid remote assets during render.
- Check licenses for third-party media assets separately from Remotion package licenses.
- Do not add libraries for effects that can be done cleanly with CSS, SVG, Canvas, and core Remotion.
- Do not change a reusable template's public props or visual contract in a breaking way; create a new template version or a scene-specific clip package instead.
