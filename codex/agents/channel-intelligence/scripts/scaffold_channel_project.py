#!/usr/bin/env python3
"""Scaffold a Video Factory channel/project workspace."""

from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path
from typing import Any


CHANNEL_DIRS = [
    "brand/logos",
    "brand/typography",
    "brand/imagery",
    "formats",
    "references/reference-videos",
    "references/evidence",
    "rules",
    "assets/visual",
    "assets/audio",
    "assets/remotion",
    "projects",
]

PROJECT_DIRS = [
    "scenario",
    "voiceover",
    "visuals/candidates",
    "source-media/reference-videos",
    "source-media/reference-analysis",
    "source-media/web-content",
    "source-media/loaded-videos",
    "source-media/provider-clips",
    "source-media/generated-clips",
    "remotion/props",
    "remotion/clips",
    "remotion/timeline",
    "remotion/public-projection",
    "renders/previews",
    "renders/rc",
    "renders/final",
    "reviews/assets",
    "reviews/evidence",
    "runs",
    "delivery",
]


def slugify(value: str, label: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    if not slug:
        raise ValueError(f"{label} must contain at least one letter or number")
    return slug


def posix(path: Path) -> str:
    return path.as_posix()


def channel_rel(channel_slug: str, *parts: str) -> str:
    return posix(Path("channels") / channel_slug / Path(*parts))


def project_rel(channel_slug: str, project_slug: str, *parts: str) -> str:
    return posix(Path("channels") / channel_slug / "projects" / project_slug / Path(*parts))


def write_json(path: Path, data: dict[str, Any], overwrite: bool, dry_run: bool) -> None:
    if path.exists() and not overwrite:
        return
    if dry_run:
        print(f"write {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8-sig"))


def mkdir(path: Path, dry_run: bool) -> None:
    if dry_run:
        print(f"mkdir {path}")
        return
    path.mkdir(parents=True, exist_ok=True)


def upsert_project_entry(projects: list[Any], project_entry: dict[str, Any]) -> list[Any]:
    updated: list[Any] = []
    found = False
    for item in projects:
        if not isinstance(item, dict):
            updated.append(item)
            continue
        if item.get("project_slug") == project_entry["project_slug"]:
            merged = {**item, **project_entry}
            updated.append(merged)
            found = True
        else:
            updated.append(item)
    if not found:
        updated.append(project_entry)
    return updated


def append_unique(values: list[Any], value: str) -> list[Any]:
    return values if value in values else [*values, value]


def merge_channel_profile(existing: dict[str, Any] | None, scaffold: dict[str, Any]) -> dict[str, Any]:
    if existing is None:
        return scaffold

    merged = copy.deepcopy(existing)
    for key in ["channel_profile_id", "channel_slug", "root_path"]:
        merged[key] = scaffold[key]
    for key in ["version", "status", "metadata", "brand_identity", "content_strategy", "visual_identity", "audio_identity", "governance", "qa"]:
        merged.setdefault(key, scaffold[key])

    merged["folder_layout"] = {
        **merged.get("folder_layout", {}),
        **scaffold.get("folder_layout", {}),
    }

    existing_reference = merged.get("reference_management", {})
    if not isinstance(existing_reference, dict):
        existing_reference = {}
    scaffold_reference = scaffold.get("reference_management", {})
    manifest_path = scaffold_reference.get("media_asset_manifest_paths", [""])[0]
    existing_manifest_paths = existing_reference.get("media_asset_manifest_paths", [])
    if not isinstance(existing_manifest_paths, list):
        existing_manifest_paths = []
    reference_management = {
        **scaffold_reference,
        **existing_reference,
        "source_ledger_path": scaffold_reference["source_ledger_path"],
        "reference_videos_path": scaffold_reference["reference_videos_path"],
        "evidence_path": scaffold_reference["evidence_path"],
        "media_asset_manifest_paths": append_unique(
            existing_manifest_paths,
            manifest_path,
        ),
    }
    merged["reference_management"] = reference_management
    existing_projects = merged.get("projects", [])
    if not isinstance(existing_projects, list):
        existing_projects = []
    merged["projects"] = upsert_project_entry(existing_projects, scaffold["projects"][0])
    return merged


