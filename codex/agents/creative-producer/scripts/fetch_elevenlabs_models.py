#!/usr/bin/env python3
"""Snapshot ElevenLabs models visible to the account.

This validates current provider support before generation. It does not generate
audio or spend TTS credits.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.request


API_URL = "https://api.elevenlabs.io/v1/models"


def request_json(url: str, api_key: str | None) -> object:
    headers = {"Accept": "application/json"}
    if api_key:
        headers["xi-api-key"] = api_key
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--require-api-key", action="store_true")
    args = parser.parse_args()

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if args.require_api_key and not api_key:
        print("ELEVENLABS_API_KEY is required with --require-api-key", file=sys.stderr)
        return 2

    payload = request_json(API_URL, api_key)
    models = payload if isinstance(payload, list) else payload.get("models", [])
    snapshot = {
        "provider": "elevenlabs",
        "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "endpoint": "/v1/models",
        "used_api_key": bool(api_key),
        "models": models,
    }

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(snapshot, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print(f"wrote {len(models)} models to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
