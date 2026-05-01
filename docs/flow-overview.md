# Flow Overview

## Upload And Recognition Flow

1. The browser submits an image to `POST /api/recognize` as `multipart/form-data`.
2. The Flask route validates the file field, filename, extension, and content length.
3. The route reads the image bytes and delegates to the ALPR service.
4. The ALPR service decodes the image with OpenCV.
5. The YOLO detector returns bounding box candidates.
6. The service picks the strongest candidate.
7. The cropper extracts the plate area and creates preprocessing variants.
8. The OCR reader evaluates the crop variants.
9. The post-processing step normalizes text into an Indonesian plate pattern.
10. The region lookup maps the plate prefix to a likely registration area.
11. The API returns plate text, region, confidence, bounding box, and pipeline notes.

## Error Flow

- Missing file returns `400` with code `missing_file`.
- Empty filename returns `400` with code `empty_filename`.
- Unsupported file type returns `400` with code `unsupported_file_type`.
- Image decode failure returns `400` with code `invalid_image`.
- Missing detector or OCR dependency returns `503` with code `alpr_unavailable`.
- Unexpected server failures return `500` with code `internal_error` without leaking stack traces.

## Model Flow

1. The detector checks `PLATVISION_YOLO_MODEL`.
2. If unset, it uses `models/best.pt` when the file exists.
3. If no trained local model exists, the demo uses the controlled fallback crop instead of failing on a generic YOLO download.
4. When a real YOLO model is configured, it is loaded lazily and reused for later requests.

## OCR Flow

1. PaddleOCR is initialized lazily.
2. The reader first tries the PaddleOCR 3.x `predict` API.
3. The adapter also supports common legacy result shapes for easier local compatibility.
4. The best candidate is selected by OCR confidence and plate-pattern plausibility.

## Demo Limitation

The fallback YOLO model is a generic detector. It keeps the app demonstrable, but accurate plate localization requires a trained license plate detector saved as `models/best.pt`.
