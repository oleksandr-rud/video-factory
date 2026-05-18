#!/usr/bin/env python3
"""Convert ElevenLabs character alignment to Remotion Caption[] JSON and SRT."""

from __future__ import annotations

import argparse
import json
import os
from typing import Any


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def pick_alignment(payload: dict[str, Any]) -> dict[str, Any]:
    return payload.get("normalized_alignment") or payload.get("alignment") or payload


def words_from_alignment(payload: dict[str, Any], offset_ms: int = 0) -> list[dict[str, Any]]:
    alignment = pick_alignment(payload)
    chars = alignment.get("characters") or []
    starts = alignment.get("character_start_times_seconds") or []
    ends = alignment.get("character_end_times_seconds") or []
    words: list[dict[str, Any]] = []
    current = ""
    word_start: float | None = None
    word_end: float | None = None

    for char, start, end in zip(chars, starts, ends):
        if str(char).isspace():
            if current:
                words.append({
                    "text": current,
                    "startMs": int(round((word_start or 0) * 1000)) + offset_ms,
                    "endMs": int(round((word_end or end) * 1000)) + offset_ms,
                })
            current = ""
            word_start = None
            word_end = None
            continue

        if word_start is None:
            word_start = float(start)
        current += str(char)
        word_end = float(end)

    if current:
        words.append({
            "text": current,
            "startMs": int(round((word_start or 0) * 1000)) + offset_ms,
            "endMs": int(round((word_end or word_start or 0) * 1000)) + offset_ms,
        })

    return words


def group_captions(words: list[dict[str, Any]], max_words: int, max_gap_ms: int) -> list[dict[str, Any]]:
    captions: list[dict[str, Any]] = []
    chunk: list[dict[str, Any]] = []

    def flush() -> None:
        if not chunk:
            return
        captions.append({
            "text": " ".join(word["text"] for word in chunk),
            "startMs": chunk[0]["startMs"],
            "endMs": chunk[-1]["endMs"],
            "timestampMs": chunk[0]["startMs"],
            "confidence": None,
        })
        chunk.clear()

    for word in words:
        gap = word["startMs"] - chunk[-1]["endMs"] if chunk else 0
        if chunk and (len(chunk) >= max_words or gap > max_gap_ms):
            flush()
        chunk.append(word)
    flush()
    return captions


def srt_timestamp(ms: int) -> str:
    seconds, milli = divmod(ms, 1000)
    minutes, sec = divmod(seconds, 60)
    hours, minute = divmod(minutes, 60)
    return f"{hours:02d}:{minute:02d}:{sec:02d},{milli:03d}"


def write_srt(captions: list[dict[str, Any]], path: str) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        for index, caption in enumerate(captions, start=1):
            handle.write(f"{index}\n")
            handle.write(f"{srt_timestamp(caption['startMs'])} --> {srt_timestamp(caption['endMs'])}\n")
            handle.write(f"{caption['text']}\n\n")


def scenario_offsets(path: str | None) -> dict[str, int]:
    if not path:
        return {}
    scenario = load_json(path)
    offsets = {}
    for scene in scenario.get("scenes", []):
        if scene.get("scene_id") and "start_seconds" in scene:
            offsets[scene["scene_id"]] = int(round(float(scene["start_seconds"]) * 1000))
    return offsets


def captions_from_package(path: str, scenario_path: str | None, max_words: int, max_gap_ms: int) -> list[dict[str, Any]]:
    package = load_json(path)
    offsets = scenario_offsets(scenario_path)
    captions: list[dict[str, Any]] = []
    cumulative_offset = 0
    for scene in package.get("scenes", []):
        alignment_path = scene.get("alignment_path")
        if not alignment_path:
            continue
        payload = load_json(alignment_path)
        offset = offsets.get(scene["scene_id"], cumulative_offset)
        words = words_from_alignment(payload, offset)
        captions.extend(group_captions(words, max_words, max_gap_ms))
        if words:
            cumulative_offset = max(cumulative_offset, words[-1]["endMs"])
    captions.sort(key=lambda item: item["startMs"])
    return captions


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--alignment")
    parser.add_argument("--voiceover-package")
    parser.add_argument("--scenario")
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-srt")
    parser.add_argument("--max-words", type=int, default=6)
    parser.add_argument("--max-gap-ms", type=int, default=600)
    args = parser.parse_args()

    if args.voiceover_package:
        captions = captions_from_package(args.voiceover_package, args.scenario, args.max_words, args.max_gap_ms)
    elif args.alignment:
        captions = group_captions(words_from_alignment(load_json(args.alignment)), args.max_words, args.max_gap_ms)
    else:
        raise SystemExit("Provide --alignment or --voiceover-package")

    os.makedirs(os.path.dirname(os.path.abspath(args.output_json)), exist_ok=True)
    with open(args.output_json, "w", encoding="utf-8") as handle:
        json.dump(captions, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    if args.output_srt:
        os.makedirs(os.path.dirname(os.path.abspath(args.output_srt)), exist_ok=True)
        write_srt(captions, args.output_srt)

    print(f"wrote {len(captions)} captions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
