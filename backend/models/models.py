# E:\financial-health-ai\backend\models\models.py

from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.exc import SQLAlchemyError
import datetime

from database.database import Base  # <- fixed import
from backend.utils.logger import get_logger
from backend.utils.exceptions import CustomException

# ----------------------------------
# Logger setup
# ----------------------------------
logger = get_logger("Models")

# ----------------------------------
# SME Analysis Model
# ----------------------------------
try:
    class SMEAnalysis(Base):
        __tablename__ = "sme_analyses"

        id = Column(Integer, primary_key=True, index=True)
        business_name = Column(String, default="Standard SME")
        business_type = Column(String)
        timestamp = Column(DateTime, default=datetime.datetime.utcnow)

        financial_metrics = Column(JSON)
        ai_summary = Column(String)
        risk_level = Column(String)
        report_language = Column(String, default="en")

        def __repr__(self):
            return f"<SMEAnalysis id={self.id} business_name={self.business_name} risk={self.risk_level}>"

    logger.info("SMEAnalysis model loaded successfully.")

except SQLAlchemyError as e:
    logger.exception("SQLAlchemyError occurred while defining SMEAnalysis model.")
    raise CustomException(f"Database model error: {str(e)}")

except Exception as e:
    logger.exception("Unexpected error while defining SMEAnalysis model.")
    raise CustomException(f"Unexpected model error: {str(e)}")
