# E:\financial-health-ai\backend\services\metrics.py

import sys
import pandas as pd
from typing import Dict

from backend.utils.logger import get_logger
from backend.utils.exceptions import CustomException


class FinancialMetrics:
    """
    Responsible for validating, normalizing,
    and computing financial metrics from transaction data.
    """

    REQUIRED_COLUMNS = {"date", "category", "amount", "type"}  # credit / debit

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    def validate_dataframe(self, df: pd.DataFrame) -> None:
        try:
            self.logger.info("Validating dataframe columns")
            missing = self.REQUIRED_COLUMNS - set(df.columns)
            if missing:
                raise ValueError(f"Missing required columns: {missing}")
        except Exception as e:
            self.logger.error("Dataframe validation failed", exc_info=True)
            raise CustomException(e, sys)

    def normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            self.logger.info("Normalizing dataframe")
            df = df.copy()

            # -----------------------------
            # Convert amounts to numeric
            # -----------------------------
            df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

            # -----------------------------
            # Normalize type & category
            # -----------------------------
            df["type"] = df["type"].astype(str).str.lower().str.strip()
            df["category"] = df["category"].astype(str).str.strip()

            # -----------------------------
            # Map legacy CSV types → credit/debit
            # -----------------------------
            df["type"] = df["type"].replace({"income": "credit", "expense": "debit"})

            return df
        except Exception as e:
            self.logger.error("Dataframe normalization failed", exc_info=True)
            raise CustomException(e, sys)

    def calculate_total_revenue(self, df: pd.DataFrame) -> float:
        try:
            revenue = df[df["type"] == "credit"]["amount"].sum()
            self.logger.info(f"Total revenue calculated: {revenue}")
            return revenue
        except Exception as e:
            self.logger.error("Revenue calculation failed", exc_info=True)
            raise CustomException(e, sys)

    def calculate_total_expenses(self, df: pd.DataFrame) -> float:
        try:
            expenses = df[df["type"] == "debit"]["amount"].sum()
            self.logger.info(f"Total expenses calculated: {expenses}")
            return expenses
        except Exception as e:
            self.logger.error("Expense calculation failed", exc_info=True)
            raise CustomException(e, sys)

    def calculate_net_cashflow(self, df: pd.DataFrame) -> float:
        try:
            revenue = self.calculate_total_revenue(df)
            expenses = self.calculate_total_expenses(df)
            net_cashflow = revenue - expenses

            self.logger.info(f"Net cashflow calculated: {net_cashflow}")
            return net_cashflow
        except Exception as e:
            self.logger.error("Net cashflow calculation failed", exc_info=True)
            raise CustomException(e, sys)

    def category_breakdown(self, df: pd.DataFrame) -> Dict[str, float]:
        try:
            breakdown = df.groupby("category")["amount"].sum().to_dict()
            self.logger.info("Category breakdown calculated")
            return breakdown
        except Exception as e:
            self.logger.error("Category breakdown failed", exc_info=True)
            raise CustomException(e, sys)

    def monthly_cashflow(self, df: pd.DataFrame) -> Dict[str, float]:
        try:
            self.logger.info("Calculating monthly cashflow")
            df = df.copy()
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df["month"] = df["date"].dt.to_period("M").astype(str)

            monthly = df.groupby("month").apply(
                lambda x: x[x["type"] == "credit"]["amount"].sum()
                - x[x["type"] == "debit"]["amount"].sum()
            )

            return monthly.to_dict()
        except Exception as e:
            self.logger.error("Monthly cashflow calculation failed", exc_info=True)
            raise CustomException(e, sys)

    def compute_financial_metrics(self, df: pd.DataFrame) -> Dict:
        """
        Orchestrates all metric calculations
        """
        try:
            self.logger.info("Starting financial metrics computation")

            self.validate_dataframe(df)
            df = self.normalize_dataframe(df)

            metrics = {
                "total_revenue": self.calculate_total_revenue(df),
                "total_expenses": self.calculate_total_expenses(df),
                "net_cashflow": self.calculate_net_cashflow(df),
                "category_breakdown": self.category_breakdown(df),
                "monthly_cashflow": self.monthly_cashflow(df),
            }

            # Optional derived metrics
            metrics["expense_ratio"] = (
                metrics["total_expenses"] / metrics["total_revenue"]
                if metrics["total_revenue"] > 0
                else 0
            )

            self.logger.info("Financial metrics computation completed")
            return metrics

        except Exception as e:
            self.logger.error("Financial metrics computation failed", exc_info=True)
            raise CustomException(e, sys)
