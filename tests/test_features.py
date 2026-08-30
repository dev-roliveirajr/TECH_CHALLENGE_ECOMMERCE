import pandas as pd
import pytest

from src import config
from src.features import (
    build_preprocessing_pipeline,
    get_feature_lists,
    split_features_target,
)


def test_get_feature_lists_separates_types_and_excludes_leakage(sample_dataframe):
    numeric, categorical = get_feature_lists(sample_dataframe)

    assert "order_value" in numeric
    assert "customer_region" in categorical
    assert set(config.EXCLUDED_FROM_MODEL).isdisjoint(numeric + categorical)


def test_split_features_target_removes_target_identifiers_and_risk_groups(
    sample_dataframe,
):
    enriched = sample_dataframe.assign(
        is_detractor=[1, 1, 0, 0],
        delay_group="Sem Atraso",
        contacts_group="Sem Contato",
        support_group="Rápido (0-2 dias)",
    )

    features, target = split_features_target(enriched)

    assert target.tolist() == [1, 1, 0, 0]
    assert "is_detractor" not in features
    assert "customer_id" not in features
    assert "delay_group" not in features


def test_split_features_target_requires_target(sample_dataframe):
    with pytest.raises(ValueError, match="não foi encontrada"):
        split_features_target(sample_dataframe)


def test_preprocessing_pipeline_imputes_and_encodes_data():
    frame = pd.DataFrame({"amount": [1.0, None, 3.0], "region": ["Norte", None, "Sul"]})
    preprocessor = build_preprocessing_pipeline(["amount"], ["region"])

    transformed = preprocessor.fit_transform(frame)

    assert transformed.shape == (3, 4)
    assert transformed.dtype.kind == "f"
