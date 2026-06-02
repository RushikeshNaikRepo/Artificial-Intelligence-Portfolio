import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
from pydantic import BaseModel, Field

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SafetySense AI Auditor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CUSTOM ENTERPRISE UI/UX CSS ---
# Kept strictly flushed to the left margin to avoid multi-line string indentation crashes
st.markdown(
    """
<style>
/* Main App Background and Fonts */
.stApp {
    background-color: #0F1216 !important;
    color: #E2E8F0 !important;
}

/* Headers styling */
h1, h2, h3 {
    color: #F1F5F9 !important;
    font-family: 'Inter', sans-serif;
    font-weight: 700;
}

/* Custom metric card wrapper */
.metric-card {
    background-color: #1E2530;
    padding: 20px;
    border-radius: 10px;
    border-left: 5px solid #3B82F6;
    margin-bottom: 15px;
}

/* Sidebar styling adjustment */
[data-testid="stSidebar"] {
    background-color: #151B23 !important;
    border-right: 1px solid #212B36;
}

/* Divider color matching */
hr {
    border-color: #2D3748 !important;
}
</style>
""", 
    unsafe_with_html=True
)

# --- 3. API INITIALIZATION & STRUCTURED OUTPUT SCHEMA ---
class SafetyAuditReport(BaseModel):
    status: str = Field(description="Must be exactly either 'Safe' or 'Violation'")
    score: int = Field(description="Compliance rating score from 1 to 10")
    finding: str = Field(description="Highly detailed technical description of PPE elements or hazards found")

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_LOCAL_FALLBACK_KEY")

if API_KEY and API_KEY != "YOUR_LOCAL_FALLBACK_KEY":
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-3-flash-preview')
else:
    st.error("⚠️ Gemini API Key not found. Please configure it in st.secrets or environment variables.")

# --- 4. SIDEBAR DEVELOPER PROFILE ---
with st.sidebar:
    st.markdown("## 🛡️ Control Panel")
    st.markdown("---")
    st.markdown("### 🛠️
