import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai

# --- 1. SETTINGS & AI CONFIG ---
st.set_page_config(page_title="AI Powered Visualization Maker", layout="wide")
st.title("📊 AI Powered Visualization Maker")

# Securely load the API Key from Streamlit Secrets
try:
    # Use gemini-2.0-flash for the best balance of speed and stability
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
    MODEL_NAME = "gemini-2.0-flash" 
except Exception as e:
    st.error("⚠️ API Key missing! Add 'GEMINI_API_KEY' to Streamlit Secrets.")
    st.stop()

# --- 2. FILE UPLOADER ---
st.sidebar.header("📁 Data Ingestion")
uploaded_file = st.sidebar.file_uploader("Upload Excel or CSV", type=['csv', 'xlsx'])

if uploaded_file:
    # Handle Multi-sheet Excel
    if uploaded_file.name.endswith('.xlsx'):
        xl = pd.ExcelFile(uploaded_file)
        all_sheets = xl.sheet_names
        selected_sheets = st.sidebar.multiselect("Select sheets to load", all_sheets, default=all_sheets[0])
        dfs = {s: pd.read_excel(uploaded_file, sheet_name=s) for s in selected_sheets}
    else:
        dfs = {"Data": pd.read_csv(uploaded_file)}

    # --- 3. JOIN & CARDINALITY LOGIC ---
    active_df = list(dfs.values())[0]
    
    if len(dfs) > 1:
        st.sidebar.subheader("🔗 Data Relationships")
        left_tab = st.sidebar.selectbox("Left Sheet", list(dfs.keys()))
        right_tab = st.sidebar.selectbox("Right Sheet", list(dfs.keys()))
        
        common_cols = list(set(dfs[left_tab].columns) & set(dfs[right_tab].columns))
        
        if common_cols:
            join_col = st.sidebar.selectbox("Join Key (Column)", common_cols)
            
            # Calculate Cardinality
            left_unique = dfs[left_tab][join_col].is_unique
            right_unique = dfs[right_tab][join_col].is_unique
            card_label = f"{'1' if left_unique else 'M'}:{'1' if right_unique else 'M'}"
            st.sidebar.info(f"Detected Cardinality: {card_label}")
            
            if st.sidebar.button("Execute Join"):
                active_df = pd.merge(dfs[left_tab], dfs[right_tab], on=join_col, how='inner')
                st.success(f"Successfully joined on {join_col}")
        else:
            st.sidebar.warning("No common columns found to join.")

    # --- 4. VISUALIZATION CONTROLS ---
    st.write("### 🔍 Data Preview", active_df.head(5))
    
    view_option = st.radio("Choose Output Type:", ["Visualizations Menu", "Automated Dashboard"])

    if view_option == "Visualizations Menu":
        st.subheader("🎨 Custom Visualization")
        c1, c2, c3 = st.columns(3)
        with c1: chart_type = st.selectbox("Chart Type", ["Bar", "Pie", "Line", "Area", "Scatter"])
        with c2: x_axis = st.selectbox("X-Axis", active_df.columns)
        with c3: y_axis = st.selectbox("Y-Axis", active_df.select_dtypes(include='number').columns)

        if chart_type == "Bar": fig = px.bar(active_df, x=x_axis, y=y_axis)
        elif chart_type == "Pie": fig = px.pie(active_df, names=x_axis, values=y_axis)
        elif chart_type == "Line": fig = px.line(active_df, x=x_axis, y=y_axis)
        elif chart_type == "Area": fig = px.area(active_df, x=x_axis, y=y_axis)
        else: fig = px.scatter(active_df, x=x_axis, y=y_axis)
        
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.subheader("🚀 Automated Dashboard")
        num_cols = active_df.select_dtypes(include='number').columns
        if len(num_cols) >= 2:
            col_a, col_b = st.columns(2)
            with col_a: st.plotly_chart(px.histogram(active_df, x=num_cols[0], title="Data Distribution"))
            with col_b: st.plotly_chart(px.box(active_df, y=num_cols[1], title="Outlier Detection"))
        else:
            st.warning("Not enough numeric data for an automated dashboard.")

    # --- 5. NLQ CHAT WINDOW ---
    st.divider()
    st.subheader("💬 AI Data Assistant")
    user_query = st.text_input("Ask a question about your data (e.g., 'Which region has highest sales?')")

    if user_query:
        with st.spinner("Gemini is thinking..."):
            try:
                # Prepare context for the AI
                prompt = f"""
                Dataset Columns: {active_df.columns.tolist()}
                Data Sample: {active_df.head(3).to_dict()}
                User Question: {user_query}
                
                Instructions: Answer the question based on the provided columns. 
                Suggest which chart would best represent this answer.
                """
                
                response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
                st.info(f"🤖 **AI Analysis:**\n\n{response.text}")
                
            except Exception as e:
                st.error(f"AI Error: {str(e)}")
                st.info("Try checking your API limits or model availability in AI Studio.")
