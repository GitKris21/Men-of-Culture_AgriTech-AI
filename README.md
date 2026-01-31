# 🌾 LLM-Based Self-Correcting Smart Farming Agent

A practical demonstration of an **LLM-powered agent** using **LangGraph** ,  that provides **continuous, personalized farming advice** based on real-time inputs like soil condition, weather, and crop stage  with a built-in **feedback loop** to re-evaluate decisions when conditions change.



## 📌 Overview

Traditional farming recommendations are often **one-time and static**.  
This project focuses on building an **intelligent agent** that:

- Understands the **current state of a farm**
- Gives **context-aware advice**
- Continuously **monitors changes**
- **Revisits and corrects its own decisions** using a feedback loop


##SYSTEM ARCHITECTURE##
START
→ Initialize AI Agent

→ Human Input
  • Crop Name
  • Sowing Date
  • Location

→ API Inputs
  • Location API
  • Weather API (Open-Meteo)
    – Current weather data
    – Weather forecast

→ Other Derived Details
  • Soil Moisture (estimated from weather conditions)
  • Crop Stage
    = Current Date − Sowing Date

→ Input Sent to LLM
  • Structured contextual data
  • Passed using LangGraph

→ LLM Searches for Solution
  • Analyzes crop stage
  • Evaluates weather and soil context
  • Determines optimal farming actions

→ Final Output from LLM
  • Context-aware recommendations
  • 7-Day actionable farming plan

→ Check for Weather / Condition Changes
  • Are there changes affecting the 7-day plan?

→ YES
  → Feedback Loop
    • Fetch updated weather data
    • Update context
    • Re-send inputs to LLM
    → Back to Input Sent to LLM

→ NO
  → END
    • Final plan delivered to the user


## 🧠 What the Agent Does

### Inputs
- Soil condition
- Weather data
- Crop stage
- Minimal manual input from farmer

### Variables Considered
- Soil quality
- Rainfall patterns
- Crop cycle
- Regional and seasonal constraints

### Outputs
- Personalized farming advice
- Best crop practices for **current conditions**
- Dynamic suggestions (not one-time recommendations)
- Updated advice when conditions change

---

## 🔁 Feedback Loop (Core Idea)

The agent **does not assume its first decision is final**.

### Example:
- Advice is generated assuming **sunny weather**
- Weather changes to **rainy**
- Agent detects the change
- Decision loops back
- **New advice is generated** based on updated conditions

This makes the agent **self-correcting and adaptive**.

---

## 🧩 Key Agent Features

- ✅ Identifies the **current state of the farm**
- 🔄 Continuously monitors environmental changes
- 🧠 Uses an **LLM for reasoning and decision-making**
- ♻️ Revisits past decisions to check if they still hold true
- 🌱 Provides practical, real-world farming suggestions

---

## 🛠️ Tech Stack

- **Python**
- **LangGraph** – for agent workflow & feedback loops
- **LangChain**
- **LLM (Groq / OpenAI compatible)**
- Weather & location data (API or simulated)

---

## 🏗️ Architecture Breakdown

### 1. State Definition
The agent maintains a structured state containing:
- Current farm conditions
- Last generated advice
- Environmental changes
- Feedback signals

### 2. Decision Node (LLM)
Uses an LLM to:
- Analyze inputs
- Apply agricultural reasoning
- Generate best practices dynamically

### 3. Evaluation Node
Checks whether:
- Conditions have changed
- The previous advice is still valid

### 4. Conditional Routing
- If advice still holds → END
- If conditions change → Loop back and regenerate advice

---

## ▶️ How It Works (Step-by-Step)

Step 1: AI Agent Initialization

Step 2: Human Input Collection

Step 3: Automatic API Data Fetching

Step 4: Context Enrichment

Step 5: Structured Input to LLM

Step 6: LLM Reasoning & Decision Making

Step 7: Generation of 7-Day Action Plan

Step 8: Condition Monitoring

Step 9: Feedback Loop (Adaptive Intelligence)

Step 10: Final Output

The user receives a context-aware, up-to-date decision support output tailored to their crop and environmental conditions.

---

## 🌟 Why This Matters

- Farming conditions are **dynamic**, not static
- One-time recommendations fail in real life
- This agent behaves more like a **real assistant**, not a rule engine
- Demonstrates **true agentic behavior** using LLMs

---

## 🚀 Future Enhancements (Plan to implement)

- Real-time weather API integration
- IoT sensor data for soil monitoring
- Multilingual farmer support

---

## ➕ Additional Ideas Added

The following enhancements were **added beyond the original scope** to strengthen the agent design:

- Continuous monitoring instead of one-time recommendation
- Explicit decision re-validation logic
- LLM-driven reasoning rather than rule-based logic
- Scalable agent architecture using LangGraph

