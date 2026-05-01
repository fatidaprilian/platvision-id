from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ...errors import InvalidImageError
from .domain import BoundingBox


@dataclass(frozen=True)
class ImageVariant:
    name: str
    image: Any


def decode_image(image_bytes: bytes) -> Any:
    import cv2
    import numpy as np

    buffer = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    if image is None:
        raise InvalidImageError()
    return image


def crop_plate(image: Any, box: BoundingBox, padding_ratio: float = 0.08) -> Any:
    height, width = image.shape[:2]
    clamped = box.clamp(width, height)
    pad_x = int((clamped.x2 - clamped.x1) * padding_ratio)
    pad_y = int((clamped.y2 - clamped.y1) * padding_ratio)
    padded = BoundingBox(
        x1=clamped.x1 - pad_x,
        y1=clamped.y1 - pad_y,
        x2=clamped.x2 + pad_x,
        y2=clamped.y2 + pad_y,
    ).clamp(width, height)

    if padded.area <= 0:
        raise InvalidImageError()
    return image[padded.y1 : padded.y2, padded.x1 : padded.x2]


def build_plate_variants(crop: Any) -> list[ImageVariant]:
    import cv2
    import numpy as np

    variants = [ImageVariant("raw", crop)]
    grayscale = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    variants.append(ImageVariant("grayscale", grayscale))

    equalized = cv2.equalizeHist(grayscale)
    variants.append(ImageVariant("equalized", equalized))

    threshold = cv2.adaptiveThreshold(
        equalized,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        7,
    )
    variants.append(ImageVariant("adaptive-threshold", threshold))

    sharpen_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(equalized, -1, sharpen_kernel)
    variants.append(ImageVariant("sharpened", sharpened))
    return variants
