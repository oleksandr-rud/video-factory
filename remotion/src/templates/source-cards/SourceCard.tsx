import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export type SourceCardProps = {
  eyebrow?: string;
  sourceName: string;
  sourceDetail?: string;
  claim?: string;
  accentColor?: string;
  backgroundColor?: string;
  textColor?: string;
};

export const sourceCardDefaultProps: SourceCardProps = {
  eyebrow: "Evidence",
  sourceName: "Reusable source card",
  sourceDetail: "Designed for citations, references, and claim receipts",
  claim: "Source-backed visuals stay traceable through the media manifest.",
  accentColor: "#f6c34a",
  backgroundColor: "#111827",
  textColor: "#f9fafb",
};

export const SourceCard: React.FC<SourceCardProps> = ({
  eyebrow,
  sourceName,
  sourceDetail,
  claim,
  accentColor = "#f6c34a",
  backgroundColor = "#111827",
  textColor = "#f9fafb",
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames, fps, height, width } = useVideoConfig();
  const entrance = spring({
    frame,
    fps,
    config: { damping: 20, stiffness: 120, mass: 0.9 },
  });
  const fadeOut = interpolate(
    frame,
    [durationInFrames - 18, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  const opacity = entrance * fadeOut;
  const scale = interpolate(entrance, [0, 1], [0.965, 1]);
  const cardWidth = Math.min(width * 0.82, 860);

  return (
    <AbsoluteFill
      style={{
        alignItems: "center",
        background:
          "linear-gradient(135deg, rgba(18, 24, 38, 1), rgba(34, 44, 56, 1))",
        justifyContent: "center",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          position: "absolute",
          height: height * 0.62,
          width: width * 0.62,
          borderRadius: "50%",
          background: accentColor,
          filter: "blur(120px)",
          opacity: 0.18,
          right: -width * 0.25,
          top: height * 0.12,
        }}
      />
      <div
        style={{
          opacity,
          transform: `scale(${scale})`,
          width: cardWidth,
          border: "1px solid rgba(255, 255, 255, 0.12)",
          borderRadius: 8,
          background: backgroundColor,
          boxShadow: "0 28px 72px rgba(0, 0, 0, 0.34)",
          color: textColor,
          padding: "42px 46px",
        }}
      >
        {eyebrow ? (
          <div
            style={{
              color: accentColor,
              fontSize: 26,
              fontWeight: 820,
              letterSpacing: 0,
              lineHeight: 1,
              marginBottom: 22,
              textTransform: "uppercase",
            }}
          >
            {eyebrow}
          </div>
        ) : null}
        <div
          style={{
            fontSize: 58,
            fontWeight: 840,
            letterSpacing: 0,
            lineHeight: 0.98,
          }}
        >
          {sourceName}
        </div>
        {sourceDetail ? (
          <div
            style={{
              color: "rgba(249, 250, 251, 0.72)",
              fontSize: 30,
              fontWeight: 560,
              lineHeight: 1.16,
              marginTop: 18,
            }}
          >
            {sourceDetail}
          </div>
        ) : null}
        {claim ? (
          <div
            style={{
              borderTop: "1px solid rgba(255, 255, 255, 0.14)",
              color: "rgba(249, 250, 251, 0.88)",
              fontSize: 34,
              fontWeight: 660,
              lineHeight: 1.18,
              marginTop: 34,
              paddingTop: 26,
            }}
          >
            {claim}
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};
