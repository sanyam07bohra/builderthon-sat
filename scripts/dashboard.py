import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Space Debris Dashboard", layout="wide")
st.title("🛰️ Satellite Collision Risk Dashboard")

try:
    df = pd.read_csv("data/collision_risks.csv")
    st.metric("Total Risk Events", len(df))
    
    # Create a 3D Scatter or Map
    st.subheader("Global Risk Map")
    fig = px.scatter_geo(df, lat=[0]*len(df), lon=[0]*len(df), hover_name="Satellite 1", 
                         title="Risk Encounters", projection="natural earth")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Detailed Log")
    st.dataframe(df)
except:
    st.warning("No data found. Run the scripts in Step 3 and 4 first!")