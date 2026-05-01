from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Protocol

from ...errors import AlprUnavailableError
from .domain import OcrCandidate
from .preprocessing import ImageVariant


class PlateOcrReader(Protocol):
    name: str

    def read(self, variants: list[ImageVariant]) -> list[OcrCandidate]:
        raise NotImplementedError


class PaddleOcrReader:
    name = "paddleocr"

    def __init__(self) -> None:
        self._ocr = None

    def read(self, variants: list[ImageVariant]) -> list[OcrCandidate]:
        ocr = self._load_ocr()
        candidates: list[OcrCandidate] = []

        for variant in variants:
            candidates.extend(self._read_variant(ocr, variant))

        return candidates

    def _load_ocr(self):
        if self._ocr is not None:
            return self._ocr

        try:
            from paddleocr import PaddleOCR
        except ImportError as exc:
            raise AlprUnavailableError(
                "alpr_unavailable",
                "PaddleOCR is not installed. Install the project dependencies first.",
            ) from exc

        try:
            self._ocr = PaddleOCR(
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
            )
        except TypeError:
            self._ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
        return self._ocr

    def _read_variant(self, ocr, variant: ImageVariant) -> list[OcrCandidate]:
        import cv2

        with tempfile.TemporaryDirectory() as temp_dir:
            image_path = Path(temp_dir) / f"{variant.name}.png"
            cv2.imwrite(str(image_path), variant.image)

            if hasattr(ocr, "predict"):
                output = ocr.predict(str(image_path))
                return _parse_predict_output(output, variant.name)

            output = ocr.ocr(str(image_path), cls=True)
            return _parse_legacy_output(output, variant.name)


def _parse_predict_output(output, variant_name: str) -> list[OcrCandidate]:
    candidates: list[OcrCandidate] = []
    for page in output or []:
        payload = getattr(page, "json", None)
        if callable(payload):
            page_data = payload
        elif isinstance(page, dict):
            page_data = page
        else:
            page_data = getattr(page, "res", {})

        result = page_data.get("res", page_data) if isinstance(page_data, dict) else {}
        texts = result.get("rec_texts", []) if isinstance(result, dict) else []
        scores = result.get("rec_scores", []) if isinstance(result, dict) else []
        for index, text in enumerate(texts):
            score = float(scores[index]) if index < len(scores) else 0.0
            if text:
                candidates.append(OcrCandidate(text=str(text), confidence=score, variant_name=variant_name))
    return candidates


def _parse_legacy_output(output, variant_name: str) -> list[OcrCandidate]:
    candidates: list[OcrCandidate] = []
    for page in output or []:
        for line in page or []:
            if len(line) < 2:
                continue
            text_payload = line[1]
            if not text_payload:
                continue
            text = str(text_payload[0])
            score = float(text_payload[1]) if len(text_payload) > 1 else 0.0
            candidates.append(OcrCandidate(text=text, confidence=score, variant_name=variant_name))
    return candidates
