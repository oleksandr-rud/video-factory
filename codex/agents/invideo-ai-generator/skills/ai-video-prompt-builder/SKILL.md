---
name: ai-video-prompt-builder
description: Build model-ready positive prompts and InVideo prompt guide notes for AI-generated clips. Use for scene-specific InVideo, Veo, Sora, Kling, or Agent One generation prompts that need camera, subject, action, environment, lighting, style, audio, references, and duration constraints.
---

# AI Video Prompt Builder

Read `../../references/invideo-ai-generation.md` when model-specific prompt structure matters.

Workflow:

1. Start from the visual pack scene goal and selected model route.
2. Write one concrete positive prompt using visual filmmaking language:
   - camera/lens
   - subject
   - action
   - environment
   - lighting
   - style
   - audio
   - duration/aspect/reference constraints
3. Keep the clip scoped to one primary action unless the model route explicitly supports multi-shot sequencing.
4. If the brief includes parsed web content, use claim/source/evidence refs for factual grounding but do not copy article text or page imagery into the prompt unless rights are approved.
5. For image-to-video, describe motion and temporal progression more than static image details.
6. Add Prompt Guide notes for stable brand, character, camera, lighting, or voice rules that should persist across generations.
7. Add output fields for `positive_prompt`, `prompt_guides`, `settings`, and `reference_assets` in `codex/contracts/ai-video-generation-package.schema.json`.

Return the positive prompt, prompt guide notes, settings, and assumptions. Do not generate media unless approval is already recorded.
