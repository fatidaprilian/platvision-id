# Platvision ID Project Brief

## Purpose

Platvision ID is a demo Automatic License Plate Recognition (ALPR) web application for Indonesian vehicle plates. The first version lets a user upload an image, detects the plate area with a YOLO-family object detector, reads the cropped plate with Optical Character Recognition (OCR), and maps the front plate code to an Indonesian region.

## Confirmed Requirements

- The system must use the newest available Ultralytics YOLO path that is practical for a demo.
- The user can replace the demo model with a custom `models/best.pt` license plate detector.
- The app must expose a small Flask web interface and JSON API for image upload.
- The ALPR flow must include detection, localization, preprocessing, recognition, and post-processing.
- PaddleOCR is the preferred OCR engine because it is more suitable for varied plate typography than a basic Tesseract-only flow.
- The local demo may optionally query the official South Sumatra tax lookup for BG plates and show the returned due date, amount, vehicle fields, and owner or address fields only when the source provides them.

## Assumptions To Validate

- The first demo can run on CPU, with GPU treated as an optional acceleration path.
- A pretrained generic YOLO model can prove the integration path, but accurate plate localization requires a trained license plate model.
- The application does not need login, persistent storage, or streaming video in the first version.
- Uploaded images are short-lived request inputs, not records to keep in a database.
- The optional tax lookup depends on an external public website and can fail independently from ALPR recognition.

## User Workflow

1. The user opens the web page.
2. The user uploads a vehicle image.
3. The server validates the file.
4. The ALPR pipeline locates the likely plate crop.
5. OCR reads the crop.
6. The server normalizes the plate text and maps the plate prefix to a region.
7. The UI shows the detected text, region, confidence, and pipeline notes.
8. If the plate is a BG plate, the UI can show optional tax lookup data returned by the official South Sumatra source. For other known regions, the UI links to the official source when automated lookup requires captcha, an app flow, or extra owner data.

## Non-Goals For Version 1

- No live camera stream.
- No plate history database.
- No account system.
- No training UI.
- No production deployment automation.
- No broad national tax lookup scraping. The first automated tax lookup adapter is limited to South Sumatra/BG; other known regions are linked as manual official sources unless a safe public endpoint is available.

## Demo Model Policy

The app defaults to `models/best.pt` when that file exists. If it is missing, the app can use `yolo26n.pt` through the Ultralytics package, but the local demo does not depend on downloading that file. A controlled demo fallback uses a simple plate-like bright-region heuristic and then falls back to a fixed crop when no trained plate model is available. The API marks that result as a fallback.

## Training Handoff

The expected training output is `models/best.pt`. Dataset preparation lives under `datasets/`, and training notes live under `docs/training/`. After a Kaggle dataset is selected and converted to YOLO format, `platvision-train-detector` can fine-tune YOLO weights and copy the best run artifact to `models/best.pt`.

## Validation Strategy

- Unit tests cover Indonesian plate normalization and region lookup.
- API tests cover upload validation and response shape with fake ALPR dependencies.
- Manual smoke testing covers one browser upload with the installed YOLO and OCR dependencies.

## Next Action

Run the Phase 1 smoke test in `docs/roadmap.md`. After the upload flow is proven, choose a Kaggle dataset, verify its license and annotation quality, then train a plate detector and place the exported model at `models/best.pt`.
