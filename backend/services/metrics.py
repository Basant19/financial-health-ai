import pandas as pd
from typing import Dict

REQUIRED_COLUMNS = {
    "date",
    "category",
    "description",
    "amount",
    "type"   # credit / debit
}
def validate_dataframe(df: pd.DataFrame):
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

REQUIRED_COLUMNS = {"date", "category", "amount", "type"}
def validate_dataframe(df: pd.DataFrame):
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    df["type"] = df["type"].str.lower().str.strip()
    df["category"] = df["category"].str.strip()

    return df

def calculate_total_revenue(df: pd.DataFrame) -> float:
    revenue_df = df[df["type"] == "credit"]
    return revenue_df["amount"].sum()

def calculate_total_expenses(df: pd.DataFrame) -> float:
    expense_df = df[df["type"] == "debit"]
    return expense_df["amount"].sum()

def calculate_net_cashflow(df: pd.DataFrame) -> float:
    revenue = calculate_total_revenue(df)
    expenses = calculate_total_expenses(df)
    return revenue - expenses

def category_breakdown(df: pd.DataFrame) -> Dict[str, float]:
    grouped = df.groupby("category")["amount"].sum()
    return grouped.to_dict()


def monthly_cashflow(df: pd.DataFrame) -> Dict[str, float]:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["month"] = df["date"].dt.to_period("M").astype(str)

    monthly = df.groupby("month").apply(
        lambda x: x[x["type"] == "credit"]["amount"].sum()
                - x[x["type"] == "debit"]["amount"].sum()
    )

    return monthly.to_dict()

def compute_financial_metrics(df: pd.DataFrame) -> Dict:
    validate_dataframe(df)
    df = normalize_dataframe(df)

    metrics = {
        "total_revenue": calculate_total_revenue(df),
        "total_expenses": calculate_total_expenses(df),
        "net_cashflow": calculate_net_cashflow(df),
        "category_breakdown": category_breakdown(df),
        "monthly_cashflow": monthly_cashflow(df)
    }

    return metrics
