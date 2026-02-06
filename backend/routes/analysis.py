# backend/routes/analysis.py

import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.utils.logger import get_logger
from backend.utils.exceptions import CustomException
from database.database import get_db

# Core Services
from backend.services.file_parser import FileParser
from backend.services.metrics import FinancialMetrics
from backend.services.risk_engine import FinancialRiskEngine
from backend.services.ai_service import FinancialAIService
from backend.services.translation import Translator
from backend.services.db_service import save_sme_analysis

# Value-Added & Integration Services
from backend.services.recommendation_engine import RecommendationEngine
from backend.services.forecasting import FinancialForecaster
from backend.services.tax_service import TaxComplianceService
from backend.services.external_connector import ExternalConnector  # NEW

# ----------------------------------
# Router setup
# ----------------------------------
router = APIRouter(
    prefix="/analysis",
    tags=["Financial Analysis"]
)

logger = get_logger("AnalysisRoute")

# ----------------------------------
# Initialize services
# ----------------------------------
file_parser = FileParser()
metrics_service = FinancialMetrics()
risk_engine = FinancialRiskEngine()
ai_service = FinancialAIService()
translator = Translator(ai_service=ai_service)
recommendation_engine = RecommendationEngine()
forecaster = FinancialForecaster()
tax_service = TaxComplianceService()
external_connector = ExternalConnector()  # NEW

# ----------------------------------
# Deterministic helpers
# ----------------------------------
def calculate_credit_score(metrics: dict, risk: dict):
    """Calculates a baseline credit score (0-100) based on financial health."""
    score = 100
    if metrics.get("net_cashflow", 0) < 0:
        score -= 30
    if metrics.get("debt_ratio", 0) > 0.7:
        score -= 20
    if risk.get("overall_risk") == "High":
        score -= 25
    
    score = max(score, 0)
    
    if score >= 80: grade = "A"
    elif score >= 65: grade = "B"
    elif score >= 50: grade = "C"
    else: grade = "D"
    
    return score, grade

# ----------------------------------
# POST /analysis/run
# ----------------------------------
@router.post("/run")
async def run_financial_analysis(
    file: UploadFile = File(...),
    business_type: str = "Retail",
    language: str = "en",
    db: Session = Depends(get_db)
):
    """
    End-to-end SME financial health analysis pipeline:
    Parsed Data + External API Verifications -> Insights.
    """
    temp_file_path = None

    try:
        logger.info(f"Received file for analysis: {file.filename}")

        # 0. Save uploaded file temporarily
        suffix = os.path.splitext(file.filename)[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            temp_file_path = tmp.name
            tmp.write(await file.read())

        # 1. Parsing & Basic Metrics
        df = file_parser.parse_file(temp_file_path)
        df["type"] = df["type"].astype(str).str.lower().str.strip()
        df["type"] = df["type"].replace({"income": "credit", "expense": "debit"})
        metrics = metrics_service.compute_financial_metrics(df)

        # 2. External Data Integration (NEW)
        # We use a placeholder ID for simulation
        external_insights = external_connector.get_integrated_data_summary(business_id=file.filename)

        # 3. Risk & Credit Evaluation
        risk_result = risk_engine.evaluate_financial_risk(metrics)
        overall_risk = risk_result.get("overall_risk", "Unknown")
        credit_score, credit_grade = calculate_credit_score(metrics, risk_result)

        # 4. Financial Product Recommendations
        product_recommendations = recommendation_engine.get_recommendations(
            metrics=metrics, 
            risk_level=overall_risk
        )

        # 5. Financial Forecasting & Tax Check
        forecast_data = forecaster.project_cashflow(
            current_revenue=metrics.get("total_revenue", 0.0),
            current_expenses=metrics.get("total_expenses", 0.0)
        )
        tax_report = tax_service.perform_tax_check(metrics)

        # 6. AI Narrative & Translation
        ai_report = ai_service.generate_financial_report(
            metrics_context=f"Financials: {metrics}, External Status: {external_insights}",
            risk_context=str(risk_result)
        )

        if language.lower() != "en":
            ai_report = translator.translate_report(ai_report, language)

        # 7. Database Persistence
        db_entry = save_sme_analysis(
            db=db,
            business_name=file.filename,
            business_type=business_type,
            financial_metrics=metrics,
            ai_summary=ai_report,
            risk_level=overall_risk,
            report_language=language
        )

        # -----------------------------
        # Final Response Object
        # -----------------------------
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "business_info": {
                    "type": business_type,
                    "source": file.filename,
                    "external_verifications": external_insights # NEW
                },
                "financial_summary": {
                    "metrics": metrics, 
                    "risk": risk_result
                },
                "credit_readiness": {
                    "score": credit_score, 
                    "grade": credit_grade
                },
                "projections": forecast_data,
                "banking_products": product_recommendations,
                "tax_compliance": tax_report,
                "ai_report": ai_report,
                "meta": {
                    "language": language,
                    "db_id": db_entry.id
                }
            }
        )

    except CustomException as ce:
        logger.error(f"Custom analysis error: {ce}")
        raise HTTPException(status_code=400, detail=str(ce))
    except Exception as e:
        logger.exception("Critical error in analysis route")
        raise HTTPException(status_code=500, detail="Financial analysis pipeline failed")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)