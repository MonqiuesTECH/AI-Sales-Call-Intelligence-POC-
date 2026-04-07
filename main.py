import streamlit as st
import pandas as pd
import json
from groq import Groq

# --- CONFIGURATION ---
st.set_page_config(page_title="Revenue & Ops Platform", layout="wide", page_icon="👔")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("Missing GROQ_API_KEY in Streamlit secrets.")
    st.stop()

# --- MOCK DATABASE (EXTREME VARIANCE DATA PRE-LOAD) ---
def init_db():
    # 1. CRM DEALS (Updated to reflect rep performance)
    st.session_state.crm_deals = pd.DataFrame({
        'Deal_ID': ['D-101', 'D-102', 'D-103', 'D-104', 'D-105'],
        'Client': ['SunCity Commercial Array', 'Oakridge HOA Residential', 'GreenTech Warehouse', 'Horizon Farms Microgrid', 'Metro Park Facilities'],
        'Rep': ['Monique Bruce', 'Alex Rivera', 'Sarah Chen', 'David Thorne', 'Elena Rostova'],
        'Stage': ['Negotiation', 'Stalled', 'Closed Won', 'Discovery', 'Closed Lost'], # Elena lost hers
        'Value': [350000, 120000, 850000, 420000, 210000] 
    })
    
    # 2. INTERNAL OPERATIONS TASKS 
    st.session_state.ops_tasks = pd.DataFrame({
        'Task_ID': ['T-01', 'T-02', 'T-03', 'T-04', 'T-05'],
        'Deal_ID': ['D-103', 'D-103', 'D-101', 'D-105', 'Internal'],
        'Task Name': ['Submit City Permits', 'Order Inverters', 'Draft HOA Proposal', 'Cancel Procurement (Lost Deal)', 'Mandatory Compliance Training'],
        'Owner': ['Ops Team', 'Procurement', 'Alex Rivera', 'Engineering', 'Elena Rostova'],
        'Status': ['Working on it', 'Done', 'Stuck', 'Done', 'To Do'],
        'Priority': ['High', 'Critical', 'Medium', 'Critical', 'Critical'],
        'Timeline': pd.to_datetime(['2026-04-10', '2026-04-05', '2026-04-12', '2026-04-08', '2026-04-09']).date
    })

    st.session_state.bd_view = "overview" 

    # 3. MARKETING DATA
    st.session_state.marketing_data = pd.DataFrame({
        "Channel": ["Google Local Service Ads", "Door-to-Door Canvassing", "Facebook Lead Forms", "Commercial Outbound"],
        "Traffic/Volume": ["15k impressions", "800 doors knocked", "12k clicks", "5k emails sent"],
        "Leads Generated": [180, 45, 310, 85],
        "AI Health Score (%)": [88, 71, 62, 78] 
    })

    # 4. INTERACTIONS (The Core of the Demo - Diverse Performance Examples)
    st.session_state.interactions = [
        {
            "Type": "Call", "Direction": "Outbound", "Rep": "Elena Rostova", "Deal_ID": "D-105",
            "Content": "Prospect: 'I read that the solar tax credit is only 30%.' \n\nElena: 'No, listen to me, if you sign today I guarantee you a 100% write-off. My buddy does taxes. Just sign the DocuSign right now, stop overthinking it, you're losing me money by stalling.'",
            "Analysis": {
                "kpi_scores": {"clarity": 2, "confidence": 9, "objection_handling": 1, "closing": 1},
                "key_takeaways": ["Violated federal compliance (false tax advice)", "Aggressive and hostile tone", "Zero active listening"],
                "manager_coaching_playbook": "🚨 CRITICAL ALERT: Immediate termination review required. Elena provided fraudulent tax advice and exhibited severely aggressive behavior towards a prospect. Halt all outbound calling privileges immediately."
            }
        },
        {
            "Type": "Call", "Direction": "Inbound", "Rep": "David Thorne", "Deal_ID": "D-104",
            "Content": "Prospect: 'How does the Enphase 5P battery handle surge loads if the grid goes down?' \n\nDavid: 'Uh, yeah, so... the battery is good. It holds power. I think it can run a fridge? Let me... I'd have to Google the surge thing. It's basically a big battery.'",
            "Analysis": {
                "kpi_scores": {"clarity": 4, "confidence": 2, "objection_handling": 2, "closing": 3},
                "key_takeaways": ["Severe lack of product knowledge", "Lost prospect trust immediately", "Hesitant and anxious tone"],
                "manager_coaching_playbook": "David is severely struggling with technical competence, causing deal collapse. Mandate completion of the Enphase Storage Certification before his next solo pitch. Pair him with Sarah for shadowing this week."
            }
        },
        {
            "Type": "Call", "Direction": "Outbound", "Rep": "Alex Rivera", "Deal_ID": "D-102",
            "Content": "Prospect: 'The numbers look okay, but I need to talk to my wife.' \n\nAlex: 'Yeah, totally understandable! Wives are the real bosses, right? Take your time, talk to her, and just shoot me an email whenever you guys figure it out. Have a great weekend!'",
            "Analysis": {
                "kpi_scores": {"clarity": 7, "confidence": 6, "objection_handling": 2, "closing": 1},
                "key_takeaways": ["Failed to isolate the objection", "Zero urgency created", "Did not set a follow-up meeting"],
                "manager_coaching_playbook": "Alex builds great rapport but completely folds at the close. Coach him on the 'Spouse Objection' framework. He needs to secure a hard calendar invite for a follow-up rather than leaving the ball in the prospect's court."
            }
        },
        {
            "Type": "Call", "Direction": "Inbound", "Rep": "Sarah Chen", "Deal_ID": "D-103",
            "Content": "Prospect: 'I'm worried about the panels voiding my roof warranty.' \n\nSarah: 'I completely understand that concern, John. We actually use a proprietary triple-flashing mount system specifically designed to maintain GAF roof warranties. Let me pull up the engineering spec sheet for you right now so you can see how we seal the penetrations.'",
            "Analysis": {
                "kpi_scores": {"clarity": 9, "confidence": 9, "objection_handling": 10, "closing": 8},
                "key_takeaways": ["Excellent technical knowledge", "Validates concerns before answering", "Uses proof-sources effectively"],
                "manager_coaching_playbook": "Sarah is performing exceptionally. Consider having her lead the next team meeting on objection handling regarding roof warranties to help upskill David and Alex."
            }
        }
    ]

