#!/usr/bin/env python3
"""Build a scene-level timeline sync plan from scenario, voiceover, and visuals."""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

PRIMARY_SELECTION_VALUES = {"approved_primary", "primary", "selected_primary"}
FALLBACK_SELECTION_VALUES = {"approved_fallback", "fallback", "selected_fallback"}


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


def selection_decisions(payload: Any) -> dict[str, dict[str, Any]]:
    decisions: dict[str, dict[str, Any]] = {}
    if not isinstance(payload, dict):
        return decisions

    for ranking in payload.get("scene_rankings", []):
        scene_id = ranking.get("scene_id")
        decision_id = ranking.get("selection_decision_id") or ranking.get("ranking_id") or (
            f"{scene_id}-visual-selection" if scene_id else None
        )
        primary_candidate_id = ranking.get("primary_candidate_id")
        if primary_candidate_id:
            decisions[primary_candidate_id] = {
                "scene_id": scene_id,
                "selection_authority": "visual-producer",
                "selection_decision_id": decision_id,
                "selection_status": "approved_primary",
                "decision": "primary",
            }
        for candidate_id in ranking.get("fallback_candidate_ids", []):
            decisions.setdefault(candidate_id, {
                "scene_id": scene_id,
                "selection_authority": "visual-producer",
                "selection_decision_id": decision_id,
                "selection_status": "approved_fallback",
                "decision": "fallback",
            })
        for decision in ranking.get("candidate_decisions", []):
            candidate_id = decision.get("candidate_id")
            decision_value = decision.get("decision")
            if not candidate_id or decision_value not in {"primary", "fallback"}:
                continue
            decisions[candidate_id] = {
                "scene_id": scene_id,
                "selection_authority": "visual-producer",
                "selection_decision_id": decision_id,
                "selection_status": "approved_primary" if decision_value == "primary" else "approved_fallback",
                "decision": decision_value,
            }
    return decisions


def apply_selection_decisions(candidates: list[dict[str, Any]], payload: Any) -> list[dict[str, Any]]:
    decisions = selection_decisions(payload)
    if not decisions:
        return candidates

    by_id: dict[str, dict[str, Any]] = {}
    for candidate in candidates:
        candidate_id = candidate.get("candidate_id")
        if not candidate_id:
            continue
        merged = dict(candidate)
        if candidate_id in decisions:
            for key, value in decisions[candidate_id].items():
                merged.setdefault(key, value)
        by_id[candidate_id] = merged

    for candidate_id, decision in decisions.items():
        if candidate_id not in by_id:
            by_id[candidate_id] = {
                "candidate_id": candidate_id,
                "scene_id": decision.get("scene_id"),
                "route": "unassigned",
                **decision,
            }
    return list(by_id.values())


def selection_role(candidate: dict[str, Any]) -> str | None:
    values = [
        candidate.get("selection_status"),
        candidate.get("decision"),
        candidate.get("selection_role"),
        candidate.get("candidate_decision"),
        candidate.get("ranking_decision"),
        candidate.get("visual_decision"),
    ]
    normalized = {str(value).strip().lower() for value in values if value is not None}
    if normalized & PRIMARY_SELECTION_VALUES:
        return "primary"
    if normalized & FALLBACK_SELECTION_VALUES:
        return "fallback"
    if candidate.get("is_primary") or candidate.get("primary_selected"):
        return "primary"
    if candidate.get("is_fallback") or candidate.get("fallback_selected"):
        return "fallback"
    return None


