import streamlit as st
import pandas as pd
import json
from groq import Groq

# --- CONFIGURATION ---
st.set_page_config(page_title="Company Brain OS", layout="wide", page_icon="🧠")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("Missing GROQ_API_KEY in Streamlit secrets.")
    st.stop()

# --- MOCK DATABASE (THE COMPANY BRAIN) ---
def init_db():
    st.session_state.crm_deals = pd.DataFrame({
        'Deal_ID': ['D-101', 'D-102', 'D-103', 'D-104', 'D-105'],
        'Client': ['SunCity Commercial Array', 'Oakridge HOA Residential', 'GreenTech Warehouse', 'Horizon Farms Microgrid', 'Metro Park Facilities'],
        'Rep': ['Monique Bruce', 'Alex Rivera', 'Sarah Chen', 'David Thorne', 'Elena Rostova'],
        'Stage': ['Negotiation', 'Stalled', 'Closed Won', 'Discovery', 'Closed Lost'], 
        'Value': [350000, 120000, 850000, 420000, 210000] 
    })
    
    st.session_state.ops_tasks = pd.DataFrame({
        'Task_ID': ['T-01', 'T-02', 'T-03', 'T-04', 'T-05', 'T-06', 'T-07', 'T-08'],
        'Deal_ID': ['D-103', 'D-103', 'D-101', 'D-105', 'Internal', 'D-101', 'D-104', 'D-103'],
        'Task Name': ['Submit City Permits', 'Order Inverters', 'Draft HOA Proposal', 'Cancel Procurement (Lost)', 'Mandatory Safety Training', 'Site Shading Analysis', 'Interconnection Agreement', 'Schedule Install Crew'],
        'Owner': ['Ops Team', 'Procurement', 'Alex Rivera', 'Engineering', 'Elena Rostova', 'Engineering', 'Ops Team', 'Ops Team'],
        'Status': ['Done', 'Done', 'Stuck', 'Done', 'To Do', 'Working on it', 'Working on it', 'To Do'],
        'Priority': ['High', 'Critical', 'Medium', 'Critical', 'Critical', 'High', 'Medium', 'High'],
        'Timeline': pd.to_datetime(['2026-04-10', '2026-04-05', '2026-04-12', '2026-04-08', '2026-04-09', '2026-04-14', '2026-04-18', '2026-04-22']).date
    })

    st.session_state.marketing_data = pd.DataFrame({
        "Channel": ["Google Local Service Ads", "Door-to-Door Canvassing", "Facebook Lead Forms", "Commercial Outbound"],
        "Traffic/Volume": ["15k impressions", "800 doors knocked", "12k clicks", "5k emails sent"],
        "Leads Generated": [180, 45, 310, 85],
        "AI Health Score (%)": [88, 71, 62, 78] 
    })

    st.session_state.interactions = [
        {
            "Type": "Call", "Direction": "Outbound", "Rep": "Elena Rostova", "Deal_ID": "D-105",
            "Content": "Prospect: 'I read that the solar tax credit is only 30%.' \n\nElena: 'No, listen to me, if you sign today I guarantee you a 100% write-off.'",
            "Analysis": {"kpi_scores": {"clarity": 2, "confidence": 9, "objection_handling": 1, "closing": 1}, "key_takeaways": ["Violated federal compliance"], "manager_coaching_playbook": "🚨 CRITICAL: Elena provided fraudulent tax advice."}
        },
        {
            "Type": "Call", "Direction": "Inbound", "Rep": "Sarah Chen", "Deal_ID": "D-103",
            "Content": "Prospect: 'I'm worried about the panels voiding my roof warranty.' \n\nSarah: 'I completely understand. We use a proprietary triple-flashing mount to maintain GAF warranties. Let me send the spec.'",
            "Analysis": {"kpi_scores": {"clarity": 9, "confidence": 9, "objection_handling": 10, "closing": 8}, "key_takeaways": ["Excellent technical knowledge"], "manager_coaching_playbook": "Sarah handled technical objections perfectly."}
        }
    ]

    st.session_state.ceo_metrics = {"ARR": 10400000, "Cash_Runway_Months": 14, "Burn_Rate": 450000, "Active_Agents": 3}
    
    # Message Brokers & Routers
    st.session_state.push_notifications = [] 
    st.session_state.task_evidence = [] 
    st.session_state.bd_view = "overview"

# --- BULLETPROOF INITIALIZATION ---
required_keys = ['crm_deals', 'ops_tasks', 'marketing_data', 'interactions', 'ceo_metrics', 'push_notifications', 'task_evidence', 'bd_view']
for key in required_keys:
    if key not in st.session_state:
        init_db()
        break

