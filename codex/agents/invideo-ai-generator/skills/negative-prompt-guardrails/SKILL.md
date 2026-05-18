---
name: negative-prompt-guardrails
description: Build negative constraints for AI video generation and convert them into model-safe positive phrasing when needed. Use when prompts must prevent artifacts, unwanted style, identity drift, random logos, unreadable text, camera shake, or other generation failures.
---

# Negative Prompt Guardrails

Read `../../references/invideo-ai-generation.md` before deciding whether to use a separate negative prompt or a positive rewrite.

Workflow:

1. List risks from the scene: artifacts, identity drift, wrong brand, wrong setting, unwanted camera motion, unreadable text, unsafe imagery, bad hands/faces, flicker, or style mismatch.
2. Decide negative mode:
   - `separate_field` when the model supports negative prompts.
   - `converted_to_positive_constraints` when the model prefers positive phrasing.
   - `prompt_guide` when the constraint should persist across multiple generations.
   - `unsupported` when the provider cannot apply it reliably.
3. For separate negative prompts, write visible unwanted elements as a compact comma-separated list. Avoid command language such as "no" and "do not".
4. For positive rewrites, describe the desired state. Example: "locked camera, steady tripod shot" instead of "no camera shake".
5. Check that negative constraints do not contradict the positive prompt.

Return `negative_prompt`, `negative_prompt_mode`, positive rewrite notes, and residual risks.
