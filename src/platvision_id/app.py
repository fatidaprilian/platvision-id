from __future__ import annotations

from flask import Flask, jsonify, render_template
from werkzeug.exceptions import HTTPException, RequestEntityTooLarge

from .config import AppConfig, load_config
from .errors import ClientError
from .modules.alpr.service import AlprService
from .routes import create_api_blueprint


def create_app(config: AppConfig | None = None, alpr_service: AlprService | None = None) -> Flask:
    app_config = config or load_config()
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = app_config.max_content_length
    app.config["PLATVISION_CONFIG"] = app_config

    app.register_blueprint(create_api_blueprint(app_config, alpr_service))

    @app.get("/")
    def index() -> str:
        return render_template("index.html")

    @app.errorhandler(ClientError)
    def handle_client_error(error: ClientError):
        return jsonify({"code": error.code, "message": error.message}), error.status_code

    @app.errorhandler(RequestEntityTooLarge)
    def handle_request_too_large(_: RequestEntityTooLarge):
        return jsonify(
            {
                "code": "request_too_large",
                "message": "Upload an image smaller than the configured request limit.",
            }
        ), 413

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        return jsonify(
            {
                "code": error.name.lower().replace(" ", "_"),
                "message": error.description,
            }
        ), error.code or 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(_: Exception):
        app.logger.exception("Unhandled request failure")
        return jsonify({"code": "internal_error", "message": "The server could not process the image."}), 500

    return app


def main() -> None:
    create_app().run(debug=True)


if __name__ == "__main__":
    main()
