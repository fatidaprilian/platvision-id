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
  "cropPreview": "data:image/jpeg;base64,...",
  "diagnostics": {
    "detector": "ultralytics",
    "ocr": "paddleocr",
    "fallbackUsed": false,
    "notes": []
  },
  "tax": {
    "supported": true,
    "status": "found",
    "source": "Bapenda Sumsel",
    "sourceUrl": "https://bapenda.sumselprov.go.id/cek_pajak/t_ulang",
    "message": "Vehicle tax data was returned by the official source.",
    "paymentStatus": "amount_due",
    "registeredPlate": "BG1352AE",
    "ownerName": "EXAMPLE OWNER",
    "ownerAddress": "EXAMPLE ADDRESS",
    "taxDueDate": "01-09-2026",
    "stnkExpiryDate": "01-09-2028",
    "vehicleBrand": "TOYOTA",
    "vehicleModel": "INNOVA",
    "vehicleYear": "2021",
    "totalDue": "2.243.000,00"
  }
}
```

`cropPreview` is optional. When present, it is a small JPEG data URL of the detected plate crop used by OCR so the browser can show what the recognition step actually read.

`tax` is optional. It is returned only when the tax lookup adapter is enabled and the recognized plate can be checked or rejected by that adapter. Current status values are:

- `found`: the official source returned vehicle tax data.
- `not_found`: the official source returned no matching vehicle data.
- `manual_source_only`: the region has an official source, but automated lookup is not used because the flow requires captcha, an app, or extra owner data.
- `unsupported_region`: the normalized plate is outside the adapter's supported region.
- `lookup_failed`: the official source could not be reached or parsed safely.

The first automated adapter supports South Sumatra/BG plates through the official Bapenda Sumsel lookup page. Owner and address fields may be present in local demo responses only when the official source returns them.

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
- Optional tax lookup data may include personal data from an external official source. Keep this feature local unless privacy, consent, and legal requirements are reviewed.
