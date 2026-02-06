# backend/routes/report.py

from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from fastapi import Depends
from sqlalchemy.orm import Session
from database.database import get_db
from backend.services.db_service import load_sme_history
from backend.utils.logger import get_logger
from backend.utils.exceptions import CustomException

router = APIRouter(
    prefix="/report",
    tags=["Financial Report"]
)

logger = get_logger("ReportRoute")


@router.post("/generate")
def generate_financial_report(payload: dict = Body(...)):
    """
    Generates an investor-ready financial report
    from /analysis/run response (FULL PAYLOAD).
    """

    try:
        logger.info("Starting report generation")

        # -----------------------------
        # Validate expected structure
        # -----------------------------
        financial_summary = payload.get("financial_summary")
        ai_report = payload.get("ai_report")

        if financial_summary is None or ai_report is None:
            logger.warning("Invalid payload: missing financial_summary or ai_report")
            raise HTTPException(
                status_code=400,
                detail="Invalid payload: missing financial_summary or ai_report"
            )

        metrics = financial_summary.get("metrics")
        risk = financial_summary.get("risk")

        if metrics is None or risk is None:
            logger.warning("Invalid payload: missing metrics or risk data")
            raise HTTPException(
                status_code=400,
                detail="Invalid payload: missing metrics or risk data"
            )

        overall_risk = risk.get("overall_risk", "Unknown")
        logger.debug(f"Metrics and risk data validated. Overall risk: {overall_risk}")

        # -----------------------------
        # Investor-ready report structure
        # -----------------------------
        report = {
            "executive_summary": {
                "overall_health": overall_risk,
                "credit_grade": payload.get("credit_readiness", {}).get("grade"),
                "key_message": (
                    "This report provides an overview of financial health, "
                    "risk exposure, and credit readiness based on "
                    "deterministic analysis."
                )
            },
            "financial_highlights": metrics,
            "risk_assessment": {
                "overall_risk": overall_risk,
                "risk_breakdown": risk.get("risk_breakdown", {})
            },
            "recommendations": payload.get("recommendations", {}),
            "ai_insights": {
                "narrative": ai_report
            },
            "disclaimer": (
                "All financial figures are computed using deterministic rules. "
                "AI is used strictly for explanation and recommendations."
            )
        }

        logger.info("Investor-ready financial report generated successfully")

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "report": report
            }
        )

    except HTTPException:
        # re-raise clean HTTP errors
        raise

    except CustomException as ce:
        logger.error(f"Custom exception during report generation: {ce}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(ce))

    except Exception as e:
        logger.exception("Unhandled exception occurred during report generation")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during report generation"
        )
@router.get("/history")
def get_sme_analysis_history(
    db: Session = Depends(get_db),
    limit: int = 50
):
    """
    Returns the latest SME analyses from the database.
    """
    try:
        logger.info("Starting report history fetch")
        history = load_sme_history(db, limit=limit)
        logger.info(f"Fetched {len(history)} records from DB")
        return JSONResponse(
            status_code=200,
            content={"status": "success", "history": history}
        )

    except Exception as e:
        logger.exception("Error fetching SME analysis history")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching history"
        )