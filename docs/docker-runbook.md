# Docker Runbook

## Purpose

This project uses Docker for the demo runtime so heavy Machine Learning dependencies stay inside the container. The Docker path is CPU-first. It installs PyTorch CPU wheels before installing Ultralytics so the image does not pull CUDA packages by default.

The Dockerfile has three lanes:

- `development`: Flask debug server, source volume mounted, full Machine Learning dependencies.
- `production`: Gunicorn WSGI server, non-root runtime user, full Machine Learning dependencies.
- `test`: lightweight dependency lane without YOLO, PaddleOCR, PaddlePaddle, or PyTorch. Tests use fakes at the ML boundary.

The PaddleOCR lane pins `paddleocr==3.3.3` with `paddlepaddle==3.2.0`. Newer 3.3.x PaddlePaddle CPU builds can fail with a oneDNN PIR runtime error during OCR inference, so this project uses the compatible pair until that upstream issue is resolved.

The first OCR request may download PaddleOCR model files into the container. Later requests are faster while the container cache remains available.

## Official Documentation Checked

- Dockerfile best practices, checked on 2026-04-27: use trusted base images, keep images small, use `.dockerignore`, rebuild with `--pull`, and avoid unnecessary packages.
- Docker Compose file reference, checked on 2026-04-27: use the current Compose Specification through `compose.yaml` and do not add the obsolete top-level `version` field.
- PyTorch local install guide, checked on 2026-04-27: choose the CPU compute platform when CUDA is not required.
- Gunicorn install and quickstart documentation, checked on 2026-04-27: install through pip and run a WSGI app with the `MODULE:VARIABLE` pattern.

## Development Build And Run

```bash
docker compose build --pull development
docker compose up development
```

Open:

```text
http://localhost:5000
```

## Run Tests In Docker

```bash
docker compose --profile test run --rm test
```

## Production Build And Run

```bash
docker compose --profile production build --pull production
docker compose --profile production up production
```

## Model Mount

The Compose file mounts local `./models` to `/app/models` as read-only. Put a trained license plate detector here:

```text
models/best.pt
```

If `models/best.pt` is missing, the app still starts. For accurate plate detection, provide a trained detector.

## Clean Rebuild

Use this when dependencies change or the image cache looks stale:

```bash
docker compose build --pull --no-cache development
```

## Notes

- The development container exposes port `5000`.
- The production container maps host `5000` to container `8000`.
- Health checks call `GET /health`.
- The production runtime user is non-root.
- The top-level Compose `version` field is intentionally omitted.
