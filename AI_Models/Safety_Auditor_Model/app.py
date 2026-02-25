import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re

# --- 1. CONFIGURATION ---
# Use the key you found earlier
# This tells the website to look for the key in the "Secrets" settings we will set later
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)

# UPDATED FOR 2026: 'gemini-3-flash-preview' is the current stable free-tier model
MODEL_NAME = 'gemini-3-flash-preview'
model = genai.GenerativeModel(MODEL_NAME)

st.set_page_config(page_title="SafetySense AI", page_icon="🛡️")
st.title("🛡️ SafetySense AI Auditor")
st.caption("Powered by Gemini 3 Flash")

# --- 2. UPLOAD SECTION ---
uploaded_file = st.file_uploader("Upload site photo...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption='Workspace for Audit', use_container_width=True)
    
    if st.button("Generate Audit Report"):
        with st.spinner('Gemini 3 is auditing...'):
            try:
                # We ask for a "Reasoning-First" audit
                prompt = """
                Perform a professional industrial safety audit. 
                Check for PPE (Helmets, Vests), Trip Hazards, and Unsafe Behavior.
                Return ONLY a JSON object. No markdown, no extra text.
                Example: {"status": "Violation", "score": 3, "finding": "Worker missing helmet."}
                """
                
                # Using the latest generation method
                response = model.generate_content([prompt, img])
                
                # Cleanup: Just in case the AI adds ```json ... ```
                clean_text = re.search(r'\{.*\}', response.text, re.DOTALL)
                
                if clean_json := clean_text:
                    result = json.loads(clean_json.group())
                    
                    # --- 3. DISPLAY RESULTS ---
                    st.divider()
                    st.subheader("Audit Results")
                    
                    if result['status'] == "Safe":
                        st.success(f"✅ STATUS: {result['status']}")
                    else:
                        st.error(f"⚠️ STATUS: {result['status']}")
                        
                    st.metric("Safety Compliance Score", f"{result['score']}/10")
                    st.info(f"**Inspector's Finding:** {result['finding']}")
                else:
                    st.warning("Audit generated but format was unexpected. See below:")
                    st.write(response.text)

            except Exception as e:
                # If 404 happens again, we list the models for you automatically
                st.error(f"Error: {e}")
                if "404" in str(e):
                    st.info("Searching for an available model on your account...")
                    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    st.write("Try replacing the MODEL_NAME in your code with one of these:")
                    st.code(available_models)