from __future__ import annotations

import base64
from pathlib import Path

from ...config import AppConfig
from ...errors import AlprUnavailableError
from .detector import DemoFallbackDetector, PlateDetector, UltralyticsPlateDetector
from .domain import OcrCandidate, PlateRecognition
from .ocr import PaddleOcrReader, PlateOcrReader
from .postprocessing import choose_best_plate_candidate, extract_region_code
from .preprocessing import build_plate_variants, crop_plate, decode_image
from .region_lookup import lookup_region
from .tax_lookup import OfficialTaxLookup, TaxLookup


class AlprService:
    def __init__(
        self,
        detector: PlateDetector,
        ocr_reader: PlateOcrReader,
        fallback_detector: PlateDetector | None = None,
        tax_lookup: TaxLookup | None = None,
    ) -> None:
        self.detector = detector
        self.ocr_reader = ocr_reader
        self.fallback_detector = fallback_detector
        self.tax_lookup = tax_lookup

    def recognize(self, image_bytes: bytes) -> PlateRecognition:
        image = decode_image(image_bytes)
        notes: list[str] = []
        primary_detector_name = self.detector.name
        primary_detection_count = 0
        primary_best_confidence: float | None = None

        try:
            detections = self.detector.detect(image)
            primary_detection_count = len(detections)
            primary_best_confidence = max((detection.confidence for detection in detections), default=None)
        except Exception:
            if self.fallback_detector is None:
                raise
            detections = []
            notes.append("The detector failed to load or run, so the demo fallback crop was used.")

        if _should_prefer_demo_fallback(self.detector, detections) and self.fallback_detector is not None:
            detections = []
            notes.append("The default YOLO model is generic, so the demo fallback crop was used until a trained plate model is provided.")

        if not detections and self.fallback_detector is not None:
            detections = self.fallback_detector.detect(image)
            notes.append("No YOLO plate detection was usable, so the demo fallback crop was used.")

        if not detections:
            raise AlprUnavailableError(
                "alpr_unavailable",
                "No license plate candidate was detected. Try another image or provide a trained plate model.",
            )

        selected_detection = detections[0]
        if selected_detection.fallback_used:
            notes.append("Fallback crop is for demo only and is not a trained plate localization result.")

        plate_crop = crop_plate(image, selected_detection.box)
        variants = build_plate_variants(plate_crop)
        try:
            ocr_candidates = self.ocr_reader.read(variants)
        except Exception:
            ocr_candidates = []
            notes.append("OCR failed at runtime. The image was localized, but text recognition did not complete.")

        normalized_plate, best_candidate = choose_best_plate_candidate(ocr_candidates)

        if not normalized_plate:
            normalized_plate = "UNREADABLE"
            notes.append("OCR did not return a readable Indonesian plate pattern.")

        region = lookup_region(extract_region_code(normalized_plate))
        confidence = _combined_confidence(selected_detection.confidence, best_candidate)
        crop_preview = _encode_crop_preview(plate_crop)
        tax_info = self._lookup_tax(normalized_plate, notes)

        return PlateRecognition(
            raw_text=best_candidate.text if best_candidate else "",
            normalized_plate=normalized_plate,
            confidence=confidence,
            region=region,
            detection=selected_detection,
            ocr_engine=self.ocr_reader.name,
            notes=tuple(notes),
            crop_preview=crop_preview,
            diagnostics={
                "primaryDetector": primary_detector_name,
                "primaryDetections": primary_detection_count,
                "primaryBestConfidence": round(primary_best_confidence, 4) if primary_best_confidence is not None else None,
                "selectedDetector": selected_detection.detector_name,
                "selectedConfidence": round(selected_detection.confidence, 4),
            },
            tax_info=tax_info,
        )

    def _lookup_tax(self, normalized_plate: str, notes: list[str]) -> dict[str, object] | None:
        if self.tax_lookup is None or normalized_plate == "UNREADABLE":
            return None
        try:
            return self.tax_lookup.lookup(normalized_plate)
        except Exception:
            notes.append("Tax lookup failed at runtime, but ALPR recognition completed.")
            return {
                "supported": True,
                "status": "lookup_failed",
                "source": "Bapenda Sumsel",
                "message": "Tax lookup failed at runtime.",
            }


def build_default_service(config: AppConfig) -> AlprService:
    fallback_detector = DemoFallbackDetector() if config.enable_demo_fallback else None
    if fallback_detector is not None and _should_use_fallback_as_primary(config.yolo_model_path):
        return AlprService(
            detector=fallback_detector,
            ocr_reader=PaddleOcrReader(),
            tax_lookup=OfficialTaxLookup(config.tax_lookup_timeout) if config.enable_tax_lookup else None,
        )

    return AlprService(
        detector=UltralyticsPlateDetector(
            model_path=config.yolo_model_path,
            confidence=config.yolo_confidence,
        ),
        ocr_reader=PaddleOcrReader(),
        fallback_detector=fallback_detector,
        tax_lookup=OfficialTaxLookup(config.tax_lookup_timeout) if config.enable_tax_lookup else None,
    )


def _combined_confidence(detection_confidence: float, candidate: OcrCandidate | None) -> float:
    if candidate is None:
        return detection_confidence * 0.4
    return (detection_confidence * 0.45) + (candidate.confidence * 0.55)


def _should_prefer_demo_fallback(detector: PlateDetector, detections) -> bool:
    if not getattr(detector, "uses_generic_demo_model", False):
        return False
    return not any("plate" in detection.label.lower() for detection in detections)


def _should_use_fallback_as_primary(model_path: str) -> bool:
    model_name = Path(model_path).name
    return model_name.startswith("yolo") and model_name.endswith(".pt") and not Path(model_path).exists()


def _encode_crop_preview(crop) -> str | None:
    try:
        import cv2

        success, encoded = cv2.imencode(".jpg", crop, [int(cv2.IMWRITE_JPEG_QUALITY), 82])
    except Exception:
        return None
    if not success:
        return None
    image_base64 = base64.b64encode(encoded.tobytes()).decode("ascii")
    return f"data:image/jpeg;base64,{image_base64}"
