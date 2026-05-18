#!/usr/bin/env python3
"""Run or prepare an OpenRouter hybrid video critique."""

from __future__ import annotations

import argparse
import base64
import json
import os
import pathlib
import re
import sys
import urllib.request
from typing import Any


OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = os.environ.get("OPENROUTER_VIDEO_MODEL", "qwen/qwen3.6-plus")
DEFAULT_MAX_VIDEO_BYTES = 256 * 1024 * 1024
DEFAULT_MAX_FRAME_IMAGES = int(os.environ.get("OPENROUTER_VIDEO_REVIEW_MAX_FRAME_IMAGES", "12"))


REPORT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": True,
    "required": [
        "status",
        "review_mode",
        "video_observations",
        "scene_reviews",
        "scores",
        "findings",
        "revision_plan",
        "gate_decision",
        "limitations",
        "qa",
    ],
    "properties": {
        "status": {"type": "string"},
        "review_mode": {"type": "string"},
        "video_observations": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "scene_reviews": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "scores": {"type": "object", "additionalProperties": True},
        "findings": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "revision_plan": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "gate_decision": {"type": "object", "additionalProperties": True},
        "limitations": {"type": "array", "items": {"type": "string"}},
        "qa": {"type": "object", "additionalProperties": True},
    },
}


def load_json(path: str | None) -> Any:
    if not path:
        return None
    with open(path, "r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def drop_none(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: drop_none(item) for key, item in value.items() if item is not None}
    if isinstance(value, list):
        return [drop_none(item) for item in value]
    return value


def read_text(path: str | None, limit: int = 12000) -> str:
    if not path or not os.path.exists(path):
        return ""
    return pathlib.Path(path).read_text(encoding="utf-8", errors="replace")[:limit]


def load_text_or_json(path: str | None, limit: int = 16000) -> Any:
    if not path or not os.path.exists(path):
        return None
    try:
        return load_json(path)
    except json.JSONDecodeError:
        return read_text(path, limit)


def required_report_defaults(artifact_paths: dict[str, Any], artifacts: dict[str, Any]) -> dict[str, Any]:
    producer_criteria = artifacts.get("producer_criteria") if isinstance(artifacts.get("producer_criteria"), dict) else {}
    quality_thresholds = (
        producer_criteria.get("quality_thresholds")
        or producer_criteria.get("review_thresholds")
        or {
            "overall_min": 8,
            "category_min": 7,
            "max_major_findings": 0,
            "allow_minor_findings": True,
        }
    )
    return {
        "producer_criteria": {
            "criteria_prompt_path": artifact_paths.get("producer_criteria_path") or "",
            "acceptance_criteria": producer_criteria.get("acceptance_criteria", []),
            "required_rules": producer_criteria.get("required_rules", []),
            "forbidden_rules": producer_criteria.get("forbidden_rules", []),
            "style_rules": producer_criteria.get("style_rules", []),
            "quality_thresholds": quality_thresholds,
        },
        "scores": {
            "story_clarity": 0,
            "visual_relevance": 0,
            "subtitle_sync": 0,
            "platform_fit": 0,
            "factual_alignment": 0,
            "overall": 0,
        },
        "gate_decision": {
            "status": "needs_approval",
            "release_candidate": False,
            "failed_gates": [],
            "waived_gates": [],
            "next_action": "ask_user",
            "stop_reason": "OpenRouter video critique requires approval before gate decision.",
        },
    }


def merge_required_report_defaults(report: dict[str, Any], defaults: dict[str, Any]) -> None:
    for key in ("producer_criteria", "scores", "gate_decision"):
        report[key] = {**defaults[key], **(report.get(key) or {})}
    report["producer_criteria"]["quality_thresholds"] = {
        **defaults["producer_criteria"]["quality_thresholds"],
        **(report["producer_criteria"].get("quality_thresholds") or {}),
    }


def video_mime_type(video_path: str) -> str:
    suffix = pathlib.Path(video_path).suffix.lower()
    return {
        ".mp4": "video/mp4",
        ".mpeg": "video/mpeg",
        ".mpg": "video/mpeg",
        ".mov": "video/mov",
        ".webm": "video/webm",
    }.get(suffix, "video/mp4")


def video_data_url(video_path: str, max_video_bytes: int, allow_large_upload: bool) -> str:
    path = pathlib.Path(video_path)
    size = path.stat().st_size
    if size > max_video_bytes and not allow_large_upload:
        raise ValueError(
            f"Video is {size} bytes, above --max-video-bytes={max_video_bytes}. "
            "Use --video-url for hosted media or pass --allow-large-upload after approval."
        )
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{video_mime_type(video_path)};base64,{encoded}"


def image_mime_type(image_path: str) -> str:
    suffix = pathlib.Path(image_path).suffix.lower()
    return {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }.get(suffix, "image/jpeg")


def image_data_url(image_path: str) -> str:
    path = pathlib.Path(image_path)
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{image_mime_type(image_path)};base64,{encoded}"


def selected_frame_image_paths(review_assets: dict[str, Any], max_frame_images: int) -> list[str]:
    paths: list[str] = []
    if max_frame_images <= 0:
        return paths
    for sample in review_assets.get("frame_samples", []):
        frame_path = sample.get("frame_path")
        if frame_path and os.path.exists(frame_path):
            paths.append(frame_path)
        if len(paths) >= max_frame_images:
            break
    return paths


def extract_output_text(response: dict[str, Any]) -> str:
    choices = response.get("choices") or []
    if choices:
        content = (choices[0].get("message") or {}).get("content", "")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            texts = []
            for item in content:
                if isinstance(item, dict) and "text" in item:
                    texts.append(str(item["text"]))
            return "\n".join(texts)
    if response.get("output_text"):
        return str(response["output_text"])
    return ""


def parse_jsonish(text: str) -> dict[str, Any] | None:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.S)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
    return None


