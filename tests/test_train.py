import pandas as pd

from src import config
from src.modeling import train


def test_train_and_evaluate_creates_model_and_reports(
    tmp_path, modeling_dataframe, monkeypatch
):
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    models_dir = tmp_path / "models"
    processed_dir = data_dir / "processed"
    processed_dir.mkdir(parents=True)
    modeling_dataframe.to_csv(processed_dir / "processed_nps_data.csv", index=False)

    monkeypatch.setattr(config, "DATA_DIR", data_dir)
    monkeypatch.setattr(config, "REPORTS_DIR", reports_dir)
    monkeypatch.setattr(config, "MODELS_DIR", models_dir)

    train.train_and_evaluate()

    assert (models_dir / "detractor_classifier.joblib").exists()
    metrics = pd.read_csv(reports_dir / "model_metrics.csv")
    cv_metrics = pd.read_csv(reports_dir / "model_cv_metrics.csv")
    importance = pd.read_csv(reports_dir / "model_feature_importance.csv")
    assert metrics.loc[0, "model"] == "LogisticRegression"
    assert set(cv_metrics["model"]) == {
        "DummyClassifier",
        "LogisticRegression",
        "RandomForestClassifier",
    }
    assert not importance.empty
