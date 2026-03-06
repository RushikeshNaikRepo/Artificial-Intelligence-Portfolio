import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai

# --- 1. CONFIGURATION & AI SETUP ---
st.set_page_config(page_title="AI Powered Visualization Maker", layout="wide")

# Theme / Title
st.title("📊 AI Powered Visualization Maker")
st.markdown("---")

# Secure API Connection
try:
    # We use 1.5-flash as the primary to avoid the 'Resource Exhausted' quota errors
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
    PRIMARY_MODEL = "gemini-1.5-flash" 
except Exception as e:
    st.error("⚠️ API Key Error: Please check your Streamlit Secrets for 'GEMINI_API_KEY'")
    st.stop()

# --- 2. SIDEBAR: DATA INGESTION ---
st.sidebar.header("📁 Step 1: Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload Excel or CSV", type=['csv', 'xlsx'])

if uploaded_file:
    # Multi-sheet logic
    if uploaded_file.name.endswith('.xlsx'):
        xl = pd.ExcelFile(uploaded_file)
        all_sheets = xl.sheet_names
        selected_sheets = st.sidebar.multiselect("Select sheets to include", all_sheets, default=all_sheets[0])
        dfs = {s: pd.read_excel(uploaded_file, sheet_name=s) for s in selected_sheets}
    else:
        dfs = {"CSV_Data": pd.read_csv(uploaded_file)}

    # --- 3. JOIN & CARDINALITY LOGIC ---
    active_df = list(dfs.values())[0]
    
    if len(dfs) > 1:
        st.sidebar.subheader("🔗 Step 2: Relationships")
        left_tab = st.sidebar.selectbox("Left Table", list(dfs.keys()))
        right_tab = st.sidebar.selectbox("Right Table", list(dfs.keys()))
        
        common_cols = list(set(dfs[left_tab].columns) & set(dfs[right_tab].columns))
        
        if common_cols:
            join_col = st.sidebar.selectbox("Join Key", common_cols)
            
            # Check Cardinality (Technically sound logic)
            left_u = dfs[left_tab][join_col].is_unique
            right_u = dfs[right_tab][join_col].is_unique
            card = f"{'1' if left_u else 'M'}:{'1' if right_u else 'M'}"
            st.sidebar.info(f"Detected Cardinality: {card}")
            
            if st.sidebar.button("Join Sheets"):
                active_df = pd.merge(dfs[left_tab], dfs[right_tab], on=join_col, how='inner')
                st.success(f"Successfully joined on {join_col}")
        else:
            st.sidebar.warning("No common columns found for join.")

    # --- 4. DASHBOARD VS VISUALIZATIONS ---
    st.write("### 🔍 Data Preview", active_df.head(5))
    
    view_option = st.radio("Choose Output Mode:", ["Dashboard", "Individual Visualizations"])

    # GLOBAL FILTER LOGIC (For Dashboard)
    # Filter only columns with few unique values (for clean UI)
    filter_cols = [c for c in active_df.columns if active_df[c].nunique() <= 10]
    filtered_df = active_df.copy()

    if view_option == "Dashboard":
        st.subheader("🚀 Strategic Automated Dashboard")
        
        # Dashboard Filters
        if filter_cols:
            st.write("#### 🛠️ Filters")
            f_cols = st.columns(len(filter_cols[:3]))
            for i, col in enumerate(filter_cols[:3]):
                with f_cols[i]:
                    selection = st.multiselect(f"Filter {col}", options=active_df[col].unique(), default=active_df[col].unique())
                    filtered_df = filtered_df[filtered_df[col].isin(selection)]
        
        st.divider()

        # 4-Visual Grid
        num_cols = filtered_df.select_dtypes(include='number').columns.tolist()
        cat_cols = filtered_df.select_dtypes(include='object').columns.tolist()

        if len(num_cols) >= 1:
            r1c1, r1c2 = st.columns(2)
            r2c1, r2c2 = st.columns(2)

            with r1c1:
                st.plotly_chart(px.histogram(filtered_df, x=num_cols[0], title=f"Distribution of {num_cols[0]}"), use_container_width=True)
            
            with r1c2:
                cat_target = cat_cols[0] if cat_cols else num_cols[0]
                st.plotly_chart(px.pie(filtered_df, names=cat_target, values=num_cols[0], title=f"Composition of {num_cols[0]}"), use_container_width=True)

            with r2c1:
                st.plotly_chart(px.bar(filtered_df, x=cat_cols[0] if cat_cols else num_cols[0], y=num_cols[-1], title="Comparison Analysis", color_discrete_sequence=['#00CC96']), use_container_width=True)

            with r2c2:
                if len(num_cols) > 1:
                    st.plotly_chart(px.scatter(filtered_df, x=num_cols[0], y=num_cols[1], title="Correlation View"), use_container_width=True)
                else:
                    st.plotly_chart(px.box(filtered_df, y=num_cols[0], title="Statistical Spread"), use_container_width=True)
        else:
            st.warning("Please upload numeric data for the dashboard.")

    else:
        # Individual Visualizations Menu
        st.subheader("🎨 Custom Visualizations")
        menu_col1, menu_col2, menu_col3 = st.columns(3)
        with menu_col1: v_type = st.selectbox("Chart Type", ["Bar", "Pie", "Line", "Area", "Scatter"])
        with menu_col2: x_val = st.selectbox("X-Axis", active_df.columns)
        with menu_col3: y_val = st.selectbox("Y-Axis", active_df.select_dtypes('number').columns)

        if v_type == "Bar": fig = px.bar(active_df, x=x_val, y=y_val)
        elif v_type == "Pie": fig = px.pie(active_df, names=x_val, values=y_val)
        elif v_type == "Line": fig = px.line(active_df, x=x_val, y=y_val)
        elif v_type == "Area": fig = px.area(active_df, x=x_val, y=y_val)
        else: fig = px.scatter(active_df, x=x_val, y=y_val)
        st.plotly_chart(fig, use_container_width=True)

    # --- 5. NLQ CHAT (WITH FALLBACK) ---
    st.divider()
    st.subheader("💬 AI Analyst Chat")
    query = st.text_input("Ask about your data:")
    
    if query:
        with st.spinner("Analyzing..."):
            try:
                prompt = f"Data schema: {active_df.columns.tolist()}. Question: {query}. Provide a concise analytical insight."
                response = client.models.generate_content(model=PRIMARY_MODEL, contents=prompt)
                st.info(f"🤖 **AI Insight:**\n\n{response.text}")
            except Exception as e:
                st.error("The AI is currently busy (Quota limit). Please wait 30 seconds and try again.")
