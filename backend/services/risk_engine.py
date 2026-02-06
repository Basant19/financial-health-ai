import sys
from typing import Dict

from backend.utils.logger import get_logger
from backend.utils.exceptions import CustomException


class FinancialRiskEngine:
    """
    Rule-based financial risk evaluation engine.
    Fully deterministic and explainable.
    """

    RISK_THRESHOLDS = {
        "profit_margin": {
            "high": 0.20,
            "medium": 0.10
        },
        "cashflow": {
            "negative": 0
        },
        "expense_ratio": {
            "high": 0.80,
            "medium": 0.60
        }
    }

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    # -----------------------------
    # Profitability Risk
    # -----------------------------
    def assess_profitability_risk(
        self,
        total_revenue: float,
        total_expenses: float
    ) -> Dict:
        try:
            self.logger.info("Assessing profitability risk")

            if total_revenue == 0:
                return {
                    "level": "High",
                    "reason": "No revenue recorded"
                }

            profit_margin = (total_revenue - total_expenses) / total_revenue

            if profit_margin < self.RISK_THRESHOLDS["profit_margin"]["medium"]:
                level = "High"
            elif profit_margin < self.RISK_THRESHOLDS["profit_margin"]["high"]:
                level = "Medium"
            else:
                level = "Low"

            result = {
                "level": level,
                "profit_margin": round(profit_margin, 2),
                "reason": f"Profit margin at {round(profit_margin * 100, 1)}%"
            }

            self.logger.info(f"Profitability risk result: {result}")
            return result

        except Exception as e:
            self.logger.error("Profitability risk assessment failed", exc_info=True)
            raise CustomException(e, sys)

    # -----------------------------
    # Cash Flow Risk
    # -----------------------------
    def assess_cashflow_risk(self, net_cashflow: float) -> Dict:
        try:
            self.logger.info("Assessing cashflow risk")

            if net_cashflow < self.RISK_THRESHOLDS["cashflow"]["negative"]:
                result = {
                    "level": "High",
                    "reason": "Negative cash flow"
                }
            elif net_cashflow == 0:
                result = {
                    "level": "Medium",
                    "reason": "Break-even cash flow"
                }
            else:
                result = {
                    "level": "Low",
                    "reason": "Positive cash flow"
                }

            self.logger.info(f"Cashflow risk result: {result}")
            return result

        except Exception as e:
            self.logger.error("Cashflow risk assessment failed", exc_info=True)
            raise CustomException(e, sys)

    # -----------------------------
    # Expense Load Risk
    # -----------------------------
    def assess_expense_risk(
        self,
        total_revenue: float,
        total_expenses: float
    ) -> Dict:
        try:
            self.logger.info("Assessing expense load risk")

            if total_revenue == 0:
                return {
                    "level": "High",
                    "reason": "Expenses without revenue"
                }

            expense_ratio = total_expenses / total_revenue

            if expense_ratio > self.RISK_THRESHOLDS["expense_ratio"]["high"]:
                level = "High"
            elif expense_ratio > self.RISK_THRESHOLDS["expense_ratio"]["medium"]:
                level = "Medium"
            else:
                level = "Low"

            result = {
                "level": level,
                "expense_ratio": round(expense_ratio, 2),
                "reason": f"Expenses are {round(expense_ratio * 100, 1)}% of revenue"
            }

            self.logger.info(f"Expense risk result: {result}")
            return result

        except Exception as e:
            self.logger.error("Expense risk assessment failed", exc_info=True)
            raise CustomException(e, sys)

    # -----------------------------
    # Aggregate Risk
    # -----------------------------
    def aggregate_risk_levels(self, risks: Dict[str, Dict]) -> str:
        try:
            self.logger.info("Aggregating overall risk level")

            levels = [risk["level"] for risk in risks.values()]

            if "High" in levels:
                overall = "High"
            elif "Medium" in levels:
                overall = "Medium"
            else:
                overall = "Low"

            self.logger.info(f"Overall risk level: {overall}")
            return overall

        except Exception as e:
            self.logger.error("Risk aggregation failed", exc_info=True)
            raise CustomException(e, sys)

    # -----------------------------
    # Public Orchestrator
    # -----------------------------
    def evaluate_financial_risk(self, metrics: Dict) -> Dict:
        """
        Entry point for risk evaluation.
        """
        try:
            self.logger.info("Starting financial risk evaluation")

            profitability_risk = self.assess_profitability_risk(
                metrics["total_revenue"],
                metrics["total_expenses"]
            )

            cashflow_risk = self.assess_cashflow_risk(
                metrics["net_cashflow"]
            )

            expense_risk = self.assess_expense_risk(
                metrics["total_revenue"],
                metrics["total_expenses"]
            )

            risks = {
                "profitability": profitability_risk,
                "cashflow": cashflow_risk,
                "expense_load": expense_risk
            }

            overall_risk = self.aggregate_risk_levels(risks)

            result = {
                "overall_risk": overall_risk,
                "risk_breakdown": risks
            }

            self.logger.info("Financial risk evaluation completed")
            return result

        except Exception as e:
            self.logger.error("Financial risk evaluation failed", exc_info=True)
            raise CustomException(e, sys)
