import os
import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

TEST_CSV = r"E:\financial-health-ai\notebook\sample_finance.csv"

# -----------------------------
# Helper to ensure CSV exists
# -----------------------------
if not os.path.exists(TEST_CSV):
    os.makedirs(os.path.dirname(TEST_CSV), exist_ok=True)
    with open(TEST_CSV, "w") as f:
        f.write("date,category,description,amount,type\n")
        f.write("2026-01-01,Revenue,Product Sales,5000,credit\n")
        f.write("2026-01-02,Expenses,Office Rent,1000,debit\n")
        f.write("2026-01-03,Revenue,Consulting,2500,credit\n")
        f.write("2026-01-04,Expenses,AWS Cloud,300,debit\n")
        f.write("2026-01-05,Receivables,Invoice #104,1500,credit\n")

# -----------------------------
# 1. Test /analysis/run
# -----------------------------
def test_analysis_run_endpoint():
    with open(TEST_CSV, "rb") as f:
        response = client.post(
            "/analysis/run",
            files={"file": ("sample_finance.csv", f, "text/csv")},
            data={"business_type": "Retail", "language": "en"}
        )
    assert response.status_code == 200
    data = response.json()
    print("Run Response:", data)

    # Basic validation
    assert "financial_summary" in data
    assert "ai_report" in data
    assert "credit_readiness" in data
    assert "db_id" in data

# -----------------------------
# 2. Test /report/history
# -----------------------------
def test_report_history_endpoint():
    response = client.get("/report/history?limit=5")
    assert response.status_code == 200
    data = response.json()
    print("History Response:", data)
    assert "history" in data
    assert isinstance(data["history"], list)
    if data["history"]:
        first_entry = data["history"][0]
        assert "financial_metrics" in first_entry
        assert "ai_summary" in first_entry
        assert "risk_level" in first_entry

# -----------------------------
# 3. Test /report/generate
# -----------------------------
def test_report_generate_endpoint():
    # Simulate payload using previous analysis structure
    payload = {
        "financial_summary": {
            "metrics": {"net_cashflow": 6700, "debt_ratio": 0.2, "expense_ratio": 0.25},
            "risk": {"overall_risk": "Low"}
        },
        "ai_report": "Sample AI report text",
        "credit_readiness": {"score": 85, "grade": "A"},
        "recommendations": {"cost_optimization": [], "working_capital": [], "credit_products": []},
        "meta": {"language": "en", "data_source": "sample_finance.csv"}
    }

    response = client.post("/report/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    print("Generate Response:", data)

    assert "report" in data
    assert "executive_summary" in data["report"]
