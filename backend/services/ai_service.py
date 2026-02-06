# backend/services/ai_service.py

import os
import sys
from typing import TypedDict, Dict, Any

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage

from backend.utils.logger import get_logger
from backend.utils.exceptions import CustomException

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

# -----------------------------
# Clean Structured Output Schema
# -----------------------------
class AnalysisResponse(TypedDict):
    """
    Structured financial analysis for SMEs.
    Note: Keep docstrings simple to avoid schema bloat in the API call.
    """
    health_summary: str
    risk_explanation: str
    improvement_recommendations: str

# -----------------------------
# LangGraph State
# -----------------------------
class FinancialAIState(TypedDict):
    metrics_context: str
    risk_context: str
    ai_result: Dict[str, Any]

# -----------------------------
# AI Service Class
# -----------------------------
class FinancialAIService:
    """
    AI explanation layer using Structured Output to ensure valid JSON responses.
    Automatically traces to LangSmith via environment variables.
    """

    def __init__(self):
        try:
            self.logger = get_logger(self.__class__.__name__)

            # Initialize base model
            
            base_model = init_chat_model(
                "google_genai:gemini-2.5-flash",
                api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=0.1,
                max_output_tokens=500, # Increased slightly for descriptive content
            )

            # Bind structured output
            # This handles parsing internally and avoids the JsonOutputParser crash
            self.llm = base_model.with_structured_output(AnalysisResponse)

            self.logger.info("FinancialAIService initialized with clean Structured Output")

        except Exception as e:
            raise CustomException(e, sys)

    # -----------------------------
    # Unified AI Node
    # -----------------------------
    def ai_analysis_node(self, state: FinancialAIState) -> Dict[str, Any]:
        """
        Converts deterministic data into structured narratives.
        Handles empty or malformed LLM responses via fallback logic.
        """
        try:
            self.logger.info("Running AI analysis node")

            # Clean, concise prompt to prevent 'writer's block' in the model
            prompt = f"""Analyze the following SME financial data. 
Return ONLY a JSON object with a summary, risk explanation, and recommendations.

METRICS:
{state['metrics_context']}

RISKS:
{state['risk_context']}
"""

            # Invoke the model (The wrapper returns a dict directly)
            result = self.llm.invoke([HumanMessage(content=prompt)])

            # Safety check for empty or invalid output
            if not result or not isinstance(result, dict):
                self.logger.warning("LLM returned empty or invalid structure - using fallback")
                return {"ai_result": self._fallback_json(state)}

            return {"ai_result": result}

        except Exception as e:
            self.logger.error(f"AI Node parsing error: {str(e)}", exc_info=True)
            return {"ai_result": self._fallback_json(state)}

    # -----------------------------
    # Deterministic Fallback
    # -----------------------------
    def _fallback_json(self, state: FinancialAIState) -> Dict[str, str]:
        """
        Provides a safe, rule-based response if the AI layer fails.
        """
        metrics = state.get("metrics_context", "N/A")
        risks = state.get("risk_context", "N/A")

        return {
            "health_summary": f"Automated analysis based on metrics: {metrics[:100]}...",
            "risk_explanation": f"Rule-based risk detection: {risks[:100]}...",
            "improvement_recommendations": "Maintain liquidity, monitor debt ratios, and optimize operational expenses."
        }

    # -----------------------------
    # Public API
    # -----------------------------
    def generate_financial_report(self, metrics_context: str, risk_context: str) -> str:
        """
        Compiles the LangGraph and returns the final string report.
        """
        try:
            self.logger.info("Generating final report narrative")

            graph = StateGraph(FinancialAIState)
            graph.add_node("ai_analysis", self.ai_analysis_node)
            graph.add_edge(START, "ai_analysis")
            graph.add_edge("ai_analysis", END)
            workflow = graph.compile()

            final_state = workflow.invoke({
                "metrics_context": metrics_context, 
                "risk_context": risk_context, 
                "ai_result": {}
            })

            ai = final_state["ai_result"]

            return f"""
OVERALL FINANCIAL HEALTH
{ai.get('health_summary', '')}

RISK ANALYSIS
{ai.get('risk_explanation', '')}

IMPROVEMENT RECOMMENDATIONS
{ai.get('improvement_recommendations', '')}
""".strip()

        except Exception as e:
            self.logger.error("Report generation workflow failed", exc_info=True)
            fb = self._fallback_json({"metrics_context": metrics_context, "risk_context": risk_context})
            return f"HEALTH: {fb['health_summary']}\nRISKS: {fb['risk_explanation']}"