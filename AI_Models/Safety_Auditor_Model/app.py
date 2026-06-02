import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
from pydantic import BaseModel, Field
import json

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SafetySense AI Auditor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. API INITIALIZATION & STRUCTURED OUTPUT SCHEMA ---
class SafetyAuditReport(BaseModel):
    status: str = Field(description="Must be exactly either 'Safe' or 'Violation'")
    score: int = Field(description="Compliance rating score from 1 to 10")
    finding: str = Field(description="Highly detailed technical description of PPE elements or hazards found")

# Robust API Key retrieval
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_LOCAL_FALLBACK_KEY")

if API_KEY and API_KEY != "YOUR_LOCAL_FALLBACK_KEY":
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-3-flash-preview')
else:
    st.error("⚠️ Gemini API Key not found. Please configure it in st.secrets or environment variables.")

# --- 3. SIDEBAR DEVELOPER PROFILE (NATIVE VIEW) ---
with st.sidebar:
    st.title("🛡️ Control Panel")
    st.divider()
    st.subheader("🛠️ Developer Profile")
    st.write("**Name:** Rushikesh Naik")
    st.write("**Role:** Data Analyst / AI Developer")
    st.divider()
    st.info("Engineered using structured computer vision architectures to process high-reliability site safety diagnostics.")

# --- 4. MAIN DASHBOARD UI ---
st.title("🛡️ SafetySense AI Auditor")
st.caption("Enterprise Site Compliance & HSE Dashboard")
st.divider()

# Create clean side-by-side dashboard layout
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.header("📷 Live Feed / Upload")
    uploaded_file = st.file_uploader("Drop worksite imagery here...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        
        # Optimize image dimension boundaries for processing efficiency
        if img.size[0] > 1920:
            img.thumbnail((1920, 1920))
            
        st.image(img, caption='Optimized Worksite Scan Target', use_container_width=True)

with col2:
    st.header("📝 Active Audit Output")
    
    if uploaded_file:
        # Action button spanning the container width
        if st.button("🚀 Execute Safety Scan", use_container_width=True):
            with st.spinner('AI Analytics core parsing site visual signatures...'):
                try:
                    prompt = """
                    Perform a rigorous health, safety, and environment (HSE) audit on this work zone.
                    Inspect closely for the presence or visual absence of hard hats (helmets), high-visibility vests, protective gloves, and footwear.
                    Identify any open structural risks, trip hazards, or compliance variations.
                    """
                    
                    # Direct structured API call
                    response = model.generate_content(
                        [prompt, img],
                        generation_config=genai.GenerationConfig(
                            response_mime_type="application/json",
                            response_schema=SafetyAuditReport
                        )
                    )
                    
                    # Safe dictionary parsing
                    result = json.loads(response.text)
                    
                    st.subheader("Operational Assessment")
                    
                    # Using Streamlit's native container alerts instead of HTML
                    if result['status'].lower() == "safe":
                        st.success("### ✅ SITE STATUS: COMPLIANT")
                    else:
                        st.error("### ⚠️ SITE STATUS: HSE VIOLATION DETECTED")
                    
                    # Native high-visibility metric component
                    st.metric(label="Calculated Compliance Index", value=f"{result['score']} / 10")
                    
                    st.subheader("System Diagnostics Summary")
                    st.info(result['finding'])
                    
                    # --- AUTO GENERATED DOWNLOAD TEXT REPORT ---
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
                    st.error(f"Execution Error during analysis parsing: {e}")
    else:
        st.info("Awaiting visual media uplink. Please upload a site asset into Column 1 to initialize.")
