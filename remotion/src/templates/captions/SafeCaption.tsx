import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export type SafeCaptionProps = {
  text: string;
  highlight?: string;
  accentColor?: string;
  backgroundColor?: string;
  textColor?: string;
  bottom?: number;
};

export const safeCaptionDefaultProps: SafeCaptionProps = {
  text: "Reusable caption block",
  highlight: "Reusable",
  accentColor: "#ff6b4a",
  backgroundColor: "rgba(8, 12, 18, 0.82)",
  textColor: "#ffffff",
};

export const SafeCaption: React.FC<SafeCaptionProps> = ({
  text,
  highlight,
  accentColor = "#ff6b4a",
  backgroundColor = "rgba(8, 12, 18, 0.82)",
  textColor = "#ffffff",
  bottom,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames, fps, height, width } = useVideoConfig();
  const entrance = spring({
    frame,
    fps,
    config: { damping: 16, stiffness: 150, mass: 0.8 },
  });
  const fadeOut = interpolate(
    frame,
    [durationInFrames - 14, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  const opacity = entrance * fadeOut;
  const y = interpolate(entrance, [0, 1], [24, 0]);
  const captionBottom = bottom ?? Math.round(height * 0.12);
  const words = text.split(" ");

  return (
    <AbsoluteFill
      style={{
        alignItems: "center",
        justifyContent: "flex-end",
        paddingBottom: captionBottom,
      }}
    >
      <div
        style={{
          opacity,
          transform: `translateY(${y}px)`,
          maxWidth: Math.min(width * 0.86, 920),
          borderRadius: 8,
          background: backgroundColor,
          color: textColor,
          fontSize: 46,
          fontWeight: 820,
          letterSpacing: 0,
          lineHeight: 1.08,
          padding: "22px 28px",
          textAlign: "center",
        }}
      >
        {words.map((word, index) => {
          const normalizedWord = word.toLowerCase().replace(/[^a-z0-9]/g, "");
          const normalizedHighlight = highlight
            ?.toLowerCase()
            .replace(/[^a-z0-9]/g, "");
          const isHighlighted =
            normalizedHighlight !== undefined &&
            normalizedHighlight.length > 0 &&
            normalizedWord === normalizedHighlight;

          return (
            <span
              key={`${word}-${index}`}
              style={{ color: isHighlighted ? accentColor : textColor }}
            >
              {word}
              {index < words.length - 1 ? " " : ""}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
