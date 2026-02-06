# backend/routes/analysis.py

import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.utils.logger import get_logger
from backend.utils.exceptions import CustomException
from database.database import get_db

from backend.services.file_parser import FileParser
from backend.services.metrics import FinancialMetrics
from backend.services.risk_engine import FinancialRiskEngine
from backend.services.ai_service import FinancialAIService
from backend.services.db_service import save_sme_analysis

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

# ----------------------------------
# Deterministic helpers
# ----------------------------------
def calculate_credit_score(metrics: dict, risk: dict):
    score = 100
    if metrics.get("net_cashflow", 0) < 0:
        score -= 30
    if metrics.get("debt_ratio", 0) > 0.7:
        score -= 20
    if risk.get("overall_risk") == "High":
        score -= 25
    score = max(score, 0)
    if score >= 80:
        grade = "A"
    elif score >= 65:
        grade = "B"
    elif score >= 50:
        grade = "C"
    else:
        grade = "D"
    return score, grade

def generate_recommendations(metrics: dict, risk: dict):
    recs = {"cost_optimization": [], "working_capital": [], "credit_products": []}
    if metrics.get("expense_ratio", 0) > 0.6:
        recs["cost_optimization"].append(
            "Review and reduce high operational expenses"
        )
    if metrics.get("net_cashflow", 0) < 0:
        recs["working_capital"].append(
            "Improve receivables collection and cash flow predictability"
        )
    if risk.get("overall_risk") in ["Medium", "High"]:
        recs["credit_products"].append(
            "Consider short-term working capital financing"
        )
    return recs

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
    End-to-end SME financial health analysis:
    File → Metrics → Risk → Credit → AI Explanation → Save to DB
    """
    temp_file_path = None

    try:
        logger.info(f"Received file for analysis: {file.filename}")

        # -----------------------------
        # Save uploaded file temporarily
        # -----------------------------
        suffix = os.path.splitext(file.filename)[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            temp_file_path = tmp.name
            tmp.write(await file.read())
        logger.debug(f"Temporary file saved at: {temp_file_path}")

        # -----------------------------
        # 1. Parse file
        # -----------------------------
        df = file_parser.parse_file(temp_file_path)
        logger.debug(f"Parsed file successfully: rows={len(df)}")

        # -----------------------------
        # 2. Compute financial metrics
        # -----------------------------
        # Map CSV types to "credit"/"debit"
        df["type"] = df["type"].astype(str).str.lower().str.strip()
        df["type"] = df["type"].replace({"income": "credit", "expense": "debit"})
        
        metrics = metrics_service.compute_financial_metrics(df)
        logger.debug(f"Financial metrics computed: {metrics}")

        # -----------------------------
        # 3. Risk evaluation
        # -----------------------------
        risk_result = risk_engine.evaluate_financial_risk(metrics)
        logger.debug(f"Risk evaluation result: {risk_result}")

        # -----------------------------
        # 4. Creditworthiness
        # -----------------------------
        credit_score, credit_grade = calculate_credit_score(metrics, risk_result)
        logger.debug(f"Credit score: {credit_score}, grade: {credit_grade}")

        # -----------------------------
        # 5. Recommendations
        # -----------------------------
        recommendations = generate_recommendations(metrics, risk_result)
        logger.debug(f"Recommendations: {recommendations}")

        # -----------------------------
        # 6. AI explanation
        # -----------------------------
        metrics_context = f"{metrics}"
        risk_context = f"{risk_result}"
        ai_report = ai_service.generate_financial_report(
            metrics_context=metrics_context,
            risk_context=risk_context
        )
        logger.debug(f"AI report generated: {ai_report}")

        # -----------------------------
        # 7. Save analysis to PostgreSQL (encrypted)
        # -----------------------------
        db_entry = save_sme_analysis(
            db=db,
            business_name=file.filename,
            business_type=business_type,
            financial_metrics=metrics,
            ai_summary=ai_report,
            risk_level=risk_result.get("overall_risk", "Unknown"),
            report_language=language
        )
        logger.info(f"Analysis saved to DB with ID: {db_entry.id}")

        # -----------------------------
        # Final response
        # -----------------------------
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "business_type": business_type,
                "financial_summary": {"metrics": metrics, "risk": risk_result},
                "credit_readiness": {"score": credit_score, "grade": credit_grade},
                "recommendations": recommendations,
                "ai_report": ai_report,
                "meta": {"language": language, "data_source": file.filename},
                "db_id": db_entry.id
            }
        )

    except CustomException as ce:
        logger.error("Custom exception occurred", exc_info=True)
        raise HTTPException(status_code=400, detail=str(ce))

    except Exception as e:
        logger.exception("Unhandled exception occurred")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during financial analysis"
        )

    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            logger.debug(f"Temporary file removed: {temp_file_path}")
