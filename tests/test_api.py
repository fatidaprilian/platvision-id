from io import BytesIO

import pytest

from platvision_id.app import create_app
from platvision_id.config import AppConfig
from platvision_id.modules.alpr.domain import BoundingBox, Detection, PlateRecognition, RegionInfo


class FakeAlprService:
    def recognize(self, image_bytes: bytes) -> PlateRecognition:
        assert image_bytes
        return PlateRecognition(
            raw_text="D 1234 ABC",
            normalized_plate="D 1234 ABC",
            confidence=0.88,
            region=RegionInfo(code="D", name="Bandung Raya"),
            detection=Detection(
                box=BoundingBox(x1=1, y1=2, x2=3, y2=4),
                confidence=0.9,
                label="plate",
                detector_name="fake-yolo",
            ),
            ocr_engine="fake-ocr",
            notes=(),
        )


@pytest.fixture()
def app():
    config = AppConfig(
        max_content_length=8 * 1024 * 1024,
        upload_extensions=frozenset({"jpg", "jpeg", "png", "webp"}),
        yolo_model_path="yolo26n.pt",
        yolo_confidence=0.25,
        enable_demo_fallback=True,
    )
    return create_app(config, FakeAlprService())


@pytest.fixture()
def client(app):
    return app.test_client()


def test_health(client) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["model"] == "yolo26n.pt"


def test_recognize_returns_plate_response(client) -> None:
    response = client.post(
        "/api/recognize",
        data={"image": (BytesIO(b"not-empty"), "vehicle.jpg")},
        content_type="multipart/form-data",
    )

    payload = response.get_json()
    assert response.status_code == 200
    assert payload["normalizedPlate"] == "D 1234 ABC"
    assert payload["region"]["name"] == "Bandung Raya"
    assert payload["diagnostics"]["detector"] == "fake-yolo"


def test_recognize_rejects_unsupported_extension(client) -> None:
    response = client.post(
        "/api/recognize",
        data={"image": (BytesIO(b"not-empty"), "vehicle.txt")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.get_json()["code"] == "unsupported_file_type"
