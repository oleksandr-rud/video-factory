#!/usr/bin/env python3
"""Audit Video Factory agent skills, script references, and handoff coverage."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


HARDENING_SECTIONS = [
    "Inputs",
    "Workflow",
    "Required Output",
    "Contract Fields Populated",
    "Status Policy",
    "Evidence Required",
    "Media Manifest Policy",
    "Approval And Stop Conditions",
    "Definition Of Done",
    "Handoff Summary Shape",
]

PAID_API_TERMS = [
    "api",
    "paid",
    "credit",
    "credits",
    "generation",
    "generate",
    "download",
    "licensed",
    "license",
    "provider",
    "openrouter",
    "openai",
    "elevenlabs",
    "freepik",
    "pexels",
    "invideo",
    "tts",
    "voice",
    "critique",
]

APPROVAL_TERMS = [
    "approval",
    "approved",
    "needs_approval",
    "director approval",
    "stop before",
]

SCRIPT_REF_RE = re.compile(
    r"(?P<path>(?:[A-Za-z]:)?(?:[./\\\w-]+[\\/])?[\w.-]*\.py)"
)


@dataclass
class SkillAudit:
    path: str
    agent: str
    name: str | None
    has_frontmatter: bool
    missing_sections: list[str]
    script_refs: list[dict[str, str | bool]]
    approval_gate_required: bool
    approval_gate_present: bool


def repo_path(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def parse_frontmatter(text: str) -> tuple[bool, dict[str, str]]:
    if not text.startswith("---\n"):
        return False, {}
    end = text.find("\n---", 4)
    if end == -1:
        return False, {}
    fields: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"').strip("'")
    return True, fields


def heading_names(text: str) -> set[str]:
    names: set[str] = set()
    for line in text.splitlines():
        if line.startswith("#"):
            title = line.lstrip("#").strip()
            if title:
                names.add(title.lower())
    return names


def normalize_candidate(raw: str) -> str:
    candidate = raw.strip("`'\"()[],;:")
    while candidate.endswith(".") and not candidate.endswith(".py"):
        candidate = candidate[:-1]
    return candidate.replace("\\", "/")


def resolve_script_ref(raw: str, skill_path: Path, root: Path) -> Path:
    normalized = normalize_candidate(raw)
    if re.match(r"^[A-Za-z]:/", normalized):
        return Path(normalized)
    if normalized.startswith("codex/") or normalized.startswith("AGENTS.md"):
        return root / normalized
    return (skill_path.parent / normalized).resolve()


def find_script_refs(text: str, skill_path: Path, root: Path) -> list[dict[str, str | bool]]:
    refs: list[dict[str, str | bool]] = []
    seen: set[str] = set()
    for match in SCRIPT_REF_RE.finditer(text):
        raw = normalize_candidate(match.group("path"))
        if raw in seen:
            continue
        seen.add(raw)
        resolved = resolve_script_ref(raw, skill_path, root)
        refs.append(
            {
                "raw": raw,
                "resolved": repo_path(resolved, root)
                if str(resolved).startswith(str(root))
                else str(resolved),
                "exists": resolved.exists(),
            }
        )
    return refs


def agent_from_skill_path(path: Path, root: Path) -> str:
    rel = path.relative_to(root).parts
    if len(rel) >= 4 and rel[0] == "codex" and rel[1] == "agents":
        return rel[2]
    return "unknown"


def audit_skills(root: Path) -> list[SkillAudit]:
    audits: list[SkillAudit] = []
    for skill_path in sorted((root / "codex" / "agents").glob("*/skills/*/SKILL.md")):
        text = skill_path.read_text(encoding="utf-8")
        has_frontmatter, fields = parse_frontmatter(text)
        headings = heading_names(text)
        missing_sections = [
            section for section in HARDENING_SECTIONS if section.lower() not in headings
        ]
        lower = text.lower()
        approval_gate_required = any(term in lower for term in PAID_API_TERMS)
        approval_gate_present = any(term in lower for term in APPROVAL_TERMS)
        audits.append(
            SkillAudit(
                path=repo_path(skill_path, root),
                agent=agent_from_skill_path(skill_path, root),
                name=fields.get("name"),
                has_frontmatter=has_frontmatter
                and bool(fields.get("name"))
                and bool(fields.get("description")),
                missing_sections=missing_sections,
                script_refs=find_script_refs(text, skill_path, root),
                approval_gate_required=approval_gate_required,
                approval_gate_present=approval_gate_present,
            )
        )
    return audits


def parse_director_handoff_map(root: Path) -> set[str]:
    agent_path = root / "codex" / "agents" / "director" / "AGENT.md"
    if not agent_path.exists():
        return set()
    text = agent_path.read_text(encoding="utf-8")
    refs: set[str] = set()
    for match in re.finditer(r"`(?P<path>\.\./[^`]+/SKILL\.md)`", text):
        resolved = (agent_path.parent / match.group("path")).resolve()
        if str(resolved).startswith(str(root)):
            refs.add(repo_path(resolved, root))
    return refs


def non_director_skills(audits: Iterable[SkillAudit]) -> set[str]:
    return {audit.path for audit in audits if audit.agent != "director"}


def build_report(root: Path) -> dict[str, object]:
    audits = audit_skills(root)
    handoff_refs = parse_director_handoff_map(root)
    missing_handoff = sorted(non_director_skills(audits) - handoff_refs)
    stale_handoff = sorted(handoff_refs - {audit.path for audit in audits})
    missing_script_refs = [
        {
            "skill": audit.path,
            "script": ref["raw"],
            "resolved": ref["resolved"],
        }
        for audit in audits
        for ref in audit.script_refs
        if not ref["exists"]
    ]
    missing_approval = [
        audit.path
        for audit in audits
        if audit.approval_gate_required and not audit.approval_gate_present
    ]
    missing_frontmatter = [audit.path for audit in audits if not audit.has_frontmatter]
    strong_skills = [audit.path for audit in audits if not audit.missing_sections]
    by_agent: dict[str, dict[str, int]] = {}
    for audit in audits:
        stats = by_agent.setdefault(
            audit.agent,
            {"skills": 0, "strong": 0, "missing_sections": 0},
        )
        stats["skills"] += 1
        stats["missing_sections"] += len(audit.missing_sections)
        if not audit.missing_sections:
            stats["strong"] += 1
    return {
        "repo_root": str(root),
        "summary": {
            "skills": len(audits),
            "non_director_skills": len(non_director_skills(audits)),
            "director_handoff_refs": len(handoff_refs),
            "strong_skills": len(strong_skills),
            "missing_script_refs": len(missing_script_refs),
            "missing_handoff_refs": len(missing_handoff),
            "stale_handoff_refs": len(stale_handoff),
            "skills_missing_frontmatter": len(missing_frontmatter),
            "api_or_paid_skills_missing_approval_terms": len(missing_approval),
        },
        "by_agent": by_agent,
        "missing_script_refs": missing_script_refs,
        "missing_handoff_refs": missing_handoff,
        "stale_handoff_refs": stale_handoff,
        "skills_missing_frontmatter": missing_frontmatter,
        "api_or_paid_skills_missing_approval_terms": missing_approval,
        "skill_hardening": [asdict(audit) for audit in audits],
    }


def print_text_report(report: dict[str, object]) -> None:
    summary = report["summary"]
    print("Video Factory agent audit")
    print("")
    for key, value in summary.items():
        print(f"{key}: {value}")
    print("")
    print("By agent:")
    by_agent = report["by_agent"]
    for agent in sorted(by_agent):
        stats = by_agent[agent]
        avg_missing = (
            stats["missing_sections"] / stats["skills"] if stats["skills"] else 0
        )
        print(
            f"- {agent}: {stats['skills']} skills, "
            f"{stats['strong']} strong, avg missing sections {avg_missing:.1f}"
        )

    checks = [
        ("Missing script references", report["missing_script_refs"]),
        ("Missing Director handoff refs", report["missing_handoff_refs"]),
        ("Stale Director handoff refs", report["stale_handoff_refs"]),
        ("Skills missing frontmatter", report["skills_missing_frontmatter"]),
        (
            "API/paid-looking skills missing approval terms",
            report["api_or_paid_skills_missing_approval_terms"],
        ),
    ]
    for title, values in checks:
        print("")
        print(f"{title}: {len(values)}")
        for value in values:
            print(f"- {value}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root to audit")
    parser.add_argument("--json", action="store_true", help="Print JSON report")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero on missing scripts, handoff drift, missing frontmatter, or approval-gate warnings",
    )
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    report = build_report(root)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_text_report(report)

    summary = report["summary"]
    if args.strict and any(
        summary[key]
        for key in [
            "missing_script_refs",
            "missing_handoff_refs",
            "stale_handoff_refs",
            "skills_missing_frontmatter",
            "api_or_paid_skills_missing_approval_terms",
        ]
    ):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
