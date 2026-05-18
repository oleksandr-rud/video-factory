#!/usr/bin/env python3
"""Search Pexels stock videos and normalize results for Visual Producer."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import urllib.parse
import urllib.request
from typing import Any


DEFAULT_API_BASE_URL = os.environ.get("PEXELS_API_BASE_URL", "https://api.pexels.com")
DEFAULT_LOCALE = os.environ.get("PEXELS_VIDEO_SEARCH_LOCALE", "en-US")
DEFAULT_LIMIT = int(os.environ.get("PEXELS_VIDEO_SEARCH_LIMIT", "25"))


def api_key() -> str | None:
    return os.environ.get("PEXELS_API_KEY")


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


def get_json(url: str, key: str) -> tuple[dict[str, Any], dict[str, str]]:
    request = urllib.request.Request(
        url,
        method="GET",
        headers={
            "Authorization": key,
            "accept": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        headers = {
            header: value
            for header, value in response.headers.items()
            if header.lower().startswith("x-ratelimit")
        }
        return json.loads(response.read().decode("utf-8")), headers


def download_url(url: str, output_path: pathlib.Path) -> None:
    request = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(request, timeout=180) as response:
        output_path.write_bytes(response.read())


def video_items(response: dict[str, Any]) -> list[dict[str, Any]]:
    videos = response.get("videos")
    if isinstance(videos, list):
        return [item for item in videos if isinstance(item, dict)]
    return []


def int_or_none(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str) and value.strip().isdigit():
        return int(value)
    return None


def float_or_none(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def first_picture(pictures: Any) -> str:
    if isinstance(pictures, list):
        for picture in pictures:
            if isinstance(picture, dict) and picture.get("picture"):
                return str(picture["picture"])
    return ""


def normalize_video_files(files: Any) -> list[dict[str, Any]]:
    if not isinstance(files, list):
        return []
    normalized = []
    for item in files:
        if not isinstance(item, dict):
            continue
        normalized.append(
            drop_none(
                {
                    "id": item.get("id"),
                    "quality": item.get("quality"),
                    "file_type": item.get("file_type"),
                    "width": int_or_none(item.get("width")),
                    "height": int_or_none(item.get("height")),
                    "fps": float_or_none(item.get("fps")),
                    "link": item.get("link"),
                }
            )
        )
    return normalized


def select_video_file(
    files: list[dict[str, Any]],
    preferred_quality: str | None = None,
    file_id: str | None = None,
) -> dict[str, Any] | None:
    if file_id:
        for item in files:
            if str(item.get("id")) == str(file_id):
                return item
        return None

    candidates = [
        item
        for item in files
        if item.get("link")
        and item.get("file_type") == "video/mp4"
        and ".m3u8" not in str(item.get("link"))
    ]
    if preferred_quality:
        quality_matches = [item for item in candidates if item.get("quality") == preferred_quality]
        if quality_matches:
            candidates = quality_matches
    if not candidates:
        return None

    quality_score = {"uhd": 4, "hd": 3, "sd": 2, "hls": 1}

    def score(item: dict[str, Any]) -> tuple[int, int, float]:
        width = int_or_none(item.get("width")) or 0
        height = int_or_none(item.get("height")) or 0
        fps = float_or_none(item.get("fps")) or 0
        return (quality_score.get(str(item.get("quality")), 0), width * height, fps)

    return sorted(candidates, key=score, reverse=True)[0]


def context_fields(args: argparse.Namespace) -> dict[str, str]:
    return {
        "project_id": args.project_id,
        "project_path": args.project_path,
        "channel_profile_id": args.channel_profile_id,
        "channel_slug": args.channel_slug,
        "channel_profile_path": args.channel_profile_path,
        "media_asset_manifest_path": args.media_asset_manifest_path,
    }


def normalize_result(
    result: dict[str, Any],
    scene_id: str | None,
    term: str,
    args: argparse.Namespace,
) -> dict[str, Any]:
    video_id = result.get("id") or "unknown"
    source_url = result.get("url") or f"https://www.pexels.com/video/{video_id}/"
    files = normalize_video_files(result.get("video_files"))
    selected_file = select_video_file(files, args.download_quality, args.download_file_id)
    pictures = result.get("video_pictures") if isinstance(result.get("video_pictures"), list) else []
    user = result.get("user") if isinstance(result.get("user"), dict) else {}
    candidate = {
        "candidate_id": f"{scene_id + '-' if scene_id else ''}pexels-{video_id}",
        "scene_id": scene_id or "",
        **context_fields(args),
        "route": "stock_clip",
        "provider": "pexels",
        "source_url": source_url,
        "preview_url": result.get("image") or first_picture(pictures),
        "prompt_or_query": term,
        "license_summary": (
            "Pexels License stock video candidate; free personal/commercial use is generally allowed, "
            "API attribution/link-back is required by Pexels guidelines, and final use must avoid "
            "restricted likeness, endorsement, trademark, or unmodified resale contexts."
        ),
        "cost_estimate": "free API/content; subject to Pexels rate limits and final-use rights checks",
        "technical": {
            "duration_seconds": float_or_none(result.get("duration")),
            "width": int_or_none(result.get("width")),
            "height": int_or_none(result.get("height")),
            "fps": float_or_none(selected_file.get("fps")) if selected_file else None,
        },
        "scores": {
            "semantic_fit": 0,
            "continuity_fit": 0,
            "technical_fit": 0,
            "rights_fit": 0,
            "editability": 0,
            "total": 0,
        },
        "status": "proposed",
        "pexels": {
            "id": video_id,
            "url": source_url,
            "image": result.get("image"),
            "duration": result.get("duration"),
            "width": result.get("width"),
            "height": result.get("height"),
            "user": user,
            "attribution": {
                "text": f"Video by {user.get('name', 'Pexels contributor')} on Pexels",
                "creator_name": user.get("name"),
                "creator_url": user.get("url"),
                "pexels_url": source_url,
            },
            "video_files": files,
            "selected_video_file": selected_file,
            "video_pictures": pictures,
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


def target_candidates(args: argparse.Namespace, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if args.download_all:
        return candidates
    ids = {str(value) for value in args.download_video_id}
    return [candidate for candidate in candidates if str(candidate.get("pexels", {}).get("id")) in ids]


def download_filename(candidate: dict[str, Any], selected_file: dict[str, Any], url: str) -> str:
    video_id = candidate.get("pexels", {}).get("id") or "unknown"
    file_id = selected_file.get("id") or "file"
    quality = selected_file.get("quality") or "video"
    width = selected_file.get("width") or "w"
    height = selected_file.get("height") or "h"
    suffix = pathlib.Path(urllib.parse.urlparse(url).path).suffix
    if suffix.lower() not in (".mp4", ".mov", ".m4v"):
        suffix = ".mp4"
    return f"pexels-{safe_slug(video_id)}-{safe_slug(file_id)}-{safe_slug(quality)}-{width}x{height}{suffix}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--term", "--query", dest="term", required=True)
    parser.add_argument("--scene-id")
    parser.add_argument("--locale", default=DEFAULT_LOCALE)
    parser.add_argument("--limit", "--per-page", dest="limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--orientation", choices=["landscape", "portrait", "square"])
    parser.add_argument("--size", choices=["large", "medium", "small"])
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
    parser.add_argument("--save-downloads", action="store_true")
    parser.add_argument("--download-dir")
    parser.add_argument("--download-video-id", action="append", default=[])
    parser.add_argument("--download-all", action="store_true")
    parser.add_argument("--download-quality", choices=["uhd", "hd", "sd"])
    parser.add_argument("--download-file-id")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--approved", action="store_true", help="Legacy alias for --approved-api-search only.")
    parser.add_argument("--approved-api-search", action="store_true")
    parser.add_argument("--approved-file-download", action="store_true")
    parser.add_argument("--approval-id")
    parser.add_argument("--file-download-approval-id")
    args = parser.parse_args()

    output_path = pathlib.Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    api_search_approved = bool(args.approved_api_search or args.approved)
    file_download_approved = bool(args.approved_file_download)

    if args.limit < 1 or args.limit > 80:
        print("Pexels --limit/--per-page must be between 1 and 80", file=sys.stderr)
        return 2

    try:
        query_params = {
            "query": args.term,
            "page": args.page,
            "per_page": args.limit,
            "orientation": args.orientation,
            "size": args.size,
            "locale": args.locale,
            **parse_extra_params(args.param),
        }
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    request_url = build_url(args.api_base_url, "/v1/videos/search", query_params)
    base_payload: dict[str, Any] = {
        "provider": "pexels",
        "status": "prepared",
        "query": {
            "term": args.term,
            "locale": args.locale,
            "limit": args.limit,
            "page": args.page,
            "orientation": args.orientation,
            "size": args.size,
            "request_url": request_url,
        },
        "approval": {
            "api_search_approved": api_search_approved,
            "api_search_approval_id": args.approval_id,
            "save_downloads_requested": args.save_downloads,
            "file_download_approved": file_download_approved,
            "file_download_approval_id": args.file_download_approval_id,
            "download_policy": (
                "Pexels API search returns direct video_files links. API search requires "
                "--approved-api-search or legacy --approved. Saving files requires "
                "--approved-file-download plus --download-video-id or --download-all."
            ),
        },
        "results": [],
        "candidates": [],
        "candidate_paths": [],
        "limitations": [
            "Pexels API results include direct video file links as part of normal search results.",
            "Pexels API guidelines require prominent Pexels link-back and photographer credit when possible.",
            "Pexels content still needs final-use review for likeness, endorsement, trademark, and unmodified resale restrictions.",
        ],
    }

    if not args.execute:
        output_path.write_text(json.dumps(drop_none(base_payload), indent=2, ensure_ascii=False), encoding="utf-8")
        print(output_path)
        return 0

    if not api_search_approved:
        print("Refusing Pexels API call without --approved-api-search", file=sys.stderr)
        return 2
    if args.save_downloads and not args.download_dir:
        print("--download-dir is required with --save-downloads", file=sys.stderr)
        return 2
    if args.save_downloads and not file_download_approved:
        print("Refusing file download without --approved-file-download", file=sys.stderr)
        return 2
    if args.save_downloads and not args.download_all and not args.download_video_id:
        print("--save-downloads requires --download-video-id or --download-all", file=sys.stderr)
        return 2

    key = api_key()
    if not key:
        print("PEXELS_API_KEY is required for --execute", file=sys.stderr)
        return 2

    try:
        response, rate_limit = get_json(request_url, key)
    except Exception as exc:  # noqa: BLE001 - CLI should surface provider errors.
        print(f"Pexels video search failed: {exc}", file=sys.stderr)
        return 2

    results = video_items(response)
    candidates = [normalize_result(result, args.scene_id, args.term, args) for result in results]

    if args.save_downloads:
        download_base = pathlib.Path(args.download_dir)
        selected_candidates = target_candidates(args, candidates)
        if not selected_candidates:
            print("No matching Pexels candidates for requested download ids", file=sys.stderr)
            return 2
        for candidate in selected_candidates:
            selected_file = candidate.get("pexels", {}).get("selected_video_file")
            if not isinstance(selected_file, dict) or not selected_file.get("link"):
                candidate.setdefault("pexels", {})["download_error"] = "No selectable video file link"
                continue
            url = str(selected_file["link"])
            target_dir = download_base
            if len(selected_candidates) > 1:
                target_dir = download_base / safe_slug(candidate.get("candidate_id"))
            target_dir.mkdir(parents=True, exist_ok=True)
            filename = download_filename(candidate, selected_file, url)
            local_path = target_dir / filename
            try:
                download_url(url, local_path)
                candidate["local_path"] = str(local_path)
                candidate["status"] = "downloaded"
                candidate["pexels"]["downloaded_video_file"] = selected_file
                candidate["pexels"]["download_filename"] = filename
            except Exception as exc:  # noqa: BLE001 - preserve partial results.
                candidate["pexels"]["download_error"] = str(exc)

    candidate_paths = write_candidate_files(candidates, args.candidate_dir)
    payload = {
        **base_payload,
        "status": "searched",
        "rate_limit": rate_limit,
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
