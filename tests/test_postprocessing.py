from platvision_id.modules.alpr.domain import OcrCandidate
from platvision_id.modules.alpr.postprocessing import (
    choose_best_plate_candidate,
    extract_plate_text,
    extract_region_code,
)
from platvision_id.modules.alpr.region_lookup import lookup_region


def test_extract_plate_text_normalizes_indonesian_plate() -> None:
    assert extract_plate_text("plat: d-1234 abc") == "D 1234 ABC"


def test_choose_best_candidate_prefers_plate_pattern() -> None:
    plate_text, candidate = choose_best_plate_candidate(
        [
            OcrCandidate(text="BANDUNG", confidence=0.95, variant_name="raw"),
            OcrCandidate(text="D 1234 ABC", confidence=0.75, variant_name="threshold"),
        ]
    )

    assert plate_text == "D 1234 ABC"
    assert candidate is not None
    assert candidate.variant_name == "threshold"


def test_region_lookup_for_bandung_prefix() -> None:
    assert extract_region_code("D 1234 ABC") == "D"
    region = lookup_region("D")
    assert region.name == "Bandung Raya"
