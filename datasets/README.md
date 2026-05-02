# Dataset Workspace

This directory is the local workspace for the YOLO license plate detection dataset. Keep raw downloads, converted images, and labels local unless the dataset license explicitly allows redistribution.

## Expected Layout

```text
datasets/
  platvision-id.yaml
  platvision-id/
    images/
      train/
      val/
      test/
    labels/
      train/
      val/
      test/
```

Each label file must use YOLO detection format:

```text
class_id center_x center_y width height
```

Values are normalized from `0` to `1`. This project uses one class:

```text
0 license_plate
```

## Kaggle Intake Checklist

- Record dataset name, URL, license, and download date in `docs/training/dataset-notes.md`.
- Confirm the license allows academic use.
- Verify that the annotation format can be converted to YOLO bounding boxes.
- Prefer Indonesian plates. If the dataset is not Indonesian, record the domain gap.
- Split by source image or sequence, not random near-duplicates.
- Do not commit private vehicle images unless the license and privacy policy allow it.

Large dataset files are ignored by git. Commit only metadata, conversion scripts, and notes.
