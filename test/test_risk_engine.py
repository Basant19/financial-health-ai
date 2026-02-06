import pytest

from backend.services.risk_engine import FinancialRiskEngine
from backend.utils.exceptions import CustomException


# ----------------------------
# FIXTURES
# ----------------------------

@pytest.fixture
def risk_engine():
    return FinancialRiskEngine()


# ----------------------------
# PROFITABILITY RISK TESTS
# ----------------------------

def test_profitability_risk_high_due_to_zero_revenue(risk_engine):
    result = risk_engine.assess_profitability_risk(
        total_revenue=0,
        total_expenses=5000
    )

    assert result["level"] == "High"
    assert "No revenue" in result["reason"]


def test_profitability_risk_high(risk_engine):
    result = risk_engine.assess_profitability_risk(
        total_revenue=10000,
        total_expenses=9500
    )

    assert result["level"] == "High"


def test_profitability_risk_medium(risk_engine):
    result = risk_engine.assess_profitability_risk(
        total_revenue=10000,
        total_expenses=8500
    )

    assert result["level"] == "Medium"


def test_profitability_risk_low(risk_engine):
    result = risk_engine.assess_profitability_risk(
        total_revenue=10000,
        total_expenses=7000
    )

    assert result["level"] == "Low"


# ----------------------------
# CASHFLOW RISK TESTS
# ----------------------------

def test_cashflow_risk_high(risk_engine):
    result = risk_engine.assess_cashflow_risk(net_cashflow=-1000)

    assert result["level"] == "High"


def test_cashflow_risk_medium(risk_engine):
    result = risk_engine.assess_cashflow_risk(net_cashflow=0)

    assert result["level"] == "Medium"


def test_cashflow_risk_low(risk_engine):
    result = risk_engine.assess_cashflow_risk(net_cashflow=5000)

    assert result["level"] == "Low"


# ----------------------------
# EXPENSE LOAD RISK TESTS
# ----------------------------

def test_expense_risk_high_due_to_zero_revenue(risk_engine):
    result = risk_engine.assess_expense_risk(
        total_revenue=0,
        total_expenses=3000
    )

    assert result["level"] == "High"


def test_expense_risk_high(risk_engine):
    result = risk_engine.assess_expense_risk(
        total_revenue=10000,
        total_expenses=9000
    )

    assert result["level"] == "High"


def test_expense_risk_medium(risk_engine):
    result = risk_engine.assess_expense_risk(
        total_revenue=10000,
        total_expenses=7000
    )

    assert result["level"] == "Medium"


def test_expense_risk_low(risk_engine):
    result = risk_engine.assess_expense_risk(
        total_revenue=10000,
        total_expenses=4000
    )

    assert result["level"] == "Low"


# ----------------------------
# AGGREGATION TESTS
# ----------------------------

def test_aggregate_risk_high(risk_engine):
    risks = {
        "profitability": {"level": "Low"},
        "cashflow": {"level": "High"},
        "expense_load": {"level": "Low"},
    }

    overall = risk_engine.aggregate_risk_levels(risks)
    assert overall == "High"


def test_aggregate_risk_medium(risk_engine):
    risks = {
        "profitability": {"level": "Medium"},
        "cashflow": {"level": "Low"},
        "expense_load": {"level": "Low"},
    }

    overall = risk_engine.aggregate_risk_levels(risks)
    assert overall == "Medium"


def test_aggregate_risk_low(risk_engine):
    risks = {
        "profitability": {"level": "Low"},
        "cashflow": {"level": "Low"},
        "expense_load": {"level": "Low"},
    }

    overall = risk_engine.aggregate_risk_levels(risks)
    assert overall == "Low"


# ----------------------------
# FULL ORCHESTRATION TEST
# ----------------------------

def test_evaluate_financial_risk(risk_engine):
    metrics = {
        "total_revenue": 20000,
        "total_expenses": 14000,
        "net_cashflow": 6000,
    }

    result = risk_engine.evaluate_financial_risk(metrics)

    assert result["overall_risk"] == "Medium"
    assert "risk_breakdown" in result
    assert "profitability" in result["risk_breakdown"]
    assert "cashflow" in result["risk_breakdown"]
    assert "expense_load" in result["risk_breakdown"]
