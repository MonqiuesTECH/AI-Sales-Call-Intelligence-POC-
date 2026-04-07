import streamlit as st
import pandas as pd
import json
from groq import Groq

# --- CONFIGURATION ---
st.set_page_config(page_title="AI CRM Intelligence POC", layout="wide", page_icon="📈")

# Initialize Groq
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("Missing GROQ_API_KEY in Streamlit secrets.")
    st.stop()

# --- MOCK DATABASE (SESSION STATE) ---
# This simulates your backend (Postgres/MongoDB) for the POC
if 'crm_deals' not in st.session_state:
    st.session_state.crm_deals = pd.DataFrame({
        'Deal_ID': ['D-101', 'D-102', 'D-103'],
        'Client': ['TechCorp', 'Global Logistics', 'Retail Giant'],
        'Rep': ['Monique Bruce', 'Alex Rivera', 'Monique Bruce'],
        'Stage': ['Discovery', 'Negotiation', 'Closed Won'],
        'Value': ['$50,000', '$120,000', '$15,000']
    })

if 'call_logs' not in st.session_state:
    st.session_state.call_logs = []

# --- AI PROCESSING LOGIC ---
def analyze_call_with_ai(transcript_text, rep_name):
    """Forces Groq to return strict JSON for the CRM database"""
    prompt = f"""
    Analyze the following sales call transcript for {rep_name}.
    You must evaluate the 4 core KPIs on a scale of 1-10.
    
    Transcript: {transcript_text}
    
    Output ONLY valid JSON with the exact following schema:
    {{
        "kpi_scores": {{
            "clarity": int,
            "confidence": int,
            "objection_handling": int,
            "closing": int
        }},
        "key_takeaways": ["point 1", "point 2"],
        "feedback": "Plain English constructive feedback",
        "adaptive_suggestion": "One specific training action based on the lowest score"
    }}
    """
    
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)

# --- VIEWS ---

def view_sales_rep():
    st.header("👤 Sales Representative Hub")
    st.markdown("Manage your deals and log new meeting intelligence.")
    
    # 1. CRM Table
    st.subheader("Active Deals")
    st.dataframe(st.session_state.crm_deals, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # 2. Call Logging (The AI Engine)
    st.subheader("🎙️ Log a Call (Zoom/Meet Sync Mock)")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        selected_deal = st.selectbox("Associate with Deal", st.session_state.crm_deals['Deal_ID'])
        uploaded_file = st.file_uploader("Upload Call Audio", type=["mp3", "wav", "m4a"])
    
    if uploaded_file and st.button("Transcribe & Analyze"):
        with st.spinner("Transcribing via Groq Whisper-v3..."):
            # Whisper Transcription
            transcription = client.audio.transcriptions.create(
                file=(uploaded_file.name, uploaded_file.read()),
                model="whisper-large-v3",
                response_format="text"
            )
            
        with st.spinner("Extracting KPIs via Llama 3..."):
            # AI Analysis
            analysis_data = analyze_call_with_ai(transcription, "Sales Rep")
            
            # Save to mock database
            st.session_state.call_logs.append({
                "Deal_ID": selected_deal,
                "Transcript": transcription,
                "Analysis": analysis_data
            })
            
        st.success("Call logged and analyzed successfully!")
        
        # Display Results to Rep
        st.subheader("🧠 Post-Call Intelligence")
        scores = analysis_data["kpi_scores"]
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Clarity", f"{scores['clarity']}/10")
        c2.metric("Confidence", f"{scores['confidence']}/10")
        c3.metric("Objection Handling", f"{scores['objection_handling']}/10")
        c4.metric("Closing", f"{scores['closing']}/10")
        
        st.info(f"**💡 Adaptive Coaching Suggestion:** {analysis_data['adaptive_suggestion']}")
        
        with st.expander("View Full Breakdown"):
            st.write("**Key Takeaways:**")
            for t in analysis_data['key_takeaways']:
                st.write(f"- {t}")
            st.write("**Detailed Feedback:**")
            st.write(analysis_data['feedback'])

def view_admin_dashboard():
    st.header("👑 Sales Manager Dashboard")
    st.markdown("Overview of team activity, KPI trends, and adaptive learning needs.")
    
    if not st.session_state.call_logs:
        st.warning("No call data available yet. Have a rep upload a call to populate the dashboard.")
        return
        
    # Aggregate Data
    all_scores = []
    for log in st.session_state.call_logs:
        all_scores.append(log['Analysis']['kpi_scores'])
    
    df_scores = pd.DataFrame(all_scores)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Team KPI Averages")
        avg_scores = df_scores.mean().reset_index()
        avg_scores.columns = ['KPI', 'Average Score']
        st.bar_chart(avg_scores, x='KPI', y='Average Score', color="#D4AF37") # A touch of gold
        
    with col2:
        st.subheader("Recent Coaching Needs")
        for idx, log in enumerate(st.session_state.call_logs):
            deal = log['Deal_ID']
            suggestion = log['Analysis']['adaptive_suggestion']
            st.error(f"**Deal {deal}:** {suggestion}")

# --- MAIN APP ROUTING ---
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Select View:", ["Sales Rep Hub", "Manager Dashboard"])

st.sidebar.divider()
st.sidebar.markdown("""
**POC Architecture:**
1. **Frontend:** Streamlit
2. **Database:** Session State (Mock)
3. **Transcription:** Groq Whisper-v3
4. **Intelligence:** Groq Llama 3 (JSON Mode)
""")

if app_mode == "Sales Rep Hub":
    view_sales_rep()
elif app_mode == "Manager Dashboard":
    view_admin_dashboard()
