import os
import pytest

from backend.services.file_parser import FileParser
from backend.services.metrics import FinancialMetrics
from backend.services.risk_engine import FinancialRiskEngine
from backend.services.ai_service import FinancialAIService


# -----------------------------
# Test Inputs
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(BASE_DIR, "notebook", "sample_finance.csv")
PDF_PATH = os.path.join(BASE_DIR, "notebook", "sample_finance.csv.pdf")


@pytest.mark.integration
def test_generate_financial_report_from_csv():
    """
    Full end-to-end AI test using CSV input and real LLM.
    """

    # 1. Parse file
    parser = FileParser()
    df = parser.parse_file(CSV_PATH)
    assert not df.empty

    # 2. Compute metrics
    metrics_service = FinancialMetrics()
    metrics = metrics_service.compute_financial_metrics(df)

    assert isinstance(metrics, dict)
    assert "total_revenue" in metrics
    assert "net_cashflow" in metrics

    # 3. Risk analysis
    risk_engine = FinancialRiskEngine()
    risks = risk_engine.evaluate_financial_risk(metrics)

    assert isinstance(risks, dict)
    assert "overall_risk" in risks

    metrics_context = f"FINANCIAL METRICS:\n{metrics}"
    risk_context = f"IDENTIFIED RISKS:\n{risks}"

    # 4. Invoke real AI (NO mocking)
    ai_service = FinancialAIService()
    report = ai_service.generate_financial_report(
        metrics_context=metrics_context,
        risk_context=risk_context
    )

    # 5. Assertions (LLM-safe, structure-based)
    assert isinstance(report, str)
    assert len(report) > 100

    assert "OVERALL FINANCIAL HEALTH" in report
    assert "RISK ANALYSIS" in report
    assert "IMPROVEMENT RECOMMENDATIONS" in report


@pytest.mark.integration
def test_generate_financial_report_from_pdf():
    """
    Same end-to-end test using PDF input.
    """

    parser = FileParser()
    df = parser.parse_file(PDF_PATH)
    assert not df.empty

    metrics = FinancialMetrics().compute_financial_metrics(df)
    risks = FinancialRiskEngine().evaluate_financial_risk(metrics)

    metrics_context = f"FINANCIAL METRICS:\n{metrics}"
    risk_context = f"IDENTIFIED RISKS:\n{risks}"

    ai_service = FinancialAIService()
    report = ai_service.generate_financial_report(
        metrics_context=metrics_context,
        risk_context=risk_context
    )

    assert isinstance(report, str)
    assert len(report.strip()) > 100
    assert "OVERALL FINANCIAL HEALTH" in report
