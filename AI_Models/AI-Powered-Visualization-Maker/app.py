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

    # Extract Data Types for dynamic operations
    num_cols = filtered_df.select_dtypes('number').columns.tolist()
    cat_cols = filtered_df.select_dtypes('object').columns.tolist()

    # --- NEW FEATURE: UI/UX TABBED INTERFACE ---
    tab_workspace, tab_dashboard, tab_ai = st.tabs(["📋 Data Workspace", "📊 Visual Dashboard", "🤖 AI Analyst"])

    # ==========================================
    # TAB 1: DATA WORKSPACE (Data Prep & Profiling)
    # ==========================================
    with tab_workspace:
        st.write("### 🔍 Preview", filtered_df.head(5))
        
        # New Feature: Export Processed Data Button
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Dataset (CSV)",
            data=csv_data,
            file_name="filtered_data.csv",
            mime="text/csv"
        )
        
        st.divider()
        
        # New Feature: Data Engineering Layer (Aggregation Builder)
        st.write("### 🧮 Group-By & Aggregation Builder")
        if cat_cols and num_cols:
            col_g1, col_g2, col_g3 = st.columns(3)
            with col_g1:
                group_col = st.selectbox("Group By (Category)", cat_cols, key="group_col_select")
            with col_g2:
                target_num_col = st.selectbox("Target Metric (Numeric)", num_cols, key="target_num_select")
            with col_g3:
                agg_func = st.selectbox("Aggregation Method", ["sum", "mean", "count", "min", "max"])
            
            if st.button("Generate Summary Table"):
                summary_df = filtered_df.groupby(group_col)[target_num_col].agg(agg_func).reset_index()
                st.dataframe(summary_df, use_container_width=True)
        else:
            st.info("Aggregation builder requires at least one categorical and one numeric column.")

    # ==========================================
    # TAB 2: VISUAL DASHBOARD (KPIs, Charts, & Anomalies)
    # ==========================================
    with tab_dashboard:
        if filtered_df.empty:
            st.warning("No data matches filters.")
        elif not num_cols:
            st.warning("Upload numeric data to see charts.")
        else:
            # New Feature: High-Level Dynamic Metric Cards
            st.write("### 📈 Key Performance Indicators")
            metric_cols = st.columns(min(len(num_cols), 4) + 1)
            with metric_cols[0]:
                st.metric(label="Total Records", value=f"{len(filtered_df):,}")
            
            for idx, n_col in enumerate(num_cols[:4]):
                with metric_cols[idx + 1]:
                    col_sum = filtered_df[n_col].sum()
                    # Format to clean string representation
                    formatted_val = f"{col_sum:,.2f}" if isinstance(col_sum, float) else f"{col_sum:,}"
                    st.metric(label=f"Total {n_col}", value=formatted_val)
            
            st.divider()

            # Existing Charts Grid Layout
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

            # New Feature: Statistical Anomaly Detection Section
            st.divider()
            st.write("### 🚨 Statistical Anomaly Detection")
            anomaly_col = st.selectbox("Select Numeric Column to Scan for Outliers", num_cols)
            
            mean_val = filtered_df[anomaly_col].mean()
            std_val = filtered_df[anomaly_col].std()
            
            if std_val > 0:
                # Flag rows that are more than 2 standard deviations away from the mean
                outliers = filtered_df[abs(filtered_df[anomaly_col] - mean_val) > (2 * std_val)]
                if not outliers.empty:
                    st.error(f"Found {len(outliers)} data point(s) behaving as statistical anomalies (> 2 Standard Deviations from mean):")
                    st.dataframe(outliers[[cat_cols[0] if cat_cols else anomaly_col, anomaly_col]], use_container_width=True)
                else:
                    st.success("No significant statistical anomalies detected in this metric profile.")
            else:
                st.info("Not enough variation to calculate anomalies.")

    # ==========================================
    # TAB 3: AI ANALYST (Groq Chat Integration)
    # ==========================================
    with tab_ai:
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
