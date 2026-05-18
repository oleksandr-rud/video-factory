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
