import streamlit as st
import pandas as pd
from groq import Groq
from openai import OpenAI # Used specifically for Whisper transcription
import os

# --- INITIAL SETUP ---
st.set_page_config(page_title="Sales Intelligence POC", layout="wide")

# Initialize Clients (Pulling from Streamlit Secrets)
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
whisper_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- MOCK CRM DATA ---
CRM_DATA = {
    "Users": ["Monique Bruce", "Team Member A"],
    "Clients": ["TechCorp Solutions", "Global Logistics Inc.", "Retail Giant"]
}

# --- UI HEADER ---
st.title("📞 Sales Call Intelligence Dashboard")
st.subheader("High-Performance Transcription & AI Scoring")

with st.sidebar:
    st.header("Session Settings")
    rep = st.selectbox("Select Sales Rep", CRM_DATA["Users"])
    client_name = st.selectbox("Select Client", CRM_DATA["Clients"])
    st.divider()
    st.success("Connected to Groq LPU™")

# --- STEP 1: UPLOAD ---
uploaded_file = st.file_uploader("Upload Sales Call Audio", type=["mp3", "wav", "m4a"])

if uploaded_file:
    st.audio(uploaded_file)
    
    if st.button("🚀 Run Analysis"):
        with st.spinner("Processing with Groq Speed..."):
            
            # --- STEP 2: TRANSCRIPTION (WHISPER) ---
            # Standard Whisper API call
            transcript = whisper_client.audio.transcriptions.create(
                model="whisper-1", 
                file=uploaded_file
            )
            transcript_text = transcript.text
            
            # --- STEP 3: AI ANALYSIS (GROQ) ---
            # Using Llama 3 or Mixtral for blazing fast scoring
            completion = groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "You are a sales coaching expert. Analyze transcripts for Clarity, Confidence, and Objection Handling. Provide scores out of 10 and brief feedback."},
                    {"role": "user", "content": f"Analyze this transcript for {rep} calling {client_name}: {transcript_text}"}
                ],
                temperature=0.5,
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
                
                # Visual Chart
                chart_data = pd.DataFrame({
                    'Metric': ['Clarity', 'Confidence', 'Objections'],
                    'Score': [8, 7, 9] # In MVP, you can parse these from the AI response
                })
                st.bar_chart(chart_data, x='Metric', y='Score')
else:
    st.info("Upload a recording to see the AI scoring engine in action.")