# --- BULLETPROOF INITIALIZATION ---
required_keys = ['crm_deals', 'ops_tasks', 'bd_view', 'marketing_data', 'interactions']
for key in required_keys:
    if key not in st.session_state:
        init_db()
        break

# --- AI PROCESSING LOGIC ---
def analyze_interaction_with_ai(content, rep_name, type="call"):
    if type == "call":
        prompt = f"""Analyze this solar sales call transcript for {rep_name} using AI Sales Training standards. Transcript: {content} Output valid JSON: {{"kpi_scores": {{"clarity": int, "confidence": int, "objection_handling": int, "closing": int}}, "key_takeaways": ["point 1"], "manager_coaching_playbook": "Actionable advice."}}"""
    else:
        prompt = f"""Analyze this solar sales email by {rep_name} using AI Sales Training standards. Email: {content} Output valid JSON: {{"kpi_scores": {{"clarity": int, "persuasion": int, "call_to_action": int, "personalization": int}}, "key_takeaways": ["point 1"], "manager_coaching_playbook": "Actionable advice."}}"""
        
    response = client.chat.completions.create(
        model="llama3-8b-8192", messages=[{"role": "user", "content": prompt}], temperature=0.1, response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

# --- VIEWS ---

def view_sales_rep():
    st.header("👤 Sales Representative Hub")
    st.dataframe(st.session_state.crm_deals, use_container_width=True, hide_index=True, column_config={"Value": st.column_config.NumberColumn("Value", format="$%d")})
    st.divider()
    
    rep_list = st.session_state.crm_deals['Rep'].unique()
    col1, col2 = st.columns([1, 2])
    with col1:
        selected_rep = st.selectbox("Identify User", rep_list)
        selected_deal = st.selectbox("Associate Deal", st.session_state.crm_deals[st.session_state.crm_deals['Rep'] == selected_rep]['Deal_ID'])
        comm_direction = st.radio("Direction", ["Outbound", "Inbound"], horizontal=True)
    
    with col2:
        tab1, tab2 = st.tabs(["🎙️ Log Call", "📧 Sync Email"])
        with tab1:
            uploaded_file = st.file_uploader("Upload Call Audio", type=["mp3", "wav", "m4a"], key="audio_up")
            if uploaded_file and st.button("Analyze Call"):
                with st.spinner("Processing..."):
                    transcription = client.audio.transcriptions.create(file=(uploaded_file.name, uploaded_file.read()), model="whisper-large-v3", response_format="text")
                    analysis_data = analyze_interaction_with_ai(transcription, selected_rep, type="call")
                    st.session_state.interactions.append({"Type": "Call", "Direction": comm_direction, "Rep": selected_rep, "Deal_ID": selected_deal, "Content": transcription, "Analysis": analysis_data})
                st.success("Call synced.")
        with tab2:
            email_text = st.text_area("Paste Email Text", height=150)
            if email_text and st.button("Analyze Email"):
                with st.spinner("Processing..."):
                    analysis_data = analyze_interaction_with_ai(email_text, selected_rep, type="email")
                    st.session_state.interactions.append({"Type": "Email", "Direction": comm_direction, "Rep": selected_rep, "Deal_ID": selected_deal, "Content": email_text, "Analysis": analysis_data})
                st.success("Email synced.")

# --- THE MONDAY.COM CLONE VIEW ---
def view_operations_board():
    st.header("📋 Operations & Project Board")
    st.markdown("Internal task management and post-sale project tracking. *Replaces Monday.com dependency.*")
    
    stuck_tasks = len(st.session_state.ops_tasks[st.session_state.ops_tasks['Status'] == 'Stuck'])
    completed_tasks = len(st.session_state.ops_tasks[st.session_state.ops_tasks['Status'] == 'Done'])
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Active Projects", len(st.session_state.ops_tasks))
    c2.metric("Tasks Completed", completed_tasks)
    c3.metric("Blocked/Stuck Tasks", stuck_tasks, delta_color="inverse" if stuck_tasks > 0 else "normal", delta=f"{stuck_tasks} Needs Attention")

    st.divider()
    st.subheader("Active Tasks (Interactive Board)")
    
    st.session_state.ops_tasks['Timeline'] = pd.to_datetime(st.session_state.ops_tasks['Timeline']).dt.date
    
    edited_df = st.data_editor(
        st.session_state.ops_tasks,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "Status": st.column_config.SelectboxColumn("Status", options=["To Do", "Working on it", "Stuck", "Done"], required=True),
            "Priority": st.column_config.SelectboxColumn("Priority", options=["Low", "Medium", "High", "Critical"], required=True),
            "Timeline": st.column_config.DateColumn("Timeline", format="YYYY-MM-DD")
        }
    )
    st.session_state.ops_tasks = edited_df
    st.info("💡 **Tip:** Double click any cell to edit it, or click the '+' at the bottom to add a new task, just like Monday.com.")

