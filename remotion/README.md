# Video Factory Remotion App

Shared Remotion workspace for deterministic clips, full-video timeline assembly, preview stills, and render release candidates.

## Commands

```console
npm install
npm run studio
npm run lint
npm run still:main
npm run render:main
```

## Asset Policy

Canonical source media belongs in `channels/<channel-slug>/projects/<project-slug>/source-media/`.

Render-needed media is copied or mirrored into `remotion/public/channels/<channel-slug>/projects/<project-slug>/...` and referenced from Remotion with `staticFile()`.

Every media file used or emitted by a render should be recorded in the project `media-asset-manifest.json`.

## Reusable Templates

Reusable Remotion bits are registered in `src/templateRegistry.tsx`, implemented under `src/templates/`, and described by shared contracts under `templates/`.

Current starter templates:

- `vf.lower-third.minimal.v1` / `TemplateLowerThirdMinimal`
- `vf.source-card.standard.v1` / `TemplateSourceCardStandard`
- `vf.caption.safe.v1` / `TemplateSafeCaption`
- `vf.overlay.soft-vignette.v1` / `TemplateSoftVignetteOverlay`

Project-specific template contracts should be written under `channels/<channel-slug>/projects/<project-slug>/remotion/templates/` using `codex/contracts/remotion-template.schema.json` when a shared template is customized or promoted from a project clip. Scene-specific uses still need a `remotion-clip-package` that points back to the template id and contract path.
