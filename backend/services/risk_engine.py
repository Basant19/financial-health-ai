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
#Profitability Risk Assessment
def assess_profitability_risk(total_revenue: float, total_expenses: float):
    if total_revenue == 0:
        return {
            "level": "High",
            "reason": "No revenue recorded"
        }

    profit_margin = (total_revenue - total_expenses) / total_revenue

    if profit_margin < RISK_THRESHOLDS["profit_margin"]["medium"]:
        level = "High"
    elif profit_margin < RISK_THRESHOLDS["profit_margin"]["high"]:
        level = "Medium"
    else:
        level = "Low"

    return {
        "level": level,
        "profit_margin": round(profit_margin, 2),
        "reason": f"Profit margin at {round(profit_margin * 100, 1)}%"
    }
#Cash Flow Risk Assessment
def assess_cashflow_risk(net_cashflow: float):
    if net_cashflow < RISK_THRESHOLDS["cashflow"]["negative"]:
        return {
            "level": "High",
            "reason": "Negative cash flow"
        }
    elif net_cashflow == 0:
        return {
            "level": "Medium",
            "reason": "Break-even cash flow"
        }
    else:
        return {
            "level": "Low",
            "reason": "Positive cash flow"
        }
#Expense Load Risk
def assess_expense_risk(total_revenue: float, total_expenses: float):
    if total_revenue == 0:
        return {
            "level": "High",
            "reason": "Expenses without revenue"
        }

    expense_ratio = total_expenses / total_revenue

    if expense_ratio > RISK_THRESHOLDS["expense_ratio"]["high"]:
        level = "High"
    elif expense_ratio > RISK_THRESHOLDS["expense_ratio"]["medium"]:
        level = "Medium"
    else:
        level = "Low"

    return {
        "level": level,
        "expense_ratio": round(expense_ratio, 2),
        "reason": f"Expenses are {round(expense_ratio * 100, 1)}% of revenue"
    }
def aggregate_risk_levels(risks: dict):
    levels = [r["level"] for r in risks.values()]

    if "High" in levels:
        return "High"
    elif "Medium" in levels:
        return "Medium"
    else:
        return "Low"
def evaluate_financial_risk(metrics: dict) -> dict:
    profitability_risk = assess_profitability_risk(
        metrics["total_revenue"],
        metrics["total_expenses"]
    )

    cashflow_risk = assess_cashflow_risk(
        metrics["net_cashflow"]
    )

    expense_risk = assess_expense_risk(
        metrics["total_revenue"],
        metrics["total_expenses"]
    )

    risks = {
        "profitability": profitability_risk,
        "cashflow": cashflow_risk,
        "expense_load": expense_risk
    }

    overall_risk = aggregate_risk_levels(risks)

    return {
        "overall_risk": overall_risk,
        "risk_breakdown": risks
    }