def view_head_of_bd():
    if st.session_state.bd_view == "details":
        view_bd_details()
        return

    st.header("👔 Head of BD Dashboard (Team Overview)")
    
    col_time, col_btn = st.columns([1, 4])
    with col_time:
        st.selectbox("View Data For:", ["Daily", "Weekly", "Monthly", "Yearly"], index=2)
    with col_btn:
        st.write("") 
        st.write("") 
        if st.button("📊 See Details (Rep Breakdown, SEO & Campaigns)", type="primary"):
            st.session_state.bd_view = "details"
            st.rerun()

    total_calls = sum(1 for i in st.session_state.interactions if i['Type'] == 'Call')
    clean_values = st.session_state.crm_deals['Value'].astype(str).str.replace(r'[$,]', '', regex=True)
    total_pipeline = pd.to_numeric(clean_values, errors='coerce').sum()
    
    overall_rating = 0
    if st.session_state.interactions:
        total_score = 0
        for log in st.session_state.interactions:
            scores = log['Analysis']['kpi_scores']
            log_avg = (sum(scores.values()) / (len(scores) * 10)) * 100
            total_score += log_avg
        overall_rating = total_score / len(st.session_state.interactions)

    if overall_rating > 0 and overall_rating < 75:
        st.error(f"⚠️ **AI ALERT:** Team Overall Sales Rating has dropped to {overall_rating:.1f}%. Immediate interventions required.")
    else:
        st.success(f"✅ **AI TRACKER:** Team is performing well at {overall_rating:.1f}%.")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Comm Logs Processed", len(st.session_state.interactions))
    m2.metric("Active Solar Pipeline", f"${total_pipeline:,.0f}")
    
    delta_str = ""
    if overall_rating > 0:
        delta = overall_rating - 75
        delta_str = f"{delta:+.1f}% vs Target"
    m3.metric("AI Sales Rating", f"{overall_rating:.1f}%" if overall_rating > 0 else "0%", delta_str, delta_color="normal" if overall_rating >= 75 else "inverse")
    m4.metric("Critical Alerts", "1", delta="Elena Rostova", delta_color="inverse")
    
    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🎯 Targeted AI Coaching")
        # Show newest logs at the top
        for log in st.session_state.interactions:
            # Color code expander based on severity
            icon = "🚨" if "CRITICAL" in log['Analysis']['manager_coaching_playbook'] else "💡"
            with st.expander(f"{icon} Coach {log['Rep']} - {log['Type']}"):
                st.write(log['Analysis']['manager_coaching_playbook'])

    with c2:
        st.subheader("🗄️ Team Comm Archive")
        for log in st.session_state.interactions:
            with st.expander(f"🎙️ {log['Rep']} (Deal {log['Deal_ID']})"):
                st.markdown(f"**Transcript:**\n\n*{log['Content']}*")
                st.caption("AI KPI Breakdown:")
                st.json(log['Analysis']['kpi_scores'])

