import folium
from streamlit_folium import st_folium
import streamlit as st
import importlib
import agent

importlib.reload(agent)

app = agent.app   # your graph

st.title("🛰️ Agentic FTTP Cost Intelligence Scout")

st.subheader("📍 Route Selection (Optional Advanced Mode)")

col1, col2 = st.columns(2)

with col1:
    from_loc = st.text_input("From Location", "")

with col2:
    to_loc = st.text_input("To Location", "")

if not from_loc or not to_loc:
    st.warning("Please enter both From and To locations")

if st.button("Get Cost Intelligence"):
    with st.spinner("Calculating route... please wait"):
        st.session_state["result"] = app.invoke({
            "from_loc": from_loc,
            "to_loc": to_loc,
            "scenarios": [],
            "raw_data": {},
            "verified_costs": {},
            "confidence": "",
            "report": "",
            "messages": []
        })

# ✅ ONLY DISPLAY HERE
if "result" in st.session_state:

    result = st.session_state["result"]

    st.success(f"Confidence: {result['confidence']}")
    st.markdown(result["report"])

    map_data = result["raw_data"]

    if map_data.get("route_coords"):

        m = folium.Map(location=map_data["start"], zoom_start=10)

        folium.Marker(map_data["start"], tooltip="Start").add_to(m)
        folium.Marker(map_data["end"], tooltip="End").add_to(m)

        folium.PolyLine(map_data["route_coords"], color="blue", weight=5).add_to(m)

        st.subheader("🗺️ Route Visualization")
        st_folium(m, width=700)