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

LANGUAGE_ALIASES = {
    "en": "english",
    "eng": "english",
    "english": "english",
    "uk": "ukrainian",
    "ukr": "ukrainian",
    "ua": "ukrainian",
    "ukrainian": "ukrainian",
    "es": "spanish",
    "spa": "spanish",
    "spanish": "spanish",
    "fr": "french",
    "fra": "french",
    "fre": "french",
    "french": "french",
    "de": "german",
    "deu": "german",
    "ger": "german",
    "german": "german",
    "pt": "portuguese",
    "por": "portuguese",
    "portuguese": "portuguese",
    "it": "italian",
    "ita": "italian",
    "italian": "italian",
    "pl": "polish",
    "pol": "polish",
    "polish": "polish",
    "ru": "russian",
    "rus": "russian",
    "russian": "russian",
    "ja": "japanese",
    "jpn": "japanese",
    "japanese": "japanese",
    "zh": "chinese",
    "cmn": "chinese",
    "chinese": "chinese",
}

QUALITY_CATEGORY_POINTS = {
    "professional": 30.0,
    "premade": 22.0,
    "generated": 16.0,
    "cloned": 8.0,
}

RECORDING_QUALITY_POINTS = {
    "studio": 26.0,
    "high": 18.0,
    "clean": 14.0,
    "good": 10.0,
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


def normalize_term(value: Any) -> str:
    text = re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()
    return " ".join(text.split())


def normalize_language(value: Any) -> str:
    text = normalize_term(value)
    return LANGUAGE_ALIASES.get(text, text)


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


def collect_provider_voice_refs(brief: dict[str, Any]) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    direction = nested_voice_direction(brief)
    for container in (
        brief,
        direction,
        brief.get("audio_identity") if isinstance(brief.get("audio_identity"), dict) else {},
        brief.get("voice_profile") if isinstance(brief.get("voice_profile"), dict) else {},
    ):
        for ref in as_list((container or {}).get("provider_voice_refs")):
            if isinstance(ref, dict):
                refs.append(ref)
    return refs


def voice_ref_policy(ref: dict[str, Any]) -> str:
    policy = normalize_term(ref.get("selection_policy")).replace(" ", "_")
    usage = normalize_term(ref.get("usage"))
    if policy:
        return policy
    if any(term in usage for term in ("exact", "locked", "required", "default", "primary", "narrator")):
        return "exact_required"
    if "fallback" in usage:
        return "fallback"
    return "preferred"


def provider_voice_ref_match(voice: dict[str, Any], refs: list[dict[str, Any]]) -> tuple[str | None, dict[str, Any] | None, list[str]]:
    reasons: list[str] = []
    for ref in refs:
        if ref.get("provider") and str(ref.get("provider")).lower() != "elevenlabs":
            continue
        if ref.get("voice_id") and ref.get("voice_id") == voice.get("voice_id"):
            policy = voice_ref_policy(ref)
            reasons.append(f"matches channel provider voice ref: {policy}")
            return policy, ref, reasons
    return None, None, reasons


def nested_voice_direction(brief: dict[str, Any]) -> dict[str, Any]:
    for key in ("voice_direction", "audio_identity", "voice_profile"):
        value = brief.get(key)
        if isinstance(value, dict):
            if key == "audio_identity" and isinstance(value.get("voice_profile"), dict):
                return value["voice_profile"]
            return value
    return {}


def first_text_value(*values: Any) -> str:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, list):
            for item in value:
                nested = first_text_value(item)
                if nested:
                    return nested
    return ""


def infer_target_language(brief: dict[str, Any]) -> str:
    direction = nested_voice_direction(brief)
    return first_text_value(
        brief.get("target_language"),
        brief.get("language"),
        brief.get("language_code"),
        direction.get("target_language"),
        direction.get("language"),
        direction.get("language_code"),
    )


