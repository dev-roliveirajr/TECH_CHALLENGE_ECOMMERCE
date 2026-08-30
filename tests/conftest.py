import pandas as pd
import pytest


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame(
        {
            "customer_id": ["c-1", "c-2", "c-3", "c-4"],
            "order_id": ["o-1", "o-2", "o-3", "o-4"],
            "nps_score": [0, 6, 7, 10],
            "customer_age": [25, 35, 45, 55],
            "customer_tenure_months": [1, 12, 24, 36],
            "order_value": [100.0, 200.0, 300.0, 400.0],
            "items_quantity": [1, 2, 3, 4],
            "discount_value": [0.0, 5.0, 10.0, 15.0],
            "payment_installments": [1, 2, 3, 4],
            "delivery_time_days": [2, 3, 4, 5],
            "delivery_delay_days": [0, 1, 3, 5],
            "freight_value": [10.0, 20.0, 30.0, 40.0],
            "delivery_attempts": [1, 1, 2, 3],
            "customer_service_contacts": [0, 1, 3, 5],
            "resolution_time_days": [1, 2, 6, 9],
            "complaints_count": [0, 1, 2, 3],
            "repeat_purchase_30d": [0, 1, 0, 1],
            "csat_internal_score": [8.0, 7.0, 9.0, 6.0],
            "customer_region": ["Sul", "Norte", "Sul", "Norte"],
        }
    )


@pytest.fixture
def modeling_dataframe(sample_dataframe):
    rows = pd.concat([sample_dataframe] * 8, ignore_index=True)
    rows["customer_id"] = [f"c-{index}" for index in range(len(rows))]
    rows["order_id"] = [f"o-{index}" for index in range(len(rows))]
    rows["is_detractor"] = [index % 2 for index in range(len(rows))]
    return rows
