import matplotlib.pyplot as plt
import pytest

from src.plots import (
    plot_delivery_time_boxplot,
    plot_detraction_by_delay,
    plot_detraction_by_region,
    plot_nps_distribution,
    plot_order_structure_analysis,
    plot_spearman_correlation_matrix,
    prepare_order_structure_features,
)


@pytest.mark.parametrize(
    "plot_function",
    [
        plot_nps_distribution,
        plot_detraction_by_delay,
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