# --- AI PROCESSING LOGIC ---
def analyze_interaction_with_ai(content, rep_name, type="call"):
    system_prompt = """You are an AI sales leadership coach. You must output ONLY valid JSON.
    Schema: {"kpi_scores": {"clarity": 8, "confidence": 8, "objection_handling": 8, "closing": 8}, "key_takeaways": ["point 1"], "manager_coaching_playbook": "Actionable advice."}"""
    user_prompt = f"Analyze this {type} interaction for Sales Rep: {rep_name}.\n\nText: {content}"
    
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192", messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], temperature=0.1, response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"kpi_scores": {"clarity": 5, "confidence": 5, "objection_handling": 5, "closing": 5}, "key_takeaways": ["API Analysis Failed"], "manager_coaching_playbook": "API error."}

# --- 1. CEO COMMAND CENTER ---
def view_ceo_command_center():
    st.header("🏢 CEO Command Center")
    st.markdown("The Company Brain: Cross-departmental synthesis powered by Gemini OS.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Projected ARR", f"${st.session_state.ceo_metrics['ARR']:,.0f}", "+12% YoY")
    c2.metric("Total Pipeline", "$1,950,000")
    total_tasks = len(st.session_state.ops_tasks)
    stuck = len(st.session_state.ops_tasks[st.session_state.ops_tasks['Status'] == 'Stuck'])
    flow_health = ((total_tasks - stuck) / total_tasks) * 100 if total_tasks > 0 else 100
    c3.metric("Ops Delivery Health", f"{flow_health:.0f}%", f"-{stuck} Stuck Projects", delta_color="inverse")
    c4.metric("Active AI Agents", st.session_state.ceo_metrics['Active_Agents'])
    st.divider()
    st.subheader("🧠 Gemini Executive Synthesis")
    st.error("🚨 **Systemic Risk Detected (Sales vs. Ops):** Deal D-103 (GreenTech Warehouse) was marked 'Closed Won', but Operations is STUCK on Permitting. Revenue recognition will be delayed. Recommend immediate COO intervention.")
    st.warning("⚠️ **Marketing vs. Sales Alignment:** Facebook Lead Forms are generating high volume (310 leads), but AI Sales Ratings for these leads average 45%. Recommend Marketing shift budget to Google Local Service Ads.")

# --- 2. EMPLOYEE TERMINAL (Sales & Ops) ---
def view_employee_terminal():
    st.header("👤 Employee Terminal (Sales & Field Ops)")
    st.markdown("Log intelligence, sync emails, and clear operational roadblocks.")
    
    selected_rep = st.selectbox("Identify User (Demo Purposes)", st.session_state.crm_deals['Rep'].unique())
    st.divider()

    tab_inbox, tab_crm, tab_log = st.tabs(["📥 Action Inbox (Zero-Meeting)", "💼 Active Pipeline", "🎙️ AI Comm Logging"])

    with tab_inbox:
        st.subheader("Zero-Meeting Action Items")
        rep_alerts = [alert for alert in st.session_state.push_notifications if alert['Owner'] == selected_rep and not alert.get('Resolved', False)]
        
        if not rep_alerts:
            st.success("🎉 Inbox Zero. No pending requests from Operations.")
        else:
            for idx, alert in enumerate(rep_alerts):
                st.warning(f"🔔 **URGENT REQUEST FROM COO:** Update required on Task **{alert['Task_ID']} ({alert['Task Name']})** for Deal {alert['Deal_ID']}.")
                with st.form(key=f"update_form_{idx}"):
                    update_notes = st.text_area("Status Update / Explanation")
                    uploaded_evidence = st.file_uploader("Attach Evidence (Site Videos .mp4, Photos .jpg, Permits .pdf)", type=["png", "jpg", "jpeg", "pdf", "mp4", "mov"], accept_multiple_files=True)
                    new_status = st.selectbox("Update Task Status", ["Working on it", "Done", "Stuck"])
                    if st.form_submit_button("Submit Evidence & Clear Alert"):
                        alert['Resolved'] = True
                        st.session_state.ops_tasks.loc[st.session_state.ops_tasks['Task_ID'] == alert['Task_ID'], 'Status'] = new_status
                        file_names = [file.name for file in uploaded_evidence] if uploaded_evidence else ["No files attached"]
                        st.session_state.task_evidence.append({
                            "Task_ID": alert['Task_ID'], "Rep": selected_rep, "Notes": update_notes, "Files": file_names, "New_Status": new_status
                        })
                        st.success("Update pushed to Operations Dashboard.")
                        st.rerun()

    with tab_crm:
        st.dataframe(st.session_state.crm_deals[st.session_state.crm_deals['Rep'] == selected_rep], use_container_width=True, hide_index=True)

    with tab_log:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("🤖 Gemini Workspace Auto-Sync")
            selected_deal = st.selectbox("Associate Deal", st.session_state.crm_deals[st.session_state.crm_deals['Rep'] == selected_rep]['Deal_ID'])
            if st.button("✨ Auto-Sync (Gmail & Meet)", type="primary"):
                with st.spinner("Gemini is reading your Google Workspace..."):
                    mock_email = f"Hey {selected_rep}, let's move forward with the solar proposal. Call me tomorrow to finalize."
                    analysis_data = analyze_interaction_with_ai(mock_email, selected_rep, type="email")
                    st.session_state.interactions.append({"Type": "Email", "Direction": "Inbound", "Rep": selected_rep, "Deal_ID": selected_deal, "Content": mock_email, "Analysis": analysis_data})
                st.success("Gemini automatically synced 1 thread to the CRM.")
        with col2:
            st.subheader("🎙️ Manual Audio Upload")
            uploaded_file = st.file_uploader("Upload Call Audio", type=["mp3", "wav", "m4a"], key="audio_up")
            if uploaded_file and st.button("Analyze Call"):
                with st.spinner("Processing..."):
                    transcription = client.audio.transcriptions.create(file=(uploaded_file.name, uploaded_file.read()), model="whisper-large-v3", response_format="text")
                    analysis_data = analyze_interaction_with_ai(transcription, selected_rep, type="call")
                    st.session_state.interactions.append({"Type": "Call", "Direction": "Outbound", "Rep": selected_rep, "Deal_ID": selected_deal, "Content": transcription, "Analysis": analysis_data})
                st.success("Call synced.")

