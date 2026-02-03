# context: This is still a very raw code and still does not work as intended.

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from database import SiScannerDatabase
import time

# --- 1. Desktop UI Configuration ---
st.set_page_config(
    page_title="siScanner | Desktop Command Center",
    page_icon="📡",
    layout="wide", # Maximizes desktop screen real estate
    initial_sidebar_state="expanded"
)

# --- 2. Initialize Persistence Layer ---
if 'db' not in st.session_state:
    st.session_state.db = SiScannerDatabase()

# --- 3. Custom CSS for "Industrial Dark" Aesthetic ---
st.markdown("""
    <style>
    .main { background-color: #05070a; }
    .stMetric { background-color: #11151c; padding: 15px; border-radius: 10px; border: 1px solid #1f2937; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. Sidebar Controls ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/radar.png", width=80)
    st.title("siScanner v1.0")
    st.markdown("---")
    
    op_mode = st.radio("Control Mode", ["Live Telemetry", "Archive Analytics"])
    
    st.markdown("---")
    st.info("EE ITB 2024 | Batch 2024")

# --- 5. Main Dashboard Logic ---
if op_mode == "Archive Analytics":
    st.title("📊 Spatial Data Analytics")
    sessions = st.session_state.db.get_all_sessions()
    
    if not sessions:
        st.warning("No data found in siScanner_DB. Please run simulate_data.py first.")
    else:
        # Layout: Top bar with metrics
        col1, col2, col3 = st.columns(3)
        
        session_options = {str(s['timestamp']): s['_id'] for s in sessions}
        selected_label = st.selectbox("Select Historical Scan", list(session_options.keys()))
        
    # --- Replace the Scan Visualization Block in app/dashboard.py ---

    if st.button("🚀 Render Spatial Map", use_container_width=True):
        scan = st.session_state.db.get_session_by_id(session_options[selected_label])
        df = pd.DataFrame(scan['data'])
        
        # Force Numeric Types (Safety First)
        df['dist'] = pd.to_numeric(df['dist'], errors='coerce')
        df['angle'] = pd.to_numeric(df['angle'], errors='coerce')
        df = df.dropna(subset=['dist', 'angle'])

        fig = go.Figure()

        # The 3D-Look Radar Trace
        fig.add_trace(go.Scatterpolar(
            r=df['dist'],
            theta=df['angle'],
            mode='markers',
            marker=dict(
                size=10,
                color=df['dist'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Distance (mm)"),
                line=dict(width=1, color='white')
            )
        ))

        fig.update_layout(
            template="plotly_dark",
            polar=dict(
                bgcolor="#0e1117",
                # We use 'sector' to show the 0-180 degree sweep area
                sector=[0, 180], 
                angularaxis=dict(
                    thetaunit="degrees",
                    direction="clockwise",
                    rotation=90,      # Puts the 90-degree mark at the top
                    gridcolor="#1f2937"
                ),
                radialaxis=dict(
                    range=[0, df['dist'].max() + 200], # Auto-scale distance
                    showline=True,
                    gridcolor="#1f2937"
                )
            ),
            height=750,
            title=dict(text="siScanner Spatial Projection", font=dict(size=24, color="#00FFCC"))
        )

        st.plotly_chart(fig, use_container_width=True)

else:
    st.title("📡 Live Telemetry Bridge")
    st.info("Hardware connection (pyserial) pending. System currently in standby.")
    st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJqZ3R4Z3R4Z3R4Z3R4Z3R4Z3R4Z3R4Z3R4Z3R4Z3R4JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKMGpxNfQC7rN04/giphy.gif")