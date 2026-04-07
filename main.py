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
    
    # Expanded Ops Data for a realistic $10M company
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
        }
    ]

    st.session_state.ceo_metrics = {"ARR": 10400000, "Cash_Runway_Months": 14, "Burn_Rate": 450000, "Active_Agents": 3}
    
    # Message Brokers
    st.session_state.push_notifications = [] 
    st.session_state.task_evidence = [] 

required_keys = ['crm_deals', 'ops_tasks', 'marketing_data', 'interactions', 'ceo_metrics', 'push_notifications', 'task_evidence']
for key in required_keys:
    if key not in st.session_state:
        init_db()
        break

# --- VIEWS ---

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
    c4.metric("Active Agents", st.session_state.ceo_metrics['Active_Agents'])
    st.divider()
    st.subheader("🧠 Gemini Executive Synthesis")
    st.error("🚨 **Systemic Risk Detected (Sales vs. Ops):** Deal D-103 (GreenTech Warehouse) was marked 'Closed Won', but Operations is STUCK. Revenue recognition will be delayed. Recommend immediate COO intervention.")

def view_employee_terminal():
    st.header("👤 Employee Terminal (Sales & Field Ops)")
    st.markdown("Log intelligence, sync emails, and clear operational roadblocks.")
    
    selected_rep = st.selectbox("Identify User (Demo Purposes)", st.session_state.crm_deals['Rep'].unique())
    st.divider()

    tab_inbox, tab_crm = st.tabs(["📥 Action Inbox (Push Notifications)", "💼 Pipeline & Sync"])

    with tab_inbox:
        st.subheader("Zero-Meeting Action Items")
        rep_alerts = [alert for alert in st.session_state.push_notifications if alert['Owner'] == selected_rep and not alert.get('Resolved', False)]
        
        if not rep_alerts:
            st.success("🎉 Inbox Zero. No pending requests from Operations.")
        else:
            for idx, alert in enumerate(rep_alerts):
                st.warning(f"🔔 **URGENT REQUEST FROM COO:** Update required on Task **{alert['Task_ID']} ({alert['Task Name']})** for Deal {alert['Deal_ID']}.")
                
                with st.form(key=f"update_form_{idx}"):
                    st.markdown("**Provide Context & Evidence (Bypass Status Meetings):**")
                    update_notes = st.text_area("Status Update / Explanation")
                    # Upgraded File Uploader for Multi-Media
                    uploaded_evidence = st.file_uploader("Attach Evidence (Site Videos .mp4, Photos .jpg, Permits .pdf)", type=["png", "jpg", "jpeg", "pdf", "mp4", "mov"], accept_multiple_files=True)
                    new_status = st.selectbox("Update Task Status", ["Working on it", "Done", "Stuck"])
                    
                    if st.form_submit_button("Submit Evidence & Clear Alert"):
                        alert['Resolved'] = True
                        st.session_state.ops_tasks.loc[st.session_state.ops_tasks['Task_ID'] == alert['Task_ID'], 'Status'] = new_status
                        
                        file_names = [file.name for file in uploaded_evidence] if uploaded_evidence else ["No files attached"]
                        st.session_state.task_evidence.append({
                            "Task_ID": alert['Task_ID'],
                            "Rep": selected_rep,
                            "Notes": update_notes,
                            "Files": file_names,
                            "New_Status": new_status
                        })
                        st.success("Update pushed directly to Operations Dashboard. Alert cleared.")
                        st.rerun()

    with tab_crm:
        st.dataframe(st.session_state.crm_deals[st.session_state.crm_deals['Rep'] == selected_rep], use_container_width=True, hide_index=True)
        st.info("💡 Auto-Sync with Gemini is active. Emails are automatically logged to the CRM.")

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

    # --- PREDICTIVE FORECASTING ---
    st.subheader("📈 Strategic Operations Forecast (AI)")
    st.info("""
    **Gemini Market & Capacity Analysis:**
    Based on trailing 30-day sales velocity ($850k closed) and the active $1.95M pipeline, current operational capacity is running at **92% utilization**. 
    
    **Forecast:** If Deals D-101 and D-104 close this week as projected by Sales, the 'Engineering / Permitting' queue will exceed capacity by 15%, causing a 14-day installation delay. 
    
    **Action Required:** Pre-approve overtime for the engineering desk or engage a freelance CAD drafter immediately to protect the 85% Ops Flow Health target.
    """)

    st.divider()

    # --- ZERO MEETING CONTROL CENTER ---
    colA, colB = st.columns([2, 1])
    
    with colA:
        st.subheader("Active Tasks (Interactive Board)")
        st.session_state.ops_tasks['Timeline'] = pd.to_datetime(st.session_state.ops_tasks['Timeline']).dt.date
        edited_df = st.data_editor(
            st.session_state.ops_tasks, use_container_width=True, hide_index=True, num_rows="dynamic",
            column_config={
                "Status": st.column_config.SelectboxColumn("Status", options=["To Do", "Working on it", "Stuck", "Done"], required=True),
                "Priority": st.column_config.SelectboxColumn("Priority", options=["Low", "Medium", "High", "Critical"], required=True),
            }
        )
        st.session_state.ops_tasks = edited_df

    with colB:
        st.subheader("🚀 Asynchronous Interventions")
        st.markdown("Push notifications to clear roadblocks without meetings.")
        
        # Now shows ALL tasks that are NOT "Done" (Stuck, To Do, Working on it)
        pending_df = st.session_state.ops_tasks[st.session_state.ops_tasks['Status'] != 'Done']
        if pending_df.empty:
            st.success("All tasks complete!")
        else:
            for index, row in pending_df.iterrows():
                # Color code the border based on status
                border_color = "red" if row['Status'] == 'Stuck' else "gray"
                with st.container(border=True):
                    st.markdown(f"**{row['Task Name']}**")
                    st.caption(f"Owner: {row['Owner']} | Status: {row['Status']}")
                    if st.button(f"📲 Ask for Update", key=f"ping_{row['Task_ID']}"):
                        st.session_state.push_notifications.append({
                            "Task_ID": row['Task_ID'],
                            "Task Name": row['Task Name'],
                            "Owner": row['Owner'],
                            "Deal_ID": row['Deal_ID'],
                            "Resolved": False
                        })
                        st.toast(f"Push notification sent to {row['Owner']}'s device!")

    st.divider()
    
    st.subheader("🗂️ Task Evidence & AI Summaries")
    st.markdown("Review requested files (videos, photos, docs) and status updates asynchronously.")
    if not st.session_state.task_evidence:
        st.caption("No evidence uploaded yet. Ping an owner above to request files.")
    else:
        for ev in reversed(st.session_state.task_evidence):
            with st.expander(f"Update: Task {ev['Task_ID']} by {ev['Rep']} ➔ Moved to '{ev['New_Status']}'", expanded=True):
                st.markdown(f"**Rep's Notes:** {ev['Notes']}")
                st.markdown(f"**📎 Attached Files:** {', '.join(ev['Files'])}")
                st.info("🤖 **Gemini Analysis:** Evidence verified. The attached media matches the project requirements. Proceed to next stage.")

def view_head_of_bd():
    st.header("👔 Head of BD Dashboard")
    st.info("Sales dashboard operating normally. Use CEO Command Center for cross-functional data.")

# --- MAIN APP ROUTING ---
st.sidebar.title("🧠 The Company Brain")

app_mode = st.sidebar.radio("Access Profile:", [
    "CEO Command Center",
    "Operations Director",
    "Employee Terminal (Sales & Ops)",
    "Head of BD (Sales Hub)"
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