def merge_video_project(existing: dict[str, Any] | None, scaffold: dict[str, Any]) -> dict[str, Any]:
    if existing is None:
        return scaffold

    merged = copy.deepcopy(existing)
    for key in ["project_id", "project_slug", "channel_profile_id", "channel_slug", "channel_profile_path", "root_path"]:
        merged[key] = scaffold[key]
    for key in ["status", "objective", "brief", "deliverables", "runs", "change_log", "qa"]:
        merged.setdefault(key, scaffold[key])

    merged["artifacts"] = {
        **merged.get("artifacts", {}),
        **scaffold.get("artifacts", {}),
    }
    merged["folder_layout"] = {
        **merged.get("folder_layout", {}),
        **scaffold.get("folder_layout", {}),
    }
    merged["remotion_setup"] = {
        **merged.get("remotion_setup", {}),
        **scaffold.get("remotion_setup", {}),
    }
    return merged


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("channel_slug")
    parser.add_argument("project_slug")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--channel-name", default=None)
    parser.add_argument("--objective", default="Planned video project")
    parser.add_argument("--platform", default="youtube")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    channel_slug = slugify(args.channel_slug, "channel_slug")
    project_slug = slugify(args.project_slug, "project_slug")
    channel_root = repo_root / "channels" / channel_slug
    project_root = channel_root / "projects" / project_slug
    remotion_public_project_root = (
        repo_root / "remotion" / "public" / "channels" / channel_slug / "projects" / project_slug
    )

    for rel in CHANNEL_DIRS:
        mkdir(channel_root / rel, args.dry_run)
    for rel in PROJECT_DIRS:
        mkdir(project_root / rel, args.dry_run)
    mkdir(remotion_public_project_root, args.dry_run)

    channel_profile_id = f"channel-{channel_slug}"
    project_id = f"project-{channel_slug}-{project_slug}"
    manifest_id = f"media-{channel_slug}-{project_slug}"

    channel_profile = {
        "channel_profile_id": channel_profile_id,
        "channel_slug": channel_slug,
        "version": "1.0.0",
        "status": "draft",
        "root_path": channel_rel(channel_slug),
        "metadata": {
            "name": args.channel_name or channel_slug,
            "domain": "unknown",
            "primary_platforms": [args.platform],
        },
        "brand_identity": {
            "promise": "unknown",
            "values": [],
            "positioning": "unknown",
        },
        "content_strategy": {},
        "visual_identity": {},
        "audio_identity": {},
        "governance": {},
        "folder_layout": {
            "brand_path": channel_rel(channel_slug, "brand"),
            "formats_path": channel_rel(channel_slug, "formats"),
            "references_path": channel_rel(channel_slug, "references"),
            "rules_path": channel_rel(channel_slug, "rules"),
            "assets_path": channel_rel(channel_slug, "assets"),
            "evidence_path": channel_rel(channel_slug, "references", "evidence"),
            "projects_path": channel_rel(channel_slug, "projects"),
        },
        "reference_management": {
            "source_ledger_path": channel_rel(channel_slug, "references", "source-ledger.json"),
            "reference_videos_path": channel_rel(channel_slug, "references", "reference-videos"),
            "evidence_path": channel_rel(channel_slug, "references", "evidence"),
            "media_asset_manifest_paths": [project_rel(channel_slug, project_slug, "media-asset-manifest.json")],
        },
        "projects": [
            {
                "project_id": project_id,
                "project_slug": project_slug,
                "path": project_rel(channel_slug, project_slug),
                "status": "planned",
            }
        ],
        "evidence": [],
        "qa": {
            "status": "partial",
            "summary": "Scaffolded profile; brand/channel data needs enrichment.",
            "missing_assets": [],
            "risks": ["Channel profile contains placeholders."],
        },
    }

    project = {
        "project_id": project_id,
        "project_slug": project_slug,
        "channel_profile_id": channel_profile_id,
        "channel_slug": channel_slug,
        "channel_profile_path": channel_rel(channel_slug, "channel-profile.json"),
        "status": "planned",
        "root_path": project_rel(channel_slug, project_slug),
        "objective": args.objective,
        "brief": {"platform": args.platform},
        "deliverables": [],
        "artifacts": {
            "production_run_path": project_rel(channel_slug, project_slug, "production-run.json"),
            "producer_criteria_path": project_rel(channel_slug, project_slug, "producer-criteria.json"),
            "media_asset_manifest_paths": [project_rel(channel_slug, project_slug, "media-asset-manifest.json")],
            "remotion_project_contract_path": "remotion/remotion-project.json",
            "remotion_app_root_path": "remotion",
        },
        "folder_layout": {
            "scenario_path": project_rel(channel_slug, project_slug, "scenario"),
            "voiceover_path": project_rel(channel_slug, project_slug, "voiceover"),
            "visuals_path": project_rel(channel_slug, project_slug, "visuals"),
            "source_media_path": project_rel(channel_slug, project_slug, "source-media"),
            "reference_videos_path": project_rel(channel_slug, project_slug, "source-media", "reference-videos"),
            "reference_analysis_path": project_rel(channel_slug, project_slug, "source-media", "reference-analysis"),
            "web_content_path": project_rel(channel_slug, project_slug, "source-media", "web-content"),
            "loaded_videos_path": project_rel(channel_slug, project_slug, "source-media", "loaded-videos"),
            "rendered_clips_path": project_rel(channel_slug, project_slug, "source-media", "generated-clips"),
            "remotion_path": project_rel(channel_slug, project_slug, "remotion"),
            "remotion_public_projection_path": project_rel(channel_slug, project_slug, "remotion", "public-projection"),
            "remotion_public_path": posix(
                Path("remotion") / "public" / "channels" / channel_slug / "projects" / project_slug
            ),
            "renders_path": project_rel(channel_slug, project_slug, "renders"),
            "reviews_path": project_rel(channel_slug, project_slug, "reviews"),
            "review_assets_path": project_rel(channel_slug, project_slug, "reviews", "assets"),
            "runs_path": project_rel(channel_slug, project_slug, "runs"),
            "delivery_path": project_rel(channel_slug, project_slug, "delivery"),
        },
        "remotion_setup": {
            "remotion_project_id": "shared-remotion-app",
            "remotion_project_contract_path": "remotion/remotion-project.json",
            "app_root_path": "remotion",
            "public_root_path": "remotion/public",
            "static_file_prefix": f"channels/{channel_slug}/projects/{project_slug}/",
            "composition_ids": ["VideoFactoryMain"],
        },
        "runs": [],
        "change_log": ["Scaffolded project workspace."],
        "qa": {
            "status": "partial",
            "summary": "Project folders scaffolded; production artifacts are not generated yet.",
            "residual_risks": [],
        },
    }

    manifest = {
        "manifest_id": manifest_id,
        "project_id": project_id,
        "project_slug": project_slug,
        "project_path": project_rel(channel_slug, project_slug),
        "channel_profile_id": channel_profile_id,
        "channel_slug": channel_slug,
        "channel_profile_path": channel_rel(channel_slug, "channel-profile.json"),
        "source_ledger_path": channel_rel(channel_slug, "references", "source-ledger.json"),
        "status": "planned",
        "assets": [],
        "qa": {
            "status": "not_run",
            "summary": "No media assets loaded yet.",
            "missing_assets": [],
            "rights_risks": [],
            "technical_risks": [],
        },
    }

    channel_profile_path = channel_root / "channel-profile.json"
    project_path = project_root / "project.json"
    existing_channel_profile = None if args.overwrite else read_json(channel_profile_path)
    existing_project = None if args.overwrite else read_json(project_path)
    channel_profile = merge_channel_profile(existing_channel_profile, channel_profile)
    project = merge_video_project(existing_project, project)

    write_json(channel_profile_path, channel_profile, True, args.dry_run)
    write_json(channel_root / "references" / "source-ledger.json", {"sources": []}, args.overwrite, args.dry_run)
    write_json(project_path, project, True if existing_project is not None else args.overwrite, args.dry_run)
    write_json(project_root / "media-asset-manifest.json", manifest, args.overwrite, args.dry_run)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
