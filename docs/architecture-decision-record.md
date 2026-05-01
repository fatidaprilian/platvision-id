# Architecture Decision Record

## ADR-001: Flask Monolith With Feature-Oriented ALPR Module

Status: Accepted for the first demo.

### Context

The repository did not contain an existing application runtime. The requested system is a small ALPR demo with one upload workflow, one inference pipeline, and no persistent data. A monolith is the simplest reliable shape because the workflow is synchronous and every step depends on the previous one.

### Decision

Use a Python Flask application with a feature-oriented ALPR module.

- `src/platvision_id/app.py` creates the Flask app and registers routes.
- `src/platvision_id/routes.py` owns HTTP input validation and response mapping.
- `src/platvision_id/modules/alpr/` owns detection, preprocessing, OCR, normalization, and region lookup.
- External ML libraries are wrapped behind small adapters so tests can use fakes.

### Runtime Choice

Python is the best fit because Ultralytics YOLO, PaddleOCR, OpenCV, and scientific image tooling are mature in the Python ecosystem. Flask is enough for the first demo because the app has a small web surface and does not need asynchronous routing, background jobs, or a large API framework.

### Current Official Documentation Signals

- Ultralytics documentation, checked on 2026-04-27, presents YOLO26 as the latest YOLO generation and shows `pip install -U ultralytics` plus `YOLO("yolo26n.pt")` examples.
- PaddleOCR documentation, checked on 2026-04-27, shows the 3.x `PaddleOCR(...).predict(...)` API and states that PaddleOCR depends on PaddlePaddle 3.0 or above.
- Flask documentation, checked on 2026-04-27, recommends `multipart/form-data`, file validation, `secure_filename`, and `MAX_CONTENT_LENGTH` for uploads.

### Consequences

- The app is easy to run for a classroom demo.
- The first version is not a production camera-streaming service.
- The model file remains replaceable by environment variable.
- Accurate plate detection depends on a real custom plate detector, not the generic YOLO fallback model.

### Alternatives Considered

- FastAPI: good for a larger API surface, but unnecessary for one upload workflow.
- Separate frontend SPA: more moving parts than this demo needs.
- Microservices for detection and OCR: operationally too heavy for the current requirements.

## ADR-002: Configurable YOLO Detector With Demo Fallback

Status: Accepted for the first demo.

### Context

The user asked for the newest YOLO path as long as it is available for demo. Latest official Ultralytics docs reference YOLO26, but a generic pretrained model is not the same as an Indonesian license plate detector.

### Decision

Use `models/best.pt` when present. Otherwise use `yolo26n.pt` to keep the demo runnable through the Ultralytics package. If no detection is usable and `PLATVISION_ENABLE_DEMO_FALLBACK=true`, crop the center-lower region and mark the result as `fallback`.

### Consequences

- The demo can run before a custom model is available.
- Result metadata clearly warns when a fallback crop was used.
- Replacing the detector with a trained Roboflow/CVAT/Label Studio model only changes configuration, not the app flow.