def build_prompt(review_assets: dict[str, Any], artifacts: dict[str, Any], attached_frame_count: int) -> str:
    frame_lines = []
    for sample in review_assets.get("frame_samples", []):
        frame_lines.append(
            f"- {sample.get('timestamp_seconds')}s"
            f" scene={sample.get('scene_id', 'unknown')}"
            f" reason={sample.get('reason', 'sample')}"
        )

    artifact_text = json.dumps(artifacts, indent=2, ensure_ascii=False)
    return f"""You are an independent senior video critic for the Video Factory production pipeline.

Review the attached video and any attached sampled frame stills, using the artifact text for scenario, timing, captions, channel rules, producer criteria, rights notes, and previous iteration context. Be direct and evidence-based.

Important evidence rules:
- Use the video input for temporal evidence: motion, transitions, continuity, pacing, scene boundaries, and time-localized visual events.
- Use attached sampled frame stills as sharper checkpoints for captions, visible text, safe areas, framing, watermarks, brand details, and single-frame artifacts.
- Do not infer spoken audio content unless captions, transcript, or voiceover artifacts are supplied.
- Treat producer criteria as binding. The general rubric fills gaps but does not override the criteria.
- Mark missing evidence as unknown or fail according to the gate policy. Do not invent provenance, licensing, or source support.
- Distinguish blocking delivery defects from taste preferences.

Return JSON only. Use this shape:
{{
  "status": "reviewed|needs_revision|blocked|approved",
  "review_mode": "hybrid|direct_video",
  "video_observations": [{{"timestamp_seconds": 0, "scene_id": "scene-01", "observation": "..."}}],
  "scores": {{"story_clarity": 0-10, "hook_strength": 0-10, "pacing": 0-10, "visual_quality": 0-10, "visual_relevance": 0-10, "audio_quality": 0-10, "subtitle_sync": 0-10, "brand_fit": 0-10, "platform_fit": 0-10, "factual_alignment": 0-10, "originality": 0-10, "accessibility": 0-10, "overall": 0-10}},
  "findings": [{{"severity": "blocker|major|minor|note", "category": "story|hook|pacing|visual|audio|subtitles|sync|brand|platform|factual|rights|technical|accessibility|engagement|redundancy|other", "scene_id": "scene-01", "timestamp_seconds": 0, "evidence": "...", "description": "...", "recommendation": "...", "owner_agent": "..."}}],
  "scene_reviews": [{{"scene_id": "scene-01", "status": "pass|fail|partial|unknown|waived", "summary": "...", "criteria_results": [{{"criterion": "...", "status": "pass|fail|waived|not_applicable|unknown", "evidence": "...", "recommendation": "..."}}]}}],
  "revision_plan": [{{"priority": 1, "owner_agent": "...", "affected_artifacts": ["..."], "action": "...", "expected_impact": "...", "requires_user_approval": false}}],
  "gate_decision": {{"status": "pass|fail|needs_approval|blocked", "release_candidate": false, "stop_reason": "...", "failed_gates": ["..."], "waived_gates": ["..."], "next_action": "approve_rc|revise_and_rerender|ask_user|stop_blocked"}},
  "limitations": ["..."],
  "qa": {{"status": "pass|fail|partial|not_run", "summary": "...", "residual_risks": ["..."]}}
}}

Required passes:
1. Build timestamped observations that cover the whole video.
2. Evaluate every scene id in the scenario or timeline sync plan.
3. Check hook, story clarity, pacing, payoff, and source alignment.
4. Check visual relevance, visual quality, framing, safe areas, captions, visible text, continuity, AI/stock artifacts, and watermarks.
5. Check platform fit: aspect ratio, opening frame, duration, CTA, and mobile readability.
6. Check factual, rights, likeness, brand, accessibility, and redundancy risks.
7. Produce a revision plan mapped to owner agents.

Frame sample index from the prepared review package:
{chr(10).join(frame_lines)}

Attached frame stills in this request: {attached_frame_count}

Artifacts:
{artifact_text}
"""


