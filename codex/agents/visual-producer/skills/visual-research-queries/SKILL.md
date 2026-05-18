---
name: visual-research-queries
description: Generate and refine search queries for scene-level visual research across stock providers, internal footage, web references, and AI generation prompts. Use when a scene needs visual candidates.
---

# Visual Research Queries

For each scene:

1. Extract concrete nouns, actions, location, mood, camera angle, and motion.
2. Create broad, narrow, and fallback search queries.
3. Avoid copyrighted character, brand, or celebrity terms unless explicitly supplied and authorized.
4. Include negative criteria for unsuitable clips.
5. Map each query to a route: stock, generated video, Remotion, or user media.

Return queries grouped by scene id and route.
