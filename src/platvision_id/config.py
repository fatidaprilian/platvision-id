from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class AppConfig:
    max_content_length: int
    upload_extensions: frozenset[str]
    yolo_model_path: str
    yolo_confidence: float
    enable_demo_fallback: bool
    enable_tax_lookup: bool
    tax_lookup_timeout: float


def default_model_path() -> str:
    local_model = PROJECT_ROOT / "models" / "best.pt"
    if local_model.exists():
        return str(local_model)
    return "yolo26n.pt"


def load_config() -> AppConfig:
    return AppConfig(
        max_content_length=int(os.getenv("PLATVISION_MAX_CONTENT_LENGTH", str(8 * 1024 * 1024))),
        upload_extensions=frozenset({"jpg", "jpeg", "png", "webp"}),
        yolo_model_path=os.getenv("PLATVISION_YOLO_MODEL", default_model_path()),
        yolo_confidence=float(os.getenv("PLATVISION_YOLO_CONFIDENCE", "0.25")),
        enable_demo_fallback=os.getenv("PLATVISION_ENABLE_DEMO_FALLBACK", "true").lower()
        in {"1", "true", "yes", "on"},
        enable_tax_lookup=os.getenv("PLATVISION_ENABLE_TAX_LOOKUP", "true").lower()
        in {"1", "true", "yes", "on"},
        tax_lookup_timeout=float(os.getenv("PLATVISION_TAX_LOOKUP_TIMEOUT", "8")),
    )
