---
name: revision-prioritization
description: Convert critique findings into a prioritized revision plan mapped to the responsible Video Factory agents, affected artifacts, approval needs, and expected viewer impact. Use after artifact audit or multimodal video critique.
---

# Revision Prioritization

Use this after findings exist.

## Workflow

1. Sort by severity, viewer impact, and dependency order.
2. Map each fix to an owner:
   - `channel-intelligence` for reference/channel/source/redundancy problems
   - `creative-producer` for scenario, narration, voice direction, or claims
   - `visual-producer` for visual route, candidate, or research problems
   - `invideo-ai-generator` for AI generation prompt/output problems
   - `remotion-clip-builder` for component, VFX, overlay, or short clip problems
   - `remotion-video-producer` for timeline, captions, audio mix, transitions, export, or render problems
   - `director` for budget, rights, scope, or user decision problems
3. Preserve stable ids. Recommend scene id changes only when scene boundaries or order must change.
4. Mark fixes requiring user approval, paid generation, licensed media, or rights decisions.
5. Group small polish issues so the Director can decide whether to spend another revision loop.
6. Set the next loop action:
   - `approve_rc` when every hard gate passes or is waived
   - `revise_and_rerender` when production agents can fix the issues
   - `ask_user` when approval, rights, spend, missing source, or waiver is needed
   - `stop_blocked` when max iterations or repeated blockers prevent progress

Return a concise revision plan inside the critique report.
