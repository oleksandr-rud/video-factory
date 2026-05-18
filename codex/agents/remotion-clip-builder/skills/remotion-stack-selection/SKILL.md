---
name: remotion-stack-selection
description: Choose Remotion-native templates, packages, component primitives, and VFX helpers for a video scene or render pipeline. Use before adding Remotion dependencies for subtitles, 3D, Lottie, Rive, Skia, transitions, motion blur, audio visualization, transparent overlays, captions, or render tooling.
---

# Remotion Stack Selection

Read `../../references/remotion-component-stack.md` before adding a dependency, template, or component primitive.

Default choices:

1. Use core Remotion first: `AbsoluteFill`, `Sequence`, `Series`, `interpolate`, `spring`, `Audio`, `OffthreadVideo`, `Img`, `staticFile`, and typed props.
2. Choose an official Remotion template when a project shape already matches the job: Blank, Hello World, Prompt to Motion Graphics SaaS, 3D, Audiogram, Music Visualization, Prompt to Video, Skia, Overlay, Code Hike, Stargazer, TikTok, or render server templates.
3. Use `@remotion/captions` for caption parsing, TikTok-style pages, word highlighting, and `.srt` export.
4. Use `@remotion/transitions` for scene transitions and overlay transitions.
5. Use `@remotion/light-leaks`, `@remotion/motion-blur`, `@remotion/noise`, `@remotion/starburst`, `@remotion/shapes`, `@remotion/paths`, and `@remotion/rounded-text-box` for code-native VFX and motion graphics.
6. Use `@remotion/lottie` or `@remotion/rive` only for approved local animation assets.
7. Use `@remotion/three` for 3D scenes and `@remotion/skia` for Skia-heavy vector/canvas effects.
8. Use `@remotion/media-utils`, `@remotion/media`, Mediabunny, and `@remotion/renderer` for media metadata, audio visualization, decode checks, and render tooling.

Rules:

- Stay inside Remotion-native packages and official Remotion templates unless the Director explicitly approves an exception.
- Do not use generic HTML, dashboard, icon-pack, or website component libraries as the production component source.
- Do not add a dependency if CSS, SVG, Canvas, or core Remotion can do it clearly.
- Keep all Remotion packages on the same exact version as the project's `remotion` dependency.
- Avoid runtime network dependencies; place assets in `public/` or import them locally.
- Record each selected package, reason, license note, and fallback in the scene plan.
