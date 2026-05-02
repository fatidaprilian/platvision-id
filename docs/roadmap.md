# Roadmap

## Goal

Build Platvision ID from a working demo into a measurable ALPR project that is strong enough for a class project or thesis defense. The roadmap keeps the first version practical, then adds dataset work, model training, evaluation, and optional production hardening.

## Phase 0: Current Baseline

Status: Done.

The current baseline has a Flask upload UI, Docker development and production lanes, a YOLO detector adapter, a PaddleOCR adapter, post-processing for Indonesian plate text, and API tests with fake Machine Learning dependencies.

Exit criteria:

- Docker development image builds.
- Docker production image builds.
- Test container passes.
- `/health` responds from the running development container.

## Phase 1: Demo Smoke Test

Purpose: prove that the app runs end to end before dataset work starts.

Tasks:

- Open `http://localhost:5000`.
- Upload 3 to 5 vehicle images.
- Confirm that the UI shows result JSON, fallback notes, and error states cleanly.
- Capture screenshots for project evidence.
- Record which cases fail: no plate crop, bad OCR, wrong region, or unreadable image.

Exit criteria:

- At least one image completes the full upload flow.
- Fallback behavior is visible when no trained plate model exists.
- Known limitations are documented in the report notes.

## Phase 2: Dataset Collection

Status: Scaffold ready; dataset not selected yet.

Purpose: prepare a license plate detection dataset for YOLO training.

Candidate source:

- Kaggle dataset, selected later after checking license, annotation format, plate country/domain fit, and image quality.

Dataset acceptance checklist:

- License allows academic use.
- Images contain visible license plates.
- Annotation format can be converted to YOLO bounding boxes.
- Dataset has enough variation: daylight, night, blur, distance, angle, and vehicle type.
- Indonesian plates are preferred. If the dataset is not Indonesian, document the domain gap.
- Sensitive data policy is clear. Do not publish raw personal or private vehicle images without permission.

Minimum practical target:

- 500 labeled plate images for a first training run.
- 1,500 or more labeled images for a stronger evaluation.
- Split by image source, not random duplicates: train 70%, validation 20%, test 10%.

Exit criteria:

- Dataset source and license are recorded.
- Labels are verified on a small sample.
- A YOLO dataset YAML exists. Current scaffold: `datasets/platvision-id.yaml`.
- Train, validation, and test folders are ready under `datasets/platvision-id/`.

## Phase 3: Annotation And Cleaning

Purpose: improve label quality before training.

Tasks:

- Inspect bounding boxes around plates.
- Remove images where the plate is impossible to read or not visible.
- Normalize labels to one class: `license_plate`.
- Convert labels to YOLO format if needed.
- Keep a small `dataset-notes.md` file with source, cleaning decisions, and known bias.

Recommended tools:

- Roboflow for fast class-project labeling and augmentation.
- CVAT for precise manual labeling and video frame workflows.
- Label Studio if the project later combines detection labels with OCR text labels.

Exit criteria:

- Label sample passes manual review.
- No mixed class names remain.
- Dataset notes explain what was removed and why.

## Phase 4: YOLO Training

Status: CLI scaffold ready; blocked on dataset.

Purpose: replace the generic demo detector with a trained plate detector.

Tasks:

- Train with the latest practical Ultralytics YOLO model available in the project environment.
- Track metrics: precision, recall, mAP50, mAP50-95, training loss, validation loss.
- Export the best model to `models/best.pt`.
- Keep training command, dataset version, image size, epoch count, and hardware notes.

Recommended first run:

- Image size: 640.
- Epochs: 50 to 100.
- Batch size: based on GPU memory, or CPU fallback if needed.
- Early stopping: enabled if training plateaus.

Exit criteria:

- `models/best.pt` exists.
- Validation mAP50 is recorded.
- The app detects plate crops without demo fallback on test images.
- The demo fallback can be disabled after the trained model is verified.

Training scaffold:

- Dataset config: `datasets/platvision-id.yaml`.
- Training command: `platvision-train-detector --data datasets/platvision-id.yaml --output models/best.pt`.
- Training notes: `docs/training/yolo-training.md`.
- Dataset notes: `docs/training/dataset-notes.md`.

## Phase 5: OCR And Post-Processing Tuning

Purpose: improve text recognition after the detector is trained.

Tasks:

- Keep the PaddleOCR and PaddlePaddle versions pinned to a tested compatible pair unless a newer pair is verified in Docker.
- Compare OCR results from raw, grayscale, equalized, threshold, and sharpened crops.
- Add plate-specific character correction only when supported by evidence.
- Improve regex handling for Indonesian formats.
- Add confidence notes when OCR output is weak.

Examples of correction risks:

- `O` and `0` can be confused.
- `I` and `1` can be confused.
- `B` and `8` can be confused.

Do not blindly replace characters. Apply corrections only in known plate positions.

Exit criteria:

- OCR examples are recorded before and after tuning.
- Region lookup works for common Indonesian prefixes.
- Low-confidence OCR is marked clearly in the UI/API.

## Phase 6: Evaluation Report

Purpose: make the project defensible.

Metrics:

- Detection precision.
- Detection recall.
- mAP50.
- OCR exact-match accuracy.
- Plate prefix accuracy.
- End-to-end success rate.
- Average inference time per image.

Test set rules:

- Do not evaluate only on training images.
- Keep the final test set separate until the end.
- Include failure examples in the report.

Exit criteria:

- Evaluation table exists.
- Confusion or failure analysis exists.
- The report explains dataset limits and domain gap.

## Phase 7: Demo Polish

Purpose: make the demo clean for presentation.

Tasks:

- Show the detected bounding box on the preview image.
- Show crop preview next to OCR output.
- Add a simple diagnostics panel with detector confidence, OCR confidence, and fallback state.
- Add sample images under a documented demo-only folder if licensing allows.

Exit criteria:

- A lecturer can understand each ALPR stage from the UI.
- Error messages are clear.
- Demo limitations are visible and honest.

## Phase 8: Optional Hardening

Purpose: prepare for broader local use.

Optional tasks:

- Add batch image upload.
- Add camera or video input.
- Add result export as CSV.
- Add model warmup on startup.
- Add request timing logs.
- Add a small benchmark command.
- Add GPU Docker lane only if the machine and deployment need it.

Exit criteria:

- New features have tests or a manual validation checklist.
- Performance changes are measured.
- Docker documentation explains CPU versus GPU usage.

## Recommended Next Step

Run Phase 1 first. Do not start dataset work until the current Docker demo has been opened in the browser and tested with a few sample images. After that, choose a Kaggle dataset and validate its license and annotation quality before training.