# --- 3. OPERATIONS BOARD ---
def view_operations_board():
    st.header("📋 Operations & Project Board")
    st.markdown("Internal task management and post-sale project tracking.")
    
    total_tasks = len(st.session_state.ops_tasks)
    stuck_tasks = len(st.session_state.ops_tasks[st.session_state.ops_tasks['Status'] == 'Stuck'])
    flow_rate = ((total_tasks - stuck_tasks) / total_tasks) * 100 if total_tasks > 0 else 100
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Active Projects", total_tasks)
    c2.metric("Blocked/Stuck Tasks", stuck_tasks, delta_color="inverse" if stuck_tasks > 0 else "normal", delta=f"{stuck_tasks} Needs Attention")
    c3.metric("Ops Flow Health", f"{flow_rate:.0f}%", f"{flow_rate - 85:+.1f}% vs Target", delta_color="normal" if flow_rate >= 85 else "inverse")
    c4.metric("Evidence Uploaded", len(st.session_state.task_evidence))

    st.divider()

    st.subheader("📈 Strategic Operations Forecast (AI)")
    st.info("**Forecast:** Based on the trailing 30-day sales velocity ($850k closed), current operational capacity is running at **92% utilization**. If Deals D-101 and D-104 close this week as projected by Sales, the 'Engineering' queue will exceed capacity by 15%, causing a 14-day installation delay. \n\n**Action Required:** Pre-approve overtime for the engineering desk immediately to protect the 85% Ops Flow Health target.")
    st.divider()

    colA, colB = st.columns([2, 1])
    with colA:
        st.subheader("Active Tasks (Interactive Board)")
        st.session_state.ops_tasks['Timeline'] = pd.to_datetime(st.session_state.ops_tasks['Timeline']).dt.date
        st.session_state.ops_tasks = st.data_editor(
            st.session_state.ops_tasks, use_container_width=True, hide_index=True, num_rows="dynamic",
            column_config={
                "Status": st.column_config.SelectboxColumn("Status", options=["To Do", "Working on it", "Stuck", "Done"], required=True),
                "Priority": st.column_config.SelectboxColumn("Priority", options=["Low", "Medium", "High", "Critical"], required=True),
            }
        )

    with colB:
        st.subheader("🚀 Asynchronous Interventions")
        pending_df = st.session_state.ops_tasks[st.session_state.ops_tasks['Status'] != 'Done']
        if pending_df.empty:
            st.success("All tasks complete!")
        else:
            for index, row in pending_df.iterrows():
                with st.container(border=True):
                    st.markdown(f"**{row['Task Name']}**")
                    st.caption(f"Owner: {row['Owner']} | Status: {row['Status']}")
                    if st.button(f"📲 Ask for Update", key=f"ping_{row['Task_ID']}"):
                        st.session_state.push_notifications.append({"Task_ID": row['Task_ID'], "Task Name": row['Task Name'], "Owner": row['Owner'], "Deal_ID": row['Deal_ID'], "Resolved": False})
                        st.toast(f"Push notification sent to {row['Owner']}'s device!")

    st.divider()
    st.subheader("🗂️ Task Evidence & AI Summaries")
    if not st.session_state.task_evidence:
        st.caption("No evidence uploaded yet. Ping an owner above to request files.")
    else:
        for ev in reversed(st.session_state.task_evidence):
            with st.expander(f"Update: Task {ev['Task_ID']} by {ev['Rep']} ➔ Moved to '{ev['New_Status']}'", expanded=True):
                st.markdown(f"**Rep's Notes:** {ev['Notes']}")
                st.markdown(f"**📎 Attached Files:** {', '.join(ev['Files'])}")
                st.info("🤖 **Gemini Analysis:** Evidence verified. The attached media matches the project requirements. Proceed to next stage.")

