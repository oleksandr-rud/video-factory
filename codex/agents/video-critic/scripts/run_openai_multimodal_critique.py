#!/usr/bin/env python3
"""Run or prepare an OpenAI Responses API multimodal video critique."""

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


RESPONSES_URL = "https://api.openai.com/v1/responses"
DEFAULT_MODEL = os.environ.get("OPENAI_VISION_MODEL", "gpt-5.2")


def load_json(path: str | None) -> Any:
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as handle:
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
    text = pathlib.Path(path).read_text(encoding="utf-8", errors="replace")
    return text[:limit]


def load_text_or_json(path: str | None, limit: int = 16000) -> Any:
    if not path or not os.path.exists(path):
        return None
    try:
        return load_json(path)
    except json.JSONDecodeError:
        return read_text(path, limit)


def image_data_url(path: str) -> str:
    suffix = pathlib.Path(path).suffix.lower().lstrip(".") or "jpeg"
    mime = "jpeg" if suffix in {"jpg", "jpeg"} else suffix
    data = pathlib.Path(path).read_bytes()
    encoded = base64.b64encode(data).decode("ascii")
    return f"data:image/{mime};base64,{encoded}"


def extract_output_text(response: dict[str, Any]) -> str:
    texts: list[str] = []
    if response.get("output_text"):
        return str(response["output_text"])
    for item in response.get("output", []):
        for content in item.get("content", []):
            if "text" in content:
                texts.append(str(content["text"]))
    return "\n".join(texts)


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


def build_prompt(review_assets: dict[str, Any], artifacts: dict[str, Any], max_frames: int) -> str:
    frame_lines = []
    for sample in review_assets.get("frame_samples", [])[:max_frames]:
        frame_lines.append(
            f"- {sample.get('timestamp_seconds')}s"
            f" scene={sample.get('scene_id', 'unknown')}"
            f" reason={sample.get('reason', 'sample')}"
            f" file={sample.get('frame_path')}"
        )

    artifact_text = json.dumps(artifacts, indent=2, ensure_ascii=False)
    return f"""You are an independent senior video critic for a production pipeline.

Review the rendered video using sampled frames plus artifact text. Be direct and evidence-based.

Return JSON only. Follow this shape:
{{
  "status": "reviewed|needs_revision|blocked|approved",
  "review_mode": "multimodal_frames|hybrid",
  "video_observations": [{{"timestamp_seconds": 0, "scene_id": "scene-01", "observation": "..."}}],
  "scores": {{"story_clarity": 0-10, "hook_strength": 0-10, "pacing": 0-10, "visual_quality": 0-10, "visual_relevance": 0-10, "audio_quality": 0-10, "subtitle_sync": 0-10, "brand_fit": 0-10, "platform_fit": 0-10, "factual_alignment": 0-10, "originality": 0-10, "accessibility": 0-10, "overall": 0-10}},
  "findings": [{{"severity": "blocker|major|minor|note", "category": "story|hook|pacing|visual|audio|subtitles|sync|brand|platform|factual|rights|technical|accessibility|engagement|redundancy|other", "scene_id": "scene-01", "timestamp_seconds": 0, "evidence": "...", "description": "...", "recommendation": "...", "owner_agent": "..."}}],
  "scene_reviews": [{{"scene_id": "scene-01", "status": "pass|fail|partial|unknown|waived", "summary": "...", "criteria_results": [{{"criterion": "...", "status": "pass|fail|waived|not_applicable|unknown", "evidence": "...", "recommendation": "..."}}]}}],
  "revision_plan": [{{"priority": 1, "owner_agent": "...", "affected_artifacts": ["..."], "action": "...", "expected_impact": "...", "requires_user_approval": false}}],
  "gate_decision": {{"status": "pass|fail|needs_approval|blocked", "release_candidate": false, "stop_reason": "...", "failed_gates": ["..."], "waived_gates": ["..."], "next_action": "approve_rc|revise_and_rerender|ask_user|stop_blocked"}},
  "limitations": ["..."],
  "qa": {{"status": "pass|fail|partial|not_run", "summary": "...", "residual_risks": ["..."]}}
}}

Critique dimensions:
- hook, story clarity, payoff, source alignment
- visual relevance, frame quality, continuity, artifacts, safe areas
- voice, music, SFX, audio clarity
- subtitle accuracy, sync, readability, mobile fit
- brand/channel fit, novelty, redundancy risk
- platform fit, duration, aspect ratio, CTA, delivery readiness
- factual, rights, likeness, watermark, and accessibility risks

Gate discipline:
- Evaluate every scene id in the scenario or timeline sync plan.
- Treat the producer criteria as binding. Mark each required rule pass, fail, waived, not_applicable, or unknown.
- A release candidate can pass only when hard gates pass or are explicitly waived.
- Missing evidence for a hard gate is unknown or fail, not pass.

Frame samples:
{chr(10).join(frame_lines)}

Artifacts:
{artifact_text}
"""


