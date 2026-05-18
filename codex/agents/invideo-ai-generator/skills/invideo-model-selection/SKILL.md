---
name: invideo-model-selection
description: Choose the correct InVideo AI route, quality mode, and model for AI-generated video clips or full InVideo-managed scenes. Use when a scene is marked for ai_video_generation and needs Agent One, Basic, Pro, Ultra, Sora 2, Veo 3.1, Kling 3.0, or a fallback model decision.
---

# InVideo Model Selection

Read `../../references/invideo-ai-generation.md` before selecting a model.

Workflow:

1. Classify the scene: background visual, product/brand shot, human performance, dialogue/lipsync, multi-character scene, transition insert, full story segment, or short clip.
2. Choose the lowest adequate quality mode:
   - Basic: stock-backed background or straightforward clip.
   - Pro: important generated clip with realistic motion or acting.
   - Ultra: high-stakes realism, brand/product integration, or full story generation.
3. Choose model route:
   - Sora 2 Pro for 4-12 second clips when Sora is explicitly desired.
   - Veo 3.1 for high-fidelity cinematic 4-8 second shots, camera/lens control, first/last frame continuity, or product demo shots.
   - Kling 3.0 for 3-15 second clips with native audio, multi-shot sequencing, multi-character continuity, or lip sync.
   - Agent One for full InVideo-managed videos or conversational iterative editing.
4. Record duration, aspect ratio, resolution, input types, reference assets, and credit/cost risk.
5. Provide one cheaper fallback and one non-AI fallback when possible.

Return the selected route, model/settings, rationale, risks, and approval requirement.
