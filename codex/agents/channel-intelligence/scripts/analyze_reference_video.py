#!/usr/bin/env python3
"""Prepare deterministic reference-video evidence for Channel Intelligence."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


DEFAULT_MAX_SCENES = int(os.environ.get("REFERENCE_ANALYSIS_MAX_SCENES", "24"))
DEFAULT_MAX_FRAMES = int(os.environ.get("REFERENCE_ANALYSIS_MAX_FRAMES", "72"))
DEFAULT_FRAMES_PER_SCENE = int(os.environ.get("REFERENCE_ANALYSIS_FRAMES_PER_SCENE", "3"))
DEFAULT_FALLBACK_SEGMENT_SECONDS = float(os.environ.get("REFERENCE_ANALYSIS_FALLBACK_SEGMENT_SECONDS", "8"))


def env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def slugify(value: str, fallback: str = "item") -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip()).strip("-").lower()
    return slug or fallback


def drop_none(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: drop_none(item) for key, item in value.items() if item is not None}
    if isinstance(value, list):
        return [drop_none(item) for item in value if item is not None]
    return value


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(drop_none(data), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def relpath(path: Path | str | None, repo_root: Path) -> str | None:
    if not path:
        return None
    item = Path(path)
    try:
        resolved = item.resolve()
    except OSError:
        return item.as_posix()
    try:
        return resolved.relative_to(repo_root).as_posix()
    except ValueError:
        return str(resolved)


def path_is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def run_json(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def fraction_to_float(value: Any) -> float | None:
    if value in (None, "", "0/0"):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value)
    if "/" in text:
        numerator, denominator = text.split("/", 1)
        try:
            den = float(denominator)
            if den == 0:
                return None
            return float(numerator) / den
        except ValueError:
            return None
    try:
        return float(text)
    except ValueError:
        return None


def probe_video(video_path: Path, work_dir: Path, repo_root: Path) -> tuple[dict[str, Any], str | None, list[str]]:
    notes: list[str] = []
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return {}, None, ["ffprobe not found; metadata unavailable."]
    try:
        payload = run_json([
            ffprobe,
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_streams",
            "-show_format",
            str(video_path),
        ])
    except Exception as exc:  # noqa: BLE001 - CLI artifact should preserve tool failure.
        return {}, None, [f"ffprobe failed: {exc}"]

    probe_path = work_dir / "probe.json"
    write_json(probe_path, payload)

    video_stream = next((stream for stream in payload.get("streams", []) if stream.get("codec_type") == "video"), {})
    audio_stream = next((stream for stream in payload.get("streams", []) if stream.get("codec_type") == "audio"), {})
    duration = payload.get("format", {}).get("duration") or video_stream.get("duration")
    size = payload.get("format", {}).get("size")
    metadata = {
        "duration_seconds": float(duration) if duration is not None else None,
        "width": video_stream.get("width"),
        "height": video_stream.get("height"),
        "fps": fraction_to_float(video_stream.get("avg_frame_rate") or video_stream.get("r_frame_rate")),
        "r_frame_rate": video_stream.get("r_frame_rate"),
        "video_codec": video_stream.get("codec_name"),
        "audio_codec": audio_stream.get("codec_name"),
        "has_audio": bool(audio_stream),
        "format_name": payload.get("format", {}).get("format_name"),
        "size_bytes": int(size) if size else None,
        "probe_path": relpath(probe_path, repo_root),
    }
    return drop_none(metadata), relpath(probe_path, repo_root), notes


def detect_scenes(video_path: Path, duration: float | None, max_scenes: int, fallback_segment_seconds: float) -> tuple[list[dict[str, Any]], list[str]]:
    notes: list[str] = []
    try:
        from scenedetect import SceneManager, open_video  # type: ignore
        from scenedetect.detectors import ContentDetector  # type: ignore

        video = open_video(str(video_path))
        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector())
        scene_manager.detect_scenes(video)
        scene_list = scene_manager.get_scene_list()
        scenes = []
        for index, (start, end) in enumerate(scene_list[:max_scenes], start=1):
            start_seconds = round(float(start.get_seconds()), 3)
            end_seconds = round(float(end.get_seconds()), 3)
            if end_seconds <= start_seconds:
                continue
            scenes.append({
                "scene_index": index,
                "start_seconds": start_seconds,
                "end_seconds": end_seconds,
                "detection_method": "pyscenedetect_content",
            })
        if scenes:
            if len(scene_list) > max_scenes:
                notes.append(f"PySceneDetect found {len(scene_list)} scenes; limited to {max_scenes}.")
            return scenes, notes
        notes.append("PySceneDetect returned no scenes; using fallback segments.")
    except Exception as exc:  # noqa: BLE001 - optional dependency should degrade gracefully.
        notes.append(f"PySceneDetect unavailable or failed: {exc}; using fallback segments.")

    if not duration or duration <= 0:
        return [{
            "scene_index": 1,
            "start_seconds": 0,
            "end_seconds": 0,
            "detection_method": "fallback_unknown_duration",
        }], notes

    segment = max(1.0, fallback_segment_seconds)
    count = max(1, min(max_scenes, math.ceil(duration / segment)))
    scenes = []
    for index in range(count):
        start = round(index * duration / count, 3)
        end = round((index + 1) * duration / count, 3)
        scenes.append({
            "scene_index": index + 1,
            "start_seconds": start,
            "end_seconds": end,
            "detection_method": "fallback_even_segments",
        })
    return scenes, notes


def sample_points(scenes: list[dict[str, Any]], frames_per_scene: int, max_frames: int) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    for scene in scenes:
        start = float(scene.get("start_seconds", 0))
        end = float(scene.get("end_seconds", start))
        if end <= start:
            points = [(start, "point")]
        elif frames_per_scene <= 1:
            points = [((start + end) / 2, "mid")]
        elif frames_per_scene == 2:
            offset = min(0.35, max((end - start) * 0.2, 0))
            points = [(start + offset, "start"), ((start + end) / 2, "mid")]
        else:
            offset = min(0.35, max((end - start) * 0.2, 0))
            points = [(start + offset, "start"), ((start + end) / 2, "mid"), (max(start, end - offset), "end")]
        for timestamp, reason in points:
            samples.append({
                "scene_index": scene["scene_index"],
                "timestamp_seconds": round(max(0, timestamp), 3),
                "reason": reason,
            })
    if len(samples) <= max_frames:
        return samples
    step = (len(samples) - 1) / max(max_frames - 1, 1)
    picked: list[dict[str, Any]] = []
    seen: set[int] = set()
    for index in range(max_frames):
        source_index = round(index * step)
        if source_index in seen:
            continue
        seen.add(source_index)
        picked.append(samples[source_index])
    return picked


def extract_frames(video_path: Path, samples: list[dict[str, Any]], frames_dir: Path, repo_root: Path, source_id: str) -> tuple[list[dict[str, Any]], list[str]]:
    notes: list[str] = []
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return [], ["ffmpeg not found; keyframe extraction unavailable."]
    frames_dir.mkdir(parents=True, exist_ok=True)
    extracted = []
    for index, sample in enumerate(samples, start=1):
        timestamp_ms = int(round(float(sample["timestamp_seconds"]) * 1000))
        filename = (
            f"{slugify(source_id)}-scene-{int(sample['scene_index']):03d}-"
            f"{sample['reason']}-{timestamp_ms}ms.jpg"
        )
        frame_path = frames_dir / filename
        command = [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            str(sample["timestamp_seconds"]),
            "-i",
            str(video_path),
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(frame_path),
        ]
        completed = subprocess.run(command, capture_output=True, text=True)
        if completed.returncode != 0:
            notes.append(f"ffmpeg failed at {sample['timestamp_seconds']}s: {completed.stderr[-300:]}")
            continue
        extracted.append({
            **sample,
            "frame_index": index,
            "frame_path": relpath(frame_path, repo_root),
        })
    return extracted, notes


def run_ocr(frame_samples: list[dict[str, Any]], repo_root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    notes: list[str] = []
    tesseract = shutil.which("tesseract")
    if not tesseract:
        return [], ["tesseract not found; OCR unavailable."]
    ocr_results = []
    for sample in frame_samples:
        frame_path_value = sample.get("frame_path")
        if not frame_path_value:
            continue
        frame_path = Path(frame_path_value)
        if not frame_path.is_absolute():
            frame_path = repo_root / frame_path
        completed = subprocess.run(
            [tesseract, str(frame_path), "stdout", "--psm", "6"],
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            notes.append(f"tesseract failed for {sample.get('frame_path')}: {completed.stderr[-200:]}")
            continue
        text = completed.stdout.strip()
        if text:
            ocr_results.append({
                "frame_path": sample.get("frame_path"),
                "scene_index": sample.get("scene_index"),
                "timestamp_seconds": sample.get("timestamp_seconds"),
                "text": text,
            })
    return ocr_results, notes


def group_frames_by_scene(frame_samples: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    grouped: dict[int, list[dict[str, Any]]] = {}
    for sample in frame_samples:
        grouped.setdefault(int(sample.get("scene_index", 0)), []).append(sample)
    return grouped


def build_evidence_refs(
    source_id: str,
    frame_samples: list[dict[str, Any]],
    ocr_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    evidence = []
    for sample in frame_samples:
        evidence.append({
            "evidence_id": f"ev-{slugify(source_id)}-frame-{int(sample['frame_index']):03d}",
            "source_id": source_id,
            "description": f"Reference keyframe at {sample['timestamp_seconds']}s.",
            "timestamp_seconds": sample.get("timestamp_seconds"),
            "path_or_url": sample.get("frame_path"),
            "confidence": "high",
        })
    for index, item in enumerate(ocr_results, start=1):
        evidence.append({
            "evidence_id": f"ev-{slugify(source_id)}-ocr-{index:03d}",
            "source_id": source_id,
            "description": "OCR text detected in reference keyframe.",
            "timestamp_seconds": item.get("timestamp_seconds"),
            "path_or_url": item.get("frame_path"),
            "confidence": "medium",
        })
    return evidence


def build_beats(
    source_id: str,
    scenes: list[dict[str, Any]],
    frame_samples: list[dict[str, Any]],
    ocr_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    frames_by_scene = group_frames_by_scene(frame_samples)
    ocr_by_scene: dict[int, list[dict[str, Any]]] = {}
    for item in ocr_results:
        ocr_by_scene.setdefault(int(item.get("scene_index", 0)), []).append(item)

    beats = []
    for scene in scenes:
        scene_index = int(scene["scene_index"])
        frames = frames_by_scene.get(scene_index, [])
        ocr_items = ocr_by_scene.get(scene_index, [])
        evidence_refs = [
            {
                "evidence_id": f"ev-{slugify(source_id)}-frame-{int(frame['frame_index']):03d}",
                "description": f"Keyframe sample for segment {scene_index}.",
                "timestamp_seconds": frame.get("timestamp_seconds"),
                "path_or_url": frame.get("frame_path"),
                "confidence": "high",
            }
            for frame in frames
        ]
        evidence_refs.extend(
            {
                "evidence_id": f"ev-{slugify(source_id)}-ocr-{index:03d}",
                "description": "OCR text detected in this segment.",
                "timestamp_seconds": item.get("timestamp_seconds"),
                "path_or_url": item.get("frame_path"),
                "confidence": "medium",
            }
            for index, item in enumerate(ocr_items, start=1)
        )
        ocr_preview = "; ".join(item.get("text", "").replace("\n", " ")[:120] for item in ocr_items[:3])
        beats.append(drop_none({
            "beat_id": f"beat-{slugify(source_id)}-{scene_index:03d}",
            "start_seconds": scene.get("start_seconds"),
            "end_seconds": scene.get("end_seconds"),
            "purpose": "Reference segment prepared for interpretation.",
            "shot_size": "unknown",
            "camera_motion": "unknown",
            "visual_notes": "Deterministic keyframes captured; shot grammar requires human or model interpretation.",
            "audio_notes": "Audio pattern requires transcript, waveform, or model/audio review.",
            "caption_or_graphics_notes": f"OCR detected: {ocr_preview}" if ocr_preview else "No OCR text captured for this segment.",
            "pattern_tags": [scene.get("detection_method", "unknown_detection")],
            "keyframe_paths": [frame.get("frame_path") for frame in frames if frame.get("frame_path")],
            "evidence_refs": evidence_refs,
        }))
    return beats


def load_manifest(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return read_json(path)


def append_manifest_assets(manifest_path: Path, assets: list[dict[str, Any]]) -> list[str]:
    manifest = load_manifest(manifest_path)
    if manifest is None:
        return [f"Media asset manifest not found: {manifest_path}"]
    existing_assets = manifest.get("assets", [])
    if not isinstance(existing_assets, list):
        existing_assets = []
    by_id: dict[str, dict[str, Any]] = {
        item.get("asset_id"): item for item in existing_assets if isinstance(item, dict) and item.get("asset_id")
    }
    for asset in assets:
        by_id[asset["asset_id"]] = {**by_id.get(asset["asset_id"], {}), **drop_none(asset)}
    manifest["assets"] = list(by_id.values())
    manifest.setdefault("qa", {})
    manifest["qa"]["status"] = "partial"
    manifest["qa"]["summary"] = "Reference analysis artifacts were updated; review rights and coverage before final use."
    write_json(manifest_path, manifest)
    return []


def manifest_assets(
    source_id: str,
    video_path: Path,
    repo_root: Path,
    args: argparse.Namespace,
    output_path: Path,
    probe_path: str | None,
    scenes_path: Path,
    frame_samples_path: Path,
    ocr_path: Path | None,
    frame_samples: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    source_slug = slugify(source_id)
    related_contracts = [relpath(output_path, repo_root)]
    assets = [
        {
            "asset_id": f"asset-{source_slug}-reference-video",
            "kind": "reference_video",
            "origin": "reference",
            "status": "loaded" if video_path.exists() else "referenced",
            "canonical_path": relpath(video_path, repo_root),
            "source_url": args.source_url,
            "provider": "user_supplied" if not args.source_url else "web_source",
            "title": args.title,
            "owner": args.owner,
            "rights": {
                "license_summary": args.rights_notes or "Reference analysis only; final reuse rights are not implied.",
                "usage_allowed": None,
                "approval_required": True,
                "attribution_required": None,
                "restrictions": ["Do not copy reference footage directly unless rights are separately approved."],
            },
            "technical": {},
            "related_contract_paths": related_contracts,
        },
        {
            "asset_id": f"asset-{source_slug}-reference-scenes",
            "kind": "metadata",
            "origin": "derived",
            "status": "loaded",
            "canonical_path": relpath(scenes_path, repo_root),
            "derived_from_asset_ids": [f"asset-{source_slug}-reference-video"],
            "related_contract_paths": related_contracts,
        },
        {
            "asset_id": f"asset-{source_slug}-reference-frame-samples",
            "kind": "metadata",
            "origin": "derived",
            "status": "loaded",
            "canonical_path": relpath(frame_samples_path, repo_root),
            "derived_from_asset_ids": [f"asset-{source_slug}-reference-video"],
            "related_contract_paths": related_contracts,
        },
    ]
    if probe_path:
        assets.append({
            "asset_id": f"asset-{source_slug}-reference-probe",
            "kind": "metadata",
            "origin": "derived",
            "status": "loaded",
            "canonical_path": probe_path,
            "derived_from_asset_ids": [f"asset-{source_slug}-reference-video"],
            "related_contract_paths": related_contracts,
        })
    if ocr_path:
        assets.append({
            "asset_id": f"asset-{source_slug}-reference-ocr",
            "kind": "metadata",
            "origin": "derived",
            "status": "loaded",
            "canonical_path": relpath(ocr_path, repo_root),
            "derived_from_asset_ids": [f"asset-{source_slug}-reference-video"],
            "related_contract_paths": related_contracts,
        })
    for sample in frame_samples:
        assets.append({
            "asset_id": f"asset-{source_slug}-frame-{int(sample['frame_index']):03d}",
            "kind": "image",
            "origin": "derived",
            "status": "loaded",
            "canonical_path": sample.get("frame_path"),
            "derived_from_asset_ids": [f"asset-{source_slug}-reference-video"],
            "evidence_refs": [{
                "evidence_id": f"ev-{source_slug}-frame-{int(sample['frame_index']):03d}",
                "description": "Reference keyframe sample.",
                "source_id": source_id,
                "timestamp_seconds": sample.get("timestamp_seconds"),
                "path_or_url": sample.get("frame_path"),
                "confidence": "high",
            }],
            "related_contract_paths": related_contracts,
        })
    return assets


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--work-dir", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--analysis-id")
    parser.add_argument("--video-id")
    parser.add_argument("--source-url")
    parser.add_argument("--title")
    parser.add_argument("--owner")
    parser.add_argument("--rights-notes")
    parser.add_argument("--project-id")
    parser.add_argument("--project-path")
    parser.add_argument("--channel-profile-id")
    parser.add_argument("--channel-slug")
    parser.add_argument("--channel-profile-path")
    parser.add_argument("--media-asset-manifest")
    parser.add_argument("--update-media-asset-manifest", action="store_true")
    parser.add_argument("--transcript-path")
    parser.add_argument("--embedding-index-path")
    parser.add_argument("--model-observation-path")
    parser.add_argument("--max-scenes", type=int, default=DEFAULT_MAX_SCENES)
    parser.add_argument("--max-frames", type=int, default=DEFAULT_MAX_FRAMES)
    parser.add_argument("--frames-per-scene", type=int, default=DEFAULT_FRAMES_PER_SCENE)
    parser.add_argument("--fallback-segment-seconds", type=float, default=DEFAULT_FALLBACK_SEGMENT_SECONDS)
    parser.add_argument("--enable-ocr", action="store_true", default=env_bool("REFERENCE_ANALYSIS_ENABLE_OCR"))
    parser.add_argument("--enable-whisperx", action="store_true", default=env_bool("REFERENCE_ANALYSIS_ENABLE_WHISPERX"))
    parser.add_argument("--enable-clip", action="store_true", default=env_bool("REFERENCE_ANALYSIS_ENABLE_CLIP"))
    parser.add_argument(
        "--enable-direct-video-model",
        action="store_true",
        default=env_bool("REFERENCE_ANALYSIS_ENABLE_DIRECT_VIDEO_MODEL"),
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    video_path = Path(args.video)
    if not video_path.is_absolute():
        video_path = (Path.cwd() / video_path).resolve()
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = (Path.cwd() / output_path).resolve()
    work_dir = Path(args.work_dir)
    if not work_dir.is_absolute():
        work_dir = (Path.cwd() / work_dir).resolve()
    work_dir.mkdir(parents=True, exist_ok=True)

    source_id = args.source_id
    analysis_id = args.analysis_id or f"reference-analysis-{slugify(source_id)}"
    video_id = args.video_id or f"reference-video-{slugify(source_id)}"
    limitations: list[str] = []
    if not path_is_under(output_path, repo_root):
        limitations.append("Output path is outside repo root; durable contract paths should be repo-relative for project artifacts.")
    if not path_is_under(work_dir, repo_root):
        limitations.append("Work directory is outside repo root; durable sidecar paths should be repo-relative for project artifacts.")

    technical, probe_path, probe_notes = probe_video(video_path, work_dir, repo_root)
    limitations.extend(probe_notes)
    duration = technical.get("duration_seconds") if technical else None

    scenes, scene_notes = detect_scenes(video_path, duration, args.max_scenes, args.fallback_segment_seconds)
    limitations.extend(scene_notes)
    scenes_path = work_dir / "scenes.json"
    write_json(scenes_path, {"source_id": source_id, "scenes": scenes})

    samples = sample_points(scenes, max(1, args.frames_per_scene), max(1, args.max_frames))
    frames_dir = work_dir / "keyframes"
    frame_samples, frame_notes = extract_frames(video_path, samples, frames_dir, repo_root, source_id)
    limitations.extend(frame_notes)
    frame_samples_path = work_dir / "frame-samples.json"
    write_json(frame_samples_path, {"source_id": source_id, "frame_samples": frame_samples})

    ocr_results: list[dict[str, Any]] = []
    ocr_path: Path | None = None
    if args.enable_ocr:
        ocr_results, ocr_notes = run_ocr(frame_samples, repo_root)
        limitations.extend(ocr_notes)
        ocr_path = work_dir / "ocr.json"
        write_json(ocr_path, {"source_id": source_id, "ocr_results": ocr_results})
    if args.enable_whisperx and not args.transcript_path:
        limitations.append("WhisperX automation is not wired in this local MVP; pass --transcript-path after running transcription externally.")
    if args.enable_clip and not args.embedding_index_path:
        limitations.append("CLIP embedding extraction is not wired in this local MVP; pass --embedding-index-path after running embedding extraction externally.")
    if args.enable_direct_video_model and not args.model_observation_path:
        limitations.append("Direct-video model analysis is approval-gated and not executed by this local script; pass --model-observation-path after approved capture.")

    evidence_refs = build_evidence_refs(source_id, frame_samples, ocr_results)
    beats = build_beats(source_id, scenes, frame_samples, ocr_results)
    source_slug = slugify(source_id)

    captured_artifacts = [
        {"kind": "metadata", "path": probe_path, "notes": "ffprobe JSON metadata."},
        {"kind": "metadata", "path": relpath(scenes_path, repo_root), "notes": "Scene or fallback segment boundaries."},
        {"kind": "metadata", "path": relpath(frame_samples_path, repo_root), "notes": "Extracted keyframe sample list."},
        {"kind": "image_dir", "path": relpath(frames_dir, repo_root), "notes": "Reference keyframes."},
    ]
    if ocr_path:
        captured_artifacts.append({"kind": "metadata", "path": relpath(ocr_path, repo_root), "notes": "OCR results."})
    if args.transcript_path:
        captured_artifacts.append({"kind": "transcript", "path": relpath(args.transcript_path, repo_root), "notes": "Supplied transcript."})
    if args.model_observation_path:
        captured_artifacts.append({"kind": "model_observation", "path": relpath(args.model_observation_path, repo_root), "notes": "Approved model observation."})
    if args.embedding_index_path:
        captured_artifacts.append({"kind": "embedding_index", "path": relpath(args.embedding_index_path, repo_root), "notes": "Supplied frame embedding index."})

    evidence_gaps = []
    if not args.transcript_path:
        evidence_gaps.append("Transcript not supplied; narrative rhythm and spoken claims need transcript or audio review.")
    if not args.enable_ocr:
        evidence_gaps.append("OCR not requested; on-screen text evidence is limited to keyframe inspection.")
    if not args.model_observation_path:
        evidence_gaps.append("Direct-video model observation not supplied; semantic visual interpretation remains manual/model-deferred.")
    if args.enable_clip and not args.embedding_index_path:
        evidence_gaps.append("CLIP embedding extraction requested but no embedding index was supplied.")
    if not frame_samples:
        evidence_gaps.append("No keyframes were extracted; visual evidence is incomplete.")

    status = "complete" if technical and frame_samples and not limitations else "partial"
    if not video_path.exists() and not args.transcript_path and not args.model_observation_path:
        status = "blocked"

    source_ledger_entry = {
        "source_id": source_id,
        "asset_id": f"asset-{source_slug}-reference-video",
        "kind": "reference_video",
        "path_or_url": args.source_url or relpath(video_path, repo_root),
        "local_path": relpath(video_path, repo_root),
        "title": args.title,
        "owner": args.owner,
        "rights_state": "needs_approval",
        "reusable_scope": "project_only",
        "why_it_matters": "Reference video prepared for pattern analysis; footage reuse rights are not implied.",
        "missing_assets": evidence_gaps,
        "evidence_refs": evidence_refs,
        "confidence": "high" if video_path.exists() else "unknown",
    }
    reference_beats = [
        {
            "beat_id": beat.get("beat_id"),
            "source_id": source_id,
            "video_id": video_id,
            "start_seconds": beat.get("start_seconds"),
            "end_seconds": beat.get("end_seconds"),
            "purpose": beat.get("purpose"),
            "shot_evidence": [{
                "shot_size": beat.get("shot_size"),
                "camera_motion": beat.get("camera_motion"),
                "visual_notes": beat.get("visual_notes"),
                "keyframe_paths": beat.get("keyframe_paths", []),
                "confidence": "medium" if beat.get("keyframe_paths") else "low",
            }],
            "audio_evidence": [{
                "notes": beat.get("audio_notes"),
                "confidence": "low",
            }],
            "caption_or_graphics_evidence": [{
                "notes": beat.get("caption_or_graphics_notes"),
                "confidence": "medium" if "OCR detected:" in str(beat.get("caption_or_graphics_notes")) else "low",
            }],
            "reusable_patterns": beat.get("pattern_tags", []),
            "do_not_copy_risks": ["Reference video is pattern evidence only; do not copy footage or exact edit decisions without rights approval."],
            "keyframe_paths": beat.get("keyframe_paths", []),
            "evidence_refs": beat.get("evidence_refs", []),
            "confidence": "medium" if beat.get("evidence_refs") else "low",
        }
        for beat in beats
    ]
    scene_decomposition = [
        drop_none({
            "decomposition_id": f"decomp-{source_slug}-{index:03d}",
            "source_id": source_id,
            "video_id": video_id,
            "reference_beat_id": beat.get("beat_id"),
            "start_seconds": beat.get("start_seconds"),
            "end_seconds": beat.get("end_seconds"),
            "purpose": beat.get("purpose"),
            "visual_summary": beat.get("visual_notes"),
            "audio_summary": beat.get("audio_notes"),
            "caption_or_graphics_summary": beat.get("caption_or_graphics_notes"),
            "transcript_summary": "Transcript not supplied." if not args.transcript_path else "Transcript artifact supplied for downstream review.",
            "keyframe_paths": beat.get("keyframe_paths", []),
            "reference_asset_ids": [
                f"asset-{source_slug}-reference-video",
                *[
                    f"asset-{source_slug}-frame-{int(frame.get('frame_index')):03d}"
                    for frame in frame_samples
                    if int(frame.get("scene_index", 0)) == index and frame.get("frame_index")
                ],
            ],
            "reusable_patterns": beat.get("pattern_tags", []),
            "do_not_copy_risks": [
                "Reference video is pattern evidence only; do not copy footage or exact edit decisions without rights approval."
            ],
            "evidence_refs": beat.get("evidence_refs", []),
            "model_limitations": [
                "No approved direct-video model observation supplied."
            ] if not args.model_observation_path else [],
            "confidence": "medium" if beat.get("evidence_refs") else "low",
        })
        for index, beat in enumerate(beats, start=1)
    ]
    invalidation_impact = []
    if evidence_gaps:
        invalidation_impact.append({
            "impact_id": f"impact-{source_slug}-evidence-gaps",
            "change_or_gap": "reference_video_evidence_partial",
            "affected_artifacts": ["channel_format", "scenario", "visual_pack", "timeline_sync", "critique"],
            "reason": "Missing transcript, OCR, model observation, or frame evidence can weaken downstream style, script, visual, and critique decisions.",
            "owner_agent": "channel-intelligence",
            "severity": "minor" if status != "blocked" else "blocker",
            "recommended_action": "Preserve limitations and rerun affected downstream work if missing evidence is later added.",
        })

    analysis = drop_none({
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "analysis_id": analysis_id,
        "project_id": args.project_id,
        "project_path": args.project_path,
        "channel_profile_id": args.channel_profile_id,
        "channel_slug": args.channel_slug,
        "channel_profile_path": args.channel_profile_path,
        "media_asset_manifest_path": args.media_asset_manifest,
        "status": status,
        "processing_runs": [{
            "run_id": f"processing-{slugify(source_id)}-local-reference-analysis",
            "mode": "local_deterministic",
            "tool": "analyze_reference_video.py",
            "status": "complete" if status == "complete" else status,
            "command": sys.argv,
            "inputs": [relpath(video_path, repo_root) or str(video_path)],
            "outputs": [
                relpath(output_path, repo_root),
                probe_path,
                relpath(scenes_path, repo_root),
                relpath(frame_samples_path, repo_root),
                relpath(frames_dir, repo_root),
                relpath(ocr_path, repo_root) if ocr_path else None,
            ],
            "deterministic_evidence": [
                "ffprobe metadata" if technical else None,
                "scene or fallback segment timing",
                "keyframe extraction" if frame_samples else None,
                "OCR" if args.enable_ocr else None,
            ],
            "model_inferred_evidence": ["approved model observation"] if args.model_observation_path else [],
            "limitations": limitations,
        }],
        "overall_summary": {
            "summary": (
                f"Prepared {len(scenes)} reference segments and {len(frame_samples)} keyframes for {source_id}. "
                "Use this as scene-decomposition and style-pattern evidence, not as reuse permission."
            ),
            "source_ids": [source_id],
            "reference_video_ids": [video_id],
            "duration_seconds": technical.get("duration_seconds") if technical else None,
            "scene_count": len(scenes),
            "reference_beat_count": len(reference_beats),
            "deterministic_evidence": [
                "ffprobe metadata" if technical else None,
                "scene or fallback segment timing",
                "keyframe extraction" if frame_samples else None,
                "OCR" if args.enable_ocr else None,
                "transcript artifact" if args.transcript_path else None,
            ],
            "model_inferred_evidence": ["approved model observation"] if args.model_observation_path else [],
            "reusable_patterns": sorted({tag for beat in beats for tag in beat.get("pattern_tags", [])}),
            "do_not_copy_risks": [
                "Reference analysis does not grant rights to reuse footage; treat reference as pattern evidence only."
            ],
            "evidence_gaps": evidence_gaps,
            "limitations": limitations,
            "confidence": "medium" if frame_samples else "low",
        },
        "sources": [{
            "source_id": source_id,
            "asset_id": f"asset-{slugify(source_id)}-reference-video",
            "kind": "reference_video",
            "path_or_url": args.source_url or relpath(video_path, repo_root),
            "local_path": relpath(video_path, repo_root),
            "title": args.title,
            "owner": args.owner,
            "rights_notes": args.rights_notes or "Reference analysis only; final reuse rights are not implied.",
            "summary": "Local reference video prepared for deterministic analysis.",
            "confidence": "high" if video_path.exists() else "unknown",
            "captured_artifacts": captured_artifacts,
        }],
        "source_ledger": [source_ledger_entry],
        "reference_videos": [{
            "video_id": video_id,
            "source_id": source_id,
            "media_asset_id": f"asset-{slugify(source_id)}-reference-video",
            "duration_seconds": technical.get("duration_seconds") if technical else None,
            "technical": technical,
            "artifacts": {
                "probe_json_path": probe_path,
                "scenes_json_path": relpath(scenes_path, repo_root),
                "frame_samples_json_path": relpath(frame_samples_path, repo_root),
                "keyframe_dir": relpath(frames_dir, repo_root),
                "ocr_json_path": relpath(ocr_path, repo_root) if ocr_path else None,
                "transcript_path": relpath(args.transcript_path, repo_root) if args.transcript_path else None,
                "embedding_index_path": relpath(args.embedding_index_path, repo_root) if args.embedding_index_path else None,
                "model_observation_path": relpath(args.model_observation_path, repo_root) if args.model_observation_path else None,
            },
            "transcript_path": relpath(args.transcript_path, repo_root) if args.transcript_path else None,
            "thumbnail_path": frame_samples[0].get("frame_path") if frame_samples else None,
            "shot_breakdown_path": relpath(scenes_path, repo_root),
            "beats": beats,
        }],
        "claim_ledger": [],
        "scene_decomposition": scene_decomposition,
        "reference_beats": reference_beats,
        "findings": {
            "narrative_patterns": [],
            "visual_patterns": [
                f"{len(scenes)} reference segments prepared from local timing evidence.",
                f"{len(frame_samples)} keyframes extracted for visual inspection.",
            ],
            "audio_patterns": ["Audio presence detected." if technical.get("has_audio") else "No audio stream detected or metadata unavailable."] if technical else [],
            "source_claims": [],
            "visual_evidence_opportunities": [
                "Use extracted keyframes to identify recurring shot grammar, captions, overlays, source-card behavior, and opening-frame conventions."
            ],
            "story_opportunities": [],
            "rights_or_policy_risks": [
                "Reference analysis does not grant rights to reuse footage; treat reference as pattern evidence only."
            ],
            "evidence_gaps": evidence_gaps,
            "confidence_notes": [
                "Technical metadata, segment timing, and keyframe paths are deterministic when ffprobe/ffmpeg succeed.",
                "Shot size, camera motion, mood, narrative purpose, and reusable style rules still require human or approved model interpretation.",
            ],
        },
        "evidence_refs": evidence_refs,
        "downstream_guidance": {
            "creative_producer": [
                "Use transcript or manually reviewed beats before relying on exact narrative rhythm."
            ],
            "visual_producer": [
                "Use keyframes as reference evidence for visual style and shot grammar, not as reusable footage."
            ],
            "invideo_ai_generator": [
                "Use extracted patterns only after Channel Intelligence separates reusable style from one-off reference choices."
            ],
            "remotion_clip_builder": [
                "Use reference keyframes to infer possible reusable template or VFX motifs after style extraction."
            ],
            "remotion_video_producer": [
                "Do not treat reference keyframes as production media unless rights are separately approved."
            ],
            "video_critic": [
                "Check final render provenance against reference limitations and do-not-copy risks."
            ],
        },
        "invalidation_impact": invalidation_impact,
    })

    if args.update_media_asset_manifest:
        if not args.media_asset_manifest:
            analysis.setdefault("findings", {}).setdefault("evidence_gaps", []).append(
                "Manifest update requested but --media-asset-manifest was not supplied."
            )
        else:
            manifest_path = Path(args.media_asset_manifest)
            if not manifest_path.is_absolute():
                manifest_path = repo_root / manifest_path
            assets = manifest_assets(
                source_id,
                video_path,
                repo_root,
                args,
                output_path,
                probe_path,
                scenes_path,
                frame_samples_path,
                ocr_path,
                frame_samples,
            )
            manifest_notes = append_manifest_assets(manifest_path, assets)
            if manifest_notes:
                analysis.setdefault("findings", {}).setdefault("evidence_gaps", []).extend(manifest_notes)
            else:
                analysis["processing_runs"][0].setdefault("outputs", []).append(relpath(manifest_path, repo_root))

    write_json(output_path, analysis)
    print(output_path)
    return 0 if status != "blocked" else 2


if __name__ == "__main__":
    raise SystemExit(main())
