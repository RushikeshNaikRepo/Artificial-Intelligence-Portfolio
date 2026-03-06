import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai
from groq import Groq

# --- 1. CONFIGURATION & HYBRID AI SETUP ---
st.set_page_config(page_title="AI Powered Visualization Maker", layout="wide")
st.title("📊 AI Powered Visualization Maker (Pro Edition)")
st.markdown("---")

# Secure API Connections
try:
    google_client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("⚠️ API Keys Missing! Please check Streamlit Secrets for GEMINI_API_KEY and GROQ_API_KEY.")
    st.stop()

# --- 2. SIDEBAR: DATA INGESTION ---
st.sidebar.header("📁 Step 1: Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload Excel or CSV", type=['csv', 'xlsx'])

if uploaded_file:
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
            left_u = dfs[left_tab][join_col].is_unique
            right_u = dfs[right_tab][join_col].is_unique
            card = f"{'1' if left_u else 'M'}:{'1' if right_u else 'M'}"
            st.sidebar.info(f"Detected Cardinality: {card}")
            
            if st.sidebar.button("Execute Join"):
                active_df = pd.merge(dfs[left_tab], dfs[right_tab], on=join_col, how='inner')
                st.success(f"Joined on {join_col}")

    # --- 4. ADVANCED VISUALIZATION SETTINGS ---
    st.sidebar.divider()
    st.sidebar.header("🎨 Visual Styling & Filters")
    
    available_cols = active_df.columns.tolist()
    chosen_filter_cols = st.sidebar.multiselect("Select Columns for Filters", options=available_cols)
    
    # User selects a professional scale
    color_palette = st.sidebar.selectbox("Color Palette", ["Viridis", "Plasma", "Cividis", "Magma", "Turbo", "Bluered"])
    
    use_cond_format = st.sidebar.checkbox("Enable Conditional Formatting")
    highlight_val = 0
    if use_cond_format:
        highlight_val = st.sidebar.number_input("Highlight values greater than:", value=0)

    # --- 5. DATA OUTPUT & FILTERING ---
    st.write("### 🔍 Data Preview", active_df.head(5))
    view_option = st.radio("Choose Output Mode:", ["Dashboard", "Individual Visualizations"])

    filtered_df = active_df.copy()
    if chosen_filter_cols:
        st.write("#### 🛠️ Active Filters")
        f_ui_cols = st.columns(len(chosen_filter_cols))
        for i, col in enumerate(chosen_filter_cols):
            with f_ui_cols[i]:
                selection = st.multiselect(f"{col}", options=active_df[col].unique(), default=active_df[col].unique())
                filtered_df = filtered_df[filtered_df[col].isin(selection)]

    if view_option == "Dashboard":
        st.subheader("🚀 Strategic Automated Dashboard")
        num_cols = filtered_df.select_dtypes(include='number').columns.tolist()
        cat_cols = filtered_df.select_dtypes(include='object').columns.tolist()

        if num_cols:
            r1c1, r1c2 = st.columns(2)
            r2c1, r2c2 = st.columns(2)
            
            with r1c1:
                # Distribution Chart: Fixed the color scale logic
                fig1 = px.histogram(filtered_df, x=num_cols[0], title=f"Distribution: {num_cols[0]}", 
                                    color_discrete_sequence=[color_palette.lower()])
                st.plotly_chart(fig1, use_container_width=True)
            
            with r1c2:
                # Composition Chart: Qualitative colors for categorical data
                fig2 = px.pie(filtered_df, names=cat_cols[0] if cat_cols else num_cols[0], values=num_cols[0], 
                              title="Composition Analysis", color_discrete_sequence=px.colors.qualitative.Safe)
                st.plotly_chart(fig2, use_container_width=True)

            with r2c1:
                # Conditional Formatting logic
                if use_cond_format:
                    filtered_df['Status'] = filtered_df[num_cols[0]].apply(lambda x: 'Above Threshold' if x > highlight_val else 'Below Threshold')
                    fig3 = px.bar(filtered_df, x=cat_cols[0] if cat_cols else num_cols[0], y=num_cols[0], 
                                  color='Status', color_discrete_map={'Above Threshold': 'green', 'Below Threshold': 'red'},
                                  title="Comparison (Conditional)")
                else:
                    fig3 = px.bar(filtered_df, x=cat_cols[0] if cat_cols else num_cols[0], y=num_cols[-1], 
                                  title="Standard Comparison", color_discrete_sequence=[color_palette.lower()])
                st.plotly_chart(fig3, use_container_width=True)

            with r2c2:
                # Correlation Analysis: Uses continuous scales correctly
                fig4 = px.scatter(filtered_df, x=num_cols[0], y=num_cols[-1], color=num_cols[0], 
                                  color_continuous_scale=color_palette, title="Correlation Analysis")
                st.plotly_chart(fig4, use_container_width=True)
        else:
            st.warning("Please ensure your dataset contains numeric columns.")

    else:
        # Individual Visualizations Menu
        st.subheader("🎨 Custom Visualization Menu")
        m1, m2, m3 = st.columns(3)
        with m1: v_type = st.selectbox("Chart Type", ["Bar", "Pie", "Line", "Scatter"])
        with m2: x_ax = st.selectbox("X-Axis", filtered_df.columns)
        with m3: y_ax = st.selectbox("Y-Axis", filtered_df.select_dtypes('number').columns)
        
        if v_type == "Bar": fig = px.bar(filtered_df, x=x_ax, y=y_ax, color_discrete_sequence=[color_palette.lower()])
        elif v_type == "Pie": fig = px.pie(filtered_df, names=x_ax, values=y_ax)
        elif v_type == "Line": fig = px.line(filtered_df, x=x_ax, y=y_ax)
        else: fig = px.scatter(filtered_df, x=x_ax, y=y_ax, color=y_ax, color_continuous_scale=color_palette)
        st.plotly_chart(fig, use_container_width=True)

    # --- 6. CHAT WINDOW ---
    st.divider()
    st.subheader("💬 AI Chat Assistant (Groq)")
    query = st.text_input("Ask about your data:")

    if query:
        with st.spinner("Analyzing rows..."):
            data_context = {name: df.head(50).to_dict(orient='records') for name, df in dfs.items()}
            system_instruction = f"You are a Precise Data Analyst. CONTEXT: {data_context}. Provide only final answers."
            try:
                chat_response = groq_client.chat.completions.create(
                    messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": query}],
                    model="llama-3.3-70b-versatile",
                )
                st.info(f"🤖 **Groq Analysis:**\n\n{chat_response.choices[0].message.content}")
            except Exception as e:
                st.error(f"Chat Error: {str(e)}")
