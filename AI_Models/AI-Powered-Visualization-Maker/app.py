import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai
from groq import Groq

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="AI Powered Visualization Maker", layout="wide")
st.title("📊 AI Powered Visualization Maker (Stable Pro)")

# Secure API (Uses your existing Secrets)
try:
    google_client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("🔑 API Keys not found in Secrets. Please add GEMINI_API_KEY and GROQ_API_KEY.")
    st.stop()

# --- 2. SIDEBAR: DATA LOADING ---
st.sidebar.header("📁 Data Management")
uploaded_file = st.sidebar.file_uploader("Upload Data (Excel/CSV)", type=['csv', 'xlsx'])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.xlsx'):
            xl = pd.ExcelFile(uploaded_file)
            selected_sheets = st.sidebar.multiselect("Select sheets", xl.sheet_names, default=xl.sheet_names)
            dfs = {s: pd.read_excel(uploaded_file, sheet_name=s) for s in selected_sheets}
        else:
            dfs = {"Data": pd.read_csv(uploaded_file)}
    except Exception as e:
        st.error(f"Failed to read file: {e}")
        st.stop()

    # --- 3. RELATIONAL JOIN LOGIC ---
    active_df = list(dfs.values())[0]
    if len(dfs) > 1:
        st.sidebar.subheader("🔗 Join Tables")
        left = st.sidebar.selectbox("Left Table", list(dfs.keys()))
        right = st.sidebar.selectbox("Right Table", list(dfs.keys()))
        common = list(set(dfs[left].columns) & set(dfs[right].columns))
        
        if common:
            key = st.sidebar.selectbox("Join Key", common)
            # Detect Cardinality
            l_u, r_u = dfs[left][key].is_unique, dfs[right][key].is_unique
            card = f"{'1' if l_u else 'M'}:{'1' if r_u else 'M'}"
            st.sidebar.info(f"Cardinality: {card}")
            
            if st.sidebar.button("Execute Join"):
                try:
                    active_df = pd.merge(dfs[left], dfs[right], on=key, how='inner')
                    st.success("Join successful!")
                except Exception as e:
                    st.error(f"Join error: {e}")

    # --- 4. STYLE & FILTER SETTINGS ---
    st.sidebar.divider()
    st.sidebar.header("🎨 Dashboard Controls")
    
    # User-defined filter columns
    filter_cols = st.sidebar.multiselect("Choose columns for Filters", active_df.columns.tolist())
    
    # Safe Color Palette Logic
    palette_choice = st.sidebar.selectbox("Dashboard Color Theme", ["Viridis", "Plasma", "Cividis", "Turbo"])
    
    # Conditional Formatting
    use_cond = st.sidebar.checkbox("Conditional Highlights")
    threshold = st.sidebar.number_input("Threshold Value", value=0) if use_cond else 0

    # --- 5. DATA FILTERING ---
    filtered_df = active_df.copy()
    if filter_cols:
        f_cols = st.columns(len(filter_cols))
        for i, col in enumerate(filter_cols):
            with f_cols[i]:
                vals = st.multiselect(f"Filter: {col}", options=active_df[col].unique(), default=active_df[col].unique())
                filtered_df = filtered_df[filtered_df[col].isin(vals)]

    # --- 6. VISUALIZATION OUTPUT ---
    st.write("### 🔍 Current Data View", filtered_df.head(5))
    mode = st.radio("Display Mode:", ["Automated Dashboard", "Custom Charts"])

    if filtered_df.empty:
        st.warning("Filters have removed all data. Adjust selections to see charts.")
    else:
        num_cols = filtered_df.select_dtypes('number').columns.tolist()
        cat_cols = filtered_df.select_dtypes('object').columns.tolist()

        if mode == "Automated Dashboard" and num_cols:
            r1c1, r1c2 = st.columns(2)
            r2c1, r2c2 = st.columns(2)

            with r1c1:
                # Distribution (Histogram)
                fig1 = px.histogram(filtered_df, x=num_cols[0], title=f"Dist: {num_cols[0]}", 
                                    color_discrete_sequence=[palette_choice.lower()])
                st.plotly_chart(fig1, use_container_width=True)

            with r1c2:
                # Composition (Pie)
                target = cat_cols[0] if cat_cols else num_cols[0]
                fig2 = px.pie(filtered_df, names=target, values=num_cols[0], title="Data Composition")
                st.plotly_chart(fig2, use_container_width=True)

            with r2c1:
                # Bar Chart with Conditional Styling
                if use_cond:
                    filtered_df['_color'] = filtered_df[num_cols[0]].apply(lambda x: 'High' if x > threshold else 'Low')
                    fig3 = px.bar(filtered_df, x=cat_cols[0] if cat_cols else num_cols[0], y=num_cols[0], 
                                  color='_color', color_discrete_map={'High': '#00CC96', 'Low': '#EF553B'})
                else:
                    fig3 = px.bar(filtered_df, x=cat_cols[0] if cat_cols else num_cols[0], y=num_cols[0],
                                  color_discrete_sequence=[palette_choice.lower()])
                st.plotly_chart(fig3, use_container_width=True)

            with r2c2:
                # Correlation (Scatter)
                if len(num_cols) > 1:
                    fig4 = px.scatter(filtered_df, x=num_cols[0], y=num_cols[1], color=num_cols[0], 
                                      color_continuous_scale=palette_choice)
                    st.plotly_chart(fig4, use_container_width=True)
                else:
                    st.info("Add more numeric columns for scatter analysis.")

        elif mode == "Custom Charts":
            c1, c2, c3 = st.columns(3)
            with c1: c_type = st.selectbox("Type", ["Bar", "Scatter", "Line"])
            with c2: x_ax = st.selectbox("X", filtered_df.columns)
            with c3: y_ax = st.selectbox("Y", num_cols)
            
            if c_type == "Bar": fig = px.bar(filtered_df, x=x_ax, y=y_ax, color_discrete_sequence=[palette_choice.lower()])
            elif c_type == "Scatter": fig = px.scatter(filtered_df, x=x_ax, y=y_ax, color=y_ax, color_continuous_scale=palette_choice)
            else: fig = px.line(filtered_df, x=x_ax, y=y_ax)
            st.plotly_chart(fig, use_container_width=True)

    # --- 7. AI CHAT ---
    st.divider()
    st.subheader("💬 AI Data Insights (Groq)")
    q = st.text_input("Ask about your data:")
    if q:
        with st.spinner("Analyzing..."):
            ctx = {n: d.head(30).to_dict('records') for n, d in dfs.items()}
            inst = f"Analyst Mode. Context: {ctx}. Respond clearly and perform calculations directly."
            try:
                res = groq_client.chat.completions.create(
                    messages=[{"role":"system","content":inst},{"role":"user","content":q}],
                    model="llama-3.3-70b-versatile"
                )
                st.info(f"🤖 **Insight:**\n\n{res.choices[0].message.content}")
            except Exception as e:
                st.error(f"AI could not process this request: {e}")
