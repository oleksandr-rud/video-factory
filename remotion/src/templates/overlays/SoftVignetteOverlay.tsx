import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

export type SoftVignetteOverlayProps = {
  color?: string;
  opacity?: number;
  edgeStrength?: number;
  animated?: boolean;
};

export const softVignetteOverlayDefaultProps: SoftVignetteOverlayProps = {
  color: "rgba(0, 0, 0, 1)",
  opacity: 0.42,
  edgeStrength: 68,
  animated: true,
};

export const SoftVignetteOverlay: React.FC<SoftVignetteOverlayProps> = ({
  color = "rgba(0, 0, 0, 1)",
  opacity = 0.42,
  edgeStrength = 68,
  animated = true,
}) => {
  const frame = useCurrentFrame();
  const pulse = animated
    ? interpolate(frame % 90, [0, 45, 90], [0.92, 1, 0.92])
    : 1;
  const resolvedOpacity = opacity * pulse;

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(circle at center, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 0) ${edgeStrength}%, ${color} 100%)`,
        opacity: resolvedOpacity,
        pointerEvents: "none",
      }}
    />
  );
};
