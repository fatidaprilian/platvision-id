from __future__ import annotations

from pathlib import Path

from ...config import AppConfig
from ...errors import AlprUnavailableError
from .detector import DemoFallbackDetector, PlateDetector, UltralyticsPlateDetector
from .domain import OcrCandidate, PlateRecognition
from .ocr import PaddleOcrReader, PlateOcrReader
from .postprocessing import choose_best_plate_candidate, extract_region_code
from .preprocessing import build_plate_variants, crop_plate, decode_image
from .region_lookup import lookup_region


class AlprService:
    def __init__(
        self,
        detector: PlateDetector,
        ocr_reader: PlateOcrReader,
        fallback_detector: PlateDetector | None = None,
    ) -> None:
        self.detector = detector
        self.ocr_reader = ocr_reader
        self.fallback_detector = fallback_detector

    def recognize(self, image_bytes: bytes) -> PlateRecognition:
        image = decode_image(image_bytes)
        notes: list[str] = []

        try:
            detections = self.detector.detect(image)
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

        return PlateRecognition(
            raw_text=best_candidate.text if best_candidate else "",
            normalized_plate=normalized_plate,
            confidence=confidence,
            region=region,
            detection=selected_detection,
            ocr_engine=self.ocr_reader.name,
            notes=tuple(notes),
        )


def build_default_service(config: AppConfig) -> AlprService:
    fallback_detector = DemoFallbackDetector() if config.enable_demo_fallback else None
    if fallback_detector is not None and _should_use_fallback_as_primary(config.yolo_model_path):
        return AlprService(
            detector=fallback_detector,
            ocr_reader=PaddleOcrReader(),
        )

    return AlprService(
        detector=UltralyticsPlateDetector(
            model_path=config.yolo_model_path,
            confidence=config.yolo_confidence,
        ),
        ocr_reader=PaddleOcrReader(),
        fallback_detector=fallback_detector,
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
