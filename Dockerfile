# syntax=docker/dockerfile:1.7

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DISABLE_MODEL_SOURCE_CHECK=True \
    YOLO_CONFIG_DIR=/tmp/Ultralytics \
    PLATVISION_ENABLE_DEMO_FALLBACK=true

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        libgl1 \
        libglib2.0-0 \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src ./src

RUN python -m pip install --upgrade pip setuptools wheel

FROM base AS test

COPY tests ./tests

RUN python -m pip install -e ".[dev]"

CMD ["python", "-m", "pytest"]

FROM base AS ml-deps

# Install CPU PyTorch first so Ultralytics does not pull CUDA wheels by default.
RUN python -m pip install --index-url https://download.pytorch.org/whl/cpu torch torchvision \
    && python -m pip install -e ".[ml]"

FROM ml-deps AS development

RUN python -m pip install -e ".[dev]"

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD curl --fail http://127.0.0.1:5000/health || exit 1

CMD ["python", "-m", "flask", "--app", "platvision_id.app", "run", "--debug", "--host=0.0.0.0", "--port=5000"]

FROM ml-deps AS production

RUN groupadd --gid 10001 appuser \
    && useradd --uid 10001 --gid appuser --create-home --shell /usr/sbin/nologin appuser \
    && mkdir -p /app/models /app/.cache \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD curl --fail http://127.0.0.1:8000/health || exit 1

CMD ["gunicorn", "platvision_id.wsgi:app", "--bind=0.0.0.0:8000", "--workers=1", "--threads=2", "--timeout=180", "--access-logfile=-", "--error-logfile=-"]
