#!/usr/bin/env python3
"""Reusable OpenRouter video request helper.

This is intentionally generic: it accepts a prompt plus a video URL or local
video path, optionally attaches still images, and writes the raw provider
response. Pipeline-specific critique should use the Video Critic runner.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import pathlib
import sys
import urllib.request
from typing import Any


OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = os.environ.get("OPENROUTER_VIDEO_MODEL", "qwen/qwen3.6-plus")
DEFAULT_MAX_VIDEO_BYTES = 256 * 1024 * 1024


def read_prompt(prompt: str | None, prompt_file: str | None) -> str:
    if prompt and prompt_file:
        raise ValueError("Use either --prompt or --prompt-file, not both.")
    if prompt:
        return prompt
    if prompt_file:
        return pathlib.Path(prompt_file).read_text(encoding="utf-8")
    raise ValueError("Either --prompt or --prompt-file is required.")


def mime_type(path: str, media_kind: str) -> str:
    suffix = pathlib.Path(path).suffix.lower()
    if media_kind == "video":
        return {
            ".mp4": "video/mp4",
            ".mpeg": "video/mpeg",
            ".mpg": "video/mpeg",
            ".mov": "video/mov",
            ".webm": "video/webm",
        }.get(suffix, "video/mp4")
    return {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }.get(suffix, "image/jpeg")


def data_url(path: str, media_kind: str, max_bytes: int | None = None, allow_large_upload: bool = False) -> str:
    file_path = pathlib.Path(path)
    size = file_path.stat().st_size
    if max_bytes is not None and size > max_bytes and not allow_large_upload:
        raise ValueError(
            f"{path} is {size} bytes, above limit {max_bytes}. "
            "Use a hosted URL or pass --allow-large-upload after approval."
        )
    encoded = base64.b64encode(file_path.read_bytes()).decode("ascii")
    return f"data:{mime_type(path, media_kind)};base64,{encoded}"


def response_format(format_name: str) -> dict[str, Any] | None:
    if format_name == "text":
        return None
    if format_name == "json_object":
        return {"type": "json_object"}
    raise ValueError(f"Unsupported response format: {format_name}")


def build_payload(
    model: str,
    prompt: str,
    video_url: str,
    image_urls: list[str],
    max_tokens: int,
    temperature: float,
    format_name: str,
    require_parameters: bool,
) -> dict[str, Any]:
    content: list[dict[str, Any]] = [
        {"type": "text", "text": prompt},
        {"type": "video_url", "video_url": {"url": video_url}},
    ]
    for image_url in image_urls:
        content.append({"type": "image_url", "image_url": {"url": image_url}})

    payload: dict[str, Any] = {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    formatted = response_format(format_name)
    if formatted:
        payload["response_format"] = formatted
    if require_parameters:
        payload["provider"] = {"require_parameters": True}
    return payload


def write_request_preview(path: str, payload: dict[str, Any], video_source: str, image_sources: list[str]) -> None:
    preview = json.loads(json.dumps(payload))
    image_index = 0
    for item in preview["messages"][0]["content"]:
        if item.get("type") == "video_url":
            item["video_url"]["url"] = video_source
        if item.get("type") == "image_url":
            item["image_url"]["url"] = image_sources[image_index] if image_index < len(image_sources) else "<image omitted>"
            image_index += 1
    pathlib.Path(path).write_text(json.dumps(preview, indent=2, ensure_ascii=False), encoding="utf-8")


def post_openrouter(api_key: str, payload: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        OPENROUTER_CHAT_URL,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/openai/codex",
            "X-Title": "Video Factory OpenRouter Helper",
        },
        data=json.dumps(payload).encode("utf-8"),
    )
    with urllib.request.urlopen(request, timeout=600) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt")
    parser.add_argument("--prompt-file")
    parser.add_argument("--video", help="Local video file path.")
    parser.add_argument("--video-url", help="Public or signed video URL.")
    parser.add_argument("--image", action="append", default=[], help="Optional local still image path. Repeatable.")
    parser.add_argument("--image-url", action="append", default=[], help="Optional still image URL. Repeatable.")
    parser.add_argument("--output", required=True, help="Raw response JSON path, or dry-run request preview path.")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--max-video-bytes", type=int, default=DEFAULT_MAX_VIDEO_BYTES)
    parser.add_argument("--allow-large-upload", action="store_true")
    parser.add_argument("--max-tokens", type=int, default=4000)
    parser.add_argument("--temperature", type=float, default=0)
    parser.add_argument("--response-format", choices=["text", "json_object"], default="text")
    parser.add_argument("--allow-parameter-fallback", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--approved", action="store_true")
    args = parser.parse_args()

    if bool(args.video) == bool(args.video_url):
        print("Use exactly one of --video or --video-url", file=sys.stderr)
        return 2

    try:
        prompt = read_prompt(args.prompt, args.prompt_file)
        video_url = args.video_url or data_url(
            args.video,
            "video",
            max_bytes=args.max_video_bytes,
            allow_large_upload=args.allow_large_upload,
        )
        image_urls = [*args.image_url, *[data_url(path, "image") for path in args.image]]
        payload = build_payload(
            args.model,
            prompt,
            video_url,
            image_urls,
            args.max_tokens,
            args.temperature,
            args.response_format,
            not args.allow_parameter_fallback,
        )
    except Exception as exc:  # noqa: BLE001 - convert helper errors to CLI failures.
        print(str(exc), file=sys.stderr)
        return 2

    output_path = pathlib.Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not args.execute:
        video_source = args.video_url or args.video or "<video omitted>"
        image_sources = [*args.image_url, *args.image]
        write_request_preview(str(output_path), payload, video_source, image_sources)
        print(output_path)
        return 0

    if not args.approved:
        print("Refusing OpenRouter API call without --approved", file=sys.stderr)
        return 2

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("OPENROUTER_API_KEY is required for --execute", file=sys.stderr)
        return 2

    response = post_openrouter(api_key, payload)
    output_path.write_text(json.dumps(response, indent=2, ensure_ascii=False), encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
