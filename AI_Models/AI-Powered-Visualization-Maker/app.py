import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai
from google.genai import types

# --- 1. SETUP ---
st.set_page_config(page_title="AI Powered Visualization Maker", layout="wide")
st.title("📊 AI Powered Visualization Maker")

# Connect to Gemini 3 Flash
# Note: For security, we use st.secrets. On your Mac, you can replace this with your key string just to test.
API_KEY = "YOUR_PASTED_API_KEY_HERE" 
client = genai.Client(api_key=API_KEY)

# --- 2. UPLOAD & SHEETS ---
st.sidebar.header("📁 Step 1: Upload Data")
file = st.sidebar.file_uploader("Upload Excel or CSV", type=['csv', 'xlsx'])

if file:
    if file.name.endswith('.xlsx'):
        xl = pd.ExcelFile(file)
        selected_sheets = st.sidebar.multiselect("Select Sheets", xl.sheet_names, default=xl.sheet_names[0])
        dfs = {s: pd.read_excel(file, sheet_name=s) for s in selected_sheets}
    else:
        dfs = {"Data": pd.read_csv(file)}

    # --- 3. JOINS & CARDINALITY ---
    active_df = list(dfs.values())[0]
    if len(dfs) > 1:
        st.sidebar.subheader("🔗 Step 2: Joins")
        left = st.sidebar.selectbox("Left Table", list(dfs.keys()))
        right = st.sidebar.selectbox("Right Table", list(dfs.keys()))
        common = list(set(dfs[left].columns) & set(dfs[right].columns))
        
        if common:
            key = st.sidebar.selectbox("Join Key", common)
            # Logic for Cardinality
            card = "1:1" if dfs[left][key].is_unique and dfs[right][key].is_unique else "1:M"
            st.sidebar.info(f"Cardinality: {card}")
            if st.sidebar.button("Join Sheets"):
                active_df = pd.merge(dfs[left], dfs[right], on=key)

    # --- 4. VISUALIZATION OPTIONS ---
    st.write("### Data Preview", active_df.head(5))
    mode = st.radio("Display Mode", ["Visualizations Menu", "Automated Dashboard"])

    if mode == "Visualizations Menu":
        v_type = st.selectbox("Choose Visual", ["Bar", "Pie", "Line", "Area"])
        x = st.selectbox("Select X Axis", active_df.columns)
        y = st.selectbox("Select Y Axis", active_df.select_dtypes('number').columns)
        fig = px.bar(active_df, x=x, y=y) if v_type == "Bar" else px.pie(active_df, names=x, values=y)
        st.plotly_chart(fig, use_container_width=True)
    else:
        # Automated Dashboard (Simplified)
        c1, c2 = st.columns(2)
        with c1: st.plotly_chart(px.histogram(active_df, x=active_df.columns[0]))
        with c2: st.plotly_chart(px.scatter(active_df, x=active_df.columns[0], y=active_df.columns[-1]))

    # --- 5. NLQ CHAT (Gemini 3 Flash) ---
    st.divider()
    query = st.text_input("💬 Ask Gemini 3 to analyze this data:")
    if query:
        # Use Gemini 3 Flash with 'Low' thinking for speed
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=f"Data Columns: {active_df.columns.tolist()}. User Question: {query}",
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="low")
            )
        )
        st.info(response.text)