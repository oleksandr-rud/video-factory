#!/usr/bin/env python3
"""Rank an ElevenLabs voice catalog against a video voice brief."""

from __future__ import annotations

import argparse
import json
import os
import re
from typing import Any


STYLE_TERMS = {
    "documentary": ["documentary", "authoritative", "calm", "clear", "trustworthy"],
    "cinematic": ["cinematic", "dramatic", "deep", "epic", "narration"],
    "social": ["social", "energetic", "expressive", "conversational", "friendly"],
    "tutorial": ["tutorial", "clear", "educational", "warm", "confident"],
    "luxury": ["luxury", "premium", "smooth", "calm", "elegant"],
    "urgent": ["urgent", "fast", "energetic", "intense", "news"],
    "calm": ["calm", "soft", "warm", "relaxed", "steady"],
    "technical": ["technical", "clear", "precise", "professional", "explainer"],
}


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def load_brief(path: str) -> tuple[str, dict[str, Any]]:
    raw = open(path, "r", encoding="utf-8-sig").read()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return raw, {}
    return json.dumps(parsed, ensure_ascii=False), parsed if isinstance(parsed, dict) else {}


def drop_none(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: drop_none(item) for key, item in value.items() if item is not None}
    if isinstance(value, list):
        return [drop_none(item) for item in value]
    return value


def words(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def voice_text(voice: dict[str, Any]) -> str:
    labels = voice.get("labels") or {}
    parts = [
        str(voice.get("name", "")),
        str(voice.get("category", "")),
        str(voice.get("description", "")),
        " ".join(f"{k} {v}" for k, v in labels.items()),
    ]
    return " ".join(parts).lower()


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def nested_voice_direction(brief: dict[str, Any]) -> dict[str, Any]:
    for key in ("voice_direction", "audio_identity", "voice_profile"):
        value = brief.get(key)
        if isinstance(value, dict):
            if key == "audio_identity" and isinstance(value.get("voice_profile"), dict):
                return value["voice_profile"]
            return value
    return {}


def score_voice(voice: dict[str, Any], brief_text: str, brief: dict[str, Any]) -> tuple[float, list[str]]:
    haystack = voice_text(voice)
    brief_words = words(brief_text)
    direction = nested_voice_direction(brief)
    score = 0.0
    reasons: list[str] = []

    for term in brief_words:
        if len(term) < 4:
            continue
        if term in haystack:
            score += 2.0
            reasons.append(f"matches '{term}'")

    for style, terms in STYLE_TERMS.items():
        if style in brief_words:
            for term in terms:
                if term in haystack:
                    score += 3.0
                    reasons.append(f"{style} style: {term}")

    labels = {str(k).lower(): str(v).lower() for k, v in (voice.get("labels") or {}).items()}
    for key in ("gender", "accent", "age", "use_case"):
        desired = str(brief.get(key, "")).lower()
        desired = desired or str(direction.get(key, "")).lower()
        if desired and desired in labels.get(key, ""):
            score += 5.0
            reasons.append(f"{key} fits {desired}")

    for ref in as_list(direction.get("provider_voice_refs")) + as_list(brief.get("provider_voice_refs")):
        if isinstance(ref, dict) and ref.get("voice_id") and ref.get("voice_id") == voice.get("voice_id"):
            score += 20.0
            reasons.append("matches channel provider voice reference")

    desired_traits = []
    for key in ("voice_traits", "traits", "tone", "narrator_persona", "energy_profile", "accent_policy"):
        desired_traits.extend(str(item) for item in as_list(direction.get(key) or brief.get(key)))
    for trait in desired_traits:
        for term in words(trait):
            if len(term) >= 4 and term in haystack:
                score += 4.0
                reasons.append(f"channel voice trait: {term}")

    for trait in as_list(direction.get("must_avoid_traits") or brief.get("must_avoid_traits")):
        for term in words(str(trait)):
            if len(term) >= 4 and term in haystack:
                score -= 6.0
                reasons.append(f"avoid trait matched: {term}")

    for criterion in as_list(direction.get("selection_rubric") or brief.get("selection_rubric")):
        if not isinstance(criterion, dict):
            continue
        weight = float(criterion.get("weight") or 1)
        text = " ".join(str(criterion.get(key, "")) for key in ("criterion", "notes"))
        if any(len(term) >= 4 and term in haystack for term in words(text)):
            score += weight
            reasons.append(f"rubric fit: {criterion.get('criterion', 'criterion')}")

    if voice.get("preview_url"):
        score += 0.5
    if voice.get("category") in {"professional", "premade", "generated"}:
        score += 0.5

    return score, reasons[:8]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--voice-catalog", required=True)
    parser.add_argument("--voice-brief", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--top", type=int, default=5)
    args = parser.parse_args()

    catalog = load_json(args.voice_catalog)
    brief_text, brief = load_brief(args.voice_brief)
    voices = catalog if isinstance(catalog, list) else catalog.get("voices", [])

    ranked = []
    for voice in voices:
        score, reasons = score_voice(voice, brief_text, brief)
        ranked.append(drop_none({
            "voice_id": voice.get("voice_id"),
            "name": voice.get("name"),
            "score": round(score, 2),
            "labels": voice.get("labels") or {},
            "preview_url": voice.get("preview_url"),
            "category": voice.get("category"),
            "reasons": reasons,
        }))

    ranked.sort(key=lambda item: item["score"], reverse=True)
    selected = ranked[0] if ranked else None
    output = drop_none({
        "provider": "elevenlabs",
        "voice_brief_path": args.voice_brief,
        "voice_catalog_path": args.voice_catalog,
        "selected_voice": selected,
        "candidates": ranked[: args.top],
    })

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print(f"selected {selected['name']} ({selected['voice_id']})" if selected else "no voices ranked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
