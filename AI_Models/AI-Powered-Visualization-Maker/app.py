import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai
from groq import Groq # <--- New Import

# --- 1. CONFIGURATION & HYBRID AI SETUP ---
st.set_page_config(page_title="AI Powered Visualization Maker", layout="wide")
st.title("📊 AI Powered Visualization Maker (Hybrid Mode)")

# Setup Two Clients
try:
    # 1. Google Client (For Dashboard Logic)
    google_client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    
    # 2. Groq Client (For Unlimited Chat)
    # Ensure you add 'GROQ_API_KEY' to your Streamlit Secrets!
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("⚠️ API Keys Missing! Please check Streamlit Secrets for both GEMINI_API_KEY and GROQ_API_KEY.")
    st.stop()

# --- 2. DATA INGESTION ---
st.sidebar.header("📁 Step 1: Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload Excel or CSV", type=['csv', 'xlsx'])

if uploaded_file:
    if uploaded_file.name.endswith('.xlsx'):
        xl = pd.ExcelFile(uploaded_file)
        selected_sheets = st.sidebar.multiselect("Select sheets", xl.sheet_names, default=xl.sheet_names[0])
        dfs = {s: pd.read_excel(uploaded_file, sheet_name=s) for s in selected_sheets}
    else:
        dfs = {"Data": pd.read_csv(uploaded_file)}

    # --- 3. JOIN LOGIC (Gemini Powered) ---
    active_df = list(dfs.values())[0]
    if len(dfs) > 1:
        st.sidebar.subheader("🔗 Joins")
        left = st.sidebar.selectbox("Left Table", list(dfs.keys()))
        right = st.sidebar.selectbox("Right Table", list(dfs.keys()))
        common = list(set(dfs[left].columns) & set(dfs[right].columns))
        
        if common:
            key = st.sidebar.selectbox("Join Key", common)
            if st.sidebar.button("Join Sheets"):
                active_df = pd.merge(dfs[left], dfs[right], on=key)

    # --- 4. DASHBOARD VS VISUALS ---
    st.write("### 🔍 Data Preview", active_df.head(5))
    view_option = st.radio("Choose Mode:", ["Dashboard", "Individual Visualizations"])

    if view_option == "Dashboard":
        # ... (Your existing 4-visual dashboard code here) ...
        num_cols = active_df.select_dtypes(include='number').columns.tolist()
        if len(num_cols) >= 1:
            c1, c2 = st.columns(2)
            with c1: st.plotly_chart(px.histogram(active_df, x=num_cols[0]))
            with c2: st.plotly_chart(px.pie(active_df, names=active_df.columns[0], values=num_cols[0]))
    else:
        # ... (Your existing menu code here) ...
        st.write("Use the sidebar or menus to create custom visuals.")

    # --- 5. CHAT WINDOW (GROQ POWERED - NO QUOTA LIMITS) ---
    st.divider()
    st.subheader("💬 AI Chat Assistant (Powered by Groq)")
    user_query = st.text_input("Ask a question about your data:")

    if user_query:
        with st.spinner("Groq is processing your data..."):
            # We send the schema to Groq's Llama model
            system_prompt = f"You are a data analyst. The current dataset has these columns: {active_df.columns.tolist()}. Answer the user concisely."
            
            try:
                chat_completion = groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_query},
                    ],
                    model="llama-3.3-70b-versatile", # This is a very powerful, fast model
                )
                st.info(f"🤖 **Groq Analysis:**\n\n{chat_completion.choices[0].message.content}")
            except Exception as e:
                st.error(f"Groq Error: {str(e)}")
