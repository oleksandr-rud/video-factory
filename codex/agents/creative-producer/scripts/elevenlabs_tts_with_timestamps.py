#!/usr/bin/env python3
"""Prepare or execute ElevenLabs TTS with timestamp alignment.

Default mode is dry-run. The script only calls the paid generation endpoint when
both --execute and --approved are present.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.parse
import urllib.request
from typing import Any

from elevenlabs_model_policy import (
    DEFAULT_MODEL_PROFILE,
    estimate_credit_units,
    model_metadata_dict,
    resolve_model,
)


ENDPOINT = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps"


def load_json(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def drop_none(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: drop_none(item) for key, item in value.items() if item is not None}
    if isinstance(value, list):
        return [drop_none(item) for item in value]
    return value


def scenario_scenes(scenario: dict[str, Any]) -> list[dict[str, Any]]:
    scenes = scenario.get("scenes") or []
    normalized = []
    for scene in scenes:
        text = scene.get("script") or scene.get("narration") or scene.get("text") or ""
        normalized.append({
            "scene_id": scene.get("scene_id"),
            "text": text.strip(),
            "expected_duration_seconds": (
                scene.get("end_seconds", 0) - scene.get("start_seconds", 0)
                if "end_seconds" in scene and "start_seconds" in scene
                else None
            ),
        })
    return [scene for scene in normalized if scene["scene_id"] and scene["text"]]


def package_scenes(package: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "scene_id": scene["scene_id"],
            "text": scene.get("text") or scene.get("script") or "",
            "expected_duration_seconds": scene.get("expected_duration_seconds"),
        }
        for scene in package.get("scenes", [])
        if scene.get("scene_id") and (scene.get("text") or scene.get("script"))
    ]


def post_json(url: str, api_key: str, payload: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        method="POST",
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        data=json.dumps(payload).encode("utf-8"),
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def duration_from_alignment(alignment: dict[str, Any]) -> float | None:
    ends = alignment.get("character_end_times_seconds") or []
    if not ends:
        return None
    return float(max(ends))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario")
    parser.add_argument("--voiceover-package")
    parser.add_argument("--output", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--voice-id")
    parser.add_argument("--voice-name")
    parser.add_argument("--model-id")
    parser.add_argument("--model-profile", help=f"default: {DEFAULT_MODEL_PROFILE}")
    parser.add_argument("--allow-deprecated-model", action="store_true")
    parser.add_argument("--language-code")
    parser.add_argument("--target-language")
    parser.add_argument("--target-accent")
    parser.add_argument("--output-format", default="mp3_44100_128")
    parser.add_argument("--stability", type=float, default=0.5)
    parser.add_argument("--similarity-boost", type=float, default=0.75)
    parser.add_argument("--style", type=float, default=0.0)
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument("--use-speaker-boost", action="store_true")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--apply-text-normalization", choices=("auto", "on", "off"))
    parser.add_argument("--apply-language-text-normalization", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--approved", action="store_true")
    args = parser.parse_args()

    if not args.scenario and not args.voiceover_package:
        print("Provide --scenario or --voiceover-package", file=sys.stderr)
        return 2

    package: dict[str, Any] = {}
    if args.voiceover_package:
        package = load_json(args.voiceover_package)
    scenario = load_json(args.scenario) if args.scenario else {}

    voice_selection = package.get("voice_selection") or {}
    voice_id = args.voice_id or voice_selection.get("voice_id")
    if not voice_id:
        print("voice_id is required through --voice-id or voiceover package", file=sys.stderr)
        return 2

    scenes = package_scenes(package) if package else scenario_scenes(scenario)
    if not scenes:
        print("No scenes with narration text found", file=sys.stderr)
        return 2

    selected_model_id, model_metadata, model_notes = resolve_model(
        model_id=args.model_id or voice_selection.get("model_id"),
        profile=args.model_profile or voice_selection.get("model_profile"),
        allow_deprecated=args.allow_deprecated_model,
    )
    target_language = args.target_language or voice_selection.get("target_language")
    target_accent = args.target_accent or voice_selection.get("target_accent")
    for scene in scenes:
        if model_metadata.character_limit and len(scene["text"]) > model_metadata.character_limit:
            print(
                f"Scene {scene['scene_id']} has {len(scene['text'])} characters, "
                f"above {selected_model_id} limit {model_metadata.character_limit}",
                file=sys.stderr,
            )
            return 2

    if args.execute and not args.approved:
        print("Refusing paid generation without --approved", file=sys.stderr)
        return 2

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if args.execute and not api_key:
        print("ELEVENLABS_API_KEY is required for --execute", file=sys.stderr)
        return 2

    audio_dir = os.path.join(args.output_dir, "audio")
    alignment_dir = os.path.join(args.output_dir, "alignment")
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(alignment_dir, exist_ok=True)

    scene_outputs = []
    endpoint = ENDPOINT.format(voice_id=urllib.parse.quote(voice_id))
    endpoint = f"{endpoint}?{urllib.parse.urlencode({'output_format': args.output_format})}"

    for index, scene in enumerate(scenes):
        previous_text = scenes[index - 1]["text"] if index > 0 else None
        next_text = scenes[index + 1]["text"] if index + 1 < len(scenes) else None
        payload: dict[str, Any] = {
            "text": scene["text"],
            "model_id": selected_model_id,
            "voice_settings": {
                "stability": args.stability,
                "similarity_boost": args.similarity_boost,
                "style": args.style,
                "speed": args.speed,
                "use_speaker_boost": args.use_speaker_boost,
            },
        }
        if args.language_code:
            payload["language_code"] = args.language_code
        if args.seed is not None:
            payload["seed"] = args.seed
        if args.apply_text_normalization:
            payload["apply_text_normalization"] = args.apply_text_normalization
        if args.apply_language_text_normalization:
            payload["apply_language_text_normalization"] = True
        if previous_text:
            payload["previous_text"] = previous_text
        if next_text:
            payload["next_text"] = next_text

        scene_entry = {
            "scene_id": scene["scene_id"],
            "text": scene["text"],
            "expected_duration_seconds": scene.get("expected_duration_seconds"),
            "request_payload": payload,
        }

        if args.execute:
            response = post_json(endpoint, api_key or "", payload)
            audio_path = os.path.join(audio_dir, f"{scene['scene_id']}.mp3")
            alignment_path = os.path.join(alignment_dir, f"{scene['scene_id']}.json")
            with open(audio_path, "wb") as audio_file:
                audio_file.write(base64.b64decode(response["audio_base64"]))
            with open(alignment_path, "w", encoding="utf-8") as alignment_file:
                json.dump(response, alignment_file, indent=2, ensure_ascii=False)
                alignment_file.write("\n")

            alignment = response.get("normalized_alignment") or response.get("alignment") or {}
            scene_entry.update({
                "audio_path": audio_path,
                "alignment_path": alignment_path,
                "duration_seconds": duration_from_alignment(alignment),
            })

        scene_outputs.append(drop_none(scene_entry))

    character_count = sum(len(scene["text"]) for scene in scenes)
    output = drop_none({
        "voiceover_id": package.get("voiceover_id") or f"{scenario.get('scenario_id', 'scenario')}-voiceover",
        "scenario_id": package.get("scenario_id") or scenario.get("scenario_id"),
        "channel_format_id": package.get("channel_format_id") or scenario.get("channel_format_id"),
        "reference_analysis_id": package.get("reference_analysis_id") or scenario.get("reference_analysis_id"),
        "provider": "elevenlabs",
        "status": "generated" if args.execute else "ready_for_approval",
        "voice_selection": {
            **voice_selection,
            "voice_id": voice_id,
            "voice_name": args.voice_name or voice_selection.get("voice_name"),
            "model_id": selected_model_id,
            "model_profile": model_metadata.profile,
            "model_metadata": model_metadata_dict(model_metadata),
            "model_policy_notes": model_notes,
            "target_language": target_language,
            "target_accent": target_accent,
            "language_code": args.language_code or voice_selection.get("language_code"),
            "settings": {
                "stability": args.stability,
                "similarity_boost": args.similarity_boost,
                "style": args.style,
                "speed": args.speed,
                "use_speaker_boost": args.use_speaker_boost,
            },
        },
        "generation_policy": {
            "requires_user_approval": True,
            "approved": args.approved,
            "endpoint": "/v1/text-to-speech/:voice_id/with-timestamps",
            "model_id": selected_model_id,
            "model_profile": model_metadata.profile,
            "model_quality_score": model_metadata.quality_score,
            "target_language": target_language,
            "target_accent": target_accent,
            "output_format": args.output_format,
            "text_normalization": args.apply_text_normalization,
            "character_count": character_count,
            "estimated_credits": estimate_credit_units(character_count, selected_model_id),
            "character_limit": model_metadata.character_limit,
            "model_selection_reason": model_metadata.selection_note,
            "model_policy_notes": model_notes,
            "notes": "Dry-run writes request payloads only." if not args.execute else "Executed with explicit approval flag.",
        },
        "scenes": scene_outputs,
        "captions": {"source": "elevenlabs_timestamps" if args.execute else "unknown"},
        "scripts": [
            {
                "purpose": "ElevenLabs TTS with timestamps",
                "path": "codex/agents/creative-producer/scripts/elevenlabs_tts_with_timestamps.py",
            }
        ],
        "qa": {
            "status": "not_run" if not args.execute else "partial",
            "summary": "Prepared generation payloads." if not args.execute else "Generated audio and timestamp alignment; caption conversion still required.",
        },
    })

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
