# backend/services/forecasting.py

import sys
from typing import Dict, List, Any
from backend.utils.logger import get_logger
from backend.utils.exceptions import CustomException

class FinancialForecaster:
    """
    Provides 3-month simple linear projections for cashflow.
    """
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    def project_cashflow(self, current_revenue: float, current_expenses: float) -> List[Dict[str, Any]]:
        try:
            self.logger.info("Starting 3-month financial forecasting")
            
            # Basic validation
            if current_revenue is None or current_expenses is None:
                self.logger.warning("Incomplete data for forecasting; using zeroed defaults")
                current_revenue = current_revenue or 0.0
                current_expenses = current_expenses or 0.0

            projections = []
            
            # Simple growth scenario: 5% revenue increase vs 2% expense increase
            for i in range(1, 4):
                proj_rev = round(current_revenue * (1 + (0.05 * i)), 2)
                proj_exp = round(current_expenses * (1 + (0.02 * i)), 2)
                
                projections.append({
                    "month": i,
                    "projected_revenue": proj_rev,
                    "projected_expenses": proj_exp,
                    "projected_net": round(proj_rev - proj_exp, 2)
                })
            
            self.logger.info(f"Forecasting complete. Month 3 Projected Net: {projections[-1]['projected_net']}")
            return projections

        except Exception as e:
            self.logger.error("Failed to generate financial projections", exc_info=True)
            raise CustomException(e, sys)