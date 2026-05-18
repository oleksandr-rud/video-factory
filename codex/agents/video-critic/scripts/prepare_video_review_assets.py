#!/usr/bin/env python3
"""Extract frame samples and metadata for independent video critique."""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
from typing import Any


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


def run_json(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def probe_video(video_path: str) -> tuple[dict[str, Any], list[str]]:
    notes: list[str] = []
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return {}, ["ffprobe not found; metadata unavailable."]
    try:
        payload = run_json([
            ffprobe,
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_streams",
            "-show_format",
            video_path,
        ])
    except Exception as exc:  # noqa: BLE001 - report tool failure to artifact.
        return {}, [f"ffprobe failed: {exc}"]

    video_stream = next((stream for stream in payload.get("streams", []) if stream.get("codec_type") == "video"), {})
    audio_stream = next((stream for stream in payload.get("streams", []) if stream.get("codec_type") == "audio"), {})
    duration = payload.get("format", {}).get("duration") or video_stream.get("duration")

    metadata = {
        "duration_seconds": float(duration) if duration is not None else None,
        "width": video_stream.get("width"),
        "height": video_stream.get("height"),
        "r_frame_rate": video_stream.get("r_frame_rate"),
        "video_codec": video_stream.get("codec_name"),
        "audio_codec": audio_stream.get("codec_name"),
        "has_audio": bool(audio_stream),
        "format_name": payload.get("format", {}).get("format_name"),
        "size_bytes": int(payload.get("format", {}).get("size", 0)) if payload.get("format", {}).get("size") else None,
    }
    return drop_none(metadata), notes


def timeline_timestamps(timeline: dict[str, Any] | None, max_frames: int) -> list[dict[str, Any]]:
    if not timeline:
        return []
    samples: list[dict[str, Any]] = []
    for scene in timeline.get("scenes", []):
        start = float(scene.get("start_seconds", 0))
        end = float(scene.get("end_seconds", start))
        if end <= start:
            continue
        points = [
            (start + min(0.35, max((end - start) * 0.2, 0)), "scene_start"),
            ((start + end) / 2, "scene_mid"),
        ]
        if end - start > 2:
            points.append((max(start, end - 0.35), "scene_end"))
        for timestamp, reason in points:
            samples.append({
                "timestamp_seconds": round(timestamp, 3),
                "scene_id": scene.get("scene_id"),
                "reason": reason,
            })
    return evenly_limit(samples, max_frames)


def evenly_limit(samples: list[dict[str, Any]], max_frames: int) -> list[dict[str, Any]]:
    if len(samples) <= max_frames:
        return samples
    step = (len(samples) - 1) / max(max_frames - 1, 1)
    picked = []
    seen = set()
    for index in range(max_frames):
        source_index = round(index * step)
        if source_index in seen:
            continue
        seen.add(source_index)
        picked.append(samples[source_index])
    return picked


def even_timestamps(duration: float | None, max_frames: int) -> list[dict[str, Any]]:
    if not duration or duration <= 0:
        return [{"timestamp_seconds": 0, "reason": "fallback"}]
    count = max(1, max_frames)
    if count == 1:
        return [{"timestamp_seconds": round(duration / 2, 3), "reason": "even_sample"}]
    start = min(0.5, duration / 4)
    end = max(start, duration - min(0.5, duration / 4))
    return [
        {
            "timestamp_seconds": round(start + ((end - start) * index / (count - 1)), 3),
            "reason": "even_sample",
        }
        for index in range(count)
    ]


def extract_frames(video_path: str, samples: list[dict[str, Any]], frames_dir: str) -> tuple[list[dict[str, Any]], list[str]]:
    notes: list[str] = []
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return [], ["ffmpeg not found; frame extraction unavailable."]

    os.makedirs(frames_dir, exist_ok=True)
    extracted = []
    for index, sample in enumerate(samples, start=1):
        frame_name = f"frame-{index:03d}-{sample['timestamp_seconds']:.3f}s.jpg".replace(".", "_", 1)
        frame_path = os.path.join(frames_dir, frame_name)
        command = [
            ffmpeg,
            "-y",
            "-ss",
            str(sample["timestamp_seconds"]),
            "-i",
            video_path,
            "-frames:v",
            "1",
            "-q:v",
            "2",
            frame_path,
        ]
        completed = subprocess.run(command, capture_output=True, text=True)
        if completed.returncode != 0:
            notes.append(f"ffmpeg failed at {sample['timestamp_seconds']}s: {completed.stderr[-300:]}")
            continue
        extracted.append({
            **sample,
            "frame_path": frame_path,
        })
    return extracted, notes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--render-package")
    parser.add_argument("--scenario")
    parser.add_argument("--timeline-sync-plan")
    parser.add_argument("--voiceover-package")
    parser.add_argument("--caption-path")
    parser.add_argument("--reference-analysis")
    parser.add_argument("--channel-format")
    parser.add_argument("--producer-criteria")
    parser.add_argument("--previous-critique")
    parser.add_argument("--max-frames", type=int, default=24)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    metadata, notes = probe_video(args.video)
    timeline = load_json(args.timeline_sync_plan)
    samples = timeline_timestamps(timeline, args.max_frames)
    if not samples:
        samples = even_timestamps(metadata.get("duration_seconds"), args.max_frames)

    frames_dir = os.path.join(args.output_dir, "frames")
    frame_samples, frame_notes = extract_frames(args.video, samples, frames_dir)
    notes.extend(frame_notes)

    review_assets = drop_none({
        "video_path": args.video,
        "status": "prepared" if frame_samples else "partial",
        "metadata": metadata,
        "frame_samples": frame_samples,
        "artifacts": {
            "render_package_path": args.render_package,
            "scenario_path": args.scenario,
            "timeline_sync_plan_path": args.timeline_sync_plan,
            "voiceover_package_path": args.voiceover_package,
            "caption_path": args.caption_path,
            "reference_analysis_path": args.reference_analysis,
            "channel_format_path": args.channel_format,
            "producer_criteria_path": args.producer_criteria,
            "previous_critique_path": args.previous_critique,
        },
        "limitations": notes,
    })

    output_path = os.path.join(args.output_dir, "review-assets.json")
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(review_assets, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
