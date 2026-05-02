from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import Sequence


def main(argv: Sequence[str] | None = None) -> None:
    args = _parse_args(argv)
    best_model = train_detector(
        data=args.data,
        model=args.model,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        project=args.project,
        name=args.name,
        patience=args.patience,
        device=args.device,
        output=args.output,
    )
    print(f"Trained detector exported to {best_model}")


def train_detector(
    *,
    data: str,
    model: str,
    epochs: int,
    imgsz: int,
    batch: int,
    project: str,
    name: str,
    patience: int,
    device: str | None,
    output: str,
) -> Path:
    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise SystemExit(
            "Ultralytics is not installed. Install the ML dependencies first, for example: "
            'python -m pip install -e ".[ml]"'
        ) from exc

    model_instance = YOLO(model)
    train_kwargs: dict[str, object] = {
        "data": data,
        "epochs": epochs,
        "imgsz": imgsz,
        "batch": batch,
        "project": project,
        "name": name,
        "patience": patience,
    }
    if device:
        train_kwargs["device"] = device

    result = model_instance.train(**train_kwargs)
    run_dir = Path(getattr(result, "save_dir", Path(project) / name))
    source_best = run_dir / "weights" / "best.pt"
    if not source_best.exists():
        raise SystemExit(f"Training finished, but best.pt was not found at {source_best}")

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_best, output_path)
    return output_path


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train a YOLO license plate detector and copy the best weights to models/best.pt."
    )
    parser.add_argument("--data", default="datasets/platvision-id.yaml", help="YOLO dataset YAML path.")
    parser.add_argument("--model", default="yolo26n.pt", help="Pretrained YOLO weights to fine-tune.")
    parser.add_argument("--epochs", type=int, default=80, help="Training epoch count.")
    parser.add_argument("--imgsz", type=int, default=640, help="Training image size.")
    parser.add_argument("--batch", type=int, default=16, help="Batch size. Reduce this if memory is limited.")
    parser.add_argument("--project", default="runs/detect", help="Ultralytics run output directory.")
    parser.add_argument("--name", default="platvision-id", help="Ultralytics run name.")
    parser.add_argument("--patience", type=int, default=20, help="Early stopping patience.")
    parser.add_argument("--device", default=None, help="Optional device value, such as cpu, 0, or 0,1.")
    parser.add_argument("--output", default="models/best.pt", help="Where to copy the trained best.pt.")
    return parser.parse_args(argv)


if __name__ == "__main__":
    main()
