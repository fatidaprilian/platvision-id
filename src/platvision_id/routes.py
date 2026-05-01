from __future__ import annotations

from flask import Blueprint, jsonify, request
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from .config import AppConfig
from .errors import ClientError
from .modules.alpr.service import AlprService, build_default_service


def create_api_blueprint(config: AppConfig, service: AlprService | None = None) -> Blueprint:
    blueprint = Blueprint("api", __name__)
    alpr_service = service or build_default_service(config)

    @blueprint.get("/health")
    def health():
        return jsonify(
            {
                "status": "ok",
                "service": "platvision-id",
                "model": config.yolo_model_path,
            }
        )

    @blueprint.post("/api/recognize")
    def recognize():
        uploaded_image = _validated_upload(request.files.get("image"), config)
        image_bytes = uploaded_image.read()
        recognition = alpr_service.recognize(image_bytes)
        return jsonify(recognition.to_api_response())

    return blueprint


def _validated_upload(uploaded_file: FileStorage | None, config: AppConfig) -> FileStorage:
    if uploaded_file is None:
        raise ClientError("missing_file", "Upload an image using the form field named image.")

    filename = secure_filename(uploaded_file.filename or "")
    if not filename:
        raise ClientError("empty_filename", "Choose an image file before submitting.")

    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in config.upload_extensions:
        raise ClientError("unsupported_file_type", "Upload a JPG, PNG, or WEBP image.")

    return uploaded_file
