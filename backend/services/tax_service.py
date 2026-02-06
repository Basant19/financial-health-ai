# backend/services/tax_service.py

import sys
from typing import Dict, Any
from backend.utils.logger import get_logger
from backend.utils.exceptions import CustomException

class TaxComplianceService:
    """
    Rule-based engine for GST estimation and tax compliance checking.
    Calculates liability based on the standard 18% GST rate for services/goods.
    """

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        # Standard GST parameters
        self.GST_RATE = 0.18  # 18%
        self.COMPLIANCE_THRESHOLD = 2000000  # 20 Lakhs for GST registration requirement

    def perform_tax_check(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates GST liability and checks for compliance risks.
        
        Logic:
        - Output Tax = Total Revenue * 18%
        - Input Tax Credit (ITC) = Total Expenses * 18% (Estimated)
        - Net GST Liability = Output Tax - ITC
        """
        try:
            self.logger.info("Starting tax compliance and GST estimation")

            revenue = metrics.get("total_revenue", 0.0)
            expenses = metrics.get("total_expenses", 0.0)
            net_cashflow = metrics.get("net_cashflow", 0.0)

            # 1. GST Calculations
            output_tax = round(revenue * self.GST_RATE, 2)
            input_tax_credit = round(expenses * self.GST_RATE, 2)
            net_gst_payable = max(0, round(output_tax - input_tax_credit, 2))

            # 2. Compliance Flags
            compliance_flags = []
            
            # Registration check
            if revenue > self.COMPLIANCE_THRESHOLD:
                compliance_flags.append("Revenue exceeds 20L threshold. Ensure GST registration is active.")
            
            # Liquidity check (Can the business pay its tax bill?)
            is_reserve_sufficient = net_cashflow >= net_gst_payable
            if not is_reserve_sufficient:
                compliance_flags.append("Insufficient net cash flow to cover estimated GST liability.")

            # 3. Status determination
            tax_status = "Good" if is_reserve_sufficient else "Risk"

            result = {
                "estimated_output_gst": output_tax,
                "estimated_itc": input_tax_credit,
                "net_gst_payable": net_gst_payable,
                "tax_reserve_status": tax_status,
                "compliance_alerts": compliance_flags,
                "gst_rate_applied": f"{int(self.GST_RATE * 100)}%"
            }

            self.logger.info(f"Tax check completed. Net GST Payable: {net_gst_payable}")
            return result

        except Exception as e:
            self.logger.error("Error during tax compliance calculation", exc_info=True)
            raise CustomException(e, sys)