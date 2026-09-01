import pandas as pd

from src.business_metrics import (
    create_buyer_metrics,
    create_logistics_metrics,
    create_order_metrics,
    create_score_metrics,
    create_support_metrics,
    generate_business_metrics_report,
)
from src.business_metrics_html_report import generate_html_metrics_table


def _make_business_dataframe():
    df = pd.DataFrame(
        {
            "customer_id": [f"c-{i}" for i in range(1, 13)],
            "order_id": [f"o-{i}" for i in range(1, 13)],
            "customer_age": [22, 26, 28, 32, 38, 42, 48, 51, 58, 63, 70, 75],
            "customer_tenure_months": [2, 8, 14, 20, 26, 30, 38, 44, 50, 62, 80, 96],
            "customer_region": [
                "Sul",
                "Sudeste",
                "Sul",
                "Norte",
                "Nordeste",
                "Sudeste",
                "Centro-Oeste",
                "Sul",
                "Norte",
                "Nordeste",
                "Sudeste",
                "Sul",
            ],
            "order_value": [
                78,
                140,
                220,
                310,
                460,
                580,
                700,
                920,
                1100,
                1500,
                2000,
                2600,
            ],
            "items_quantity": [1, 1, 2, 3, 4, 5, 6, 8, 2, 3, 5, 9],
            "freight_value": [10, 16, 24, 38, 42, 48, 60, 65, 80, 90, 100, 120],
            "delivery_time_days": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15],
            "delivery_delay_days": [0, 0, 1, 2, 3, 3, 4, 5, 6, 7, 9, 10],
            "delivery_attempts": [1, 1, 1, 2, 2, 3, 3, 3, 4, 4, 5, 6],
            "customer_service_contacts": [0, 1, 2, 2, 3, 4, 5, 5, 6, 7, 8, 10],
            "resolution_time_days": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13],
            "complaints_count": [0, 0, 1, 1, 2, 2, 3, 4, 5, 6, 7, 9],
            "nps_score": [2, 3, 5, 6, 7, 7, 8, 8, 9, 9, 10, 10],
            "csat_internal_score": [3, 4, 5, 6, 7, 7, 8, 8, 9, 9, 10, 10],
            "repeat_purchase_30d": [0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
        }
    )
    df["is_detractor"] = (df["nps_score"] <= 6).astype(int)
    return df


def test_create_buyer_metrics_returns_expected_structure():
    df = _make_business_dataframe()

    result = create_buyer_metrics(df)

    assert not result.empty
    assert list(result.columns) == [
        "Dimensão",
        "Métrica",
        "Faixa",
        "Qtd Clientes",
        "Taxa Detração",
        "NPS Médio",
    ]
    assert result["Dimensão"].eq("Comprador").any()
    assert set(result["Métrica"]).issuperset(
        {"Faixa Etária (anos)", "Tempo de Relacionamento", "Região Geográfica"}
    )
    assert (result["Taxa Detração"].between(0, 1)).all()


def test_create_business_dimension_metrics_are_non_empty():
    df = _make_business_dataframe()

    order_metrics = create_order_metrics(df)
    logistics_metrics = create_logistics_metrics(df)
    support_metrics = create_support_metrics(df)
    score_metrics = create_score_metrics(df)

    assert not order_metrics.empty
    assert not logistics_metrics.empty
    assert not support_metrics.empty
    assert not score_metrics.empty

    assert set(order_metrics["Dimensão"]).issubset({"Pedido"})
    assert set(logistics_metrics["Dimensão"]).issubset({"Logística"})
    assert set(support_metrics["Dimensão"]).issubset({"Atendimento"})
    assert set(score_metrics["Dimensão"]).issubset({"Score"})


def test_generate_business_metrics_report_saves_csv_and_includes_all_dimensions(
    monkeypatch, tmp_path
):
    df = _make_business_dataframe()
    output_path = tmp_path / "business_metrics.csv"

    monkeypatch.setattr("src.business_metrics.load_processed_data", lambda: df)

    report = generate_business_metrics_report(output_path=output_path)

    assert output_path.exists()
    assert output_path.stat().st_size > 0
    assert not report.empty
    assert set(report["Dimensão"]) == {
        "Comprador",
        "Pedido",
        "Logística",
        "Atendimento",
        "Score",
    }
    assert "Taxa Detração" in report.columns
    assert "NPS Médio" in report.columns


def test_generate_html_metrics_table_creates_html_from_csv(tmp_path):
    report_df = pd.concat(
        [
            create_buyer_metrics(_make_business_dataframe()),
            create_order_metrics(_make_business_dataframe()),
            create_logistics_metrics(_make_business_dataframe()),
            create_support_metrics(_make_business_dataframe()),
            create_score_metrics(_make_business_dataframe()),
        ],
        ignore_index=True,
    )
    report_df["Taxa Detração"] = (report_df["Taxa Detração"] * 100).round(2).astype(
        str
    ) + "%"
    report_df["NPS Médio"] = report_df["NPS Médio"].round(2)

    csv_path = tmp_path / "business_metrics.csv"
    html_path = tmp_path / "business_metrics.html"
    report_df.to_csv(csv_path, index=False, encoding="utf-8")

    html = generate_html_metrics_table(csv_path=csv_path, output_path=html_path)

    assert html_path.exists()
    assert html_path.stat().st_size > 0
    assert "COMPRADOR" in html.upper()
    assert "LOGÍSTICA" in html.upper() or "LOGISTICA" in html.upper()
    assert "<table" in html.lower()
    assert "Taxa Detração" in html
