# API Contract

## `GET /health`

Returns application health and selected model configuration.

### Response `200`

```json
{
  "status": "ok",
  "service": "platvision-id",
  "model": "models/best.pt"
}
```

## `POST /api/recognize`

Recognizes an Indonesian license plate from an uploaded image.

### Request

Content type: `multipart/form-data`

Fields:

- `image`: required image file. Allowed extensions are `jpg`, `jpeg`, `png`, and `webp`.

Limits:

- Maximum request size is 8 MB by default.
- The server treats filenames and image bytes as untrusted input.

### Success Response `200`

```json
{
  "plate": "D 1234 ABC",
  "normalizedPlate": "D 1234 ABC",
  "region": {
    "code": "D",
    "name": "Bandung Raya"
  },
  "confidence": 0.91,
  "box": {
    "x1": 120,
    "y1": 260,
    "x2": 420,
    "y2": 330
  },
  "diagnostics": {
    "detector": "ultralytics",
    "ocr": "paddleocr",
    "fallbackUsed": false,
    "notes": []
  }
}
```

### Error Response

Errors use a stable JSON shape.

```json
{
  "code": "unsupported_file_type",
  "message": "Upload a JPG, PNG, or WEBP image."
}
```

Known error codes:

- `missing_file`
- `empty_filename`
- `unsupported_file_type`
- `invalid_image`
- `alpr_unavailable`
- `request_too_large`
- `internal_error`

## Security Notes

- The API does not store uploaded files permanently.
- The API does not expose server file paths, model stack traces, or provider internals.
- The endpoint has no authentication in version 1 because it is a local demo surface.
