# Google Colab Training Runbook

Use this path when Kaggle Notebook GPU is unavailable or requires identity checks.

## Drive Preparation

Use the Kaggle dataset zip you already uploaded to Google Drive:

```text
MyDrive/dataset/Indonesian License Plate Dataset.zip
```

## Colab Setup

1. Open Google Colab.
2. Upload `notebooks/platvision_colab_training.ipynb`.
3. Select `Runtime -> Change runtime type -> T4 GPU`.
4. Run the first cell and confirm `nvidia-smi` shows a Tesla T4.
5. Run all cells in order.

## Expected Output

The notebook reads the zip above and copies the trained model to:

```text
MyDrive/platvision-id/best.pt
```

Download that file and place it in the local repository as:

```text
models/best.pt
```

The Flask app automatically uses `models/best.pt`. When the trained detector is active, the API diagnostics should report detector `ultralytics` instead of `demo-fallback`.

## Training Defaults

- Model: `yolo26n.pt`
- Epochs: `50`
- Image size: `640`
- Batch: `8`
- Device: `0`
- Patience: `10`

If Colab reports CUDA out-of-memory, change `batch=8` to `batch=4`.
