#!/usr/bin/env python3
"""Snapshot ElevenLabs voices for offline voice ranking.

Requires ELEVENLABS_API_KEY. This lists voices only; it does not generate audio.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request


API_URL = "https://api.elevenlabs.io/v2/voices"


def request_json(url: str, api_key: str) -> dict:
    request = urllib.request.Request(url, headers={"xi-api-key": api_key})
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))


def build_url(args: argparse.Namespace, page_token: str | None) -> str:
    query: dict[str, str] = {
        "page_size": str(args.page_size),
        "include_total_count": "true" if args.include_total_count else "false",
    }
    for key in ("search", "voice_type", "category", "sort", "sort_direction"):
        value = getattr(args, key)
        if value:
            query[key] = value
    if page_token:
        query["next_page_token"] = page_token
    return f"{API_URL}?{urllib.parse.urlencode(query)}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--search")
    parser.add_argument("--voice-type")
    parser.add_argument("--category")
    parser.add_argument("--sort", default="name")
    parser.add_argument("--sort-direction", default="asc")
    parser.add_argument("--page-size", type=int, default=100)
    parser.add_argument("--include-total-count", action="store_true")
    parser.add_argument("--max-pages", type=int, default=20)
    args = parser.parse_args()

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        print("ELEVENLABS_API_KEY is required", file=sys.stderr)
        return 2

    voices: list[dict] = []
    page_token: str | None = None
    total_count = None

    for _ in range(args.max_pages):
        payload = request_json(build_url(args, page_token), api_key)
        voices.extend(payload.get("voices", []))
        total_count = payload.get("total_count", total_count)
        if not payload.get("has_more"):
            break
        page_token = payload.get("next_page_token")
        if not page_token:
            break

    snapshot = {
        "provider": "elevenlabs",
        "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "query": {
            "search": args.search,
            "voice_type": args.voice_type,
            "category": args.category,
            "sort": args.sort,
            "sort_direction": args.sort_direction,
        },
        "total_count": total_count,
        "voices": voices,
    }

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(snapshot, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print(f"wrote {len(voices)} voices to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
