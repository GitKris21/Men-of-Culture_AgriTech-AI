import requests
from typing import TypedDict, List, Dict
from datetime import datetime

from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

# ==================================================
# STATE
# ==================================================

class FarmState(TypedDict):
    crop: str
    sowing_date: str
    location: str

    latitude: float
    longitude: float

    soil_type: str
    stage: str

    weather: Dict
    weather_forecast: Dict

    weekly_plan: str
    memory: List[str]

    weather_changed: bool


# ==================================================
# LLM (SAFE WRAPPER)
# ==================================================

def get_llm():
    try:
        return ChatOllama(model="mistral", temperature=0.2)
    except Exception:
        return None


# ==================================================
# LOCATION RESOLVER (SAFE)
# ==================================================

def resolve_location(state: FarmState):
    try:
        res = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": state["location"], "format": "json", "limit": 1},
            headers={"User-Agent": "farm-agent"},
            timeout=8
        ).json()

        if res:
            return {
                "latitude": float(res[0]["lat"]),
                "longitude": float(res[0]["lon"])
            }
    except Exception:
        pass

    # Fallback: Central India (safe agronomy assumptions)
    return {"latitude": 20.0, "longitude": 78.0}


# ==================================================
# SOIL INFERENCE (SAFE)
# ==================================================

def infer_soil_type(lat: float, lon: float) -> str:
    try:
        res = requests.get(
            "https://rest.isric.org/soilgrids/v2.0/properties/query",
            params={
                "lat": lat,
                "lon": lon,
                "property": ["clay", "sand", "soc"],
                "depth": "0-30cm"
            },
            timeout=10
        ).json()

        clay = sand = soc = None
        for layer in res["properties"]["layers"]:
            v = layer["depths"][0]["values"]["mean"]
            if layer["name"] == "clay":
                clay = v
            elif layer["name"] == "sand":
                sand = v
            elif layer["name"] == "soc":
                soc = v

        if clay is not None and sand is not None:
            if clay > 40:
                return "Clayey / Black Soil"
            if sand > 60:
                return "Sandy Soil"
            if soc and soc > 15:
                return "Loamy Fertile Soil"

    except Exception:
        pass

    # Safe default
    return "Loamy Soil"


def soil_agent(state: FarmState):
    return {"soil_type": infer_soil_type(state["latitude"], state["longitude"])}


# ==================================================
# WEATHER TOOL (SAFE)
# ==================================================

def fetch_weather(lat: float, lon: float):
    try:
        data = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": "rain_sum,temperature_2m_max",
                "past_days": 3,
                "forecast_days": 7,
                "timezone": "auto"
            },
            timeout=10
        ).json()

        daily = data["daily"]
        return {
            "past": {
                "rain_last_3_days_mm": sum(daily["rain_sum"][:3]),
                "avg_temp": sum(daily["temperature_2m_max"][:3]) / 3
            },
            "forecast": {
                "rain_next_2_days": sum(daily["rain_sum"][3:5]) > 5,
                "heavy_rain_week": any(r > 20 for r in daily["rain_sum"][3:]),
                "dry_spell_5_days": sum(daily["rain_sum"][3:8]) < 2
            }
        }
    except Exception:
        # Weather-safe defaults
        return {
            "past": {"rain_last_3_days_mm": 0, "avg_temp": 30},
            "forecast": {
                "rain_next_2_days": False,
                "heavy_rain_week": False,
                "dry_spell_5_days": False
            }
        }


# ==================================================
# OBSERVATION AGENT
# ==================================================

def observe_environment(state: FarmState):
    try:
        sowing = datetime.strptime(state["sowing_date"], "%Y-%m-%d")
        days = (datetime.now() - sowing).days
    except Exception:
        days = 30

    if days < 15:
        stage = "Sowing"
    elif days < 45:
        stage = "Vegetative"
    elif days < 75:
        stage = "Flowering"
    else:
        stage = "Maturity"

    weather = fetch_weather(state["latitude"], state["longitude"])

    return {
        "stage": stage,
        "weather": weather["past"],
        "weather_forecast": weather["forecast"]
    }


