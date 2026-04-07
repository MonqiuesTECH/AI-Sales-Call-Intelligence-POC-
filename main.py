import streamlit as st
import pandas as pd
import json
from groq import Groq

# --- CONFIGURATION ---
st.set_page_config(page_title="AI CRM Intelligence", layout="wide", page_icon="📈")

# Initialize Groq
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("Missing GROQ_API_KEY in Streamlit secrets.")
    st.stop()

# --- MOCK DATABASE (SESSION STATE) ---
def init_db():
    st.session_state.crm_deals = pd.DataFrame({
        'Deal_ID': ['D-101', 'D-102', 'D-103'],
        'Client': ['TechCorp', 'Global Logistics', 'Retail Giant'],
        'Rep': ['Monique Bruce', 'Alex Rivera', 'Monique Bruce'],
        'Stage': ['Discovery', 'Negotiation', 'Closed Won'],
        'Value': [50000, 120000, 15000] # Kept strictly as integers
    })
    st.session_state.call_logs = []

if 'crm_deals' not in st.session_state or 'call_logs' not in st.session_state:
    init_db()

# --- AI PROCESSING LOGIC ---
def analyze_call_with_ai(transcript_text, rep_name):
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
    
    st.subheader("Active Deals")
    st.dataframe(
        st.session_state.crm_deals, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Value": st.column_config.NumberColumn(
                "Value",
                help="Total deal value in USD",
                format="$%d"
            )
        }
    )
    
    st.divider()
    
    st.subheader("🎙️ Log a Call (Zoom/Meet Sync)")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        rep_list = st.session_state.crm_deals['Rep'].unique()
        selected_rep = st.selectbox("Sales Representative", rep_list)
        selected_deal = st.selectbox("Associate with Deal", st.session_state.crm_deals[st.session_state.crm_deals['Rep'] == selected_rep]['Deal_ID'])
        uploaded_file = st.file_uploader("Upload Call Audio", type=["mp3", "wav", "m4a"])
    
    if uploaded_file and st.button("Transcribe & Analyze"):
        with st.spinner("Transcribing audio securely..."):
            transcription = client.audio.transcriptions.create(
                file=(uploaded_file.name, uploaded_file.read()),
                model="whisper-large-v3",
                response_format="text"
            )
            
        with st.spinner("Extracting KPIs and coaching insights..."):
            analysis_data = analyze_call_with_ai(transcription, selected_rep)
            
            st.session_state.call_logs.append({
                "Rep": selected_rep,
                "Deal_ID": selected_deal,
                "Transcript": transcription,
                "Analysis": analysis_data
            })
            
        st.success("Call logged and analyzed successfully!")
        
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
    
    # --- TOP LEVEL METRICS ---
    # Fail-safe: Force values to numeric, stripping any corrupted strings from old session memory
    clean_values = st.session_state.crm_deals['Value'].astype(str).str.replace(r'[$,]', '', regex=True)
    total_pipeline = pd.to_numeric(clean_values, errors='coerce').sum()
    
    total_calls = len(st.session_state.call_logs)
    
    if total_calls > 0:
        all_scores = [log['Analysis']['kpi_scores'] for log in st.session_state.call_logs]
        df_scores = pd.DataFrame(all_scores)
        avg_overall = df_scores.values.mean()
        clarity_avg = df_scores['clarity'].mean()
        confidence_avg = df_scores['confidence'].mean()
        objection_avg = df_scores['objection_handling'].mean()
        closing_avg = df_scores['closing'].mean()
    else:
        avg_overall = 0.0
        clarity_avg = 0.0
        confidence_avg = 0.0
        objection_avg = 0.0
        closing_avg = 0.0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Calls Analyzed", total_calls)
    m2.metric("Active Pipeline Value", f"${total_pipeline:,.0f}")
    m3.metric("Team Overall KPI Score", f"{avg_overall:.1f} / 10")
    m4.metric("Active Coaching Alerts", total_calls)
    
    st.divider()

    # --- KPI BREAKDOWN & TRENDS ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Team KPI Performance")
        kpi_chart_data = pd.DataFrame({
            'KPI': ['Clarity', 'Confidence', 'Objections', 'Closing'],
            'Score': [clarity_avg, confidence_avg, objection_avg, closing_avg]
        })
        st.altair_chart(
            st.line_chart(kpi_chart_data.set_index('KPI'), y='Score', height=300) if total_calls == 0 else st.bar_chart(kpi_chart_data.set_index('KPI'), height=300)
        )
        if total_calls == 0:
             st.caption("Awaiting call data to populate KPI distribution.")

    with col2:
        st.subheader("Historical Progress")
        trend_data = pd.DataFrame({
            "Week": ["W1", "W2", "W3", "Current"],
            "Avg Score": [6.5, 7.0, 7.2, avg_overall if avg_overall > 0 else 7.2] 
        }).set_index("Week")
        st.line_chart(trend_data, height=300)

    st.divider()

    # --- REP ACTIVITY & ADAPTIVE COACHING ---
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Call Activity by Rep")
        rep_counts = {rep: 0 for rep in st.session_state.crm_deals['Rep'].unique()}
        
        for log in st.session_state.call_logs:
            rep_counts[log['Rep']] = rep_counts.get(log['Rep'], 0) + 1
            
        activity_df = pd.DataFrame(list(rep_counts.items()), columns=['Sales Rep', 'Total Calls Analyzed'])
        st.dataframe(activity_df, use_container_width=True, hide_index=True)

    with col4:
        st.subheader("Adaptive Performance Tracking")
        if total_calls == 0:
            st.info("No actionable intelligence generated yet. Waiting for system to process incoming calls.")
        else:
            for idx, log in enumerate(st.session_state.call_logs):
                rep = log['Rep']
                deal = log['Deal_ID']
                suggestion = log['Analysis']['adaptive_suggestion']
                
                st.warning(f"**Action Required for {rep} (Deal {deal}):**\n\n{suggestion}")

# --- MAIN APP ROUTING ---
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Select View:", ["Sales Rep Hub", "Manager Dashboard"])
st.sidebar.divider()

# Added a reset button to easily clear cache during testing/demos
if st.sidebar.button("🔄 Reset POC Data"):
    init_db()
    st.rerun()

if app_mode == "Sales Rep Hub":
    view_sales_rep()
elif app_mode == "Manager Dashboard":
    view_admin_dashboard()
