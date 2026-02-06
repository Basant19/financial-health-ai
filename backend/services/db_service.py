# backend/services/db_service.py

from sqlalchemy.orm import Session
from typing import List, Dict, Union
import json
import numpy as np

from backend.models.models import SMEAnalysis
from backend.utils.logger import get_logger
from backend.utils.exceptions import CustomException
from backend.utils.security import encrypt_string, decrypt_string

logger = get_logger("DBService")


def save_sme_analysis(
    db: Session,
    business_name: str,
    business_type: str,
    financial_metrics: dict,
    ai_summary: str,
    risk_level: str,
    report_language: str = "en"
) -> SMEAnalysis:
    """
    Encrypts and saves an SMEAnalysis record to the database.

    Stores financial_metrics as JSON to preserve structure.
    Converts np.float64 → float to ensure JSON serializable.
    """
    try:
        logger.info(f"Encrypting and saving analysis for business: {business_name}")

        # Convert np.float64 to float for JSON
        def convert_np(obj):
            if isinstance(obj, np.float64):
                return float(obj)
            if isinstance(obj, dict):
                return {k: convert_np(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [convert_np(v) for v in obj]
            return obj

        metrics_json = json.dumps(convert_np(financial_metrics))
        encrypted_metrics = encrypt_string(metrics_json)
        encrypted_summary = encrypt_string(ai_summary)

        analysis = SMEAnalysis(
            business_name=business_name,
            business_type=business_type,
            financial_metrics=encrypted_metrics,
            ai_summary=encrypted_summary,
            risk_level=risk_level,
            report_language=report_language
        )

        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        logger.info(f"SME analysis saved successfully with ID: {analysis.id}")
        return analysis

    except Exception as e:
        logger.exception("Failed to save SME analysis")
        raise CustomException(f"Database save error: {str(e)}")


def load_sme_history(
    db: Session,
    limit: int = 50
) -> List[Dict[str, Union[str, dict]]]:
    """
    Loads the latest SME analysis records with decrypted metrics and AI summaries.
    Converts financial_metrics JSON back to Python dict.
    """
    try:
        logger.info(f"Fetching the last {limit} SME analyses from DB")

        analyses = (
            db.query(SMEAnalysis)
            .order_by(SMEAnalysis.timestamp.desc())
            .limit(limit)
            .all()
        )

        result: List[Dict[str, Union[str, dict]]] = []

        for a in analyses:
            try:
                decrypted_metrics_json = decrypt_string(a.financial_metrics)
                decrypted_metrics = json.loads(decrypted_metrics_json)
                decrypted_summary = decrypt_string(a.ai_summary)
            except Exception:
                decrypted_metrics = decrypted_summary = "Decryption failed"
                logger.warning(f"Failed to decrypt analysis ID {a.id}")

            result.append({
                "id": a.id,
                "business_name": a.business_name,
                "business_type": a.business_type,
                "timestamp": a.timestamp.isoformat() if a.timestamp else None,
                "financial_metrics": decrypted_metrics,
                "ai_summary": decrypted_summary,
                "risk_level": a.risk_level,
                "report_language": a.report_language
            })

        logger.info(f"Successfully fetched {len(result)} SME analyses")
        return result

    except Exception as e:
        logger.exception("Failed to load SME history")
        raise CustomException(f"Database load error: {str(e)}")
