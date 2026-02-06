# backend/services/external_connector.py

import sys
import time
import random
from typing import Dict, Any, List
from backend.utils.logger import get_logger
from backend.utils.exceptions import CustomException

class ExternalConnector:
    """
    Handles integrations with external Banking and GST APIs.
    Simulates real-world API interactions with mock data and latency.
    """

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    def fetch_banking_data(self, account_id: str) -> Dict[str, Any]:
        """
        Simulates fetching real-time balance and transaction status from a Banking API.
        Requirement: Max 2 banking/payment APIs.
        """
        try:
            self.logger.info(f"Initiating connection to Banking API for Account: {account_id}")
            
            # Simulate network latency (0.5 to 1.5 seconds)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Mock API Response
            banking_data = {
                "provider": "MockBank Global API",
                "account_status": "Active",
                "current_balance": round(random.uniform(10000, 50000), 2),
                "currency": "INR",
                "last_sync": "2026-02-06T18:45:00Z",
                "kyc_status": "Verified"
            }
            
            self.logger.info("Successfully retrieved data from Banking API")
            return banking_data

        except Exception as e:
            self.logger.error(f"Failed to fetch banking data for {account_id}", exc_info=True)
            raise CustomException(e, sys)

    def fetch_gst_filing_status(self, gstin: str) -> Dict[str, Any]:
        """
        Simulates fetching GST filing history and compliance metadata from a GSP.
        """
        try:
            self.logger.info(f"Connecting to GST Portal API for GSTIN: {gstin}")
            
            time.sleep(random.uniform(0.3, 1.0))
            
            # Mock GST Data
            gst_data = {
                "gstin": gstin,
                "filing_frequency": "Monthly",
                "last_filed_period": "January 2026",
                "compliance_score": random.choice([85, 90, 95, 100]),
                "pending_litigations": 0,
                "registration_date": "2020-05-12"
            }
            
            self.logger.info(f"GST compliance metadata retrieved for {gstin}")
            return gst_data

        except Exception as e:
            self.logger.error(f"GST API connection error for {gstin}", exc_info=True)
            raise CustomException(e, sys)

    def get_integrated_data_summary(self, business_id: str) -> Dict[str, Any]:
        """
        Orchestrates calls to multiple external providers to build a holistic profile.
        """
        try:
            self.logger.info(f"Aggregating integrated data for Business: {business_id}")
            
            bank_info = self.fetch_banking_data(f"ACC-{business_id[:5]}")
            gst_info = self.fetch_gst_filing_status(f"27AAACN{random.randint(1000,9999)}A1Z5")
            
            return {
                "banking": bank_info,
                "tax_authority": gst_info,
                "integration_timestamp": "2026-02-06T18:45:30Z"
            }
        except Exception as e:
            self.logger.error("Integration aggregation failed", exc_info=True)
            raise CustomException(e, sys)