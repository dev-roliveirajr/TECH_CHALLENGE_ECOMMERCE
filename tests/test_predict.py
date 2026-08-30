import joblib
import pandas as pd
from sklearn.dummy import DummyClassifier

from src.modeling.predict import (
    categorize_risk_band,
    load_trained_pipeline,
    run_inference,
)


def test_categorize_risk_band_boundaries():
    assert categorize_risk_band(0.50) == "Baixo Risco"
    assert categorize_risk_band(0.5001) == "Alto Risco"
    assert categorize_risk_band(0.75) == "Alto Risco"
    assert categorize_risk_band(0.7501) == "Risco Crítico"


def test_load_trained_pipeline_rejects_missing_path(tmp_path):
    missing = tmp_path / "missing.joblib"

    try:
        load_trained_pipeline(missing)
    except FileNotFoundError as error:
        assert "não localizado" in str(error)
    else:
        raise AssertionError("Era esperado erro para modelo inexistente")


def test_run_inference_scores_sorts_and_writes_output(tmp_path):
    input_path = tmp_path / "input.csv"
    model_path = tmp_path / "model.joblib"
    output_path = tmp_path / "nested" / "scored.csv"
    input_data = pd.DataFrame({"amount": [1.0, 2.0, 3.0]})
    input_data.to_csv(input_path, index=False)

    model = DummyClassifier(strategy="prior").fit([[0], [1], [2], [3]], [0, 0, 1, 1])
    joblib.dump(model, model_path)

    result = run_inference(input_path, model_path, output_path)

    assert output_path.exists()
    assert result.columns.tolist() == ["amount", "detractor_probability", "risk_band"]
    assert result["detractor_probability"].is_monotonic_decreasing
