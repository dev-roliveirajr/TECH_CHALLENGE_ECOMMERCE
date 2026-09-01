import matplotlib.pyplot as plt
import pytest

from src.plots import (
    plot_delivery_time_boxplot,
    plot_detraction_by_delay,
    plot_detraction_by_complaints_count,
    plot_detraction_by_customer_service_contacts,
    plot_detraction_by_delivery_attempts,
    plot_detraction_by_delivery_time,
    plot_detraction_by_metric,
    plot_detraction_by_region,
    plot_detraction_by_resolution_time,
    plot_nps_distribution,
    plot_order_structure_analysis,
    plot_spearman_correlation_matrix,
    plot_target_distribution,
    prepare_order_structure_features,
)


@pytest.mark.parametrize(
    "plot_function",
    [
        plot_nps_distribution,
        plot_target_distribution,
        plot_detraction_by_delay,
        plot_detraction_by_resolution_time,
        plot_detraction_by_delivery_time,
        plot_detraction_by_delivery_attempts,
        plot_detraction_by_customer_service_contacts,
        plot_detraction_by_complaints_count,
        plot_delivery_time_boxplot,
        plot_spearman_correlation_matrix,
        plot_detraction_by_region,
        plot_order_structure_analysis,
    ],
)
def test_plot_functions_save_non_empty_png(sample_dataframe, tmp_path, plot_function):
    output_path = tmp_path / f"{plot_function.__name__}.png"

    plot_function(sample_dataframe, output_path)

    assert output_path.exists()
    assert output_path.stat().st_size > 0
    assert plt.get_fignums() == []


def test_plot_detraction_by_metric_supports_custom_breakpoint(
    sample_dataframe, tmp_path
):
    output_path = tmp_path / "detraction_by_metric_custom.png"

    plot_detraction_by_metric(
        sample_dataframe,
        "complaints_count",
        output_path,
        "Test Metric Breakdown",
        "Complaints Count",
        rupture_value=2,
        rupture_label="Ponto de Ruptura: (2 reclamações)",
    )

    assert output_path.exists()
    assert output_path.stat().st_size > 0
    assert plt.get_fignums() == []


def test_plot_detraction_by_metric_draws_curve(sample_dataframe, tmp_path, monkeypatch):
    output_path = tmp_path / "detraction_by_metric_curve.png"
    plot_calls = []
    original_plot = plt.plot

    def spy_plot(*args, **kwargs):
        plot_calls.append((args, kwargs))
        return original_plot(*args, **kwargs)

    monkeypatch.setattr(plt, "plot", spy_plot)

    plot_detraction_by_metric(
        sample_dataframe,
        "complaints_count",
        output_path,
        "Test Metric Breakdown",
        "Complaints Count",
    )

    assert output_path.exists()
    assert plot_calls
    assert plt.get_fignums() == []


def test_prepare_order_structure_features_creates_region_and_quartile_columns(
    sample_dataframe,
):
    processed = prepare_order_structure_features(sample_dataframe)

    assert "customer_region_code" in processed.columns
    assert "order_value_q" in processed.columns
    assert "freight_value_q" in processed.columns
    assert processed["customer_region_code"].dropna().nunique() >= 2
    assert processed["order_value_q"].notna().all()
    assert processed["freight_value_q"].notna().all()
