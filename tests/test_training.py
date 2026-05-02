from pathlib import Path

from platvision_id import training


def test_training_cli_defaults_point_to_dataset_and_best_model() -> None:
    args = training._parse_args([])

    assert args.data == "datasets/platvision-id.yaml"
    assert args.model == "yolo26n.pt"
    assert args.output == "models/best.pt"


def test_training_main_delegates_to_train_detector(monkeypatch, capsys) -> None:
    calls = {}

    def fake_train_detector(**kwargs):
        calls.update(kwargs)
        return Path("models/best.pt")

    monkeypatch.setattr(training, "train_detector", fake_train_detector)

    training.main(["--epochs", "3", "--batch", "2", "--device", "cpu"])

    assert calls["epochs"] == 3
    assert calls["batch"] == 2
    assert calls["device"] == "cpu"
    assert "models/best.pt" in capsys.readouterr().out
