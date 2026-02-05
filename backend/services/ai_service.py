from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, HumanMessage
import os
from dotenv import load_dotenv

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

llm = init_chat_model(
    "google_genai:gemini-2.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY"),
    max_output_tokens=400,   # 👈 keep each node small
)

# -----------------------------
# Graph State
# -----------------------------
class FinancialAIState(TypedDict):
    metrics_context: str
    risk_context: str
    health_summary: str
    risk_explanation: str
    suggestions: str
    final_report: str


# -----------------------------
# Node 1: Health Summary
# -----------------------------
def health_summary_node(state: FinancialAIState):
    prompt = (
        "You are a financial analyst for Indian SMEs.\n"
        "Explain the overall financial health clearly and simply.\n\n"
        f"{state['metrics_context']}"
    )

    response = llm.invoke([
        SystemMessage(content="Explain only what is visible in the data."),
        HumanMessage(content=prompt)
    ])

    return {"health_summary": response.content}


# -----------------------------
# Node 2: Risk Explanation
# -----------------------------
def risk_explanation_node(state: FinancialAIState):
    prompt = (
        "Explain the following financial risks in simple language.\n"
        "Do not introduce new risks.\n\n"
        f"{state['risk_context']}"
    )

    response = llm.invoke([
        SystemMessage(content="Explain risks conservatively and clearly."),
        HumanMessage(content=prompt)
    ])

    return {"risk_explanation": response.content}


# -----------------------------
# Node 3: Improvement Suggestions
# -----------------------------
def suggestions_node(state: FinancialAIState):
    prompt = (
        "Based on the metrics and risks below, suggest practical improvements.\n"
        "Focus on cash flow, cost control, and credit readiness.\n\n"
        f"{state['metrics_context']}\n\n{state['risk_context']}"
    )

    response = llm.invoke([
        SystemMessage(content="Give realistic, SME-friendly advice."),
        HumanMessage(content=prompt)
    ])

    return {"suggestions": response.content}


# -----------------------------
# Node 4: Final Compiler (NO analysis)
# -----------------------------
def final_compiler_node(state: FinancialAIState):
    final_text = f"""
📊 OVERALL FINANCIAL HEALTH
{state['health_summary']}

⚠️ RISK ANALYSIS
{state['risk_explanation']}

✅ IMPROVEMENT RECOMMENDATIONS
{state['suggestions']}
"""
    return {"final_report": final_text.strip()}


# -----------------------------
# Build LangGraph
# -----------------------------
graph = StateGraph(FinancialAIState)

graph.add_node("health_summary", health_summary_node)
graph.add_node("risk_explanation", risk_explanation_node)
graph.add_node("suggestions", suggestions_node)
graph.add_node("final_compiler", final_compiler_node)

# Parallel execution
graph.add_edge(START, "health_summary")
graph.add_edge(START, "risk_explanation")
graph.add_edge(START, "suggestions")

graph.add_edge("health_summary", "final_compiler")
graph.add_edge("risk_explanation", "final_compiler")
graph.add_edge("suggestions", "final_compiler")

graph.add_edge("final_compiler", END)

workflow = graph.compile()

state_input = {
    "metrics_context": build_ai_context(clean_metrics, []),
    "risk_context": "\n".join(risk_flags),
    "health_summary": "",
    "risk_explanation": "",
    "suggestions": "",
    "final_report": ""
}

final_state = workflow.invoke(state_input)

print("\n===== AI FINANCIAL SUMMARY =====\n")
print(final_state["final_report"])
