---
name: visual-research-queries
description: Generate and refine search queries for scene-level visual research across stock providers, internal footage, web references, and AI generation prompts. Use when a scene needs visual candidates.
---

# Visual Research Queries

For each scene:

1. Extract concrete nouns, actions, location, mood, camera angle, and motion.
2. Check `reference-analysis.web_pages[].visual_evidence_candidates`, `claim_ledger[]`, and media manifest assets before inventing new search terms.
3. Create broad, narrow, and fallback search queries.
4. Avoid copyrighted character, brand, or celebrity terms unless explicitly supplied and authorized.
5. Include negative criteria for unsuitable clips.
6. Map each query to a route: stock, generated video, Remotion, user media, approved web image, or source-card/motion-graphic recreation.
7. When Freepik/Magnific or Pexels is a likely stock route, include a concise keyword/search term, optional provider filters, locale/language, and provider priority. Prefer simple searchable subjects/actions over full sentence prompts.
8. Mark Freepik/Magnific as primary by default when account/licensing is available; mark Pexels as secondary/free fallback unless the Director explicitly chooses it first.
9. Treat page images and screenshots as evidence candidates until the media asset manifest marks them approved for use; otherwise suggest redrawn diagrams, source cards, or abstracted Remotion graphics.

Return queries grouped by scene id and route.