def post_response(api_key: str, model: str, prompt: str, image_paths: list[str]) -> dict[str, Any]:
    content: list[dict[str, Any]] = [{"type": "input_text", "text": prompt}]
    for path in image_paths:
        content.append({"type": "input_image", "image_url": image_data_url(path)})
    payload = {
        "model": model,
        "input": [{"role": "user", "content": content}],
    }
    request = urllib.request.Request(
        RESPONSES_URL,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload).encode("utf-8"),
    )
    with urllib.request.urlopen(request, timeout=240) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review-assets", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--max-frames", type=int, default=24)
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
    prompt = build_prompt(review_assets, drop_none(artifacts), args.max_frames)
    output_dir = os.path.dirname(os.path.abspath(args.output))
    os.makedirs(output_dir, exist_ok=True)
    prompt_path = os.path.join(output_dir, "multimodal-critique-prompt.txt")
    pathlib.Path(prompt_path).write_text(prompt, encoding="utf-8")

    scenario = artifacts.get("scenario") or {}
    render = artifacts.get("render_package") or {}
    base_report: dict[str, Any] = {
        "critique_id": f"{render.get('render_id', 'render')}-critique",
        "render_id": render.get("render_id", "unknown"),
        "scenario_id": render.get("scenario_id") or scenario.get("scenario_id") or "unknown",
        "review_loop_id": args.review_loop_id,
        "review_iteration": args.review_iteration,
        "previous_critique_id": args.previous_critique_id,
        "status": "needs_approval",
        "review_mode": "multimodal_frames" if review_assets.get("frame_samples") else "artifact_only",
        "model": {
            "provider": "openai",
            "model_id": args.model,
            "prompt_path": prompt_path,
            "notes": "Dry-run prompt prepared; no API call made.",
        },
        "inputs": {
            "video_path": review_assets.get("video_path"),
            "review_assets_path": args.review_assets,
            **artifact_paths,
        },
        "producer_criteria": {
            "criteria_prompt_path": artifact_paths.get("producer_criteria_path"),
        },
        "scores": {"overall": 0},
        "findings": [],
        "scene_reviews": [],
        "revision_plan": [],
        "gate_decision": {
            "status": "needs_approval",
            "release_candidate": False,
            "next_action": "ask_user",
            "stop_reason": "Multimodal critique requires approval before gate decision.",
        },
        "limitations": review_assets.get("limitations", []),
        "qa": {
            "status": "not_run",
            "summary": "Multimodal critique prepared but not executed.",
        },
    }

    if args.execute and not args.approved:
        print("Refusing multimodal API call without --approved", file=sys.stderr)
        return 2

    if args.execute:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("OPENAI_API_KEY is required for --execute", file=sys.stderr)
            return 2
        image_paths = [
            sample["frame_path"]
            for sample in review_assets.get("frame_samples", [])[: args.max_frames]
            if sample.get("frame_path") and os.path.exists(sample["frame_path"])
        ]
        raw_response = post_response(api_key, args.model, prompt, image_paths)
        raw_path = os.path.join(output_dir, "multimodal-critique-response.json")
        pathlib.Path(raw_path).write_text(json.dumps(raw_response, indent=2, ensure_ascii=False), encoding="utf-8")
        output_text = extract_output_text(raw_response)
        parsed = parse_jsonish(output_text) or {}
        base_report.update(drop_none(parsed))
        base_report["model"] = {
            **base_report.get("model", {}),
            "provider": "openai",
            "model_id": args.model,
            "prompt_path": prompt_path,
            "raw_response_path": raw_path,
            "request_id": raw_response.get("id"),
            "notes": "Executed with sampled frames through Responses API image inputs.",
        }
        if not parsed.get("status") or base_report.get("status") == "needs_approval":
            base_report["status"] = "reviewed"
        if not parsed.get("qa") or base_report.get("qa", {}).get("status") == "not_run":
            base_report["qa"] = {"status": "partial", "summary": "Model critique returned."}

    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(drop_none(base_report), handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
