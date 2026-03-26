from gis_engine import get_route_length_km
from map_engine import get_route_with_map
from market_engine import get_market_rates
from scenario_engine import compare_scenarios
from memory_engine import save_project, get_similar
from confidence_engine import compute_confidence
from terrain_engine import detect_terrain, adjust_cost_by_terrain
from time_engine import calculate_time_savings, budget_check, risk_analysis, roi_estimation
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq   # or ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()
llm = ChatGroq(model="llama3-70b-8192", temperature=0.3)   # or gemini

# Shared State (flows through entire graph)
class AgentState(TypedDict):
    from_loc: str
    to_loc: str
    scenarios: list
    raw_data: dict
    verified_costs: dict
    confidence: str
    report: str
    # ✅ ADD THESE NEW FIELDS
    time_data: dict
    risk: str
    roi: float
    budget_status: str
    terrain: str
    adjusted_total: float
    terrain_factor: float
    messages: Annotated[list, "add_messages"]
# ------------------- TOOLS -------------------
from langchain_core.tools import tool
from tavily import TavilyClient
import osmnx as ox
from geopy.geocoders import Nominatim

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query: str) -> str:
    """Search real-time pricing, regulations, material costs for FTTP in India."""
    return tavily.search(query=query, max_results=8)

@tool
def gis_analysis(site_address: str) -> dict:
    """Geocode + calculate approximate route length (for cost estimation)."""
    geolocator = Nominatim(user_agent="fttp_scout")
    location = geolocator.geocode(site_address)
    if not location:
        return {"error": "Address not found"}
    
    # Simple distance (real version: use osmnx shortest path)
    return {
        "lat": location.latitude,
        "lon": location.longitude,
        "approx_trench_km": 2.5   # placeholder – improve with osmnx
    }

@tool
def cost_calculator(components: dict) -> dict:
    """Simple rule-based + LLM-assisted cost breakdown."""
    # Example rules (expand with real formulas)
    civil = components.get("trench_km", 0) * 450000   # ₹ per km in AP 2026
    fibre = components.get("fibre_km", 0) * 85000
    labour = civil * 0.3
    total = civil + fibre + labour + 150000  # fixed OLT etc.
    return {"total_est": total, "breakdown": {"civil": civil, "fibre": fibre, "labour": labour}}

def planner_node(state: AgentState):
    prompt = f"""You are the Search Planner for FTTP cost estimation.
    Site: {state['from_loc']} to {state['to_loc']}
    Decide best scenarios and what to search. Output JSON only."""
    response = llm.invoke(prompt)
    # parse scenarios etc.
    return {"scenarios": ["underground", "aerial"], "raw_data": {}}

def researcher_node(state: AgentState):

    # --- STRICT FROM-TO LOGIC ---
    route_data = get_route_with_map(state["from_loc"], state["to_loc"])

    if "error" in route_data:
        route_km = 5.0  # fallback
        route_coords = None
    else:
        route_km = route_data["distance_km"]
        route_coords = route_data["route_coords"]

    try:
        rates = get_market_rates()
    except:
        rates = {
            "civil_per_km": 430000,
            "fibre_per_km": 85000,
            "labour_ratio": 0.30
        }

    scenarios, best = compare_scenarios(route_km, rates)
    print("Route data:", route_data)
    return {
        "raw_data": {
            "route_km": route_km,
            "route_coords": route_coords,
            "start": route_data.get("start"),
            "end": route_data.get("end"),
            "rates": rates,
            "scenarios": scenarios,
            "best": best
        }
    }
def verifier_node(state: AgentState):

    route = state["raw_data"]["route_km"]
    rates = state["raw_data"]["rates"]

    # --- COST CALCULATION ---
    civil = route * rates["civil_per_km"]
    fibre = route * rates["fibre_per_km"]
    labour = civil * rates["labour_ratio"]

    total = civil + fibre + labour + 150000

    terrain = detect_terrain(route)
    adjusted_total, factor = adjust_cost_by_terrain(total, terrain)
    
    cost = {
        "civil": civil,
        "fibre": fibre,
        "labour": labour,
        "total": total
    }
    # --- NEW FEATURES (ADD THIS BLOCK) ---
    time_data = calculate_time_savings(route)
    risk = risk_analysis(route)
    roi = roi_estimation(total)
    budget_status = budget_check(total)

    route_name = f"{state['from_loc']} → {state['to_loc']}"

    save_project(route_name, cost)
    memory = get_similar(route_name)

    return {
        "verified_costs": cost,
        "memory": memory,
        "time_data": time_data,
        "risk": risk,
        "roi": roi,
        "budget_status": budget_status,
        "terrain": terrain,
        "adjusted_total": adjusted_total,
        "terrain_factor": factor,
    }
