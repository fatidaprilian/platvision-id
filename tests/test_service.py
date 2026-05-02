from platvision_id.config import AppConfig
from platvision_id.modules.alpr.detector import DemoFallbackDetector
from platvision_id.modules.alpr.domain import BoundingBox, Detection, OcrCandidate
from platvision_id.modules.alpr.preprocessing import ImageVariant
from platvision_id.modules.alpr import service as service_module
from platvision_id.modules.alpr.service import AlprService, build_default_service


class GenericDetector:
    name = "ultralytics"
    uses_generic_demo_model = True

    def detect(self, image):
        return [
            Detection(
                box=BoundingBox(x1=0, y1=0, x2=image.shape[1], y2=image.shape[0]),
                confidence=0.9,
                label="car",
                detector_name=self.name,
            )
        ]


class EmptyPlateDetector:
    name = "ultralytics"
    uses_generic_demo_model = False

    def detect(self, image):
        return []


class WorkingOcrReader:
    name = "fake-ocr"

    def read(self, variants):
        return [OcrCandidate(text="B 2156 TOR", confidence=0.87, variant_name=variants[0].name)]


class FailingOcrReader:
    name = "fake-ocr"

    def read(self, variants):
        raise RuntimeError("ocr runtime failed")


class FakeTaxLookup:
    def lookup(self, normalized_plate: str):
        return {
            "supported": True,
            "status": "found",
            "source": "Bapenda Sumsel",
            "message": f"lookup for {normalized_plate}",
        }


class FakeImage:
    shape = (480, 640, 3)


def test_generic_yolo_detection_uses_demo_fallback_crop(monkeypatch) -> None:
    _patch_image_pipeline(monkeypatch)
    service = AlprService(
        detector=GenericDetector(),
        ocr_reader=WorkingOcrReader(),
        fallback_detector=DemoFallbackDetector(),
    )

    recognition = service.recognize(_sample_image_bytes())

    assert recognition.normalized_plate == "B 2156 TOR"
    assert recognition.detection.fallback_used is True
    assert any("generic" in note for note in recognition.notes)


def test_ocr_runtime_failure_returns_unreadable_result_instead_of_raising(monkeypatch) -> None:
    _patch_image_pipeline(monkeypatch)
    service = AlprService(
        detector=GenericDetector(),
        ocr_reader=FailingOcrReader(),
        fallback_detector=DemoFallbackDetector(),
    )

    recognition = service.recognize(_sample_image_bytes())

    assert recognition.normalized_plate == "UNREADABLE"
    assert any("OCR failed" in note for note in recognition.notes)


def test_default_service_uses_fallback_primary_when_generic_yolo_file_is_missing() -> None:
    config = AppConfig(
        max_content_length=8 * 1024 * 1024,
        upload_extensions=frozenset({"jpg"}),
        yolo_model_path="yolo26n.pt",
        yolo_confidence=0.25,
        enable_demo_fallback=True,
        enable_tax_lookup=False,
        tax_lookup_timeout=8,
    )

    service = build_default_service(config)

    assert isinstance(service.detector, DemoFallbackDetector)


def test_primary_detector_miss_is_reported_in_diagnostics(monkeypatch) -> None:
    _patch_image_pipeline(monkeypatch)
    service = AlprService(
        detector=EmptyPlateDetector(),
        ocr_reader=WorkingOcrReader(),
        fallback_detector=DemoFallbackDetector(),
    )

    recognition = service.recognize(_sample_image_bytes())
    payload = recognition.to_api_response()

    assert recognition.detection.fallback_used is True
    assert payload["diagnostics"]["primaryDetector"] == "ultralytics"
    assert payload["diagnostics"]["primaryDetections"] == 0
    assert payload["diagnostics"]["selectedDetector"] == "demo-fallback"


def test_tax_lookup_is_attached_when_plate_is_readable(monkeypatch) -> None:
    _patch_image_pipeline(monkeypatch)
    service = AlprService(
        detector=EmptyPlateDetector(),
        ocr_reader=WorkingOcrReader(),
        fallback_detector=DemoFallbackDetector(),
        tax_lookup=FakeTaxLookup(),
    )

    payload = service.recognize(_sample_image_bytes()).to_api_response()

    assert payload["tax"]["status"] == "found"
    assert payload["tax"]["message"] == "lookup for B 2156 TOR"


def _sample_image_bytes() -> bytes:
    return b"fake-image"


def _patch_image_pipeline(monkeypatch) -> None:
    monkeypatch.setattr(service_module, "decode_image", lambda _: FakeImage())
    monkeypatch.setattr(service_module, "crop_plate", lambda image, box: object())
    monkeypatch.setattr(service_module, "build_plate_variants", lambda crop: [ImageVariant("raw", object())])
