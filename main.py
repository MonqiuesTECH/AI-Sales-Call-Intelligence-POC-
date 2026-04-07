import streamlit as st
import pandas as pd
from groq import Groq
import os

# --- INITIAL SETUP ---
st.set_page_config(page_title="Sales Intelligence POC", layout="wide")

# Initialize Groq Client
# Ensure GROQ_API_KEY is set in your Streamlit Secrets
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- MOCK CRM DATA ---
CRM_DATA = {
    "Users": ["Monique Bruce", "Team Member A"],
    "Clients": ["TechCorp Solutions", "Global Logistics Inc."]
}

# --- UI HEADER ---
st.title("📞 Sales Call Intelligence Dashboard")
st.subheader("Powered by Groq LPU™ Inference")

with st.sidebar:
    st.header("Session Settings")
    rep = st.selectbox("Select Sales Rep", CRM_DATA["Users"])
    client_name = st.selectbox("Select Client", CRM_DATA["Clients"])
    st.divider()
    st.success("Groq Engine: Active")

# --- STEP 1: UPLOAD ---
uploaded_file = st.file_uploader("Upload Sales Call Audio", type=["mp3", "wav", "m4a", "flac"])

if uploaded_file:
    st.audio(uploaded_file)
    
    if st.button("🚀 Run Analysis"):
        with st.spinner("Processing (Transcription + Analysis)..."):
            
            try:
                # --- STEP 2: TRANSCRIPTION (GROQ WHISPER) ---
                # We send the file directly to Groq's whisper implementation
                transcription = client.audio.transcriptions.create(
                    file=(uploaded_file.name, uploaded_file.read()),
                    model="whisper-large-v3",
                    response_format="text"
                )
                transcript_text = transcription
                
                # --- STEP 3: AI ANALYSIS (GROQ LLM) ---
                completion = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are a world-class sales coach. Analyze transcripts for Clarity, Confidence, and Objection Handling. Provide a score (1-10) for each and a brief summary of 'Areas for Improvement'."
                        },
                        {
                            "role": "user", 
                            "content": f"Transcript for {rep} calling {client_name}: {transcript_text}"
                        }
                    ],
                    temperature=0.2, # Lower temperature for more consistent scoring
                )
                
                analysis_output = completion.choices[0].message.content

                # --- STEP 4: DISPLAY DASHBOARD ---
                st.divider()
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("### 📝 Transcript")
                    st.info(transcript_text)
                    
                with col2:
                    st.markdown("### 📊 AI Performance Review")
                    st.markdown(analysis_output)
                    
                    # Optional: Add a simple metric row
                    st.columns(3)
                    # Note: For a real demo, you'd parse the scores out of the LLM response
                    # using regex or a structured JSON response.

            except Exception as e:
                st.error(f"An error occurred: {e}")
else:
    st.info("Upload a recording to begin. Groq will transcribe and score the call in seconds.")
