import { Composition } from "remotion";
import {
  MinimalLowerThird,
  minimalLowerThirdDefaultProps,
} from "./templates/lower-thirds/MinimalLowerThird";
import {
  SourceCard,
  sourceCardDefaultProps,
} from "./templates/source-cards/SourceCard";
import {
  SafeCaption,
  safeCaptionDefaultProps,
} from "./templates/captions/SafeCaption";
import {
  SoftVignetteOverlay,
  softVignetteOverlayDefaultProps,
} from "./templates/overlays/SoftVignetteOverlay";

export type ReusableTemplateCategory =
  | "lower_third"
  | "source_card"
  | "caption"
  | "overlay";

export type ReusableTemplateRegistryEntry = {
  templateId: string;
  compositionId: string;
  category: ReusableTemplateCategory;
  componentPath: string;
  contractPathHint: string;
  defaultDurationInFrames: number;
  fps: number;
  width: number;
  height: number;
  notes: string;
};

export const reusableTemplateRegistry: ReusableTemplateRegistryEntry[] = [
  {
    templateId: "vf.lower-third.minimal.v1",
    compositionId: "TemplateLowerThirdMinimal",
    category: "lower_third",
    componentPath: "remotion/src/templates/lower-thirds/MinimalLowerThird.tsx",
    contractPathHint: "remotion/templates/vf.lower-third.minimal.v1.json",
    defaultDurationInFrames: 150,
    fps: 30,
    width: 1080,
    height: 1920,
    notes: "Reusable lower third for source labels, speaker IDs, and chapter labels.",
  },
  {
    templateId: "vf.source-card.standard.v1",
    compositionId: "TemplateSourceCardStandard",
    category: "source_card",
    componentPath: "remotion/src/templates/source-cards/SourceCard.tsx",
    contractPathHint: "remotion/templates/vf.source-card.standard.v1.json",
    defaultDurationInFrames: 180,
    fps: 30,
    width: 1080,
    height: 1920,
    notes: "Reusable evidence card for references, citations, and claim receipts.",
  },
  {
    templateId: "vf.caption.safe.v1",
    compositionId: "TemplateSafeCaption",
    category: "caption",
    componentPath: "remotion/src/templates/captions/SafeCaption.tsx",
    contractPathHint: "remotion/templates/vf.caption.safe.v1.json",
    defaultDurationInFrames: 120,
    fps: 30,
    width: 1080,
    height: 1920,
    notes: "Reusable high-contrast caption block with one-word emphasis.",
  },
  {
    templateId: "vf.overlay.soft-vignette.v1",
    compositionId: "TemplateSoftVignetteOverlay",
    category: "overlay",
    componentPath: "remotion/src/templates/overlays/SoftVignetteOverlay.tsx",
    contractPathHint: "remotion/templates/vf.overlay.soft-vignette.v1.json",
    defaultDurationInFrames: 150,
    fps: 30,
    width: 1080,
    height: 1920,
    notes: "Reusable transparent-safe edge focus overlay for timeline polish.",
  },
];

export const TemplateCompositions: React.FC = () => {
  return (
    <>
      <Composition
        id="TemplateLowerThirdMinimal"
        component={MinimalLowerThird}
        durationInFrames={150}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={minimalLowerThirdDefaultProps}
      />
      <Composition
        id="TemplateSourceCardStandard"
        component={SourceCard}
        durationInFrames={180}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={sourceCardDefaultProps}
      />
      <Composition
        id="TemplateSafeCaption"
        component={SafeCaption}
        durationInFrames={120}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={safeCaptionDefaultProps}
      />
      <Composition
        id="TemplateSoftVignetteOverlay"
        component={SoftVignetteOverlay}
        durationInFrames={150}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={softVignetteOverlayDefaultProps}
      />
    </>
  );
};
