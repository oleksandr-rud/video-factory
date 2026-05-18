---
name: provider-clip-search
description: Search and normalize stock/provider video clips for scene-level candidates. Use with Pexels, Pixabay, Shutterstock, internal libraries, or another approved content provider.
---

# Provider Clip Search

1. Read scene visual requirements and query list.
2. Select providers based on availability, license policy, and budget.
3. Search for multiple candidates per scene when credentials and approval allow it; otherwise prepare exact manual queries.
4. Normalize candidate metadata: provider, source URL, preview URL, duration, resolution, FPS if available, license summary, attribution, cost, and media asset manifest entry when the clip is downloaded or otherwise loaded locally.
5. Mark paid or uncertain candidates as `needs_approval`.

Do not download or license paid assets without Director approval.