def view_bd_details():
    st.header("📊 Deep Dive Analytics")
    if st.button("🔙 Back to Team Overview"):
        st.session_state.bd_view = "overview"
        st.rerun()
        
    tab_reps, tab_marketing = st.tabs(["Sales Rep Breakdown", "Marketing & Lead Gen"])
    
    with tab_reps:
        st.subheader("Individual Rep Performance vs. Target (75%)")
        unique_reps = st.session_state.crm_deals['Rep'].unique()
        
        # Mapped perfectly to [Monique, Alex, Sarah, David, Elena]
        mock_pipelines = ["$350,000", "$120,000", "$850,000", "$420,000", "$210,000 (At Risk)"]
        mock_ratings = [85, 40, 92, 35, 12] 

        rep_data = pd.DataFrame({
            "Rep Name": unique_reps,
            "Pipeline Controlled": mock_pipelines[:len(unique_reps)],
            "AI Sales Rating": mock_ratings[:len(unique_reps)] 
        })
        st.dataframe(rep_data, use_container_width=True, hide_index=True)
        
        st.error("🚨 **AI Insight:** Elena Rostova (12%) has committed a compliance violation. David Thorne (35%) is failing technical product queries. Intervene immediately.")

    with tab_marketing:
        st.subheader("Top of Funnel Health (AI Monitored)")
        st.dataframe(
            st.session_state.marketing_data, 
            use_container_width=True, hide_index=True,
            column_config={"AI Health Score (%)": st.column_config.ProgressColumn("AI Health Score (%)", min_value=0, max_value=100)}
        )

# --- MAIN APP ROUTING ---
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Select View:", ["Sales Rep Hub", "Operations Board (Monday.com Clone)", "Head of BD Dashboard"])
st.sidebar.divider()

if st.sidebar.button("🔄 Reload Extreme Data POC"):
    for key in required_keys:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

if app_mode == "Sales Rep Hub":
    view_sales_rep()
elif app_mode == "Operations Board (Monday.com Clone)":
    view_operations_board()
elif app_mode == "Head of BD Dashboard":
    view_head_of_bd()
