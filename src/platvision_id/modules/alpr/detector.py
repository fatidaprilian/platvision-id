from __future__ import annotations

from pathlib import Path
from typing import Protocol

from ...errors import AlprUnavailableError
from .domain import BoundingBox, Detection


class PlateDetector(Protocol):
    name: str

    def detect(self, image) -> list[Detection]:
        raise NotImplementedError


class UltralyticsPlateDetector:
    name = "ultralytics"

    def __init__(self, model_path: str, confidence: float) -> None:
        self.model_path = model_path
        self.confidence = confidence
        self._model = None

    def detect(self, image) -> list[Detection]:
        model = self._load_model()
        results = model.predict(image, conf=self.confidence, verbose=False)
        detections: list[Detection] = []

        for prediction in results:
            names = getattr(prediction, "names", {}) or {}
            boxes = getattr(prediction, "boxes", None)
            if boxes is None:
                continue
            for box in boxes:
                coordinates = box.xyxy[0].detach().cpu().tolist()
                confidence = float(box.conf[0].detach().cpu().item())
                class_id = int(box.cls[0].detach().cpu().item()) if box.cls is not None else -1
                label = str(names.get(class_id, class_id))
                detections.append(
                    Detection(
                        box=BoundingBox(
                            x1=int(round(coordinates[0])),
                            y1=int(round(coordinates[1])),
                            x2=int(round(coordinates[2])),
                            y2=int(round(coordinates[3])),
                        ),
                        confidence=confidence,
                        label=label,
                        detector_name=self.name,
                    )
                )

        return sorted(detections, key=lambda detection: detection.confidence, reverse=True)

    def _load_model(self):
        if self._model is not None:
            return self._model

        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise AlprUnavailableError(
                "alpr_unavailable",
                "Ultralytics is not installed. Install the project dependencies first.",
            ) from exc

        self._model = YOLO(self.model_path)
        return self._model

    @property
    def uses_generic_demo_model(self) -> bool:
        return Path(self.model_path).name.startswith("yolo") and Path(self.model_path).suffix == ".pt"


class DemoFallbackDetector:
    name = "demo-fallback"

    def detect(self, image) -> list[Detection]:
        plate_like_box = self._detect_plate_like_region(image)
        if plate_like_box is not None:
            return [
                Detection(
                    box=plate_like_box,
                    confidence=0.28,
                    label="demo-plate-like-crop",
                    detector_name=self.name,
                    fallback_used=True,
                )
            ]

        fixed_box = self._fixed_center_lower_box(image)
        return [
            Detection(
                box=fixed_box,
                confidence=0.15,
                label="demo-center-lower-crop",
                detector_name=self.name,
                fallback_used=True,
            )
        ]

    def _detect_plate_like_region(self, image) -> BoundingBox | None:
        try:
            import cv2
        except ImportError:
            return None

        height, width = image.shape[:2]
        if width <= 0 or height <= 0:
            return None

        if len(image.shape) == 3:
            grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            grayscale = image

        blurred = cv2.GaussianBlur(grayscale, (5, 5), 0)
        _, bright_mask = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel_width = max(9, width // 18)
        kernel_height = max(3, height // 120)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_width, kernel_height))
        closed = cv2.morphologyEx(bright_mask, cv2.MORPH_CLOSE, kernel, iterations=1)
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        best_box: BoundingBox | None = None
        best_score = 0.0
        image_area = width * height
        for contour in contours:
            x, y, box_width, box_height = cv2.boundingRect(contour)
            if box_width <= 0 or box_height <= 0:
                continue

            aspect_ratio = box_width / box_height
            area_ratio = (box_width * box_height) / image_area
            if not 1.8 <= aspect_ratio <= 8.5:
                continue
            if not 0.025 <= area_ratio <= 0.65:
                continue

            roi = bright_mask[y : y + box_height, x : x + box_width]
            fill_ratio = float(cv2.countNonZero(roi)) / float(box_width * box_height)
            if fill_ratio < 0.35:
                continue

            vertical_position_penalty = abs((y + box_height / 2) / height - 0.42)
            score = (area_ratio * 2.4) + (fill_ratio * 0.75) - (vertical_position_penalty * 0.2)
            if score > best_score:
                best_score = score
                best_box = BoundingBox(x1=x, y1=y, x2=x + box_width, y2=y + box_height).clamp(width, height)

        return best_box

    def _fixed_center_lower_box(self, image) -> BoundingBox:
        height, width = image.shape[:2]
        box_width = int(width * 0.46)
        box_height = int(height * 0.16)
        x1 = int((width - box_width) / 2)
        y1 = int(height * 0.58)
        return BoundingBox(x1=x1, y1=y1, x2=x1 + box_width, y2=y1 + box_height)
