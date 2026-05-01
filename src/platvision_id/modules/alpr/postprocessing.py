from __future__ import annotations

import re

from .domain import OcrCandidate


PLATE_PATTERN = re.compile(r"\b([A-Z]{1,2})\s*([0-9]{1,4})\s*([A-Z]{0,3})\b")


def normalize_ocr_text(text: str) -> str:
    uppercase = text.upper()
    cleaned = re.sub(r"[^A-Z0-9\s]", " ", uppercase)
    return re.sub(r"\s+", " ", cleaned).strip()


def extract_plate_text(text: str) -> str:
    normalized = normalize_ocr_text(text)
    match = PLATE_PATTERN.search(normalized)
    if not match:
        return normalized

    prefix, number, suffix = match.groups()
    return " ".join(part for part in (prefix, number, suffix) if part)


def choose_best_plate_candidate(candidates: list[OcrCandidate]) -> tuple[str, OcrCandidate | None]:
    if not candidates:
        return "", None

    ranked = sorted(candidates, key=_candidate_score, reverse=True)
    best_candidate = ranked[0]
    return extract_plate_text(best_candidate.text), best_candidate


def extract_region_code(plate_text: str) -> str | None:
    match = re.match(r"^([A-Z]{1,2})\b", normalize_ocr_text(plate_text))
    return match.group(1) if match else None


def _candidate_score(candidate: OcrCandidate) -> float:
    normalized = normalize_ocr_text(candidate.text)
    pattern_bonus = 0.35 if PLATE_PATTERN.search(normalized) else 0.0
    length_penalty = min(abs(len(normalized) - 10) * 0.01, 0.12)
    return candidate.confidence + pattern_bonus - length_penalty
