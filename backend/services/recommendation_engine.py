# backend/services/recommendation_engine.py

import sys
from typing import List, Dict, Any
from backend.utils.logger import get_logger
from backend.utils.exceptions import CustomException

class RecommendationEngine:
    """
    Maps SME financial health to specific banking/NBFC products.
    """
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    def get_recommendations(self, metrics: Dict[str, Any], risk_level: str) -> List[Dict[str, str]]:
        try:
            self.logger.info(f"Generating product recommendations for risk level: {risk_level}")
            recommendations = []
            
            # Extract metrics with defaults to prevent KeyErrors
            cashflow = metrics.get('net_cashflow', 0)
            margin = metrics.get('profit_margin', 0)
            revenue = metrics.get('total_revenue', 0)

            # 1. Logic for Working Capital Loans
            if cashflow > 0 and risk_level.lower() == "low":
                recommendations.append({
                    "product": "Overdraft Facility",
                    "provider": "Partner Bank A",
                    "suitability": "High",
                    "benefit": "Optimize daily liquidity with low-interest rates."
                })
            
            # 2. Logic for Term Loans (Expansion)
            if margin > 0.20:
                recommendations.append({
                    "product": "SME Expansion Term Loan",
                    "provider": "NBFC Alpha",
                    "suitability": "Medium",
                    "benefit": "Fixed interest rate for long-term machinery or office upgrade."
                })

            # 3. Logic for Invoice Discounting
            if revenue > 5000:
                recommendations.append({
                    "product": "Invoice Discounting",
                    "provider": "TradeFin Platform",
                    "suitability": "High",
                    "benefit": "Unlock capital tied up in unpaid invoices."
                })

            self.logger.info(f"Successfully identified {len(recommendations)} financial products")
            return recommendations

        except Exception as e:
            self.logger.error("Error in RecommendationEngine logic", exc_info=True)
            raise CustomException(e, sys)