def scene_candidates(scene_id: str, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [item for item in candidates if item.get("scene_id") == scene_id]


def selected_candidate(scene_id: str, candidates: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, str | None]:
    primary = [item for item in scene_candidates(scene_id, candidates) if selection_role(item) == "primary"]
    if primary:
        return primary[0], "primary"
    fallback = [item for item in scene_candidates(scene_id, candidates) if selection_role(item) == "fallback"]
    if fallback:
        return fallback[0], "fallback"
    return None, None


def repair_candidate(scene_id: str, candidates: list[dict[str, Any]]) -> dict[str, Any] | None:
    scene_items = scene_candidates(scene_id, candidates)
    if not scene_items:
        return None
    status_rank = {"approved": 4, "generated": 3, "downloaded": 3, "proposed": 2, "needs_approval": 1}

    def score(item: dict[str, Any]) -> tuple[int, float]:
        total = ((item.get("scores") or {}).get("total") or 0)
        return status_rank.get(item.get("status"), 0), float(total)

    return sorted(scene_items, key=score, reverse=True)[0]


def pack_by_scene(visual_pack: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not visual_pack:
        return {}
    return {item.get("scene_id"): item for item in visual_pack.get("scene_packs", []) if item.get("scene_id")}


def voice_by_scene(voiceover: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not voiceover:
        return {}
    return {item.get("scene_id"): item for item in voiceover.get("scenes", []) if item.get("scene_id")}


def make_visual_source(
    scene_id: str,
    candidate: dict[str, Any] | None,
    pack: dict[str, Any] | None,
    selection_status: str,
    selection_authority: str,
    helper_selected: bool,
    director_review_required: bool,
) -> dict[str, Any]:
    if candidate:
        return drop_none({
            "candidate_id": candidate.get("candidate_id"),
            "route": candidate.get("route") or "unassigned",
            "local_path": candidate.get("local_path"),
            "media_asset_id": candidate.get("media_asset_id"),
            "source_asset_ids": candidate.get("source_asset_ids"),
            "remotion_static_file_path": candidate.get("remotion_static_file_path"),
            "remotion_clip_package_path": candidate.get("remotion_clip_package_path"),
            "template_id": candidate.get("template_id"),
            "template_ids": candidate.get("template_ids"),
            "template_contract_path": candidate.get("template_contract_path"),
            "template_contract_paths": candidate.get("template_contract_paths"),
            "ai_video_generation_package_path": candidate.get("ai_video_generation_package_path"),
            "selection_authority": candidate.get("selection_authority") or selection_authority,
            "selection_decision_id": candidate.get("selection_decision_id"),
            "selection_status": candidate.get("selection_status") or selection_status,
            "helper_selected": helper_selected,
            "director_review_required": director_review_required,
            "notes": f"status={candidate.get('status')}; selection_status={selection_status}",
        })
    routes = (pack or {}).get("routes") or []
    return {
        "route": "unassigned",
        "selection_authority": "unknown",
        "selection_status": "missing_selection",
        "helper_selected": False,
        "director_review_required": True,
        "notes": f"No Visual Producer-selected clip candidate. Planned routes: {', '.join(routes) if routes else 'none'}.",
    }


def manifest_action(
    action: str,
    reason: str,
    asset_id: str | None = None,
    canonical_path: str | None = None,
    static_file_path: str | None = None,
    rights_state: str | None = None,
    technical_metadata_state: str | None = None,
) -> dict[str, Any]:
    return drop_none({
        "action": action,
        "asset_id": asset_id,
        "canonical_path": canonical_path,
        "static_file_path": static_file_path,
        "rights_state": rights_state,
        "technical_metadata_state": technical_metadata_state,
        "reason": reason,
    })


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
    parser.add_argument(
        "--allow-repair-default",
        action="store_true",
        help="Allow helper-ranked fallback visuals. Marks selected visuals as repair_default and requires Director review.",
    )
    args = parser.parse_args()

    scenario = load_json(args.scenario)
    voiceover = load_json(args.voiceover_package)
    visual_pack = load_json(args.visual_pack)
    candidate_payload = load_json(args.clip_candidates)
    candidates = apply_selection_decisions(normalize_candidates(candidate_payload), candidate_payload)
    packs = pack_by_scene(visual_pack)
    voice = voice_by_scene(voiceover)
    findings: list[dict[str, Any]] = []
    manifest_actions: list[dict[str, Any]] = []
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

        pack = packs.get(scene_id)
        candidate, role = selected_candidate(scene_id, candidates)
        selection_status = "approved_primary" if role == "primary" else "approved_fallback" if role == "fallback" else "missing_selection"
        selection_authority = "visual-producer" if role else "unknown"
        helper_selected = False
        director_review_required = role != "primary"

        if not candidate and args.allow_repair_default:
            candidate = repair_candidate(scene_id, candidates)
            if candidate:
                selection_status = "repair_default"
                selection_authority = "timeline_helper_repair"
                helper_selected = True
                director_review_required = True
                findings.append({
                    "severity": "major",
                    "scene_id": scene_id,
                    "timestamp_seconds": start_seconds,
                    "description": "Timeline helper selected a repair_default visual because no Visual Producer selection was marked.",
                    "fix_status": "director_review_required",
                })

        visual_source = make_visual_source(
            scene_id,
            candidate,
            pack,
            selection_status,
            selection_authority,
            helper_selected,
            director_review_required,
        )
        if role == "fallback":
            findings.append({
                "severity": "major",
                "scene_id": scene_id,
                "timestamp_seconds": start_seconds,
                "description": "Timeline uses an approved fallback visual because no approved primary was marked.",
                "fix_status": "review_visual_selection",
            })
        if selection_status == "missing_selection":
            findings.append({
                "severity": "blocker",
                "scene_id": scene_id,
                "timestamp_seconds": start_seconds,
                "description": "No Visual Producer-selected primary or fallback candidate is marked for this scene.",
                "fix_status": "needs_visual_selection",
            })
        if visual_source.get("route") == "unassigned":
            findings.append({
                "severity": "major" if candidate else "blocker",
                "scene_id": scene_id,
                "timestamp_seconds": start_seconds,
                "description": "Selected visual has no renderable route.",
                "fix_status": "needs_visual_route",
            })

        if visual_source.get("media_asset_id") or visual_source.get("local_path") or visual_source.get("remotion_static_file_path"):
            manifest_actions.append(manifest_action(
                "consumed",
                f"Timeline visual source for {scene_id}.",
                asset_id=visual_source.get("media_asset_id"),
                canonical_path=visual_source.get("local_path"),
                static_file_path=visual_source.get("remotion_static_file_path"),
                rights_state="unknown",
                technical_metadata_state="partial",
            ))

        if not voice_scene.get("audio_path"):
            findings.append({
                "severity": "minor",
                "scene_id": scene_id,
                "timestamp_seconds": start_seconds,
                "description": "No generated voiceover path attached.",
                "fix_status": "needs_tts_or_manual_audio",
            })
        else:
            manifest_actions.append(manifest_action(
                "consumed",
                f"Voiceover audio for {scene_id}.",
                canonical_path=voice_scene.get("audio_path"),
                technical_metadata_state="partial",
            ))

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
        else:
            manifest_actions.append(manifest_action(
                "consumed",
                f"Caption timing for {scene_id}.",
                canonical_path=captions.get("caption_json_path"),
                technical_metadata_state="partial",
            ))

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
    if not manifest_actions:
        manifest_actions.append(manifest_action("not_applicable", "No local media artifacts were present in the supplied inputs."))
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
        "manifest_actions": manifest_actions,
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