def infer_target_accent(brief: dict[str, Any]) -> str:
    direction = nested_voice_direction(brief)
    return first_text_value(
        brief.get("target_accent"),
        brief.get("accent"),
        brief.get("accent_policy"),
        direction.get("target_accent"),
        direction.get("accent"),
        direction.get("accent_policy"),
    )


def voice_languages(voice: dict[str, Any]) -> set[str]:
    labels = voice.get("labels") or {}
    values = [
        labels.get("language"),
        labels.get("lang"),
        labels.get("locale"),
        voice.get("language"),
    ]
    values.extend(item.get("language") for item in voice.get("verified_languages") or [] if isinstance(item, dict))
    values.extend(item.get("locale") for item in voice.get("verified_languages") or [] if isinstance(item, dict))
    return {normalize_language(value) for value in values if value}


def voice_accents(voice: dict[str, Any]) -> set[str]:
    labels = voice.get("labels") or {}
    values = [
        labels.get("accent"),
        labels.get("dialect"),
        labels.get("locale"),
        voice.get("accent"),
    ]
    values.extend(item.get("accent") for item in voice.get("verified_languages") or [] if isinstance(item, dict))
    values.extend(item.get("locale") for item in voice.get("verified_languages") or [] if isinstance(item, dict))
    return {normalize_term(value) for value in values if value}


def score_quality(voice: dict[str, Any], selected_model_id: str) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []
    category = normalize_term(voice.get("category"))
    if category in QUALITY_CATEGORY_POINTS:
        points = QUALITY_CATEGORY_POINTS[category]
        score += points
        reasons.append(f"quality category: {category}")

    recording_quality = normalize_term(voice.get("recording_quality"))
    if recording_quality in RECORDING_QUALITY_POINTS:
        points = RECORDING_QUALITY_POINTS[recording_quality]
        score += points
        reasons.append(f"recording quality: {recording_quality}")

    high_quality_models = {str(item) for item in voice.get("high_quality_base_model_ids") or []}
    if selected_model_id and selected_model_id in high_quality_models:
        score += 28.0
        reasons.append(f"high-quality base model supports {selected_model_id}")
    elif high_quality_models:
        score += 16.0
        reasons.append("has high-quality base model support")

    fine_tuning_state = (voice.get("fine_tuning") or {}).get("state") or {}
    if selected_model_id and fine_tuning_state.get(selected_model_id) == "fine_tuned":
        score += 16.0
        reasons.append(f"fine-tuned for {selected_model_id}")
    elif "fine_tuned" in {str(value) for value in fine_tuning_state.values()}:
        score += 8.0
        reasons.append("has fine-tuned model state")

    if voice.get("preview_url"):
        score += 4.0
        reasons.append("has preview audio")
    verification = voice.get("voice_verification") or {}
    if verification.get("is_verified"):
        score += 8.0
        reasons.append("voice verified")
    if voice.get("is_legacy"):
        score -= 24.0
        reasons.append("legacy voice penalty")
    if voice.get("is_mixed"):
        score -= 8.0
        reasons.append("mixed voice penalty")

    return score, reasons


def score_language(voice: dict[str, Any], target_language: str) -> tuple[float, bool | None, list[str]]:
    if not target_language:
        return 0.0, None, []
    target = normalize_language(target_language)
    candidates = voice_languages(voice)
    if not candidates:
        return 0.0, None, ["no voice language metadata"]
    if target in candidates or any(target in item or item in target for item in candidates):
        return 36.0, True, [f"target language match: {target_language}"]
    return -80.0, False, [f"target language mismatch: {target_language}"]


def score_accent(voice: dict[str, Any], target_accent: str) -> tuple[float, bool | None, list[str]]:
    if not target_accent:
        return 0.0, None, []
    target = normalize_term(target_accent)
    if target in {"neutral", "unspecified", "any", "global"}:
        return 4.0, None, [f"accent policy: {target_accent}"]
    candidates = voice_accents(voice)
    if not candidates:
        return 0.0, None, ["no voice accent metadata"]
    if target in candidates or any(target in item or item in target for item in candidates):
        return 24.0, True, [f"target accent match: {target_accent}"]
    return -18.0, False, [f"target accent mismatch: {target_accent}"]