def build_payload(
    model: str,
    prompt: str,
    video_url: str,
    image_urls: list[str],
    max_tokens: int,
    temperature: float,
    structured_output: bool,
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
        "messages": [
            {
                "role": "user",
                "content": content,
            }
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if structured_output:
        payload["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": "video_critique",
                "strict": True,
                "schema": REPORT_SCHEMA,
            },
        }
        if require_parameters:
            payload["provider"] = {"require_parameters": True}
    return payload


def write_payload_preview(path: str, payload: dict[str, Any], video_source: str, frame_sources: list[str]) -> None:
    preview = json.loads(json.dumps(payload))
    frame_index = 0
    for content_item in preview["messages"][0]["content"]:
        if content_item.get("type") == "video_url":
            content_item["video_url"]["url"] = video_source
        if content_item.get("type") == "image_url":
            content_item["image_url"]["url"] = frame_sources[frame_index] if frame_index < len(frame_sources) else "<frame data omitted>"
            frame_index += 1
    pathlib.Path(path).write_text(json.dumps(preview, indent=2, ensure_ascii=False), encoding="utf-8")


def post_openrouter(api_key: str, payload: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        OPENROUTER_CHAT_URL,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/openai/codex",
            "X-Title": "Video Factory Critic",
        },
        data=json.dumps(payload).encode("utf-8"),
    )
    with urllib.request.urlopen(request, timeout=600) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review-assets", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--video-url", help="Public video URL to send instead of base64-encoding review_assets.video_path.")
    parser.add_argument("--max-video-bytes", type=int, default=DEFAULT_MAX_VIDEO_BYTES)
    parser.add_argument("--allow-large-upload", action="store_true")
    parser.add_argument("--max-frame-images", type=int, default=DEFAULT_MAX_FRAME_IMAGES)
    parser.add_argument("--no-frame-images", action="store_true")
    parser.add_argument("--max-tokens", type=int, default=12000)
    parser.add_argument("--temperature", type=float, default=0)
    parser.add_argument("--no-structured-output", action="store_true")
    parser.add_argument("--allow-parameter-fallback", action="store_true")
    parser.add_argument("--review-loop-id")
    parser.add_argument("--review-iteration", type=int, default=1)
    parser.add_argument("--previous-critique-id")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--approved", action="store_true")
    args = parser.parse_args()

    review_assets = load_json(args.review_assets)
    artifact_paths = review_assets.get("artifacts", {})
    artifacts = {
        "review_assets": review_assets,
        "render_package": load_json(artifact_paths.get("render_package_path")),
        "scenario": load_json(artifact_paths.get("scenario_path")),
        "timeline_sync_plan": load_json(artifact_paths.get("timeline_sync_plan_path")),
        "voiceover_package": load_json(artifact_paths.get("voiceover_package_path")),
        "captions_text": read_text(artifact_paths.get("caption_path")),
        "reference_analysis": load_json(artifact_paths.get("reference_analysis_path")),
        "channel_format": load_json(artifact_paths.get("channel_format_path")),
        "producer_criteria": load_text_or_json(artifact_paths.get("producer_criteria_path")),
        "previous_critique": load_json(artifact_paths.get("previous_critique_path")),
    }
    frame_paths = [] if args.no_frame_images else selected_frame_image_paths(review_assets, args.max_frame_images)
    review_mode = "hybrid" if frame_paths else "direct_video"
    prompt = build_prompt(review_assets, drop_none(artifacts), len(frame_paths))
    output_dir = os.path.dirname(os.path.abspath(args.output))
    os.makedirs(output_dir, exist_ok=True)
    prompt_path = os.path.join(output_dir, "openrouter-video-critique-prompt.txt")
    payload_preview_path = os.path.join(output_dir, "openrouter-video-critique-request-preview.json")
    pathlib.Path(prompt_path).write_text(prompt, encoding="utf-8")

    video_path = review_assets.get("video_path")
    video_source_label = args.video_url or video_path or ""
    placeholder_video_url = args.video_url or f"data:{video_mime_type(video_path or 'video.mp4')};base64,<omitted>"
    placeholder_image_urls = [f"data:{image_mime_type(path)};base64,<omitted>" for path in frame_paths]
    preview_payload = build_payload(
        args.model,
        prompt,
        placeholder_video_url,
        placeholder_image_urls,
        args.max_tokens,
        args.temperature,
        not args.no_structured_output,
        not args.allow_parameter_fallback,
    )
    write_payload_preview(payload_preview_path, preview_payload, video_source_label or placeholder_video_url, frame_paths)

    scenario = artifacts.get("scenario") or {}
    render = artifacts.get("render_package") or {}
    defaults = required_report_defaults(artifact_paths, artifacts)
    base_report: dict[str, Any] = {
        "critique_id": f"{render.get('render_id', 'render')}-openrouter-video-critique",
        "render_id": render.get("render_id", "unknown"),
        "scenario_id": render.get("scenario_id") or scenario.get("scenario_id") or "unknown",
        "review_loop_id": args.review_loop_id,
        "review_iteration": args.review_iteration,
        "previous_critique_id": args.previous_critique_id,
        "status": "needs_approval",
        "review_mode": review_mode,
        "model": {
            "provider": "openrouter",
            "model_id": args.model,
            "prompt_path": prompt_path,
            "notes": f"Dry-run {review_mode} prompt prepared; no API call made.",
        },
        "inputs": {
            "video_path": video_path,
            "review_assets_path": args.review_assets,
            "frame_image_paths": frame_paths,
            **artifact_paths,
        },
        "producer_criteria": defaults["producer_criteria"],
        "scores": defaults["scores"],
        "findings": [],
        "scene_reviews": [],
        "revision_plan": [],
        "gate_decision": defaults["gate_decision"],
        "limitations": review_assets.get("limitations", []),
        "qa": {
            "status": "not_run",
            "summary": f"OpenRouter {review_mode} critique prepared but not executed.",
        },
    }

    if args.execute and not args.approved:
        print("Refusing OpenRouter video API call without --approved", file=sys.stderr)
        return 2

    if args.execute:
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            print("OPENROUTER_API_KEY is required for --execute", file=sys.stderr)
            return 2
        if args.video_url:
            video_url = args.video_url
        else:
            if not video_path:
                print("review assets must include video_path when --video-url is not supplied", file=sys.stderr)
                return 2
            video_url = video_data_url(video_path, args.max_video_bytes, args.allow_large_upload)
        image_urls = [image_data_url(path) for path in frame_paths]

        payload = build_payload(
            args.model,
            prompt,
            video_url,
            image_urls,
            args.max_tokens,
            args.temperature,
            not args.no_structured_output,
            not args.allow_parameter_fallback,
        )
        raw_response = post_openrouter(api_key, payload)
        raw_path = os.path.join(output_dir, "openrouter-video-critique-response.json")
        pathlib.Path(raw_path).write_text(json.dumps(raw_response, indent=2, ensure_ascii=False), encoding="utf-8")
        output_text = extract_output_text(raw_response)
        parsed = parse_jsonish(output_text) or {}
        base_report.update(drop_none(parsed))
        base_report["review_mode"] = base_report.get("review_mode") or review_mode
        base_report["model"] = {
            **base_report.get("model", {}),
            "provider": "openrouter",
            "model_id": args.model,
            "prompt_path": prompt_path,
            "raw_response_path": raw_path,
            "request_id": raw_response.get("id"),
            "notes": f"Executed with OpenRouter chat completions using {review_mode} input.",
        }
        if not parsed.get("status") or base_report.get("status") == "needs_approval":
            base_report["status"] = "reviewed"
        if not parsed.get("qa") or base_report.get("qa", {}).get("status") == "not_run":
            base_report["qa"] = {"status": "partial", "summary": f"OpenRouter {review_mode} model critique returned."}

    merge_required_report_defaults(base_report, defaults)

    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(drop_none(base_report), handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