# ==================================================
# GUARANTEED 7-DAY PLANNER
# ==================================================

def fallback_plan(state: FarmState) -> str:
    return f"""
Day 1–2: Monitor crop health and soil moisture
Day 3: Light irrigation if soil is dry
Day 4: Field inspection for pests/disease
Day 5: Nutrient or soil amendment if required
Day 6: Weed management or resting day
Day 7: General monitoring and preparation

Crop: {state['crop']}
Stage: {state['stage']}
Soil: {state['soil_type']}
"""


def plan_week(state: FarmState):
    llm = get_llm()
    if not llm:
        return {"weekly_plan": fallback_plan(state)}

    prompt = f"""
Create a simple 7-day farming action plan.

Crop: {state['crop']}
Stage: {state['stage']}
Soil: {state['soil_type']}
Rain next 2 days: {state['weather_forecast']['rain_next_2_days']}

Rules:
- One action per day
- Skip irrigation if rain expected
- Keep language simple
"""

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        text = response.content.strip()
        if len(text) < 50:
            raise ValueError("Weak output")
        return {"weekly_plan": text}
    except Exception:
        return {"weekly_plan": fallback_plan(state)}


# ==================================================
# MEMORY + WEATHER MONITOR
# ==================================================

def store_plan(state: FarmState):
    mem = state.get("memory", [])
    mem.append(state["weekly_plan"])
    return {"memory": mem}


def monitor_weather(state: FarmState):
    new_forecast = fetch_weather(
        state["latitude"], state["longitude"]
    )["forecast"]

    return {
        "weather_forecast": new_forecast,
        "weather_changed": new_forecast != state["weather_forecast"]
    }


def alert_and_replan(state: FarmState):
    print("\n🚨 Weather changed → Replanning...\n")
    return {}


def decide_after_monitor(state: FarmState):
    return "replan" if state["weather_changed"] else "end"


# ==================================================
# BUILD GRAPH
# ==================================================

def build_graph():
    g = StateGraph(FarmState)

    g.add_node("loc", resolve_location)
    g.add_node("soil", soil_agent)
    g.add_node("observe", observe_environment)
    g.add_node("plan", plan_week)
    g.add_node("store", store_plan)
    g.add_node("monitor", monitor_weather)
    g.add_node("alert", alert_and_replan)

    g.add_edge(START, "loc")
    g.add_edge("loc", "soil")
    g.add_edge("soil", "observe")
    g.add_edge("observe", "plan")
    g.add_edge("plan", "store")
    g.add_edge("store", "monitor")

    g.add_conditional_edges("monitor", decide_after_monitor, {
        "replan": "alert",
        "end": END
    })

    g.add_edge("alert", "plan")
    return g.compile()


# ==================================================
# RUN
# ==================================================

if __name__ == "__main__":
    app = build_graph()

    state: FarmState = {
        "crop": input("Crop: "),
        "sowing_date": input("Sowing date (YYYY-MM-DD): "),
        "location": input("Village, State: "),
        "latitude": 0.0,
        "longitude": 0.0,
        "soil_type": "",
        "stage": "",
        "weather": {},
        "weather_forecast": {},
        "weekly_plan": "",
        "memory": [],
        "weather_changed": False
    }

    result = app.invoke(state)

    print("\n🌾 FINAL 7-DAY PLAN")
    print("=" * 40)
    print(result["weekly_plan"])
def run_agent(crop: str, sowing_date: str, location: str) -> dict:
    app = build_graph()

    state: FarmState = {
        "crop": crop,
        "sowing_date": sowing_date,
        "location": location,
        "latitude": 0.0,
        "longitude": 0.0,
        "soil_type": "",
        "stage": "",
        "weather": {},
        "weather_forecast": {},
        "weekly_plan": "",
        "memory": [],
        "weather_changed": False
    }

    return app.invoke(state)