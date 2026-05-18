#!/usr/bin/env python3
"""Build a scene artifact sync report from Video Factory production artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from typing import Any

BAD_SYNC_STATUSES = {
    "missing_downstream",
    "stale_downstream",
    "orphaned_downstream",
    "conflicting_routes",
    "needs_director_decision",
}


def load_json(path: str | None) -> Any:
    if not path:
        return None
    with open(path, "r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def file_sha256(path: str | None) -> str | None:
    if not path:
        return None
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def stable_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return f"sha256:{hashlib.sha256(payload.encode('utf-8')).hexdigest()}"


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
    if isinstance(payload, dict) and "candidates" in payload:
        return payload["candidates"]
    if isinstance(payload, dict) and "candidate_id" in payload:
        return [payload]
    return []


def list_payloads(paths: list[str]) -> list[tuple[str, dict[str, Any]]]:
    payloads: list[tuple[str, dict[str, Any]]] = []
    for path in paths:
        payload = load_json(path)
        if isinstance(payload, dict):
            payloads.append((path, payload))
    return payloads


def by_scene(payloads: list[tuple[str, dict[str, Any]]]) -> dict[str, list[tuple[str, dict[str, Any]]]]:
    result: dict[str, list[tuple[str, dict[str, Any]]]] = {}
    for path, payload in payloads:
        scene_id = payload.get("scene_id")
        if scene_id:
            result.setdefault(scene_id, []).append((path, payload))
    return result


def scene_fingerprint(scene: dict[str, Any], scene_index: int) -> str:
    return stable_hash({
        "scene_id": scene.get("scene_id"),
        "scene_index": scene_index,
        "start_seconds": scene.get("start_seconds"),
        "end_seconds": scene.get("end_seconds"),
        "script": scene.get("script"),
        "onscreen_text": scene.get("onscreen_text"),
        "visual_intent": scene.get("visual_intent"),
        "reference_use_policy": scene.get("reference_use_policy"),
        "target_content_substitution": scene.get("target_content_substitution"),
        "source_ids": scene.get("source_ids"),
        "format_notes": scene.get("format_notes"),
    })


def pack_fingerprint(pack: dict[str, Any]) -> str:
    return stable_hash({
        "scene_pack_id": pack.get("scene_pack_id"),
        "scene_id": pack.get("scene_id"),
        "scene_index": pack.get("scene_index"),
        "start_seconds": pack.get("start_seconds"),
        "end_seconds": pack.get("end_seconds"),
        "scenario_scene_fingerprint": pack.get("scenario_scene_fingerprint"),
        "routes": pack.get("routes"),
        "template_id": pack.get("template_id"),
        "template_ids": pack.get("template_ids"),
        "source_ids": pack.get("source_ids"),
        "source_asset_ids": pack.get("source_asset_ids"),
        "prop_requirements": pack.get("prop_requirements"),
    })


def pack_index(visual_pack: dict[str, Any] | None) -> tuple[dict[str, list[dict[str, Any]]], list[str]]:
    packs: dict[str, list[dict[str, Any]]] = {}
    duplicates: list[str] = []
    if not visual_pack:
        return packs, duplicates
    for pack in visual_pack.get("scene_packs", []):
        scene_id = pack.get("scene_id")
        if not scene_id:
            continue
        packs.setdefault(scene_id, []).append(pack)
    for scene_id, scene_packs in packs.items():
        if len(scene_packs) > 1:
            duplicates.append(scene_id)
    return packs, duplicates


def timeline_by_scene(timeline: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not timeline:
        return {}
    return {scene.get("scene_id"): scene for scene in timeline.get("scenes", []) if scene.get("scene_id")}


def selected_candidates_by_scene(candidates: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    selected_values = {"approved_primary", "approved_fallback", "primary", "fallback", "selected_primary", "selected_fallback"}
    for candidate in candidates:
        scene_id = candidate.get("scene_id")
        if not scene_id:
            continue
        values = {
            str(candidate.get("selection_status", "")).lower(),
            str(candidate.get("decision", "")).lower(),
            str(candidate.get("selection_role", "")).lower(),
        }
        if values & selected_values or candidate.get("is_primary") or candidate.get("primary_selected"):
            result.setdefault(scene_id, []).append(candidate)
    return result


def append_status(current: str, proposed: str) -> str:
    if current == "synced":
        return proposed
    if current == "missing_downstream" and proposed in {"stale_downstream", "orphaned_downstream", "conflicting_routes"}:
        return proposed
    if proposed == "conflicting_routes":
        return proposed
    return current


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--visual-pack")
    parser.add_argument("--clip-candidates")
    parser.add_argument("--remotion-clip-package", action="append", default=[])
    parser.add_argument("--ai-video-generation-package", action="append", default=[])
    parser.add_argument("--timeline-sync-plan")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    scenario = load_json(args.scenario)
    visual_pack = load_json(args.visual_pack)
    candidates = normalize_candidates(load_json(args.clip_candidates))
    clip_packages = list_payloads(args.remotion_clip_package)
    ai_packages = list_payloads(args.ai_video_generation_package)
    timeline = load_json(args.timeline_sync_plan)

    scenario_scenes = scenario.get("scenes", [])
    scenario_ids = [scene.get("scene_id") for scene in scenario_scenes if scene.get("scene_id")]
    known_scene_ids = set(scenario_ids)
    duplicate_scenario_ids = sorted({scene_id for scene_id in scenario_ids if scenario_ids.count(scene_id) > 1})
    packs, duplicate_pack_scene_ids = pack_index(visual_pack)
    candidate_selections = selected_candidates_by_scene(candidates)
    clips = by_scene(clip_packages)
    ai_by_scene = by_scene(ai_packages)
    timeline_scenes = timeline_by_scene(timeline)

    orphaned_artifacts: list[str] = []
    invalidated_artifacts: list[str] = []
    preserved_artifacts: list[str] = []
    checked_artifacts = [
        path for path in [
            args.scenario,
            args.visual_pack,
            args.clip_candidates,
            args.timeline_sync_plan,
            *args.remotion_clip_package,
            *args.ai_video_generation_package,
        ] if path
    ]

    scene_rows: list[dict[str, Any]] = []
    for scene_index, scene in enumerate(scenario_scenes):
        scene_id = scene.get("scene_id")
        fingerprint = scene_fingerprint(scene, scene_index)
        findings: list[str] = []
        sync_status = "synced"
        repair_owner = "none"
        repair_action = ""
        visual_pack_status = "unknown"
        props_status = "unknown"
        candidate_status = "unknown"
        clip_package_status = "unknown"
        ai_package_status = "unknown"
        timeline_status = "unknown"
        scene_pack_id = None
        scene_pack_hash = None

        scene_packs = packs.get(scene_id, [])
        if not scene_packs:
            visual_pack_status = "fail" if visual_pack else "unknown"
            sync_status = append_status(sync_status, "missing_downstream")
            findings.append("Missing scene pack for scenario scene.")
            repair_owner = "visual-producer"
            repair_action = "Rerun visual-pack-plan for this scene."
        elif len(scene_packs) > 1:
            visual_pack_status = "fail"
            sync_status = append_status(sync_status, "conflicting_routes")
            findings.append("Multiple scene packs reference the same scenario scene id.")
            repair_owner = "visual-producer"
            repair_action = "Deduplicate scene packs and preserve one current pack."
        else:
            pack = scene_packs[0]
            scene_pack_id = pack.get("scene_pack_id")
            scene_pack_hash = pack_fingerprint(pack)
            visual_pack_status = "pass"
            if pack.get("scene_index") is None or int(pack.get("scene_index")) != scene_index:
                sync_status = append_status(sync_status, "stale_downstream")
                visual_pack_status = "fail"
                findings.append("Scene pack index does not match scenario order.")
            if pack.get("scenario_scene_fingerprint") and pack.get("scenario_scene_fingerprint") != fingerprint:
                sync_status = append_status(sync_status, "stale_downstream")
                visual_pack_status = "fail"
                findings.append("Scene pack scenario fingerprint does not match current scenario scene.")
            if not pack.get("prop_requirements"):
                sync_status = append_status(sync_status, "missing_downstream")
                props_status = "fail"
                findings.append("Scene pack has no prop_requirements.")
            else:
                props_status = "pass"

        if duplicate_scenario_ids:
            sync_status = append_status(sync_status, "needs_director_decision")
            findings.append(f"Scenario contains duplicate scene ids: {', '.join(duplicate_scenario_ids)}.")
            repair_owner = "creative-producer"
            repair_action = "Regenerate scenario with unique stable scene ids."

        selected = candidate_selections.get(scene_id, [])
        if selected:
            candidate_status = "pass"
        elif candidates:
            candidate_status = "fail"
            sync_status = append_status(sync_status, "missing_downstream")
            findings.append("No selected candidate is marked for this scene.")

        scene_clips = clips.get(scene_id, [])
        if scene_clips:
            clip_package_status = "pass"
            for clip_path, clip in scene_clips:
                clip_sync = clip.get("props_sync", {})
                if clip.get("scenario_scene_fingerprint") and clip.get("scenario_scene_fingerprint") != fingerprint:
                    clip_package_status = "fail"
                    props_status = "fail"
                    sync_status = append_status(sync_status, "stale_downstream")
                    findings.append(f"Clip package has stale scenario fingerprint: {clip_path}.")
                    invalidated_artifacts.append(clip_path)
                    repair_owner = "remotion-clip-builder"
                    repair_action = "Rebuild Remotion clip package with current scenario scene and scene pack."
                if clip_sync.get("status") and clip_sync.get("status") != "synced":
                    props_status = "fail"
                    sync_status = append_status(sync_status, "stale_downstream")
                    findings.append(f"Clip package props_sync is {clip_sync.get('status')}: {clip_path}.")
        elif args.remotion_clip_package:
            clip_package_status = "fail"

        scene_ai_packages = ai_by_scene.get(scene_id, [])
        if scene_ai_packages:
            ai_package_status = "pass"
            for ai_path, package in scene_ai_packages:
                if package.get("scenario_scene_fingerprint") and package.get("scenario_scene_fingerprint") != fingerprint:
                    ai_package_status = "fail"
                    sync_status = append_status(sync_status, "stale_downstream")
                    findings.append(f"AI generation package has stale scenario fingerprint: {ai_path}.")
                    invalidated_artifacts.append(ai_path)
                    repair_owner = "invideo-ai-generator"
                    repair_action = "Rebuild AI generation package with current scenario scene and scene pack."
        elif args.ai_video_generation_package:
            ai_package_status = "fail"

        timeline_scene = timeline_scenes.get(scene_id)
        if timeline_scene:
            timeline_status = "pass"
            if timeline_scene.get("scenario_scene_fingerprint") and timeline_scene.get("scenario_scene_fingerprint") != fingerprint:
                timeline_status = "fail"
                sync_status = append_status(sync_status, "stale_downstream")
                findings.append("Timeline scene has stale scenario fingerprint.")
                invalidated_artifacts.append(args.timeline_sync_plan)
                repair_owner = "remotion-video-producer"
                repair_action = "Rerun timeline-sync-plan after scene artifact sync passes."
        elif timeline:
            timeline_status = "fail"
            sync_status = append_status(sync_status, "missing_downstream")
            findings.append("Timeline sync plan is missing this scene.")

        if sync_status == "synced":
            preserved_artifacts.extend(path for path, _payload in scene_clips)
            preserved_artifacts.extend(path for path, _payload in scene_ai_packages)

        scene_rows.append(drop_none({
            "scene_id": scene_id,
            "scene_index": scene_index,
            "start_seconds": scene.get("start_seconds"),
            "end_seconds": scene.get("end_seconds"),
            "duration_seconds": (
                float(scene.get("end_seconds", 0)) - float(scene.get("start_seconds", 0))
                if scene.get("start_seconds") is not None and scene.get("end_seconds") is not None
                else None
            ),
            "scene_fingerprint": fingerprint,
            "scene_pack_id": scene_pack_id,
            "scene_pack_fingerprint": scene_pack_hash,
            "sync_status": sync_status,
            "visual_pack_status": visual_pack_status,
            "props_status": props_status,
            "candidate_status": candidate_status,
            "clip_package_status": clip_package_status,
            "ai_package_status": ai_package_status,
            "timeline_status": timeline_status,
            "findings": findings,
            "repair_owner": repair_owner,
            "repair_action": repair_action,
        }))

    for artifact_path, payload in [*clip_packages, *ai_packages]:
        scene_id = payload.get("scene_id")
        if scene_id and scene_id not in known_scene_ids:
            orphaned_artifacts.append(artifact_path)
            invalidated_artifacts.append(artifact_path)

    if timeline:
        for scene_id in timeline_scenes:
            if scene_id not in known_scene_ids:
                orphaned_artifacts.append(args.timeline_sync_plan)
                invalidated_artifacts.append(args.timeline_sync_plan)

    pack_scene_ids = set(packs)
    for scene_id in sorted(pack_scene_ids - known_scene_ids):
        orphaned_artifacts.append(f"{args.visual_pack}#scene:{scene_id}")

    failing_rows = [row for row in scene_rows if row.get("sync_status") in BAD_SYNC_STATUSES]
    status = "pass"
    if not scenario_scenes:
        status = "not_run"
    elif failing_rows or orphaned_artifacts or duplicate_pack_scene_ids or duplicate_scenario_ids:
        status = "fail"
    elif not visual_pack or not candidates:
        status = "partial"

    output = drop_none({
        "sync_report_id": f"{scenario.get('scenario_id', 'scenario')}-scene-artifact-sync",
        "status": status,
        "scenario_id": scenario.get("scenario_id"),
        "scenario_path": args.scenario,
        "scenario_hash": file_sha256(args.scenario),
        "scene_visual_pack_id": (visual_pack or {}).get("scene_visual_pack_id"),
        "scene_visual_pack_path": args.visual_pack,
        "scene_visual_pack_hash": file_sha256(args.visual_pack),
        "checked_artifacts": checked_artifacts,
        "scene_index": scene_rows,
        "orphaned_artifacts": sorted(set(orphaned_artifacts)),
        "invalidated_artifacts": sorted(set(invalidated_artifacts)),
        "preserved_artifacts": sorted(set(preserved_artifacts)),
        "handoff_recommendations": [],
        "next_recommended_step": "Proceed to the next downstream phase." if status == "pass" else "Repair failed scene sync rows before downstream render work.",
    })

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print(f"wrote {args.output} with status={status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
