import streamlit as st
import pandas as pd
import json
from groq import Groq

# --- CONFIGURATION ---
st.set_page_config(page_title="BD Intelligence Platform", layout="wide", page_icon="👔")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("Missing GROQ_API_KEY in Streamlit secrets.")
    st.stop()

# --- MOCK DATABASE ---
def init_db():
    st.session_state.crm_deals = pd.DataFrame({
        'Deal_ID': ['D-101', 'D-102', 'D-103', 'D-104'],
        'Client': ['TechCorp', 'Global Logistics', 'Retail Giant', 'Apex Financial'],
        'Rep': ['Monique Bruce', 'Alex Rivera', 'Monique Bruce', 'Sarah Chen'],
        'Stage': ['Discovery', 'Negotiation', 'Closed Won', 'Prospecting'],
        'Value': [50000, 120000, 15000, 85000] 
    })
    st.session_state.interactions = [] # Now stores both calls and emails

if 'crm_deals' not in st.session_state or 'interactions' not in st.session_state:
    init_db()

# --- AI PROCESSING LOGIC ---
def analyze_interaction_with_ai(content, rep_name, type="call"):
    """Handles both Calls and Emails, specifically generating Head of BD coaching playbooks."""
    
    if type == "call":
        prompt = f"""
        Analyze this sales call transcript for {rep_name}.
        Transcript: {content}
        
        Output valid JSON:
        {{
            "kpi_scores": {{"clarity": int, "confidence": int, "objection_handling": int, "closing": int}},
            "key_takeaways": ["point 1", "point 2"],
            "manager_coaching_playbook": "Actionable advice for the Head of BD on exactly how to coach {rep_name} based on their weaknesses in this call."
        }}
        """
    else:
        prompt = f"""
        Analyze this outbound sales email by {rep_name}.
        Email: {content}
        
        Output valid JSON:
        {{
            "kpi_scores": {{"clarity": int, "persuasion": int, "call_to_action": int, "personalization": int}},
            "key_takeaways": ["point 1", "point 2"],
            "manager_coaching_playbook": "Actionable advice for the Head of BD on how to help {rep_name} improve their written outreach."
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
    st.markdown("Log calls and sync emails to update the BD pipeline.")
    
    # Using column_config for clean currency display
    st.dataframe(
        st.session_state.crm_deals, 
        use_container_width=True, hide_index=True,
        column_config={"Value": st.column_config.NumberColumn("Value", format="$%d")}
    )
    
    st.divider()
    
    rep_list = st.session_state.crm_deals['Rep'].unique()
    col1, col2 = st.columns([1, 2])
    with col1:
        selected_rep = st.selectbox("Identify User", rep_list)
        selected_deal = st.selectbox("Associate Deal", st.session_state.crm_deals[st.session_state.crm_deals['Rep'] == selected_rep]['Deal_ID'])
    
    with col2:
        tab1, tab2 = st.tabs(["🎙️ Log Call", "📧 Sync Email"])
        
        # --- CALL LOGGING ---
        with tab1:
            uploaded_file = st.file_uploader("Upload Call Audio", type=["mp3", "wav", "m4a"], key="audio_up")
            if uploaded_file and st.button("Transcribe & Analyze Call"):
                with st.spinner("Processing Audio via Whisper-v3..."):
                    transcription = client.audio.transcriptions.create(
                        file=(uploaded_file.name, uploaded_file.read()),
                        model="whisper-large-v3",
                        response_format="text"
                    )
                with st.spinner("Generating Coaching Insights..."):
                    analysis_data = analyze_interaction_with_ai(transcription, selected_rep, type="call")
                    st.session_state.interactions.append({
                        "Type": "Call", "Rep": selected_rep, "Deal_ID": selected_deal,
                        "Content": transcription, "Analysis": analysis_data
                    })
                st.success("Call added to Head of BD Dashboard.")
                
        # --- EMAIL LOGGING ---
        with tab2:
            email_text = st.text_area("Paste Outbound Email Text", height=150)
            if email_text and st.button("Analyze Email"):
                with st.spinner("Evaluating Email Copy..."):
                    analysis_data = analyze_interaction_with_ai(email_text, selected_rep, type="email")
                    st.session_state.interactions.append({
                        "Type": "Email", "Rep": selected_rep, "Deal_ID": selected_deal,
                        "Content": email_text, "Analysis": analysis_data
                    })
                st.success("Email synced to Head of BD Dashboard.")

def view_head_of_bd():
    st.header("👔 Head of BD Dashboard")
    st.markdown("Monitor pipeline, team communication, and targeted coaching playbooks.")
    
    total_calls = sum(1 for i in st.session_state.interactions if i['Type'] == 'Call')
    total_emails = sum(1 for i in st.session_state.interactions if i['Type'] == 'Email')
    clean_values = st.session_state.crm_deals['Value'].astype(str).str.replace(r'[$,]', '', regex=True)
    total_pipeline = pd.to_numeric(clean_values, errors='coerce').sum()
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Calls Logged", total_calls)
    m2.metric("Emails Synced", total_emails)
    m3.metric("Pipeline Managed", f"${total_pipeline:,.0f}")
    m4.metric("Coaching Alerts", len(st.session_state.interactions))
    
    st.divider()

    # --- LEADERSHIP COACHING ALERTS ---
    st.subheader("🎯 Targeted Coaching Playbooks")
    if not st.session_state.interactions:
        st.info("Awaiting team activity. When reps log calls/emails, coaching playbooks will generate here.")
    else:
        for idx, log in enumerate(st.session_state.interactions):
            rep = log['Rep']
            deal = log['Deal_ID']
            i_type = log['Type']
            playbook = log['Analysis']['manager_coaching_playbook']
            
            with st.expander(f"Action Required: Coach {rep} on {i_type} (Deal {deal})", expanded=True):
                st.markdown(f"**How you can support their growth:**\n\n{playbook}")
                
    st.divider()

    # --- THE TRANSCRIPT / EMAIL ARCHIVE ---
    st.subheader("🗄️ Communication Archive")
    st.markdown("Filter and review raw team communication.")
    
    if st.session_state.interactions:
        archive_reps = ["All Reps"] + list(st.session_state.crm_deals['Rep'].unique())
        filter_rep = st.selectbox("Filter Archive by Rep", archive_reps)
        
        for log in reversed(st.session_state.interactions): # Show newest first
            if filter_rep == "All Reps" or log['Rep'] == filter_rep:
                icon = "🎙️ Call Transcript" if log['Type'] == "Call" else "📧 Email Copy"
                with st.expander(f"{icon}: {log['Rep']} - Deal {log['Deal_ID']}"):
                    st.write(log['Content'])
    else:
        st.caption("Archive is currently empty.")

# --- MAIN APP ROUTING ---
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Select View:", ["Sales Rep Hub", "Head of BD Dashboard"])
st.sidebar.divider()

if st.sidebar.button("🔄 Reset POC Data"):
    init_db()
    st.rerun()

if app_mode == "Sales Rep Hub":
    view_sales_rep()
elif app_mode == "Head of BD Dashboard":
    view_head_of_bd()
