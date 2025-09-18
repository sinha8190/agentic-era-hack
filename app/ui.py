
import streamlit as st
import pandas as pd
import requests
import json
import time

st.set_page_config(layout="wide", page_title="CrisisIQ")

# --- STYLING ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

        body {
            font-family: 'Roboto', sans-serif;
            background-color: #f0f2f6;
        }
        .stApp {
            background-color: #f0f2f6;
        }
        h1 {
            color: #0d47a1; /* Darker Blue */
            text-align: center;
            font-weight: 700;
        }
        h2, h3 {
            color: #1565c0; /* Medium Blue */
        }
        .stButton>button {
            background-color: #1976d2; /* Brighter Blue */
            color: white;
            border-radius: 5px;
            padding: 0.5em 1em;
            border: none;
            cursor: pointer;
            font-size: 1em;
            transition: background-color 0.3s;
        }
        .stButton>button:hover {
            background-color: #1565c0; /* Medium Blue */
        }
        .stDeckGlJsonChart {
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stContainer {
            border-radius: 5px;
        }
        .card {
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            padding: 1em;
            margin-bottom: 10px;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .card .stMarkdown {
            font-size: 0.9em;
            line-height: 1.4;
        }
    </style>
""", unsafe_allow_html=True)


st.title("CrisisIQ: Real-Time Hazard Response")

# Initialize session state
if 'events' not in st.session_state:
    st.session_state.events = []
if 'hazard_location' not in st.session_state:
    st.session_state.hazard_location = pd.DataFrame()
if 'shelter_locations' not in st.session_state:
    st.session_state.shelter_locations = pd.DataFrame()
if 'log_placeholders' not in st.session_state:
    st.session_state.log_placeholders = {}

BACKEND_URL = "http://127.0.0.1:8000/run"

# --- UI LAYOUT ---
col1, col2 = st.columns([1, 1])

with col1:
    st.header("Agent Simulation")
    start_button = st.button("Start Simulation")
    st.subheader("Agent Logs")

with col2:
    st.header("Map View")
    map_placeholder = st.empty()

# --- SIMULATION LOGIC ---
if start_button:
    # Clear previous results
    st.session_state.events = []
    st.session_state.hazard_location = pd.DataFrame()
    st.session_state.shelter_locations = pd.DataFrame()
    for placeholder in st.session_state.log_placeholders.values():
        placeholder.empty()
    map_placeholder.map(pd.DataFrame())

    agent_logs = {
        "HazardReaderAgent": "",
        "CoordinatorAgent": "",
        "LogisticsAgent": "",
        "HealthAgent": "",
        "EvacuationAgent": "",
        "InfrastructureAgent": ""
    }

    cols = st.columns(2)
    for i, agent_name in enumerate(agent_logs.keys()):
        with cols[i % 2]:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            with st.container():
                st.markdown(f"### {agent_name}")
                st.session_state.log_placeholders[agent_name] = st.empty()
            st.markdown("</div>", unsafe_allow_html=True)

    try:
        with requests.post(BACKEND_URL, json={"agent_name": "HazardAgent"}, stream=True) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if line:
                    try:
                        event_data = json.loads(line.decode('utf-8'))
                        st.session_state.events.append(event_data)
                        
                        author = event_data.get('author')
                        content = event_data.get('content', {}).get('parts', [{}])[0].get('text', '')

                        if author in agent_logs:
                            agent_logs[author] += content + "\n\n"
                            st.session_state.log_placeholders[author].markdown(agent_logs[author])

                            # --- Special Handling for Map Data ---
                            # 1. Set Hazard Location from Coordinator
                            if author == "CoordinatorAgent" and "Hazard Detected" in content and st.session_state.hazard_location.empty:
                                # Coordinates for ZIP 175131 (Columbia, PA)
                                hazard_lat = 40.0337
                                hazard_lon = -76.5052
                                st.session_state.hazard_location = pd.DataFrame({
                                    'lat': [hazard_lat],
                                    'lon': [hazard_lon],
                                    'size': [1000], # Make marker bigger
                                    'color': ["#FF0000"] # Red marker
                                })

                            # 2. Extract Shelter Locations from Logistics Agent
                            if author == "LogisticsAgent" and "SHELTER_LOCATIONS_JSON:" in content:
                                try:
                                    json_str = content.split("SHELTER_LOCATIONS_JSON:")[1].strip()
                                    shelters = json.loads(json_str)
                                    st.session_state.shelter_locations = pd.DataFrame(shelters)
                                    st.session_state.shelter_locations['size'] = 500
                                    st.session_state.shelter_locations['color'] = "#0000FF" # Blue markers
                                except (json.JSONDecodeError, IndexError) as e:
                                    agent_logs[author] += f"\n**ERROR**: Could not parse shelter locations: {e}\n"
                                    st.session_state.log_placeholders[author].markdown(agent_logs[author])

                            # Update map with any new data
                            map_data = pd.concat([
                                st.session_state.hazard_location,
                                st.session_state.shelter_locations
                            ])
                            map_placeholder.map(map_data, size='size', color='color')

                        time.sleep(0.1) # Small delay for better streaming visualization

                    except json.JSONDecodeError:
                        # Handle non-JSON lines if necessary
                        pass 

    except requests.exceptions.HTTPError as e:
        print("---\n--- DETAILED ERROR ---\n---")
        print(e.response.text)
        print("----------------------")
        st.error(f"HTTP error: {e}\n{e.response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to backend: {e}")
