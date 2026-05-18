import {
  AbsoluteFill,
  Audio,
  Img,
  interpolate,
  OffthreadVideo,
  Sequence,
  staticFile,
  useCurrentFrame,
} from "remotion";

type SceneAsset = {
  kind: "image" | "video" | "none";
  staticFilePath?: string;
};

export type VideoFactoryScene = {
  id: string;
  title?: string;
  narration?: string;
  caption?: string;
  durationInFrames: number;
  background?: string;
  asset?: SceneAsset;
};

export type VideoFactoryProps = {
  title: string;
  fps: number;
  width: number;
  height: number;
  audioStaticFilePath?: string;
  scenes: VideoFactoryScene[];
};

export const defaultVideoFactoryProps: VideoFactoryProps = {
  title: "Video Factory",
  fps: 30,
  width: 1080,
  height: 1920,
  scenes: [
    {
      id: "setup",
      title: "Video Factory",
      caption: "Remotion project scaffold is ready.",
      durationInFrames: 150,
      background: "#101014",
    },
  ],
};

const SceneLayer: React.FC<{ scene: VideoFactoryScene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 18, scene.durationInFrames - 18, scene.durationInFrames], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const y = interpolate(frame, [0, 24], [36, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: scene.background ?? "#101014",
        justifyContent: "center",
        alignItems: "center",
        overflow: "hidden",
      }}
    >
      {scene.asset?.kind === "image" && scene.asset.staticFilePath ? (
        <Img
          src={staticFile(scene.asset.staticFilePath)}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      ) : null}
      {scene.asset?.kind === "video" && scene.asset.staticFilePath ? (
        <OffthreadVideo
          src={staticFile(scene.asset.staticFilePath)}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
          muted
        />
      ) : null}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, rgba(0, 0, 0, 0.14), rgba(0, 0, 0, 0.68))",
        }}
      />
      <div
        style={{
          opacity,
          transform: `translateY(${y}px)`,
          width: "84%",
          maxWidth: 900,
          textAlign: "center",
        }}
      >
        {scene.title ? (
          <div style={{ fontSize: 76, fontWeight: 750, lineHeight: 0.98 }}>
            {scene.title}
          </div>
        ) : null}
        {scene.caption ? (
          <div
            style={{
              marginTop: 32,
              fontSize: 38,
              fontWeight: 620,
              lineHeight: 1.14,
            }}
          >
            {scene.caption}
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};

export const VideoFactoryComposition: React.FC<VideoFactoryProps> = ({
  audioStaticFilePath,
  scenes,
}) => {
  let cursor = 0;

  return (
    <AbsoluteFill style={{ background: "#101014" }}>
      {audioStaticFilePath ? <Audio src={staticFile(audioStaticFilePath)} /> : null}
      {scenes.map((scene) => {
        const from = cursor;
        cursor += Math.max(scene.durationInFrames, 1);

        return (
          <Sequence
            key={scene.id}
            from={from}
            durationInFrames={Math.max(scene.durationInFrames, 1)}
          >
            <SceneLayer scene={scene} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
