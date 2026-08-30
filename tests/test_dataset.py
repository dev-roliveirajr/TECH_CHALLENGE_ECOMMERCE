import pandas as pd
import pytest

from src.dataset import (
    binarize_target,
    create_business_risk_features,
    group_contacts,
    group_delivery_delay,
    group_support,
    load_raw_data,
    validate_data,
    winsorize_outlier_columns,
)


def test_load_raw_data_reads_csv(tmp_path, sample_dataframe):
    csv_path = tmp_path / "raw.csv"
    sample_dataframe.to_csv(csv_path, index=False)

    result = load_raw_data(csv_path)

    pd.testing.assert_frame_equal(result, sample_dataframe)


def test_load_raw_data_rejects_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError, match="não localizado"):
        load_raw_data(tmp_path / "missing.csv")


def test_validate_data_accepts_valid_dataframe(sample_dataframe):
    validate_data(sample_dataframe)


@pytest.mark.parametrize(
    "column, value, message",
    [
        ("customer_id", "c-1", "unicidade"),
        ("nps_score", 11, "limites"),
        ("order_value", -1, "negativos"),
        ("repeat_purchase_30d", 2, "inválidos"),
    ],
)
def test_validate_data_rejects_invalid_values(sample_dataframe, column, value, message):
    invalid = sample_dataframe.copy()
    if column == "customer_id":
        invalid.loc[1, column] = value
    else:
        invalid.loc[0, column] = value

    with pytest.raises(ValueError, match=message):
        validate_data(invalid)


def test_binarize_target_uses_nps_detractor_boundary(sample_dataframe):
    result = binarize_target(sample_dataframe)

    assert result["is_detractor"].tolist() == [1, 1, 0, 0]
    assert "is_detractor" not in sample_dataframe


@pytest.mark.parametrize(
    "function, values, expected",
    [
        (
            group_delivery_delay,
            [0, 1, 3, 5],
            [
                "Sem Atraso",
                "Atraso Baixo (1-2 dias)",
                "Atraso Médio (3-4 dias)",
                "Atraso Crítico (5+ dias)",
            ],
        ),
        (
            group_contacts,
            [0, 1, 3, 5],
            [
                "Sem Contato",
                "Contato Baixo (1-2 contatos)",
                "Contato Médio (3-4 contatos)",
                "Contato Alto (5+ contatos)",
            ],
        ),
        (
            group_support,
            [2, 3, 6, 9],
            [
                "Rápido (0-2 dias)",
                "Médio (3-5 dias)",
                "Lento (6-8 dias)",
                "Crítico (9+ dias)",
            ],
        ),
    ],
)
def test_group_functions_cover_risk_bands(function, values, expected):
    assert [function(value) for value in values] == expected


def test_create_business_risk_features_adds_only_available_groups():
    source = pd.DataFrame({"delivery_delay_days": [0, 5]})

    result = create_business_risk_features(source)

    assert result["delay_group"].tolist() == ["Sem Atraso", "Atraso Crítico (5+ dias)"]
    assert "contacts_group" not in result
    assert "support_group" not in result


def test_winsorize_outlier_columns_clips_values_to_iqr_limits():
    source = pd.DataFrame(
        {
            "customer_service_contacts": [0, 1, 1, 2, 2, 2, 3, 10],
            "delivery_delay_days": [0, 1, 2, 2, 3, 3, 4, 12],
            "complaints_count": [0, 1, 2, 3, 4, 5, 6, 15],
        }
    )

    result = winsorize_outlier_columns(source)

    assert result["customer_service_contacts"].tolist() == [
        0.0,
        1.0,
        1.0,
        2.0,
        2.0,
        2.0,
        3.0,
        4.125,
    ]
    assert result["delivery_delay_days"].tolist() == [
        0.0,
        1.0,
        2.0,
        2.0,
        3.0,
        3.0,
        4.0,
        5.5,
    ]
    assert result["complaints_count"].tolist() == [
        0.0,
        1.0,
        2.0,
        3.0,
        4.0,
        5.0,
        6.0,
        10.5,
    ]


def test_winsorize_outlier_columns_ignores_missing_columns_and_keeps_others():
    source = pd.DataFrame(
        {
            "customer_service_contacts": [0, 1, 1, 2, 2, 2, 3, 10],
            "other_column": [10, 20, 30, 40, 50, 60, 70, 80],
        }
    )

    result = winsorize_outlier_columns(
        source,
        columns=["customer_service_contacts", "not_present"],
    )

    assert result["customer_service_contacts"].tolist() == [
        0.0,
        1.0,
        1.0,
        2.0,
        2.0,
        2.0,
        3.0,
        4.125,
    ]
    assert result["other_column"].tolist() == [10, 20, 30, 40, 50, 60, 70, 80]
