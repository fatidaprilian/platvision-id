# Dataset Notes

## Source

- Recommended first candidate: Indonesian License Plate Dataset by Juan Thomas Wijaya.
- Source URL: https://www.kaggle.com/datasets/juanthomaswijaya/indonesian-license-plate-dataset
- Provider: Kaggle.
- Download date: 2026-05-01.
- License: Unknown on Kaggle as of 2026-05-01; verify manually before publishing results or redistributing files.
- Redistribution allowed: Treat as not allowed until the dataset page states otherwise.

## Candidate Comparison

| Candidate | Fit | Annotation | License signal | Decision |
| --- | --- | --- | --- | --- |
| Indonesian License Plate Dataset by Juan Thomas Wijaya | Best domain fit for Indonesian ALPR | Detection labels are already YOLO; recognition crops also provided | Unknown | Recommended for local academic experimentation after manual license check |
| Indonesian Vehicle License Plate Dataset by M Razif Rizqullah | Strong Indonesian domain fit | Detection labels are COCO; OCR labels are CSV | Verify on Kaggle before use | Good backup if COCO-to-YOLO conversion is acceptable |
| License Plate Detection Dataset (10,125 Images) by Barkat Ali Arbab | Large generic plate detector dataset, weaker Indonesian domain fit | YOLO and COCO compatible | CC0 Public Domain | Good fallback for detection pretraining, not ideal as the final Indonesian evaluation set |
| Automatic License Plate Recognition (ALPR) Dataset by Mitesh | Large YOLO-formatted generic ALPR dataset | YOLO labels with train, valid, and test splits | PDDL | Good fallback for extra robustness, but document non-Indonesian domain gap |

## Domain Fit

- Target country or plate style: Indonesian vehicle plates.
- Dataset country or plate style: Prefer Indonesian plates.
- Domain gap: The Juan Thomas Wijaya and M Razif Rizqullah datasets are the best fit. Generic international datasets may improve detector robustness but should not be the only evaluation source.

## Annotation Format

- Original format: Use YOLO directly when using the Juan Thomas Wijaya dataset; convert COCO to YOLO if using the M Razif Rizqullah detection subset.
- Converted format: YOLO detection labels.
- Class policy: one class named `license_plate`.
- Current local detection split:
  - Train: 800 images, 800 label files, 1,530 boxes.
  - Validation: 100 images, 100 label files, 179 boxes.
  - Test: 100 images, 100 label files, 197 boxes.
  - Total: 1,000 images, 1,000 YOLO label files, 1,906 boxes.
- `labelswithLP/` contains matching YOLO boxes with plate text appended. Do not use it directly for detector training because Ultralytics expects five YOLO fields per row. Keep it for OCR experiments or later conversion scripts.

## Repository Policy

Do not commit downloaded training images or label files to the git repository by default. Keep them under `datasets/platvision-id/`, which is ignored except for `.gitkeep` placeholders and metadata files.

Commit these instead:

- Dataset source URL.
- License notes.
- Download date.
- Conversion scripts if added later.
- Cleaning decisions.
- Training metrics.

Commit a tiny sample image only when the dataset license explicitly permits redistribution and the image is appropriate for public project evidence.

## Cleaning Log

Record removed images and the reason:

| Decision | Reason | Count |
| --- | --- | ---: |
| Keep detection split | Local files match expected train, validation, and test image and YOLO label counts | 1,000 images |
| Keep `labelswithLP/` local-only | Useful for OCR text experiments, but not part of detector training input | 1,000 files |

## Split Policy

Use source-aware splits:

- Train: 70%
- Validation: 20%
- Test: 10%

Do not split near-duplicate frames across train, validation, and test.

## Validation Sample

Before training, inspect a small sample manually:

- 20 train images.
- 10 validation images.
- 10 test images.

Record issues here before running training.

## Trained Model Handoff

- Local model file: `models/best.pt`
- File size observed locally: about 5.2 MB
- Smoke test date: 2026-05-01
- Smoke test image: `datasets/platvision-id/images/test/test001.jpg`
- Smoke test result: API returned `200`, detector `ultralytics`, `fallbackUsed=false`, and OCR normalized plate `B 2842 PKM`.
- Demo confidence threshold: `PLATVISION_YOLO_CONFIDENCE=0.10` is used for the first trained model because some real-world demo images can have lower confidence than the curated test split.
