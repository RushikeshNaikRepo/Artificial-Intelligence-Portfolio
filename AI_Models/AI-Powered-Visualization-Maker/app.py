import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai
from groq import Groq

# --- 1. CONFIGURATION & HYBRID AI SETUP ---
st.set_page_config(page_title="AI Powered Visualization Maker", layout="wide")
st.title("📊 AI Powered Visualization Maker")
st.markdown("---")

# Secure API Connections
try:
    # Gemini handles the structural/logic tasks
    google_client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    # Groq handles the high-speed data chatting
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("⚠️ API Keys Missing! Please check Streamlit Secrets for GEMINI_API_KEY and GROQ_API_KEY.")
    st.stop()

# --- 2. SIDEBAR: DATA INGESTION ---
st.sidebar.header("📁 Step 1: Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload Excel or CSV", type=['csv', 'xlsx'])

if uploaded_file:
    # Handle Multi-sheet Excel
    if uploaded_file.name.endswith('.xlsx'):
        xl = pd.ExcelFile(uploaded_file)
        all_sheets = xl.sheet_names
        selected_sheets = st.sidebar.multiselect("Select sheets to load", all_sheets, default=all_sheets)
        dfs = {s: pd.read_excel(uploaded_file, sheet_name=s) for s in selected_sheets}
    else:
        dfs = {"Data": pd.read_csv(uploaded_file)}

    # --- 3. JOIN & CARDINALITY LOGIC ---
    active_df = list(dfs.values())[0]
    
    if len(dfs) > 1:
        st.sidebar.subheader("🔗 Step 2: Relationships")
        left_tab = st.sidebar.selectbox("Left Table", list(dfs.keys()))
        right_tab = st.sidebar.selectbox("Right Table", list(dfs.keys()))
        common_cols = list(set(dfs[left_tab].columns) & set(dfs[right_tab].columns))
        
        if common_cols:
            join_col = st.sidebar.selectbox("Join Key", common_cols)
            # Cardinality Logic
            left_u = dfs[left_tab][join_col].is_unique
            right_u = dfs[right_tab][join_col].is_unique
            card = f"{'1' if left_u else 'M'}:{'1' if right_u else 'M'}"
            st.sidebar.info(f"Detected Cardinality: {card}")
            
            if st.sidebar.button("Execute Join"):
                active_df = pd.merge(dfs[left_tab], dfs[right_tab], on=join_col, how='inner')
                st.success(f"Joined on {join_col}")

    # --- 4. OUTPUT MODES ---
    st.write("### 🔍 Data Preview", active_df.head(5))
    view_option = st.radio("Choose Output Mode:", ["Dashboard", "Individual Visualizations"])

    if view_option == "Dashboard":
        st.subheader("🚀 Strategic Automated Dashboard")
        
        # Dashboard Filters
        filter_cols = [c for c in active_df.columns if active_df[c].nunique() <= 10]
        filtered_df = active_df.copy()
        
        if filter_cols:
            f_cols = st.columns(len(filter_cols[:3]))
            for i, col in enumerate(filter_cols[:3]):
                with f_cols[i]:
                    selection = st.multiselect(f"Filter {col}", options=active_df[col].unique(), default=active_df[col].unique())
                    filtered_df = filtered_df[filtered_df[col].isin(selection)]
        
        st.divider()

        # 4-Visual Grid
        num_cols = filtered_df.select_dtypes(include='number').columns.tolist()
        cat_cols = filtered_df.select_dtypes(include='object').columns.tolist()

        if num_cols:
            r1c1, r1c2 = st.columns(2)
            r2c1, r2c2 = st.columns(2)
            with r1c1: st.plotly_chart(px.histogram(filtered_df, x=num_cols[0], title="Distribution"), use_container_width=True)
            with r1c2: st.plotly_chart(px.pie(filtered_df, names=cat_cols[0] if cat_cols else num_cols[0], values=num_cols[0], title="Composition"), use_container_width=True)
            with r2c1: st.plotly_chart(px.bar(filtered_df, x=cat_cols[0] if cat_cols else num_cols[0], y=num_cols[-1], title="Comparison"), use_container_width=True)
            with r2c2: st.plotly_chart(px.scatter(filtered_df, x=num_cols[0], y=num_cols[-1], title="Correlation") if len(num_cols)>1 else px.box(filtered_df, y=num_cols[0]), use_container_width=True)
    
    else:
        st.subheader("🎨 Custom Visualization Menu")
        c1, c2, c3 = st.columns(3)
        with c1: v_type = st.selectbox("Chart Type", ["Bar", "Pie", "Line", "Scatter"])
        with c2: x_ax = st.selectbox("X-Axis", active_df.columns)
        with c3: y_ax = st.selectbox("Y-Axis", active_df.select_dtypes('number').columns)
        
        fig = px.bar(active_df, x=x_ax, y=y_ax) if v_type=="Bar" else px.pie(active_df, names=x_ax, values=y_ax)
        st.plotly_chart(fig, use_container_width=True)

    # --- 5. CHAT WINDOW (IMPROVED ANALYTICAL PROMPT) ---
    st.divider()
    st.subheader("💬 AI Chat Assistant (Groq)")
    query = st.text_input("Ask about your data (e.g., 'Which Order_IDs are in the Electronics category?'):")

    if query:
        with st.spinner("Analyzing data rows..."):
            # Create a data dictionary to pass to the AI
            # We send the head of each sheet as a dictionary so the AI can 'see' the actual values
            data_context = {name: df.to_dict(orient='records') for name, df in dfs.items()}
            
            system_instruction = f"""
            You are a Precise Data Analyst. 
            CONTEXT: You have access to the following data rows: {data_context}
            
            RULES:
            1. Do NOT explain HOW to solve it or provide SQL code. 
            2. PERFORM the analysis and give the FINAL answer based ONLY on the data provided.
            3. If asked for a list (like Order IDs), list them clearly.
            4. If the data is missing, say exactly what is missing.
            """
            
            try:
                chat_response = groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": query},
                    ],
                    model="llama-3.3-70b-versatile",
                )
                st.info(f"🤖 **Groq Analysis:**\n\n{chat_response.choices[0].message.content}")
            except Exception as e:
                st.error(f"Chat Error: {str(e)}")