# --- 4. HEAD OF BD DASHBOARD (RESTORED FULLY) ---
def view_bd_details():
    st.header("📊 Deep Dive Analytics")
    if st.button("🔙 Back to Team Overview"):
        st.session_state.bd_view = "overview"
        st.rerun()
        
    tab_reps, tab_marketing = st.tabs(["Sales Rep Breakdown", "Marketing & Lead Gen"])
    
    with tab_reps:
        st.subheader("Individual Rep Performance vs. Target (75%)")
        unique_reps = st.session_state.crm_deals['Rep'].unique()
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

def view_head_of_bd():
    if st.session_state.bd_view == "details":
        view_bd_details()
        return

    st.header("👔 Head of BD Dashboard")
    st.markdown("Monitor whole-team pipeline, inbound/outbound communications, and AI-driven performance vs. AI Sales Training Standards.")
    
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
    total_emails = sum(1 for i in st.session_state.interactions if i['Type'] == 'Email')
    clean_values = st.session_state.crm_deals['Value'].astype(str).str.replace(r'[$,]', '', regex=True)
    total_pipeline = pd.to_numeric(clean_values, errors='coerce').sum()
    
    overall_rating = 0
    if st.session_state.interactions:
        total_score = sum((sum(log['Analysis']['kpi_scores'].values()) / 40) * 100 for log in st.session_state.interactions)
        overall_rating = total_score / len(st.session_state.interactions)

    if overall_rating > 0 and overall_rating < 75:
        st.error(f"⚠️ **AI ALERT:** Team Overall Sales Rating has dropped below the 75% target to {overall_rating:.1f}%. Immediate coaching required.")
    elif overall_rating >= 75:
        st.success(f"✅ **AI TRACKER:** Team is performing well. AI Sales Rating is maintaining above target at {overall_rating:.1f}%.")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Inbound/Outbound Calls", total_calls)
    m2.metric("Active Solar Pipeline", f"${total_pipeline:,.0f}")
    delta_str = f"{overall_rating - 75:+.1f}% vs Target" if overall_rating > 0 else ""
    m3.metric("AI Sales Rating", f"{overall_rating:.1f}%" if overall_rating > 0 else "0%", delta_str, delta_color="normal" if overall_rating >= 75 else "inverse")
    m4.metric("Critical Alerts", "1", delta="Elena Rostova", delta_color="inverse")
    
    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🎯 Targeted AI Coaching")
        for log in reversed(st.session_state.interactions):
            icon = "🚨" if "CRITICAL" in log['Analysis']['manager_coaching_playbook'] else "💡"
            with st.expander(f"{icon} Coach {log['Rep']} - {log['Direction']} {log['Type']}"):
                st.write(log['Analysis']['manager_coaching_playbook'])

    with c2:
        st.subheader("🗄️ Team Comm Archive")
        filter_rep = st.selectbox("Filter by Rep", ["All Team"] + list(st.session_state.crm_deals['Rep'].unique()))
        for log in reversed(st.session_state.interactions):
            if filter_rep == "All Team" or log['Rep'] == filter_rep:
                icon = "🎙️" if log['Type'] == "Call" else "📧"
                with st.expander(f"{icon} {log['Direction']} {log['Type']}: {log['Rep']} (Deal {log['Deal_ID']})"):
                    st.write(log['Content'])
                    st.caption("AI KPI Breakdown:")
                    st.json(log['Analysis']['kpi_scores'])

# --- MAIN APP ROUTING ---
st.sidebar.title("🧠 The Company Brain")

app_mode = st.sidebar.radio("Access Profile:", [
    "CEO Command Center",
    "Head of BD (Sales Hub)", 
    "Operations Director",
    "Employee Terminal (Sales & Ops)"
])
st.sidebar.divider()

if st.sidebar.button("🔄 Reset Global Database"):
    for key in required_keys:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

if app_mode == "CEO Command Center":
    view_ceo_command_center()
elif app_mode == "Employee Terminal (Sales & Ops)":
    view_employee_terminal()
elif app_mode == "Operations Director":
    view_operations_board()
elif app_mode == "Head of BD (Sales Hub)":
    view_head_of_bd()
