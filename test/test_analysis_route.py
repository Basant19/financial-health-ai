import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from database.database import engine
from backend.models.models import SMEAnalysis  # <-- use app's model only
from backend.main import app

# ----------------------------------
# Test client
# ----------------------------------
client = TestClient(app)

# ----------------------------------
# Test inputs
# ----------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(BASE_DIR, "notebook", "sample_finance.csv")
PDF_PATH = os.path.join(BASE_DIR, "notebook", "sample_finance.csv.pdf")

# ----------------------------------
# Helper: fetch last n rows from SMEAnalysis
# ----------------------------------
def fetch_last_sme_entries(n=5):
    with Session(bind=engine) as db:
        return db.query(SMEAnalysis).order_by(SMEAnalysis.id.desc()).limit(n).all()

# ----------------------------------
# Pytest fixture: cleanup after test
# ----------------------------------
@pytest.fixture
def cleanup_sme_entries():
    """
    Yield control to the test, then remove the last inserted SME entries.
    """
    yield
    with Session(bind=engine) as db:
        entries = db.query(SMEAnalysis).order_by(SMEAnalysis.id.desc()).limit(5).all()
        for entry in entries:
            db.delete(entry)
        db.commit()
        print(f"Cleaned up {len(entries)} SMEAnalysis entries from database.")

# ----------------------------------
# CSV – happy path (deterministic)
# ----------------------------------
def test_analysis_route_with_csv(cleanup_sme_entries):
    """
    End-to-end test:
    CSV → metrics → risk → credit → AI (or fallback)
    """
    with open(CSV_PATH, "rb") as f:
        response = client.post(
            "/analysis/run",
            files={"file": ("sample_finance.csv", f, "text/csv")},
        )

    # -----------------------------
    # Response sanity checks
    # -----------------------------
    assert response.status_code == 200, response.text
    data = response.json()

    # -----------------------------
    # Top-level structure
    # -----------------------------
    assert data["status"] == "success"
    for key in ["financial_summary", "credit_readiness", "recommendations", "ai_report", "meta"]:
        assert key in data

    # -----------------------------
    # Financial summary
    # -----------------------------
    summary = data["financial_summary"]
    metrics = summary["metrics"]
    risk = summary["risk"]
    for key in ["total_revenue", "total_expenses", "net_cashflow"]:
        assert key in metrics
    assert "overall_risk" in risk

    # -----------------------------
    # Credit readiness
    # -----------------------------
    credit = data["credit_readiness"]
    assert "score" in credit
    assert "grade" in credit
    assert isinstance(credit["score"], int)
    assert credit["grade"] in {"A", "B", "C", "D"}

    # -----------------------------
    # Recommendations
    # -----------------------------
    recs = data["recommendations"]
    for key in ["cost_optimization", "working_capital", "credit_products"]:
        assert key in recs

    # -----------------------------
    # AI report
    # -----------------------------
    ai_report = data["ai_report"]
    assert isinstance(ai_report, str)
    assert len(ai_report) > 100
    for section in ["OVERALL FINANCIAL HEALTH", "RISK ANALYSIS", "IMPROVEMENT RECOMMENDATIONS"]:
        assert section in ai_report

    # -----------------------------
    # Metadata
    # -----------------------------
    meta = data["meta"]
    assert meta["language"] == "en"
    assert meta["data_source"] == "sample_finance.csv"

    # -----------------------------
    # Optional: verify SMEAnalysis table
    # -----------------------------
    recent_entries = fetch_last_sme_entries(n=1)
    if recent_entries:
        last_entry = recent_entries[0]
        assert last_entry.business_name != ""
        assert last_entry.risk_level != ""
        print(f"Last SME entry stored: {last_entry.business_name}, risk: {last_entry.risk_level}")
    else:
        print("No SMEAnalysis entries found in database.")

# ----------------------------------
# Optional: PDF test
# ----------------------------------
def test_analysis_route_with_pdf(cleanup_sme_entries):
    """
    Test PDF input for the same route
    """
    if not os.path.exists(PDF_PATH):
        print("PDF_PATH does not exist, skipping PDF test")
        return

    with open(PDF_PATH, "rb") as f:
        response = client.post(
            "/analysis/run",
            files={"file": ("sample_finance.csv.pdf", f, "application/pdf")},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