def score_style(voice: dict[str, Any], brief_text: str, brief: dict[str, Any]) -> tuple[float, list[str]]:
    haystack = voice_text(voice)
    brief_words = words(brief_text)
    direction = nested_voice_direction(brief)
    score = 0.0
    reasons: list[str] = []

    for term in brief_words:
        if len(term) < 4:
            continue
        if term in haystack:
            score += 0.7
            reasons.append(f"matches '{term}'")

    for style, terms in STYLE_TERMS.items():
        if style in brief_words:
            for term in terms:
                if term in haystack:
                    score += 2.0
                    reasons.append(f"{style} style: {term}")

    labels = {str(k).lower(): str(v).lower() for k, v in (voice.get("labels") or {}).items()}
    for key in ("gender", "accent", "age", "use_case"):
        desired = str(brief.get(key, "")).lower()
        desired = desired or str(direction.get(key, "")).lower()
        if desired and desired in labels.get(key, ""):
            score += 3.0
            reasons.append(f"{key} fits {desired}")

    desired_traits = []
    for key in ("voice_traits", "traits", "tone", "narrator_persona", "energy_profile", "accent_policy"):
        desired_traits.extend(str(item) for item in as_list(direction.get(key) or brief.get(key)))
    for trait in desired_traits:
        for term in words(trait):
            if len(term) >= 4 and term in haystack:
                score += 1.5
                reasons.append(f"channel voice trait: {term}")

    for trait in as_list(direction.get("must_avoid_traits") or brief.get("must_avoid_traits")):
        for term in words(str(trait)):
            if len(term) >= 4 and term in haystack:
                score -= 8.0
                reasons.append(f"avoid trait matched: {term}")

    for criterion in as_list(direction.get("selection_rubric") or brief.get("selection_rubric")):
        if not isinstance(criterion, dict):
            continue
        weight = float(criterion.get("weight") or 1)
        text = " ".join(str(criterion.get(key, "")) for key in ("criterion", "notes"))
        if any(len(term) >= 4 and term in haystack for term in words(text)):
            score += min(weight, 4.0)
            reasons.append(f"rubric fit: {criterion.get('criterion', 'criterion')}")

    return score, reasons[:8]


