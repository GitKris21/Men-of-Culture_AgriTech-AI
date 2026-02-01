import streamlit as st
from farm_agent import run_agent

# ----------------------------------------
# PAGE CONFIG
# ----------------------------------------

st.set_page_config(
    page_title="AI Farming Agent",
    page_icon="🌾",
    layout="centered"
)

st.title("🌾 AI-Driven Farming Decision Agent")
st.caption("Autonomous • Weather-aware • Soil-aware • LangGraph-based")

st.divider()

# ----------------------------------------
# INPUT FORM
# ----------------------------------------

with st.form("farm_form"):
    crop = st.text_input("🌱 Crop", placeholder="e.g. Cotton")
    sowing_date = st.date_input("📅 Sowing Date")
    location = st.text_input("📍 Village, State", placeholder="Wardha, Maharashtra")

    submit = st.form_submit_button("Generate 7-Day Plan")

# ----------------------------------------
# RUN AGENT
# ----------------------------------------

if submit:
    if not crop or not location:
        st.error("Please fill all fields.")
    else:
        with st.spinner("🤖 Agent is observing, reasoning & planning..."):
            result = run_agent(
                crop=crop,
                sowing_date=sowing_date.strftime("%Y-%m-%d"),
                location=location
            )

        st.success("✅ Plan Generated")

        # ----------------------------------------
        # OUTPUTS
        # ----------------------------------------

        st.subheader("📋 7-Day Action Plan")
        st.text(result["weekly_plan"])

        with st.expander("🧠 Agent Inferences"):
            st.write("**Crop Stage:**", result.get("stage"))
            st.write("**Soil Type:**", result.get("soil_type"))
            st.write("**Weather (Past):**", result.get("weather"))
            st.write("**Weather (Forecast):**", result.get("weather_forecast"))

        with st.expander("🗂️ Memory (Previous Plans)"):
            for i, plan in enumerate(result.get("memory", []), 1):
                st.markdown(f"**Plan {i}:**\n```\n{plan}\n```")
