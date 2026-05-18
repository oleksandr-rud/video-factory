#!/usr/bin/env python3
"""Search Freepik/Magnific stock videos and normalize results for Visual Producer."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import urllib.parse
import urllib.request
from typing import Any


DEFAULT_API_BASE_URL = os.environ.get("FREEPIK_API_BASE_URL", "https://api.magnific.com")
DEFAULT_LANGUAGE = os.environ.get("FREEPIK_VIDEO_SEARCH_LANGUAGE", "en-US")
DEFAULT_LIMIT = int(os.environ.get("FREEPIK_VIDEO_SEARCH_LIMIT", "25"))


def api_key() -> str | None:
    return os.environ.get("FREEPIK_API_KEY") or os.environ.get("MAGNIFIC_API_KEY")


def drop_none(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: drop_none(item) for key, item in value.items() if item is not None}
    if isinstance(value, list):
        return [drop_none(item) for item in value]
    return value


def parse_extra_params(values: list[str]) -> dict[str, str]:
    params: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"Invalid --param value {value!r}; expected key=value.")
        key, item = value.split("=", 1)
        if key:
            params[key] = item
    return params


def safe_slug(value: Any) -> str:
    safe = []
    for char in str(value):
        lowered = char.lower()
        if lowered in "abcdefghijklmnopqrstuvwxyz0123456789-_.":
            safe.append(lowered)
        else:
            safe.append("-")
    slug = "".join(safe).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "item"


def build_url(base_url: str, path: str, params: dict[str, Any] | None = None) -> str:
    url = base_url.rstrip("/") + path
    clean_params = {key: value for key, value in (params or {}).items() if value not in (None, "")}
    if clean_params:
        return f"{url}?{urllib.parse.urlencode(clean_params)}"
    return url


def get_json(url: str, key: str, language: str) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        method="GET",
        headers={
            "x-magnific-api-key": key,
            "Accept-Language": language,
            "accept": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def download_url(url: str, output_path: pathlib.Path) -> None:
    request = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(request, timeout=180) as response:
        output_path.write_bytes(response.read())


def response_items(response: dict[str, Any]) -> list[dict[str, Any]]:
    data = response.get("data")
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        for key in ("items", "results", "videos", "resources"):
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    for key in ("items", "results", "videos", "resources"):
        value = response.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def first_media_url(items: Any) -> str:
    if isinstance(items, list):
        for item in items:
            if isinstance(item, dict) and item.get("url"):
                return str(item["url"])
    return ""


def parse_duration_seconds(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str) or not value:
        return None
    parts = value.split(":")
    try:
        numbers = [float(part) for part in parts]
    except ValueError:
        return None
    if len(numbers) == 2:
        return numbers[0] * 60 + numbers[1]
    if len(numbers) == 3:
        return numbers[0] * 3600 + numbers[1] * 60 + numbers[2]
    return None


def context_fields(args: argparse.Namespace) -> dict[str, str]:
    return {
        "project_id": args.project_id,
        "project_path": args.project_path,
        "channel_profile_id": args.channel_profile_id,
        "channel_slug": args.channel_slug,
        "channel_profile_path": args.channel_profile_path,
        "media_asset_manifest_path": args.media_asset_manifest_path,
    }


def normalize_result(result: dict[str, Any], scene_id: str | None, term: str, args: argparse.Namespace) -> dict[str, Any]:
    video_id = result.get("id") or result.get("video_id") or result.get("resource_id") or "unknown"
    source_url = result.get("url") or ""
    preview_url = first_media_url(result.get("previews")) or first_media_url(result.get("thumbnails"))
    thumbnails = result.get("thumbnails") if isinstance(result.get("thumbnails"), list) else []
    previews = result.get("previews") if isinstance(result.get("previews"), list) else []
    author = result.get("author") if isinstance(result.get("author"), dict) else {}
    tags = result.get("tags") if isinstance(result.get("tags"), list) else []
    premium = result.get("premium")

    candidate = {
        "candidate_id": f"{scene_id + '-' if scene_id else ''}freepik-{video_id}",
        "scene_id": scene_id or "",
        **context_fields(args),
        "route": "stock_clip",
        "provider": "freepik",
        "source_url": source_url,
        "preview_url": preview_url,
        "prompt_or_query": term,
        "license_summary": (
            "Freepik/Magnific stock video candidate; final use requires Director-approved "
            "license/download path and preserved download metadata."
        ),
        "cost_estimate": "premium/credits or download quota may apply" if premium else "free or account-limited; verify before use",
        "technical": {
            "duration_seconds": parse_duration_seconds(result.get("duration")),
            "fps": float(result["fps"]) if str(result.get("fps", "")).replace(".", "", 1).isdigit() else None,
        },
        "scores": {
            "semantic_fit": 0,
            "continuity_fit": 0,
            "technical_fit": 0,
            "rights_fit": 0,
            "editability": 0,
            "total": 0,
        },
        "status": "needs_approval",
        "freepik": {
            "id": video_id,
            "name": result.get("name"),
            "code": result.get("code"),
            "quality": result.get("quality"),
            "duration": result.get("duration"),
            "premium": premium,
            "aspect_ratio": result.get("aspect-ratio") or result.get("aspect_ratio"),
            "author": author,
            "tags": tags,
            "thumbnails": thumbnails,
            "previews": previews,
            "is_ai_generated": result.get("is_ai_generated"),
            "item_subtype": result.get("item_subtype"),
        },
    }
    return drop_none(candidate)


def write_candidate_files(candidates: list[dict[str, Any]], candidate_dir: str | None) -> list[str]:
    if not candidate_dir:
        return []
    output_dir = pathlib.Path(candidate_dir)
    paths: list[str] = []
    for candidate in candidates:
        scene_dir = output_dir / safe_slug(candidate.get("scene_id") or "scene")
        scene_dir.mkdir(parents=True, exist_ok=True)
        path = scene_dir / f"{safe_slug(candidate.get('candidate_id'))}.json"
        path.write_text(json.dumps(candidate, indent=2, ensure_ascii=False), encoding="utf-8")
        paths.append(str(path))
    return paths


def download_link_for_video(base_url: str, key: str, language: str, video_id: Any, option_id: str | None = None) -> dict[str, Any]:
    path = f"/v1/videos/{video_id}/download"
    if option_id:
        path += f"/{option_id}"
    return get_json(build_url(base_url, path), key, language)


def extract_download_url(download_response: dict[str, Any]) -> tuple[str, str]:
    data = download_response.get("data") if isinstance(download_response.get("data"), dict) else download_response
    url = data.get("signed_url") or data.get("url") or ""
    filename = data.get("filename") or pathlib.Path(urllib.parse.urlparse(url).path).name or "freepik-video"
    return str(url), str(filename)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--term", "--query", dest="term", required=True)
    parser.add_argument("--scene-id")
    parser.add_argument("--language", default=DEFAULT_LANGUAGE)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--order")
    parser.add_argument("--param", action="append", default=[], help="Extra query parameter as key=value. Repeatable.")
    parser.add_argument("--api-base-url", default=DEFAULT_API_BASE_URL)
    parser.add_argument("--output", required=True)
    parser.add_argument("--candidate-dir")
    parser.add_argument("--project-id")
    parser.add_argument("--project-path")
    parser.add_argument("--channel-profile-id")
    parser.add_argument("--channel-slug")
    parser.add_argument("--channel-profile-path")
    parser.add_argument("--media-asset-manifest-path")
    parser.add_argument("--request-download-links", action="store_true")
    parser.add_argument("--download-option-id")
    parser.add_argument("--save-downloads", action="store_true")
    parser.add_argument("--download-dir")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--approved", action="store_true", help="Legacy alias for --approved-api-search only.")
    parser.add_argument("--approved-api-search", action="store_true")
    parser.add_argument("--approved-download-links", action="store_true")
    parser.add_argument("--approved-file-download", action="store_true")
    parser.add_argument("--approval-id")
    parser.add_argument("--download-link-approval-id")
    parser.add_argument("--file-download-approval-id")
    args = parser.parse_args()

    output_path = pathlib.Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    api_search_approved = bool(args.approved_api_search or args.approved)
    download_links_approved = bool(args.approved_download_links)
    file_download_approved = bool(args.approved_file_download)

    try:
        query_params = {
            "term": args.term,
            "page": args.page,
            "limit": args.limit,
            "order": args.order,
            **parse_extra_params(args.param),
        }
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    request_url = build_url(args.api_base_url, "/v1/videos", query_params)
    base_payload: dict[str, Any] = {
        "provider": "freepik",
        "api_brand": "magnific",
        "status": "prepared",
        "query": {
            "term": args.term,
            "language": args.language,
            "limit": args.limit,
            "page": args.page,
            "order": args.order,
            "request_url": request_url,
        },
        "approval": {
            "api_search_approved": api_search_approved,
            "api_search_approval_id": args.approval_id,
            "download_links_requested": args.request_download_links,
            "download_links_approved": download_links_approved,
            "download_link_approval_id": args.download_link_approval_id,
            "save_downloads_requested": args.save_downloads,
            "file_download_approved": file_download_approved,
            "file_download_approval_id": args.file_download_approval_id,
            "download_policy": (
                "API search requires --approved-api-search or legacy --approved. "
                "Download-link retrieval requires --approved-download-links. "
                "Saving files requires --approved-file-download."
            ),
        },
        "results": [],
        "candidates": [],
        "candidate_paths": [],
        "limitations": [
            "Current Freepik stock video docs redirect to Magnific-branded API docs.",
            "Use --param for optional provider filters that are account- or query-specific.",
        ],
    }

    if not args.execute:
        output_path.write_text(json.dumps(drop_none(base_payload), indent=2, ensure_ascii=False), encoding="utf-8")
        print(output_path)
        return 0

    if not api_search_approved:
        print("Refusing Freepik/Magnific API call without --approved-api-search", file=sys.stderr)
        return 2

    if args.save_downloads and not args.request_download_links:
        print("--save-downloads requires --request-download-links", file=sys.stderr)
        return 2
    if args.save_downloads and not args.download_dir:
        print("--download-dir is required with --save-downloads", file=sys.stderr)
        return 2
    if args.request_download_links and not download_links_approved:
        print("Refusing download-link retrieval without --approved-download-links", file=sys.stderr)
        return 2
    if args.save_downloads and not file_download_approved:
        print("Refusing file download without --approved-file-download", file=sys.stderr)
        return 2

    key = api_key()
    if not key:
        print("FREEPIK_API_KEY or MAGNIFIC_API_KEY is required for --execute", file=sys.stderr)
        return 2

    try:
        response = get_json(request_url, key, args.language)
    except Exception as exc:  # noqa: BLE001 - CLI should surface provider errors.
        print(f"Freepik/Magnific video search failed: {exc}", file=sys.stderr)
        return 2

    results = response_items(response)
    if args.limit > 0:
        results = results[: args.limit]
    candidates = [normalize_result(result, args.scene_id, args.term, args) for result in results]

    if args.request_download_links:
        download_dir = pathlib.Path(args.download_dir) if args.download_dir else None
        if download_dir:
            download_dir.mkdir(parents=True, exist_ok=True)
        for candidate in candidates:
            video_id = candidate.get("freepik", {}).get("id")
            if not video_id or video_id == "unknown":
                continue
            try:
                download_response = download_link_for_video(
                    args.api_base_url,
                    key,
                    args.language,
                    video_id,
                    args.download_option_id,
                )
                download_url_value, filename = extract_download_url(download_response)
                candidate["freepik"]["download_response"] = download_response
                candidate["freepik"]["download_filename"] = filename
                candidate["freepik"]["download_url"] = download_url_value
                if args.save_downloads and download_url_value and download_dir:
                    local_path = download_dir / filename
                    download_url(download_url_value, local_path)
                    candidate["local_path"] = str(local_path)
                    candidate["status"] = "downloaded"
            except Exception as exc:  # noqa: BLE001 - preserve partial results.
                candidate["freepik"]["download_error"] = str(exc)

    candidate_paths = write_candidate_files(candidates, args.candidate_dir)
    payload = {
        **base_payload,
        "status": "searched",
        "raw_response": response,
        "results": results,
        "candidates": candidates,
        "candidate_paths": candidate_paths,
    }
    output_path.write_text(json.dumps(drop_none(payload), indent=2, ensure_ascii=False), encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
