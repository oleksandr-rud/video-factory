# Video Search Providers

Use this reference when Visual Producer needs provider-backed stock/video search. Provider search is candidate discovery until rights, technical fit, and usage path are validated.

## Freepik / Magnific Stock Video API

Primary use: search Freepik stock videos, inspect candidate metadata, and request approved download links for final production assets.

Current documentation note: Freepik API documentation currently redirects stock video API pages to Magnific-branded docs. Treat this as the current Freepik/Magnific stock-video API surface unless the provider changes it again.

Official docs:

- Stock content API: https://docs.freepik.com/api-reference/resources/stock-content
- Videos API overview: https://docs.freepik.com/api-reference/videos/videos-api
- Search videos: https://docs.magnific.com/api-reference/videos/get-all-videos-by-order
- Get video by ID: https://docs.magnific.com/api-reference/videos/get-one-video-by-id
- Download video by ID: https://docs.magnific.com/api-reference/videos/download-an-video
- Download video by option ID: https://docs.magnific.com/api-reference/videos/download-an-option-video
- Downloading content help: https://www.freepik.com/ai/docs/downloading-content

Capabilities verified from current docs:

- Base URL is documented as `https://api.magnific.com`.
- Authentication is documented with the `x-magnific-api-key` header.
- `GET /v1/videos` lists/searches videos with sorting and filters.
- `GET /v1/videos/{id}` retrieves a single video.
- `GET /v1/videos/{id}/download` returns a downloadable video asset link.
- `GET /v1/videos/{id}/download/{option-id}` downloads a specific video option.
- Video metadata can include `id`, `url`, `name`, `duration`, `quality`, `premium`, `fps`, `aspect-ratio` or `aspect_ratio`, `author`, `thumbnails`, `previews`, `tags`, `is_ai_generated`, and `item_subtype`.
- Download responses return a `filename` and URL-like fields such as `url` or `signed_url`.

Visual Producer policy:

- Use Freepik/Magnific for stock-video discovery and downloadable clip candidates.
- Use `FREEPIK_API_KEY` as the local env name; scripts also accept `MAGNIFIC_API_KEY` because the current API docs use Magnific branding.
- Search/listing may be performed only after Director approval for provider API use.
- Download-link requests and actual asset downloads require explicit Director approval because they may spend credits, consume download quota, or create licensing obligations.
- Preserve the Freepik page URL, video id, premium flag, author, tags, preview/thumbnail URLs, quality, duration, and download metadata.
- Mark candidates with `premium: true` or unknown license state as `needs_approval`.
- Do not rely on previews alone for final editing. Use approved download URLs/files for Remotion or other local editing.

Default normalized candidate notes:

- `route`: `stock_clip`
- `provider`: `freepik`
- `source_url`: Freepik video page URL when present
- `preview_url`: first video preview URL when present, otherwise first thumbnail URL
- `license_summary`: "Freepik/Magnific stock video candidate; final use requires Director-approved license/download path and preserved download metadata."
- `status`: `needs_approval` unless the Director has approved the provider, license path, and download/use route

## Pexels Video API

Secondary use: search free stock videos when Freepik/Magnific is unavailable, returns weak matches, or needs fallback coverage. Pexels is useful for broad B-roll, but the API terms and final-use restrictions still need explicit evidence.

Official docs:

- API documentation: https://www.pexels.com/api/documentation/
- Pexels license: https://www.pexels.com/license/
- License help article: https://help.pexels.com/hc/en-us/articles/360042295174-What-is-the-license-of-the-photos-and-videos-on-Pexels
- Rate-limit help article: https://help.pexels.com/hc/en-us/articles/900006470063-What-steps-can-I-take-to-avoid-hitting-the-rate-limit
- Unlimited requests help article: https://help.pexels.com/hc/en-us/articles/900005852323-How-do-I-get-unlimited-requests

Capabilities verified from current docs:

- Base URL is documented as `https://api.pexels.com`.
- Video search is `GET /v1/videos/search`.
- Authentication uses the `Authorization` header with a Pexels API key.
- Search supports `query`, `orientation`, `size`, `locale`, `page`, and `per_page`; `per_page` is capped at 80.
- Video responses include `id`, `width`, `height`, `url`, `image`, `duration`, `user`, `video_files[]`, and `video_pictures[]`.
- `video_files[]` includes direct file links, so there is no separate download-link endpoint in the normal search workflow.
- Successful API responses include rate-limit headers such as `X-Ratelimit-Limit`, `X-Ratelimit-Remaining`, and `X-Ratelimit-Reset`.

Visual Producer policy:

- Use Freepik/Magnific before Pexels when a primary provider route is approved and suitable.
- Use Pexels as a secondary/free fallback for broad stock B-roll or when Freepik results are weak.
- Use `PEXELS_API_KEY` as the local env name.
- Search/listing may be performed only after Director approval for provider API use.
- File downloads require explicit Director approval even though direct file links are present in search responses.
- Preserve Pexels page URL, video id, creator name, creator URL, image/preview URL, video file metadata, request URL, and rate-limit headers.
- Preserve attribution/link-back notes because Pexels API guidelines require a prominent Pexels link and ask for photographer/creator credit when possible.
- Do not use Pexels clips in contexts that imply endorsement, put identifiable people in an offensive or bad-light context, redistribute stock/wallpaper libraries, sell unmodified copies, or create trademark/service-mark assets.

Default normalized candidate notes:

- `route`: `stock_clip`
- `provider`: `pexels`
- `source_url`: Pexels video page URL
- `preview_url`: `image` URL when present, otherwise first `video_pictures[].picture`
- `license_summary`: "Pexels License stock video candidate; free personal/commercial use is generally allowed, API attribution/link-back is required by Pexels guidelines, and final use must avoid restricted likeness, endorsement, trademark, or unmodified resale contexts."
- `status`: `proposed` after search unless final-use rights, attribution, or context checks require approval
