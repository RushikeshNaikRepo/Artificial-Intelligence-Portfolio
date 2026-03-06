import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai
from groq import Groq

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="AI Powered Visualization Maker", layout="wide")
st.title("📊 AI Powered Visualization Maker (Stable Edition)")

# Secure API Connection
try:
    google_client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("🔑 API Keys not found. Please add GEMINI_API_KEY and GROQ_API_KEY to Secrets.")
    st.stop()

# --- 2. SIDEBAR: DATA LOADING ---
st.sidebar.header("📁 Data Management")
uploaded_file = st.sidebar.file_uploader("Upload Data (Excel/CSV)", type=['csv', 'xlsx'])

if uploaded_file:
    # 1. Load Data Safely
    if uploaded_file.name.endswith('.xlsx'):
        xl = pd.ExcelFile(uploaded_file)
        selected_sheets = st.sidebar.multiselect("Sheets to load", xl.sheet_names, default=xl.sheet_names)
        dfs = {s: pd.read_excel(uploaded_file, sheet_name=s) for s in selected_sheets}
    else:
        dfs = {"Data": pd.read_csv(uploaded_file)}

    # 2. Join Logic
    active_df = list(dfs.values())[0]
    if len(dfs) > 1:
        st.sidebar.subheader("🔗 Joins")
        left = st.sidebar.selectbox("Left Table", list(dfs.keys()))
        right = st.sidebar.selectbox("Right Table", list(dfs.keys()))
        common = list(set(dfs[left].columns) & set(dfs[right].columns))
        if common:
            key = st.sidebar.selectbox("Join Key", common)
            if st.sidebar.button("Join Sheets"):
                active_df = pd.merge(dfs[left], dfs[right], on=key, how='inner')

    # 3. UI STYLE CONTROLS
    st.sidebar.divider()
    st.sidebar.header("🎨 Styling & Filters")
    
    # Feature: Choose Filters
    all_cols = active_df.columns.tolist()
    filter_cols = st.sidebar.multiselect("Columns for Sidebar Filters", all_cols)
    
    # Feature: Global Template (Safe Styling)
    # Using 'plotly_white' or 'ggplot2' is the most stable way to change colors
    theme_choice = st.sidebar.selectbox("Dashboard Theme", ["plotly_white", "plotly_dark", "ggplot2", "seaborn"])
    
    # Feature: Conditional Formatting
    use_cond = st.sidebar.checkbox("Conditional Coloring")
    threshold = st.sidebar.number_input("Threshold", value=0) if use_cond else 0

    # --- 4. DATA FILTERING ---
    filtered_df = active_df.copy()
    if filter_cols:
        st.write("#### 🛠️ Active Filters")
        f_cols = st.columns(len(filter_cols))
        for i, col in enumerate(filter_cols):
            with f_cols[i]:
                vals = st.multiselect(f"Filter: {col}", options=active_df[col].unique(), default=active_df[col].unique())
                filtered_df = filtered_df[filtered_df[col].isin(vals)]

    # --- 5. VISUALIZATION ---
    st.write("### 🔍 Preview", filtered_df.head(5))
    num_cols = filtered_df.select_dtypes('number').columns.tolist()
    cat_cols = filtered_df.select_dtypes('object').columns.tolist()

    if filtered_df.empty:
        st.warning("No data matches filters.")
    elif not num_cols:
        st.warning("Upload numeric data to see charts.")
    else:
        r1c1, r1c2 = st.columns(2)
        r2c1, r2c2 = st.columns(2)

        with r1c1:
            # Distribution
            fig1 = px.histogram(filtered_df, x=num_cols[0], title=f"Dist: {num_cols[0]}", template=theme_choice)
            st.plotly_chart(fig1, use_container_width=True)

        with r1c2:
            # Composition
            target = cat_cols[0] if cat_cols else num_cols[0]
            fig2 = px.pie(filtered_df, names=target, values=num_cols[0], title="Composition", template=theme_choice)
            st.plotly_chart(fig2, use_container_width=True)

        with r2c1:
            # Comparison with Conditional Formatting
            if use_cond:
                filtered_df['_color'] = filtered_df[num_cols[0]].apply(lambda x: 'High' if x > threshold else 'Low')
                fig3 = px.bar(filtered_df, x=cat_cols[0] if cat_cols else num_cols[0], y=num_cols[0], 
                              color='_color', color_discrete_map={'High': '#00CC96', 'Low': '#EF553B'}, template=theme_choice)
            else:
                fig3 = px.bar(filtered_df, x=cat_cols[0] if cat_cols else num_cols[0], y=num_cols[0], template=theme_choice)
            st.plotly_chart(fig3, use_container_width=True)

        with r2c2:
            # Correlation
            if len(num_cols) > 1:
                fig4 = px.scatter(filtered_df, x=num_cols[0], y=num_cols[1], color=num_cols[0], template=theme_choice)
                st.plotly_chart(fig4, use_container_width=True)
            else:
                st.info("Scatter plot requires 2+ numeric columns.")

    # --- 6. AI CHAT ---
    st.divider()
    st.subheader("💬 AI Analyst (Groq)")
    q = st.text_input("Ask a question about the current data:")
    if q:
        with st.spinner("Analyzing..."):
            ctx = {n: d.head(30).to_dict('records') for n, d in dfs.items()}
            inst = f"Expert Analyst Mode. Context: {ctx}. Perform calculations and provide final answers."
            try:
                res = groq_client.chat.completions.create(
                    messages=[{"role":"system","content":inst},{"role":"user","content":q}],
                    model="llama-3.3-70b-versatile"
                )
                st.info(f"🤖 **Insight:**\n\n{res.choices[0].message.content}")
            except Exception as e:
                st.error(f"Chat error: {e}")
