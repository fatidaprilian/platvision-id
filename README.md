# Platvision ID

Platvision ID is a Flask demo for Indonesian Automatic License Plate Recognition (ALPR). It uploads a vehicle image, localizes a likely plate area with Ultralytics YOLO, reads the crop with PaddleOCR, and maps the plate prefix to a region.

## Quick Start

Docker is recommended for this project because YOLO, PyTorch, PaddleOCR, and PaddlePaddle are heavy local dependencies.

```bash
docker compose build --pull development
docker compose up development
```

Then open `http://localhost:5000`.

## Local Python Start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m flask --app platvision_id.app run --debug
```

Then open `http://127.0.0.1:5000`.

## Model Setup

For accurate license plate detection, place a trained YOLO model at:

```text
models/best.pt
```

Without that file, the app uses `yolo26n.pt` through Ultralytics so the demo path remains available. That fallback is a generic detector and is not a trained Indonesian plate detector.

Useful environment variables:

```bash
export PLATVISION_YOLO_MODEL=models/best.pt
export PLATVISION_ENABLE_DEMO_FALLBACK=true
export PLATVISION_ENABLE_TAX_LOOKUP=true
export PLATVISION_TAX_LOOKUP_TIMEOUT=8
export PLATVISION_MAX_CONTENT_LENGTH=8388608
export PLATVISION_YOLO_CONFIDENCE=0.10
```

The optional tax lookup currently targets the official South Sumatra/BG endpoint and is intended for a local demo.

## Detector Training

Prepare a YOLO dataset under `datasets/platvision-id/`, then train:

```bash
platvision-train-detector --data datasets/platvision-id.yaml --output models/best.pt
```

See `docs/training/yolo-training.md` and `docs/training/dataset-notes.md` before using a Kaggle dataset.

## API

- `GET /health`
- `POST /api/recognize` with `multipart/form-data` field `image`

See `docs/api-contract.md` for the response contract.

## Tests

```bash
docker compose --profile test run --rm test
```

Production-like container:

```bash
docker compose --profile production build --pull production
docker compose --profile production up production
```

Local test command, after dependencies are installed:

```bash
python -m pytest
```
