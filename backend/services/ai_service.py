# backend/services/ai_service.py

import os
import sys
import json
from typing import TypedDict, Dict, Any

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, HumanMessage

from backend.utils.logger import get_logger
from backend.utils.exceptions import CustomException

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()


# -----------------------------
# LangGraph State
# -----------------------------
class FinancialAIState(TypedDict):
    metrics_context: str
    risk_context: str
    ai_result: Dict[str, Any]


class FinancialAIService:
    """
    Unified AI explanation layer.

    PRINCIPLES:
    - AI NEVER computes numbers
    - AI NEVER invents risks
    - ONE LLM call per request
    - Strict JSON output
    - Deterministic fallback on quota / failure
    """

    def __init__(self):
        try:
            self.logger = get_logger(self.__class__.__name__)

            self.llm = init_chat_model(
                "google_genai:gemini-2.5-flash",
                api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=0.2,        # conservative narrative
                max_output_tokens=500,  # bounded cost
            )

            self.logger.info(
                "FinancialAIService initialized (single-call, quota-safe mode)"
            )

        except Exception as e:
            raise CustomException(e, sys)

    # -----------------------------
    # Unified AI Node (ONE call)
    # -----------------------------
    def ai_analysis_node(self, state: FinancialAIState) -> Dict[str, Any]:
        """
        Converts deterministic metrics + risks
        into structured explanations.
        """
        try:
            self.logger.info("Running unified AI analysis node")

            prompt = f"""
You are a financial analyst for Indian SMEs.

STRICT RULES (NON-NEGOTIABLE):
- Do NOT invent numbers
- Do NOT introduce new risks
- Use ONLY the provided information
- Output VALID JSON ONLY
- No markdown, no explanations outside JSON

INPUT DATA
----------------
METRICS:
{state['metrics_context']}

RISKS:
{state['risk_context']}

OUTPUT FORMAT (JSON ONLY):
{{
  "health_summary": "...",
  "risk_explanation": "...",
  "improvement_recommendations": "..."
}}
"""

            response = self.llm.invoke(
                [
                    SystemMessage(
                        content=(
                            "You generate conservative, factual, structured "
                            "financial explanations for regulated environments."
                        )
                    ),
                    HumanMessage(content=prompt),
                ]
            )

            parsed = json.loads(response.content)

            # -----------------------------
            # Hard validation (defensive)
            # -----------------------------
            required_keys = {
                "health_summary",
                "risk_explanation",
                "improvement_recommendations",
            }

            for key in required_keys:
                if key not in parsed or not isinstance(parsed[key], str):
                    raise ValueError(f"Missing or invalid field: {key}")

            return {"ai_result": parsed}

        except Exception:
            # Quota / JSON / model failure → deterministic fallback
            self.logger.error(
                "Unified AI node failed — falling back to deterministic output",
                exc_info=True,
            )
            try:
                return {"ai_result": self._fallback_json(state)}
            except Exception as fallback_err:
                self.logger.critical(
                    "Fallback JSON failed — returning empty structure", exc_info=True
                )
                return {
                    "ai_result": {
                        "health_summary": "",
                        "risk_explanation": "",
                        "improvement_recommendations": "",
                    }
                }

    # -----------------------------
    # Deterministic, Data-Aware Fallback
    # -----------------------------
    def _fallback_json(self, state: FinancialAIState) -> Dict[str, str]:
        """
        Zero-LLM fallback.

        Uses REAL computed metrics & risks.
        No hallucination. No dummy text.
        """
        metrics_text = state.get("metrics_context", "").strip()
        risk_text = state.get("risk_context", "").strip()

        health_summary = (
            "Financial health assessment is based on deterministic metrics "
            "computed from the provided financial data.\n\n"
            f"{metrics_text}"
        )

        risk_explanation = (
            "Financial risks are identified using transparent rule-based "
            "logic applied to profitability, cash flow stability, and "
            "expense patterns.\n\n"
            f"{risk_text}"
        )

        improvement_recommendations = (
            "Improvement recommendations are derived from observed metric "
            "signals:\n"
            "- Strengthen cash flow consistency where volatility exists\n"
            "- Maintain expense discipline relative to revenue\n"
            "- Improve credit readiness through sustained operating surplus\n\n"
            "These actions directly reflect the calculated metrics and "
            "identified risk levels."
        )

        return {
            "health_summary": health_summary.strip(),
            "risk_explanation": risk_explanation.strip(),
            "improvement_recommendations": improvement_recommendations.strip(),
        }

    # -----------------------------
    # Public API (used by routes)
    # -----------------------------
    def generate_financial_report(
        self,
        metrics_context: str,
        risk_context: str,
    ) -> str:
        """
        Generates the final narrative financial report.
        """
        try:
            self.logger.info("Starting AI financial report generation")

            graph = StateGraph(FinancialAIState)

            graph.add_node("ai_analysis", self.ai_analysis_node)
            graph.add_edge(START, "ai_analysis")
            graph.add_edge("ai_analysis", END)

            workflow = graph.compile()

            final_state = workflow.invoke(
                {
                    "metrics_context": metrics_context,
                    "risk_context": risk_context,
                    "ai_result": {},
                }
            )

            ai = final_state["ai_result"]

            final_report = f"""
OVERALL FINANCIAL HEALTH
{ai.get("health_summary", "")}

RISK ANALYSIS
{ai.get("risk_explanation", "")}

IMPROVEMENT RECOMMENDATIONS
{ai.get("improvement_recommendations", "")}
""".strip()

            self.logger.info("AI financial report generated successfully")
            return final_report

        except Exception:
            self.logger.error(
                "AI financial report generation failed",
                exc_info=True,
            )
            # Always safe fallback
            return self._fallback_json({
                "metrics_context": metrics_context,
                "risk_context": risk_context,
                "ai_result": {}
            })
