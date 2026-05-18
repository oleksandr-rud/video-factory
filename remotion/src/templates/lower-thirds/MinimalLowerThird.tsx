import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export type MinimalLowerThirdProps = {
  label?: string;
  title: string;
  detail?: string;
  align?: "left" | "right";
  accentColor?: string;
  backgroundColor?: string;
  textColor?: string;
  safeBottom?: number;
};

export const minimalLowerThirdDefaultProps: MinimalLowerThirdProps = {
  label: "Source",
  title: "Reusable lower third",
  detail: "Template-backed Remotion component",
  align: "left",
  accentColor: "#3dd6d0",
  backgroundColor: "rgba(12, 18, 24, 0.88)",
  textColor: "#f8fafc",
};

export const MinimalLowerThird: React.FC<MinimalLowerThirdProps> = ({
  label,
  title,
  detail,
  align = "left",
  accentColor = "#3dd6d0",
  backgroundColor = "rgba(12, 18, 24, 0.88)",
  textColor = "#f8fafc",
  safeBottom,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames, fps, height, width } = useVideoConfig();
  const sidePadding = Math.round(width * 0.075);
  const bottom = safeBottom ?? Math.round(height * 0.095);
  const enter = spring({
    frame,
    fps,
    config: { damping: 18, stiffness: 140, mass: 0.75 },
  });
  const exit = interpolate(
    frame,
    [durationInFrames - 18, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  const motion = enter * exit;
  const x = interpolate(motion, [0, 1], [align === "left" ? -46 : 46, 0]);

  return (
    <AbsoluteFill style={{ justifyContent: "flex-end" }}>
      <div
        style={{
          alignSelf: align === "left" ? "flex-start" : "flex-end",
          marginLeft: align === "left" ? sidePadding : 0,
          marginRight: align === "right" ? sidePadding : 0,
          marginBottom: bottom,
          opacity: motion,
          transform: `translateX(${x}px)`,
          width: Math.min(760, width - sidePadding * 2),
          borderLeft:
            align === "left" ? `8px solid ${accentColor}` : undefined,
          borderRight:
            align === "right" ? `8px solid ${accentColor}` : undefined,
          borderRadius: 8,
          background: backgroundColor,
          color: textColor,
          padding: "24px 28px",
          boxShadow: "0 20px 42px rgba(0, 0, 0, 0.24)",
        }}
      >
        {label ? (
          <div
            style={{
              color: accentColor,
              fontSize: 24,
              fontWeight: 800,
              letterSpacing: 0,
              lineHeight: 1,
              marginBottom: 12,
              textTransform: "uppercase",
            }}
          >
            {label}
          </div>
        ) : null}
        <div
          style={{
            fontSize: 46,
            fontWeight: 820,
            letterSpacing: 0,
            lineHeight: 1.02,
          }}
        >
          {title}
        </div>
        {detail ? (
          <div
            style={{
              color: "rgba(248, 250, 252, 0.76)",
              fontSize: 28,
              fontWeight: 560,
              lineHeight: 1.18,
              marginTop: 12,
            }}
          >
            {detail}
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};