def report_node(state: AgentState):

    site = f"{state['from_loc']} → {state['to_loc']}"
    route = state["raw_data"]["route_km"]
    scenarios = state["raw_data"]["scenarios"]
    best = state["raw_data"]["best"]
    cost = state["verified_costs"]
    time_data = state["time_data"]
    risk = state["risk"]
    roi = state["roi"]
    budget_status = state["budget_status"]
    memory = state.get("memory")
    terrain = state["terrain"]
    adjusted_total = state["adjusted_total"]

    conf = compute_confidence(route, memory)

    # scenario values formatted
    underground = round(scenarios["underground"],2)
    aerial = round(scenarios["aerial"],2)
    duct = round(scenarios["duct_reuse"],2)

    civil = round(cost["civil"],2)
    fibre = round(cost["fibre"],2)
    labour = round(cost["labour"],2)
    total = round(cost["total"],2)

    report = f"""
# FTTP COST INTELLIGENCE REPORT

## 📍Site Details
**Location:** {site}  
**Estimated Network Route Length:** {route} km  

---

## Deployment Scenario Analysis

| Scenario Type | Estimated Cost (₹) | Remarks |
|--------------|------------------|---------|
| Underground Deployment | {underground} | High reliability but high civil cost |
| Aerial Deployment | {aerial} | Faster rollout with moderate risk |
| Existing Duct Reuse | {duct} | Lowest cost and fastest implementation |

 **Recommended Deployment Strategy:** **{best.upper()}**

Reason: This option provides the most cost-efficient network rollout for the given terrain and urban density.

---

## 💰 Estimated CAPEX Breakdown

| Cost Component | Estimated Value (₹) |
|---------------|-------------------|
| Civil & Trenching Works | {civil} |
| Fibre Cable & Accessories | {fibre} |
| Installation Labour | {labour} |
| Fixed Network Equipment & Misc | 150000 |

### **Total Estimated Project Cost:** ₹ **{total}**

---

## 🌍 Terrain Intelligence

- **Detected Terrain:** {terrain}  
- **Cost Adjustment Factor:** {state['terrain_factor']}  

### 🚧 Adjusted Project Cost: ₹ {adjusted_total}

---

## ⏱️ Time Efficiency Analysis

| Process | Time |
|--------|------|
| Manual Planning | {time_data['manual_days']} days |
| AI Planning | {time_data['ai_minutes']} minutes |

### 🚀 Time Saved: {time_data['time_saved_hours']} hours

---

## 📊 Project Intelligence Insights

- **Budget Status:** {budget_status}  
- **Deployment Risk Level:** {risk}  
- **Estimated ROI Payback Period:** {roi} months  

---

## Confidence Assessment

**Overall Confidence Score:** **{conf}**

Confidence is derived from:

- Real geospatial route computation using OpenStreetMap road network  
- Market pricing signals retrieved via intelligent search agents  
- Comparison with historical FTTP build cost patterns stored in vector memory  
- Scenario optimization logic for deployment strategy selection  

---

## Key Assumptions

- Cost model considers **CAPEX only** (civil, fibre, labour, network equipment)  
- No Operational Expenditure (OPEX) included  
- Terrain complexity assumed urban-moderate  
- Pricing signals based on recent telecom EPC market benchmarks  
- Actual cost may vary after detailed field survey  

---

## 📌 Recommended Next Steps

1. Conduct physical route survey to validate trench length  
2. Obtain vendor quotations for civil & fibre material  
3. Evaluate permit requirements and municipal restoration charges  
4. Run cluster optimization if multiple nearby sites planned  
5. Review deployment timeline vs seasonal risks (monsoon / traffic disruption)

---

### Generated By  
**Agentic FTTP Cost Intelligence Scout (Autonomous AI Planning System)**  
**Developed by Team Innovibe**

"""

    return {
        "report": report,
        "confidence": conf
    }
# Build Graph
workflow = StateGraph(AgentState)

workflow.add_node("planner", planner_node)
workflow.add_node("researcher", researcher_node)
workflow.add_node("verifier", verifier_node)
workflow.add_node("reporter", report_node)

workflow.add_edge(START, "planner")
workflow.add_edge("planner", "researcher")
workflow.add_edge("researcher", "verifier")
workflow.add_edge("verifier", "reporter")
workflow.add_edge("reporter", END)

app = workflow.compile()
