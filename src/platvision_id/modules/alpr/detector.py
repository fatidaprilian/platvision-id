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
        height, width = image.shape[:2]
        box_width = int(width * 0.46)
        box_height = int(height * 0.16)
        x1 = int((width - box_width) / 2)
        y1 = int(height * 0.58)
        return [
            Detection(
                box=BoundingBox(x1=x1, y1=y1, x2=x1 + box_width, y2=y1 + box_height),
                confidence=0.15,
                label="demo-center-lower-crop",
                detector_name=self.name,
                fallback_used=True,
            )
        ]
