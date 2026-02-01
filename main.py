import os
from typing import TypedDict, List, Dict
from datetime import datetime

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

load_dotenv()

# ---------------- STATE ----------------

class FarmState(TypedDict):
    crop: str
    sowing_date: str
    location: str

    stage: str
    weather: Dict
    weather_forecast: Dict

    weekly_plan: str
    memory: List[str]

    weather_changed: bool


# ---------------- LLM ----------------

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
    api_key=os.getenv("GROQ_API_KEY")
)

# ---------------- OBSERVATION AGENTS ----------------

def observe_environment(state: FarmState):
    """Infer crop stage + fetch weather (mocked for demo)"""

    # Crop stage inference
    sowing = datetime.strptime(state["sowing_date"], "%d-%m-%Y")
    days = (datetime.now() - sowing).days

    if days < 15:
        stage = "sowing"
    elif days < 45:
        stage = "vegetative"
    elif days < 75:
        stage = "flowering"
    else:
        stage = "maturity"

    # Weather observation (mocked)
    weather = {
        "rain_last_3_days_mm": 10,
        "avg_temp": 32
    }

    forecast = {
        "rain_next_2_days": False,
        "heat_risk": False
    }

    return {
        "stage": stage,
        "weather": weather,
        "weather_forecast": forecast
    }

# ---------------- 7-DAY PLANNER ----------------

def plan_week(state: FarmState):
    llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
    api_key=os.getenv("GROQ_API_KEY"))
    prompt = f"""
You are an agricultural planning agent.

Crop: {state['crop']}
Stage: {state['stage']}
Location: {state['location']}
Weather forecast: {state['weather_forecast']}

TASK:
Create a 7-day action plan.
Rules:
- One primary action per day
- Avoid irrigation if rain is expected
- Avoid fertilizer near maturity
- Include rest days if no action is needed
- Keep it simple and practical
"""

    response = llm.invoke(prompt)

    return {
        "weekly_plan": response.content
    }

# ---------------- MEMORY ----------------

def store_plan(state: FarmState):
    memory = state.get("memory", [])
    memory.append(state["weekly_plan"])

    return {
        "memory": memory
    }

# ---------------- WEATHER MONITOR ----------------

def monitor_weather(state: FarmState):
    """
    Simulates weather change detection.
    In real system → re-fetch forecast & compare
    """

    # Simulate a mid-week weather change
    new_forecast = {
        "rain_next_2_days": True,   # changed
        "heat_risk": False
    }

    changed = new_forecast != state["weather_forecast"]

    return {
        "weather_forecast": new_forecast,
        "weather_changed": changed
    }

# ---------------- ALERT + REPLAN ----------------

def alert_and_replan(state: FarmState):
    print("\n🚨 WEATHER ALERT")
    print("Weather forecast has changed.")
    print("Updating your 7-day plan...\n")

    return {}  # control passes back to planner

# ---------------- CONTROL ----------------

def decide_after_monitor(state: FarmState):
    if state["weather_changed"]:
        return "replan"
    return "end"

# ---------------- BUILD GRAPH ----------------

def build_graph():
    graph = StateGraph(FarmState)

    graph.add_node("observe", observe_environment)
    graph.add_node("plan", plan_week)
    graph.add_node("store", store_plan)
    graph.add_node("monitor", monitor_weather)
    graph.add_node("alert", alert_and_replan)

    graph.add_edge(START, "observe")
    graph.add_edge("observe", "plan")
    graph.add_edge("plan", "store")
    graph.add_edge("store", "monitor")

    graph.add_conditional_edges(
        "monitor",
        decide_after_monitor,
        {
            "replan": "alert",
            "end": END
        }
    )

    graph.add_edge("alert", "plan")

    return graph.compile()

# ---------------- RUN ----------------

if __name__ == "__main__":
    app = build_graph()

    initial_state: FarmState = {
        "crop": input("Crop name: "),
        "sowing_date": input("Sowing date (YYYY-MM-DD): "),
        "location": input("Village, State: "),
        "stage": "",
        "weather": {},
        "weather_forecast": {},
        "weekly_plan": "",
        "memory": [],
        "weather_changed": False
    }

    result = app.invoke(initial_state)

    print("\n🌾 FINAL 7-DAY ACTION PLAN")
    print("=" * 50)
    print(result["weekly_plan"])
