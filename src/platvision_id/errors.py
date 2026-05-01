from __future__ import annotations


class ClientError(Exception):
    status_code = 400

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class AlprUnavailableError(ClientError):
    status_code = 503


class InvalidImageError(ClientError):
    status_code = 400

    def __init__(self) -> None:
        super().__init__("invalid_image", "Upload a valid image file.")
