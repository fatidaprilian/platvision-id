# YOLO Detector Training

## Goal

Train a license plate detector and copy the best weights to `models/best.pt`. The Flask demo automatically prefers that file when it exists, so no app code change is needed after training.

## Current Runtime Signal

Ultralytics documentation checked on 2026-05-01 shows YOLO26 as the latest line and documents custom object detection training with a dataset YAML, `epochs`, and `imgsz`. This project keeps `yolo26n.pt` as the default starter weight because it is the smallest practical demo path.

Source: https://docs.ultralytics.com/

## Dataset Layout

Prepare this structure:

```text
datasets/
  platvision-id.yaml
  platvision-id/
    images/train/
    images/val/
    images/test/
    labels/train/
    labels/val/
    labels/test/
```

The dataset YAML is `datasets/platvision-id.yaml`.

## Install ML Dependencies

Use Docker for the full demo stack. For a local training environment, install the ML extra:

```bash
python -m pip install -e ".[ml]"
```

Training is usually much faster on a GPU environment such as a local CUDA machine or Google Colab.

For Google Colab, use `notebooks/platvision_colab_training.ipynb` and the runbook in `docs/training/colab-training.md`.

## Train

Default command:

```bash
platvision-train-detector \
  --data datasets/platvision-id.yaml \
  --model yolo26n.pt \
  --epochs 80 \
  --imgsz 640 \
  --batch 16 \
  --output models/best.pt
```

CPU fallback:

```bash
platvision-train-detector --device cpu --batch 4 --epochs 20
```

GPU example:

```bash
platvision-train-detector --device 0 --batch 16 --epochs 100
```

## Handoff To The Demo App

After training, confirm:

```text
models/best.pt
```

Then restart the development container or Flask process. The app will use `models/best.pt` automatically. A successful detector run should show detector `ultralytics` instead of `demo-fallback`.

## Metrics To Record

Record these in the project report:

- Dataset source and license.
- Train, validation, and test image counts.
- Precision.
- Recall.
- mAP50.
- mAP50-95.
- End-to-end OCR success examples.
- Failure examples.

## Important Limitation

The current fallback crop is only a demo aid. It is not a substitute for `models/best.pt` because it cannot learn plate shapes across angle, lighting, blur, distance, and vehicle types.
