#!/usr/bin/env python3
"""ElevenLabs model policy for Creative Producer scripts.

Keep this file small and explicit so dry-run payloads record why a model was
selected. Use `fetch_elevenlabs_models.py` to snapshot account-visible models
when provider access is approved.
"""

from __future__ import annotations

from dataclasses import dataclass


DEFAULT_MODEL_PROFILE = "highest_quality"


@dataclass(frozen=True)
class ElevenLabsModel:
    model_id: str
    profile: str
    quality_score: int
    description: str
    character_limit: int
    languages: str
    credit_unit_note: str
    endpoint_note: str
    selection_note: str


MODEL_CATALOG: dict[str, ElevenLabsModel] = {
    "eleven_v3": ElevenLabsModel(
        model_id="eleven_v3",
        profile="highest_quality",
        quality_score=100,
        description="Latest highest-fidelity text-to-speech model for expressive content narration.",
        character_limit=5000,
        languages="70+ languages",
        credit_unit_note="Base pricing is per character, before voice/account modifiers.",
        endpoint_note="Use Text to Speech with timestamps for single narrator; use Text to Dialogue with timestamps for multi-speaker dialogue.",
        selection_note="Quality-first default for Creative Producer ElevenLabs narration; choose lower-quality models only for explicit latency, budget, or chunk-size constraints.",
    ),
    "eleven_flash_v2_5": ElevenLabsModel(
        model_id="eleven_flash_v2_5",
        profile="fast_balanced",
        quality_score=78,
        description="Current fast and lower-latency model; preferred replacement for Turbo v2.5.",
        character_limit=40000,
        languages="32 languages",
        credit_unit_note="Flash/Turbo base pricing is commonly one credit per two characters, before modifiers.",
        endpoint_note="Use when low latency, lower cost, or long chunks matter; normalize numbers before generation when needed.",
        selection_note="Use for high-volume, speed-sensitive, or budget-sensitive narration.",
    ),
    "eleven_multilingual_v2": ElevenLabsModel(
        model_id="eleven_multilingual_v2",
        profile="stable_content",
        quality_score=90,
        description="Stable high-quality multilingual model for professional content narration.",
        character_limit=10000,
        languages="29 languages",
        credit_unit_note="Base pricing is per character, before voice/account modifiers.",
        endpoint_note="Timestamped TTS endpoint defaults to this model when no model_id is supplied.",
        selection_note="Use when long-form consistency, text normalization, or conservative narration quality matters more than latest expressiveness.",
    ),
    "eleven_flash_v2": ElevenLabsModel(
        model_id="eleven_flash_v2",
        profile="fast_english",
        quality_score=70,
        description="Fast English-only model for low-latency generation.",
        character_limit=30000,
        languages="English",
        credit_unit_note="Flash/Turbo base pricing is commonly one credit per two characters, before modifiers.",
        endpoint_note="Use only for English low-latency work when v2.5 is not needed.",
        selection_note="Fallback for English-only speed-sensitive narration.",
    ),
}


PROFILE_TO_MODEL_ID = {
    "highest_quality": "eleven_v3",
    "quality": "eleven_v3",
    "quality_first": "eleven_v3",
    "content_creation": "eleven_v3",
    "latest": "eleven_v3",
    "latest_expressive": "eleven_v3",
    "expressive": "eleven_v3",
    "dialogue": "eleven_v3",
    "performance": "eleven_v3",
    "fast": "eleven_flash_v2_5",
    "fast_balanced": "eleven_flash_v2_5",
    "balanced": "eleven_flash_v2_5",
    "low_latency": "eleven_flash_v2_5",
    "budget": "eleven_flash_v2_5",
    "stable": "eleven_multilingual_v2",
    "stable_content": "eleven_multilingual_v2",
    "content": "eleven_multilingual_v2",
    "longform": "eleven_multilingual_v2",
    "english_fast": "eleven_flash_v2",
}


DEPRECATED_REPLACEMENTS = {
    "eleven_monolingual_v1": "eleven_multilingual_v2",
    "eleven_multilingual_v1": "eleven_multilingual_v2",
    "eleven_turbo_v2_5": "eleven_flash_v2_5",
    "eleven_turbo_v2": "eleven_flash_v2",
}


def model_id_for_profile(profile: str | None) -> str:
    return PROFILE_TO_MODEL_ID.get((profile or DEFAULT_MODEL_PROFILE).strip().lower(), PROFILE_TO_MODEL_ID[DEFAULT_MODEL_PROFILE])


def resolve_model(model_id: str | None = None, profile: str | None = None, allow_deprecated: bool = False) -> tuple[str, ElevenLabsModel, list[str]]:
    selected = (model_id or model_id_for_profile(profile)).strip()
    notes: list[str] = []
    replacement = DEPRECATED_REPLACEMENTS.get(selected)
    if replacement and not allow_deprecated:
        notes.append(f"replaced deprecated {selected} with {replacement}")
        selected = replacement
    elif replacement:
        notes.append(f"deprecated model explicitly allowed: {selected}; suggested replacement is {replacement}")

    metadata = MODEL_CATALOG.get(selected)
    if metadata is None:
        metadata = ElevenLabsModel(
            model_id=selected,
            profile="account_visible_or_custom",
            quality_score=0,
            description="Model was not in the local policy catalog; verify with GET /v1/models before generation.",
            character_limit=0,
            languages="unknown",
            credit_unit_note="Unknown; verify in ElevenLabs account/docs before approval.",
            endpoint_note="Verify can_do_text_to_speech through GET /v1/models before generation.",
            selection_note="Explicit model override.",
        )
        notes.append("model_id is not in local policy catalog")
    return selected, metadata, notes


def model_metadata_dict(model: ElevenLabsModel) -> dict[str, object]:
    return {
        "model_id": model.model_id,
        "model_profile": model.profile,
        "quality_score": model.quality_score,
        "description": model.description,
        "character_limit": model.character_limit,
        "languages": model.languages,
        "credit_unit_note": model.credit_unit_note,
        "endpoint_note": model.endpoint_note,
        "selection_note": model.selection_note,
    }


def estimate_credit_units(character_count: int, model_id: str) -> str:
    if model_id in {"eleven_flash_v2_5", "eleven_flash_v2", "eleven_turbo_v2_5", "eleven_turbo_v2"}:
        units = (character_count + 1) // 2
        return f"about {units} base character-credit units for {character_count} characters, before modifiers"
    return f"about {character_count} base character-credit units for {character_count} characters, before modifiers"
