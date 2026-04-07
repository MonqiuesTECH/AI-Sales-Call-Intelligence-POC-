import streamlit as st
import pandas as pd
import json
from groq import Groq

# --- CONFIGURATION ---
st.set_page_config(page_title="Revenue Intelligence Platform", layout="wide", page_icon="👔")

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
    st.session_state.interactions = []
    st.session_state.bd_view = "overview" # Controls the page routing for Head of BD
    
    # Mock data for SEO and Campaigns
    st.session_state.marketing_data = pd.DataFrame({
        "Channel": ["SEO (Organic)", "LinkedIn Ads", "Google PPC", "Cold Email Drip"],
        "Traffic/Volume": ["45k visits", "12k impressions", "8k clicks", "15k sent"],
        "Leads Generated": [340, 120, 95, 400],
        "AI Health Score (%)": [88, 71, 78, 62] # 62 and 71 are below the 75% threshold
    })

if 'crm_deals' not in st.session_state or 'interactions' not in st.session_state:
    init_db()

# --- AI PROCESSING LOGIC ---
def analyze_interaction_with_ai(content, rep_name, type="call"):
    if type == "call":
        prompt = f"""
        Analyze this sales call transcript for {rep_name} using Forbes Sales Training standards.
        Transcript: {content}
        
        Output valid JSON:
        {{
            "kpi_scores": {{"clarity": int, "confidence": int, "objection_handling": int, "closing": int}},
            "key_takeaways": ["point 1", "point 2"],
            "manager_coaching_playbook": "Actionable advice for the Head of BD to coach {rep_name}."
        }}
        """
    else:
        prompt = f"""
        Analyze this sales email by {rep_name} using Forbes Sales Training standards.
        Email: {content}
        
        Output valid JSON:
        {{
            "kpi_scores": {{"clarity": int, "persuasion": int, "call_to_action": int, "personalization": int}},
            "key_takeaways": ["point 1", "point 2"],
            "manager_coaching_playbook": "Actionable advice for the Head of BD to coach {rep_name} on email outreach."
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
    st.markdown("Log inbound/outbound communications to update the BD pipeline.")
    
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
        comm_direction = st.radio("Direction", ["Outbound", "Inbound"], horizontal=True)
    
    with col2:
        tab1, tab2 = st.tabs(["🎙️ Log Call", "📧 Sync Email"])
        
        # CALL LOGGING
        with tab1:
            uploaded_file = st.file_uploader("Upload Call Audio", type=["mp3", "wav", "m4a"], key="audio_up")
            if uploaded_file and st.button("Analyze Call"):
                with st.spinner("Processing Audio..."):
                    transcription = client.audio.transcriptions.create(
                        file=(uploaded_file.name, uploaded_file.read()),
                        model="whisper-large-v3",
                        response_format="text"
                    )
                with st.spinner("Grading against Forbes Standards..."):
                    analysis_data = analyze_interaction_with_ai(transcription, selected_rep, type="call")
                    st.session_state.interactions.append({
                        "Type": "Call", "Direction": comm_direction, "Rep": selected_rep, "Deal_ID": selected_deal,
                        "Content": transcription, "Analysis": analysis_data
                    })
                st.success("Call synced to Team Pipeline.")
                
        # EMAIL LOGGING
        with tab2:
            email_text = st.text_area("Paste Email Text", height=150)
            if email_text and st.button("Analyze Email"):
                with st.spinner("Grading Email..."):
                    analysis_data = analyze_interaction_with_ai(email_text, selected_rep, type="email")
                    st.session_state.interactions.append({
                        "Type": "Email", "Direction": comm_direction, "Rep": selected_rep, "Deal_ID": selected_deal,
                        "Content": email_text, "Analysis": analysis_data
                    })
                st.success("Email synced to Team Pipeline.")

def view_head_of_bd():
    # --- ROUTER LOGIC ---
    if st.session_state.bd_view == "details":
        view_bd_details()
        return

    # --- MAIN DASHBOARD OVERVIEW ---
    st.header("👔 Head of BD Dashboard (Team Overview)")
    st.markdown("Monitor whole-team pipeline, inbound/outbound communications, and AI-driven performance vs. Forbes Standards.")
    
    col_time, col_btn = st.columns([1, 4])
    with col_time:
        timeframe = st.selectbox("View Data For:", ["Daily", "Weekly", "Monthly", "Yearly"], index=2)
    with col_btn:
        st.write("") # Spacing
        st.write("") # Spacing
        if st.button("📊 See Details (Rep Breakdown, SEO & Campaigns)", type="primary"):
            st.session_state.bd_view = "details"
            st.rerun()

    # Calculate Top Level Metrics
    total_calls = sum(1 for i in st.session_state.interactions if i['Type'] == 'Call')
    total_emails = sum(1 for i in st.session_state.interactions if i['Type'] == 'Email')
    clean_values = st.session_state.crm_deals['Value'].astype(str).str.replace(r'[$,]', '', regex=True)
    total_pipeline = pd.to_numeric(clean_values, errors='coerce').sum()
    
    # Calculate Overall Forbes Sales Rating (Target 75%)
    overall_rating = 0
    if st.session_state.interactions:
        total_score = 0
        for log in st.session_state.interactions:
            scores = log['Analysis']['kpi_scores']
            # Convert out-of-10 scores to a percentage
            log_avg = (sum(scores.values()) / (len(scores) * 10)) * 100
            total_score += log_avg
        overall_rating = total_score / len(st.session_state.interactions)

    # AI Tracker Warning
    if overall_rating > 0 and overall_rating < 75:
        st.error(f"⚠️ **AI ALERT:** Team Overall Sales Rating has dropped below the 75% target to {overall_rating:.1f}%. Immediate coaching required.")
    elif overall_rating >= 75:
        st.success(f"✅ **AI TRACKER:** Team is performing well. Forbes Rating is maintaining above target at {overall_rating:.1f}%.")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Inbound/Outbound Calls", total_calls)
    m2.metric("Inbound/Outbound Emails", total_emails)
    m3.metric("Team Pipeline Managed", f"${total_pipeline:,.0f}")
    
    delta_str = ""
    if overall_rating > 0:
        delta = overall_rating - 75
        delta_str = f"{delta:+.1f}% vs Target"
    m4.metric("Forbes Sales Rating", f"{overall_rating:.1f}%" if overall_rating > 0 else "0%", delta_str, delta_color="normal" if overall_rating >= 75 else "inverse")
    
    st.divider()

    # --- ARCHIVE & COACHING ---
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🎯 Forbes Targeted Coaching")
        if not st.session_state.interactions:
            st.info("Awaiting team activity to generate coaching playbooks.")
        else:
            for log in st.session_state.interactions:
                with st.expander(f"Coach {log['Rep']} - {log['Direction']} {log['Type']}"):
                    st.write(log['Analysis']['manager_coaching_playbook'])

    with c2:
        st.subheader("🗄️ Team Comm Archive")
        if st.session_state.interactions:
            filter_rep = st.selectbox("Filter by Rep", ["All Team"] + list(st.session_state.crm_deals['Rep'].unique()))
            for log in reversed(st.session_state.interactions):
                if filter_rep == "All Team" or log['Rep'] == filter_rep:
                    icon = "🎙️" if log['Type'] == "Call" else "📧"
                    with st.expander(f"{icon} {log['Direction']} {log['Type']}: {log['Rep']}"):
                        st.write(log['Content'])
        else:
            st.caption("Archive is currently empty.")


def view_bd_details():
    # --- DETAILED DRILL DOWN VIEW ---
    st.header("📊 Deep Dive Analytics")
    if st.button("🔙 Back to Team Overview"):
        st.session_state.bd_view = "overview"
        st.rerun()
        
    st.markdown("Detailed breakdown of Rep Performance, Online Campaigns, and SEO Engine.")
    
    tab_reps, tab_marketing = st.tabs(["Sales Rep Breakdown", "Online Campaigns & SEO"])
    
    with tab_reps:
        st.subheader("Individual Rep Performance vs. Target (75%)")
        # In a real app, this would aggregate real data per rep. We use placeholder data to demonstrate the UI.
        rep_data = pd.DataFrame({
            "Rep Name": st.session_state.crm_deals['Rep'].unique(),
            "Total Inbound/Outbound": [5, 12, 8], # Mock interaction counts
            "Pipeline Controlled": ["$65,000", "$120,000", "$85,000"],
            "Personal Forbes Rating": [78, 82, 68] # Notice the 68 is below target
        })
        st.dataframe(rep_data, use_container_width=True, hide_index=True)
        st.info("💡 **AI Insight:** Sarah Chen's Forbes Rating has dropped to 68%. Review her outbound call transcripts to address objection handling.")

    with tab_marketing:
        st.subheader("Top of Funnel Health (AI Monitored)")
        st.markdown("The AI tracks the health of lead generation sources. Any source dropping below a **75% Health Score** requires optimization.")
        
        st.dataframe(
            st.session_state.marketing_data, 
            use_container_width=True, hide_index=True,
            # Streamlit trick to highlight failing rows visually
            column_config={
                "AI Health Score (%)": st.column_config.ProgressColumn(
                    "AI Health Score (%)",
                    help="Target is 75%",
                    format="%d",
                    min_value=0,
                    max_value=100,
                )
            }
        )
        st.warning("⚠️ **AI Insight:** Cold Email Drip (62%) and LinkedIn Ads (71%) are underperforming. Recommend A/B testing new copy and adjusting ad audience parameters.")

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
