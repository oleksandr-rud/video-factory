import "./index.css";
import { Composition } from "remotion";
import {
  VideoFactoryComposition,
  defaultVideoFactoryProps,
  type VideoFactoryProps,
} from "./Composition";

const getDuration = (props: VideoFactoryProps): number => {
  const sceneDuration = props.scenes.reduce(
    (total, scene) => total + Math.max(scene.durationInFrames, 1),
    0,
  );

  return Math.max(sceneDuration, props.fps * 5);
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="VideoFactoryMain"
        component={VideoFactoryComposition}
        durationInFrames={getDuration(defaultVideoFactoryProps)}
        fps={defaultVideoFactoryProps.fps}
        width={defaultVideoFactoryProps.width}
        height={defaultVideoFactoryProps.height}
        defaultProps={defaultVideoFactoryProps}
        calculateMetadata={({ props }) => ({
          durationInFrames: getDuration(props),
          fps: props.fps,
          width: props.width,
          height: props.height,
        })}
      />
    </>
  );
};
