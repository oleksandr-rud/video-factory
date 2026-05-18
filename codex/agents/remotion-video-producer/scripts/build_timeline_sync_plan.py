#!/usr/bin/env python3
"""Build a scene-level timeline sync plan from scenario, voiceover, and visuals."""

from __future__ import annotations

import argparse
import json
import os
from typing import Any


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


def normalize_candidates(payload: Any) -> list[dict[str, Any]]:
    if payload is None:
        return []
    if isinstance(payload, list):
        return payload
    if "candidates" in payload:
        return payload["candidates"]
    if "candidate_id" in payload:
        return [payload]
    return []


def best_candidate(scene_id: str, candidates: list[dict[str, Any]]) -> dict[str, Any] | None:
    scene_candidates = [item for item in candidates if item.get("scene_id") == scene_id]
    if not scene_candidates:
        return None
    status_rank = {"approved": 4, "generated": 3, "downloaded": 3, "proposed": 2, "needs_approval": 1}

    def score(item: dict[str, Any]) -> tuple[int, float]:
        total = ((item.get("scores") or {}).get("total") or 0)
        return status_rank.get(item.get("status"), 0), float(total)

    return sorted(scene_candidates, key=score, reverse=True)[0]


def pack_by_scene(visual_pack: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not visual_pack:
        return {}
    return {item.get("scene_id"): item for item in visual_pack.get("scene_packs", []) if item.get("scene_id")}


def voice_by_scene(voiceover: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not voiceover:
        return {}
    return {item.get("scene_id"): item for item in voiceover.get("scenes", []) if item.get("scene_id")}


def make_visual_source(scene_id: str, candidate: dict[str, Any] | None, pack: dict[str, Any] | None) -> dict[str, Any]:
    if candidate:
        return drop_none({
            "candidate_id": candidate.get("candidate_id"),
            "route": candidate.get("route") or "unassigned",
            "local_path": candidate.get("local_path"),
            "remotion_clip_package_path": candidate.get("remotion_clip_package_path"),
            "ai_video_generation_package_path": candidate.get("ai_video_generation_package_path"),
            "notes": f"status={candidate.get('status')}",
        })
    routes = (pack or {}).get("routes") or []
    return {
        "route": routes[0] if routes else "unassigned",
        "notes": "No approved/generated clip candidate selected.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--voiceover-package")
    parser.add_argument("--visual-pack")
    parser.add_argument("--clip-candidates")
    parser.add_argument("--output", required=True)
    parser.add_argument("--fps", type=float, default=30)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1920)
    args = parser.parse_args()

    scenario = load_json(args.scenario)
    voiceover = load_json(args.voiceover_package)
    visual_pack = load_json(args.visual_pack)
    candidates = normalize_candidates(load_json(args.clip_candidates))
    packs = pack_by_scene(visual_pack)
    voice = voice_by_scene(voiceover)
    findings: list[dict[str, Any]] = []
    scenes = []

    for scene in scenario.get("scenes", []):
        scene_id = scene["scene_id"]
        original_start = float(scene.get("start_seconds", 0))
        original_end = float(scene.get("end_seconds", original_start))
        voice_scene = voice.get(scene_id, {})
        duration = voice_scene.get("duration_seconds")
        start_seconds = original_start
        end_seconds = original_end
        if duration:
            end_seconds = start_seconds + float(duration)
            drift = abs(end_seconds - original_end)
            if drift > 0.5:
                findings.append({
                    "severity": "major" if drift > 2 else "minor",
                    "scene_id": scene_id,
                    "timestamp_seconds": start_seconds,
                    "description": f"Voiceover duration shifts scenario end by {drift:.2f}s.",
                    "fix_status": "review_timeline",
                })

        candidate = best_candidate(scene_id, candidates)
        pack = packs.get(scene_id)
        visual_source = make_visual_source(scene_id, candidate, pack)
        if visual_source.get("route") == "unassigned":
            findings.append({
                "severity": "major",
                "scene_id": scene_id,
                "timestamp_seconds": start_seconds,
                "description": "No visual candidate or route assigned.",
                "fix_status": "needs_visual_selection",
            })

        if not voice_scene.get("audio_path"):
            findings.append({
                "severity": "minor",
                "scene_id": scene_id,
                "timestamp_seconds": start_seconds,
                "description": "No generated voiceover path attached.",
                "fix_status": "needs_tts_or_manual_audio",
            })

        captions = {
            "caption_json_path": voice_scene.get("caption_json_path") or (voiceover or {}).get("captions", {}).get("caption_json_path"),
            "srt_path": voice_scene.get("srt_path") or (voiceover or {}).get("captions", {}).get("srt_path"),
            "start_ms": int(round(start_seconds * 1000)),
            "end_ms": int(round(end_seconds * 1000)),
            "safe_area_notes": "Keep clear of lower thirds, logos, UI details, and CTA.",
        }
        if not captions.get("caption_json_path"):
            findings.append({
                "severity": "minor",
                "scene_id": scene_id,
                "timestamp_seconds": start_seconds,
                "description": "No caption JSON path attached.",
                "fix_status": "needs_caption_generation",
            })

        scenes.append({
            "scene_id": scene_id,
            "start_seconds": start_seconds,
            "end_seconds": end_seconds,
            "start_frame": int(round(start_seconds * args.fps)),
            "end_frame": int(round(end_seconds * args.fps)),
            "narration_text": voice_scene.get("text") or scene.get("script", ""),
            "onscreen_text": scene.get("onscreen_text"),
            "visual_source": visual_source,
            "audio": {
                "voiceover_path": voice_scene.get("audio_path"),
                "start_seconds": start_seconds,
                "end_seconds": end_seconds,
                "duration_seconds": duration or (end_seconds - start_seconds),
                "duck_music": True,
            },
            "captions": captions,
            "overlay_notes": scene.get("format_notes"),
            "sync_notes": "Built from scenario timing, voiceover package, and selected visual candidates.",
        })

    duration_seconds = max((scene["end_seconds"] for scene in scenes), default=0)
    status = "pass" if not findings else ("fail" if any(f["severity"] == "blocker" for f in findings) else "partial")
    output = drop_none({
        "timeline_sync_id": f"{scenario.get('scenario_id', 'scenario')}-timeline-sync",
        "scenario_id": scenario.get("scenario_id"),
        "voiceover_id": (voiceover or {}).get("voiceover_id"),
        "scene_visual_pack_id": (visual_pack or {}).get("scene_visual_pack_id"),
        "fps": args.fps,
        "width": args.width,
        "height": args.height,
        "duration_seconds": duration_seconds,
        "scenes": scenes,
        "qa": {
            "status": status,
            "summary": "Timeline sync plan built." if status == "pass" else "Timeline sync plan built with gaps to resolve.",
            "findings": findings,
        },
    })

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print(f"wrote {args.output} with {len(findings)} findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
