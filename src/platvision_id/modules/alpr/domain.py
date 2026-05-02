from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BoundingBox:
    x1: int
    y1: int
    x2: int
    y2: int

    def clamp(self, width: int, height: int) -> "BoundingBox":
        return BoundingBox(
            x1=max(0, min(self.x1, width - 1)),
            y1=max(0, min(self.y1, height - 1)),
            x2=max(0, min(self.x2, width)),
            y2=max(0, min(self.y2, height)),
        )

    @property
    def area(self) -> int:
        return max(0, self.x2 - self.x1) * max(0, self.y2 - self.y1)

    def to_api_response(self) -> dict[str, int]:
        return {"x1": self.x1, "y1": self.y1, "x2": self.x2, "y2": self.y2}


@dataclass(frozen=True)
class Detection:
    box: BoundingBox
    confidence: float
    label: str
    detector_name: str
    fallback_used: bool = False


@dataclass(frozen=True)
class OcrCandidate:
    text: str
    confidence: float
    variant_name: str


@dataclass(frozen=True)
class RegionInfo:
    code: str | None
    name: str

    def to_api_response(self) -> dict[str, str | None]:
        return {"code": self.code, "name": self.name}


@dataclass(frozen=True)
class PlateRecognition:
    raw_text: str
    normalized_plate: str
    confidence: float
    region: RegionInfo
    detection: Detection
    ocr_engine: str
    notes: tuple[str, ...]
    crop_preview: str | None = None
    diagnostics: dict[str, object] | None = None
    tax_info: dict[str, object] | None = None

    def to_api_response(self) -> dict[str, object]:
        diagnostics: dict[str, object] = {
            "detector": self.detection.detector_name,
            "ocr": self.ocr_engine,
            "fallbackUsed": self.detection.fallback_used,
            "notes": list(self.notes),
        }
        if self.diagnostics:
            diagnostics.update(self.diagnostics)

        response: dict[str, object] = {
            "plate": self.normalized_plate,
            "normalizedPlate": self.normalized_plate,
            "rawText": self.raw_text,
            "region": self.region.to_api_response(),
            "confidence": round(self.confidence, 4),
            "box": self.detection.box.to_api_response(),
            "diagnostics": diagnostics,
        }
        if self.crop_preview:
            response["cropPreview"] = self.crop_preview
        if self.tax_info:
            response["tax"] = self.tax_info
        return response
