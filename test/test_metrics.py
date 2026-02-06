import pandas as pd
import pytest

from backend.services.metrics import FinancialMetrics
from backend.utils.exceptions import CustomException


# ----------------------------
# FIXTURES
# ----------------------------

@pytest.fixture
def metrics():
    return FinancialMetrics()


@pytest.fixture
def valid_dataframe():
    """
    Sample deterministic transaction dataset
    """
    return pd.DataFrame(
        {
            "date": [
                "2024-01-10",
                "2024-01-15",
                "2024-02-05",
                "2024-02-20",
            ],
            "category": [
                "Sales",
                "Marketing",
                "Sales",
                "Operations",
            ],
            "amount": [
                10000,
                2000,
                8000,
                3000,
            ],
            "type": [
                "credit",
                "debit",
                "credit",
                "debit",
            ],
        }
    )


@pytest.fixture
def invalid_dataframe_missing_columns():
    return pd.DataFrame(
        {
            "date": ["2024-01-01"],
            "amount": [1000],
        }
    )


# ----------------------------
# VALIDATION TESTS
# ----------------------------

def test_validate_dataframe_success(metrics, valid_dataframe):
    # Should not raise
    metrics.validate_dataframe(valid_dataframe)


def test_validate_dataframe_missing_columns(metrics, invalid_dataframe_missing_columns):
    with pytest.raises(CustomException):
        metrics.validate_dataframe(invalid_dataframe_missing_columns)


# ----------------------------
# NORMALIZATION TESTS
# ----------------------------

def test_normalize_dataframe(metrics, valid_dataframe):
    df = metrics.normalize_dataframe(valid_dataframe)

    assert df["amount"].dtype.kind in "fi"
    assert all(df["type"].isin(["credit", "debit"]))


# ----------------------------
# METRIC CALCULATION TESTS
# ----------------------------

def test_calculate_total_revenue(metrics, valid_dataframe):
    df = metrics.normalize_dataframe(valid_dataframe)
    revenue = metrics.calculate_total_revenue(df)

    assert revenue == 18000  # 10000 + 8000


def test_calculate_total_expenses(metrics, valid_dataframe):
    df = metrics.normalize_dataframe(valid_dataframe)
    expenses = metrics.calculate_total_expenses(df)

    assert expenses == 5000  # 2000 + 3000


def test_calculate_net_cashflow(metrics, valid_dataframe):
    df = metrics.normalize_dataframe(valid_dataframe)
    net_cashflow = metrics.calculate_net_cashflow(df)

    assert net_cashflow == 13000  # 18000 - 5000


# ----------------------------
# BREAKDOWN TESTS
# ----------------------------

def test_category_breakdown(metrics, valid_dataframe):
    df = metrics.normalize_dataframe(valid_dataframe)
    breakdown = metrics.category_breakdown(df)

    assert breakdown["Sales"] == 18000
    assert breakdown["Marketing"] == 2000
    assert breakdown["Operations"] == 3000


def test_monthly_cashflow(metrics, valid_dataframe):
    df = metrics.normalize_dataframe(valid_dataframe)
    monthly = metrics.monthly_cashflow(df)

    assert monthly["2024-01"] == 8000   # 10000 - 2000
    assert monthly["2024-02"] == 5000   # 8000 - 3000


# ----------------------------
# ORCHESTRATION TEST
# ----------------------------

def test_compute_financial_metrics(metrics, valid_dataframe):
    result = metrics.compute_financial_metrics(valid_dataframe)

    assert isinstance(result, dict)

    assert result["total_revenue"] == 18000
    assert result["total_expenses"] == 5000
    assert result["net_cashflow"] == 13000

    assert "category_breakdown" in result
    assert "monthly_cashflow" in result