def score_voice(
    voice: dict[str, Any],
    brief_text: str,
    brief: dict[str, Any],
    target_language: str,
    target_accent: str,
    selected_model_id: str,
    provider_voice_refs: list[dict[str, Any]],
) -> dict[str, Any]:
    ref_policy, ref, ref_reasons = provider_voice_ref_match(voice, provider_voice_refs)
    quality_score, quality_reasons = score_quality(voice, selected_model_id)
    language_score, language_match, language_reasons = score_language(voice, target_language)
    accent_score, accent_match, accent_reasons = score_accent(voice, target_accent)
    style_score, style_reasons = score_style(voice, brief_text, brief)
    ref_score = 0.0
    if ref_policy == "exact_required":
        ref_score = 10000.0
    elif ref_policy == "preferred":
        ref_score = 45.0
    elif ref_policy == "fallback":
        ref_score = 8.0
    elif ref_policy == "blocked":
        ref_score = -10000.0
    total = quality_score + language_score + accent_score + style_score
    total += ref_score
    return {
        "score": round(total, 2),
        "provider_voice_ref_score": round(ref_score, 2),
        "provider_voice_ref_policy": ref_policy,
        "provider_voice_ref": ref,
        "quality_score": round(quality_score, 2),
        "language_score": round(language_score, 2),
        "accent_score": round(accent_score, 2),
        "style_score": round(style_score, 2),
        "target_language_match": language_match,
        "target_accent_match": accent_match,
        "reasons": (ref_reasons + quality_reasons + language_reasons + accent_reasons + style_reasons)[:10],
        "quality_reasons": quality_reasons,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--voice-catalog", required=True)
    parser.add_argument("--voice-brief", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--target-language")
    parser.add_argument("--target-accent")
    parser.add_argument("--selected-model-id", default="eleven_v3")
    args = parser.parse_args()

    catalog = load_json(args.voice_catalog)
    brief_text, brief = load_brief(args.voice_brief)
    voices = catalog if isinstance(catalog, list) else catalog.get("voices", [])
    target_language = args.target_language or infer_target_language(brief)
    target_accent = args.target_accent or infer_target_accent(brief)
    provider_voice_refs = collect_provider_voice_refs(brief)
    exact_voice_ids = {
        str(ref.get("voice_id"))
        for ref in provider_voice_refs
        if ref.get("voice_id") and voice_ref_policy(ref) == "exact_required" and str(ref.get("provider", "elevenlabs")).lower() == "elevenlabs"
    }

    ranked = []
    for voice in voices:
        score = score_voice(
            voice=voice,
            brief_text=brief_text,
            brief=brief,
            target_language=target_language,
            target_accent=target_accent,
            selected_model_id=args.selected_model_id,
            provider_voice_refs=provider_voice_refs,
        )
        ranked.append(drop_none({
            "voice_id": voice.get("voice_id"),
            "name": voice.get("name"),
            "score": score["score"],
            "score_breakdown": {
                "provider_voice_ref": score["provider_voice_ref_score"],
                "quality": score["quality_score"],
                "language": score["language_score"],
                "accent": score["accent_score"],
                "style": score["style_score"],
            },
            "target_language": target_language,
            "target_accent": target_accent,
            "target_language_match": score["target_language_match"],
            "target_accent_match": score["target_accent_match"],
            "selected_model_id": args.selected_model_id,
            "provider_voice_ref_policy": score["provider_voice_ref_policy"],
            "provider_voice_ref_score": score["provider_voice_ref_score"],
            "selection_source": "channel_profile" if score["provider_voice_ref_policy"] == "exact_required" else None,
            "labels": voice.get("labels") or {},
            "preview_url": voice.get("preview_url"),
            "category": voice.get("category"),
            "recording_quality": voice.get("recording_quality"),
            "high_quality_base_model_ids": voice.get("high_quality_base_model_ids"),
            "verified_languages": voice.get("verified_languages"),
            "reasons": score["reasons"],
        }))

    ranked.sort(
        key=lambda item: (
            item.get("provider_voice_ref_policy") != "exact_required",
            item.get("target_language_match") is False,
            item.get("target_accent_match") is False,
            -((item.get("score_breakdown") or {}).get("quality") or 0),
            -(item.get("score") or 0),
        )
    )
    selected = ranked[0] if ranked else None
    exact_selected = bool(exact_voice_ids and selected and selected.get("voice_id") in exact_voice_ids)
    exact_lang_or_accent_blocked = bool(
        exact_selected
        and (selected.get("target_language_match") is False or selected.get("target_accent_match") is False)
    )
    output = drop_none({
        "provider": "elevenlabs",
        "voice_brief_path": args.voice_brief,
        "voice_catalog_path": args.voice_catalog,
        "selected_model_id": args.selected_model_id,
        "target_language": target_language,
        "target_accent": target_accent,
        "exact_channel_voice_ids": sorted(exact_voice_ids),
        "ranking_policy": "quality_first_with_target_language_and_accent_fit",
        "selected_voice": selected,
        "candidates": ranked[: args.top],
        "qa": {
            "status": "pass" if (not exact_voice_ids or exact_selected) and not exact_lang_or_accent_blocked else "fail",
            "summary": (
                "Exact channel voice selected."
                if exact_selected and not exact_lang_or_accent_blocked
                else "Exact channel voice selected but target language/accent compatibility failed."
                if exact_lang_or_accent_blocked
                else "No exact channel voice requirement or exact voice missing from ranked inventory."
            ),
        },
    })

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print(f"selected {selected['name']} ({selected['voice_id']})" if selected else "no voices ranked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
