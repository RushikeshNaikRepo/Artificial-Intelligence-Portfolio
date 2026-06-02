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
    st.markdown("### 🛠️ Developer Profile")
    st.write("**Name:** Rushikesh Naik")
    st.write("**Role:** Data Analyst / AI Developer")
    st.divider()
    st.info("Engineered using structured computer vision architectures to process high-reliability site safety diagnostics.")

# --- 5. MAIN DASHBOARD UI ---
st.title("🛡️ SafetySense AI Auditor")
st.markdown("<p style='color:#94A3B8; font-size:1.1rem;'>Enterprise Site Compliance & HSE Dashboard</p>", unsafe_with_html=True)
st.markdown("---")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 📷 Live Feed Capture / Upload")
    uploaded_file = st.file_uploader("Drop worksite imagery here...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        
        # Performance boost optimization
        if img.size[0] > 1920:
            img.thumbnail((1920, 1920))
            
        st.image(img, caption='Optimized Worksite Scan Target', use_container_width=True)

with col2:
    st.markdown("### 📝 Active Audit Output")
    
    if uploaded_file:
        if st.button("🚀 Execute Safety Scan", use_container_width=True):
            with st.spinner('AI Analytics core parsing site visual signatures...'):
                try:
                    prompt = """
                    Perform a rigorous health, safety, and environment (HSE) audit on this work zone.
                    Inspect closely for the presence or visual absence of hard hats (helmets), high-visibility vests, protective gloves, and footwear.
                    Identify any open structural risks, trip hazards, or compliance variations.
                    """
                    
                    response = model.generate_content(
                        [prompt, img],
                        generation_config=genai.GenerationConfig(
                            response_mime_type="application/json",
                            response_schema=SafetyAuditReport
                        )
                    )
                    
                    import json
                    result = json.loads(response.text)
                    
                    st.markdown("#### Operational Assessment")
                    
                    if result['status'].lower() == "safe":
                        st.markdown(f"""
                            <div style="background-color: #064E3B; padding: 15px; border-radius: 8px; border-left: 6px solid #10B981; margin-bottom: 15px;">
                                <strong style="color: #A7F3D0;">✅ SITE STATUS: COMPLIANT</strong>
                            </div>
                        """, unsafe_with_html=True)
                    else:
                        st.markdown(f"""
                            <div style="background-color: #7F1D1D; padding: 15px; border-radius: 8px; border-left: 6px solid #EF4444; margin-bottom: 15px;">
                                <strong style="color: #FCA5A5;">⚠️ SITE STATUS: HSE VIOLATION DETECTED</strong>
                            </div>
                        """, unsafe_with_html=True)
                    
                    st.metric(label="Calculated Compliance Index", value=f"{result['score']} / 10")
                    
                    st.markdown("#### System Diagnostics Summary")
                    st.info(result['finding'])
                    
                    st.divider()
                    report_text = f"""ENTERPRISE HSE AUDIT SCAN REPORT
====================================
Facility Assessment: {result['status'].upper()}
Compliance Index Score: {result['score']}/10
Log Timestamp: 2026-06-02
------------------------------------
Audit Inspection Diagnostics:
{result['finding']}
====================================
System Framework: SafetySense AI
Chief Architect: Rushikesh Naik (Data Analyst / AI Developer)
"""
                    st.download_button(
                        label="📥 Export Off-line Audit Manifest",
                        data=report_text,
                        file_name=f"HSE_Manifest_{result['status']}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"Execution Error during matrix compile: {e}")
    else:
        st.info("Awaiting visual media uplink. Please drag or upload a site asset into Column 1 to initialize.")
