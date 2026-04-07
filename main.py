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
        'Task_ID': ['T-01', 'T-02', 'T-03', 'T-04', 'T-05'],
        'Deal_ID': ['D-103', 'D-103', 'D-101', 'D-105', 'Internal'],
        'Task Name': ['Submit City Permits', 'Order Inverters', 'Draft HOA Proposal', 'Cancel Procurement (Lost Deal)', 'Mandatory Compliance Training'],
        'Owner': ['Ops Team', 'Procurement', 'Alex Rivera', 'Engineering', 'Elena Rostova'],
        'Status': ['Working on it', 'Done', 'Stuck', 'Done', 'To Do'],
        'Priority': ['High', 'Critical', 'Medium', 'Critical', 'Critical'],
        'Timeline': pd.to_datetime(['2026-04-10', '2026-04-05', '2026-04-12', '2026-04-08', '2026-04-09']).date
    })

    st.session_state.marketing_data = pd.DataFrame({
        "Channel": ["Google Local Service Ads", "Door-to-Door Canvassing", "Facebook Lead Forms", "Commercial Outbound"],
        "Traffic/Volume": ["15k impressions", "800 doors knocked", "12k clicks", "5k emails sent"],
        "Leads Generated": [180, 45, 310, 85],
        "AI Health Score (%)": [88, 71, 62, 78] 
    })

    st.session_state.interactions = [
        {
            "Type": "Call", "Direction": "Inbound", "Rep": "Sarah Chen", "Deal_ID": "D-103",
            "Content": "Prospect: 'I'm worried about the panels voiding my roof warranty.' \n\nSarah: 'I completely understand. We use a proprietary triple-flashing mount system to maintain GAF warranties. Let me send the engineering spec.'",
            "Analysis": {
                "kpi_scores": {"clarity": 9, "confidence": 9, "objection_handling": 10, "closing": 8},
                "key_takeaways": ["Excellent technical knowledge", "Strong trust building"],
                "manager_coaching_playbook": "Sarah handled technical objections perfectly."
            }
        }
    ]

    st.session_state.ceo_metrics = {"ARR": 10400000, "Cash_Runway_Months": 14, "Burn_Rate": 450000, "Active_Agents": 3}
    
    # NEW: Zero-Meeting Architecture Message Brokers
    st.session_state.push_notifications = [] # Alerts sent from COO to Reps
    st.session_state.task_evidence = [] # Files and notes uploaded back to the COO

# --- BULLETPROOF INITIALIZATION ---
required_keys = ['crm_deals', 'ops_tasks', 'marketing_data', 'interactions', 'ceo_metrics', 'push_notifications', 'task_evidence']
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
        response = client.chat.completions.create(model="llama3-8b-8192", messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], temperature=0.1, response_format={"type": "json_object"})
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"kpi_scores": {"clarity": 5, "confidence": 5, "objection_handling": 5, "closing": 5}, "key_takeaways": ["API Analysis Failed"], "manager_coaching_playbook": "API error."}

# --- VIEWS ---

def view_ceo_command_center():
    st.header("🏢 CEO Command Center")
    st.markdown("The Company Brain: Cross-departmental synthesis powered by Gemini OS.")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Projected ARR", f"${st.session_state.ceo_metrics['ARR']:,.0f}", "+12% YoY")
    c2.metric("Cash Runway", f"{st.session_state.ceo_metrics['Cash_Runway_Months']} Months", "-1 Month")
    c3.metric("Total Pipeline", "$1,950,000")
    total_tasks = len(st.session_state.ops_tasks)
    stuck = len(st.session_state.ops_tasks[st.session_state.ops_tasks['Status'] == 'Stuck'])
    flow_health = ((total_tasks - stuck) / total_tasks) * 100 if total_tasks > 0 else 100
    c4.metric("Ops Delivery Health", f"{flow_health:.0f}%", f"-{stuck} Stuck Projects", delta_color="inverse")
    
    st.divider()

    st.subheader("🤖 Autonomous Workspace Agents (Live Status)")
    a1, a2, a3 = st.columns(3)
    a1.info("**📧 Inbound Lead Parser**\n\nStatus: *Active*\n\nProcessed 42 emails today.")
    a2.warning("**🏗️ Ops Permitting Agent**\n\nStatus: *Blocked*\n\nWaiting on City API for D-103.")
    a3.success("**📁 Auto-Filing Agent**\n\nStatus: *Active*\n\nOrganized 12 site photos to CRM.")

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
        # Filter alerts for this specific rep
        rep_alerts = [alert for alert in st.session_state.push_notifications if alert['Owner'] == selected_rep and not alert.get('Resolved', False)]
        
        if not rep_alerts:
            st.success("🎉 Inbox Zero. No pending requests from Operations.")
        else:
            for idx, alert in enumerate(rep_alerts):
                st.warning(f"🔔 **URGENT REQUEST FROM COO:** Update required on Task **{alert['Task_ID']} ({alert['Task Name']})** for Deal {alert['Deal_ID']}.")
                
                with st.form(key=f"update_form_{idx}"):
                    st.markdown("**Provide Context & Evidence (Bypass Status Meetings):**")
                    update_notes = st.text_area("Status Update / Explanation")
                    uploaded_evidence = st.file_uploader("Upload Evidence (Photos, PDFs, Approvals)", type=["png", "jpg", "pdf", "mp4"])
                    new_status = st.selectbox("Update Task Status", ["Working on it", "Done", "Stuck"])
                    
                    if st.form_submit_button("Submit Evidence & Clear Alert"):
                        # Mark alert as resolved
                        alert['Resolved'] = True
                        
                        # Update the main Ops database
                        st.session_state.ops_tasks.loc[st.session_state.ops_tasks['Task_ID'] == alert['Task_ID'], 'Status'] = new_status
                        
                        # Log the evidence for the COO to see
                        file_name = uploaded_evidence.name if uploaded_evidence else "No file attached"
                        st.session_state.task_evidence.append({
                            "Task_ID": alert['Task_ID'],
                            "Rep": selected_rep,
                            "Notes": update_notes,
                            "File": file_name,
                            "New_Status": new_status
                        })
                        st.success("Update pushed directly to Operations Dashboard. Alert cleared.")
                        st.rerun()

    with tab_crm:
        st.dataframe(st.session_state.crm_deals[st.session_state.crm_deals['Rep'] == selected_rep], use_container_width=True, hide_index=True)
        # (Existing call/email sync buttons would go here)
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
        
        stuck_df = st.session_state.ops_tasks[st.session_state.ops_tasks['Status'] == 'Stuck']
        if stuck_df.empty:
            st.success("No stuck tasks currently.")
        else:
            for index, row in stuck_df.iterrows():
                with st.container(border=True):
                    st.write(f"**{row['Task Name']}** ({row['Owner']})")
                    if st.button(f"📲 Ping {row['Owner']} for Update", key=row['Task_ID']):
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
    st.markdown("Review requested files and status updates asynchronously.")
    if not st.session_state.task_evidence:
        st.caption("No evidence uploaded yet. Ping an owner above to request files.")
    else:
        for ev in reversed(st.session_state.task_evidence):
            with st.expander(f"Update: Task {ev['Task_ID']} by {ev['Rep']} ➔ Moved to '{ev['New_Status']}'", expanded=True):
                st.markdown(f"**Rep's Notes:** {ev['Notes']}")
                st.markdown(f"**📎 Attached File:** `{ev['File']}`")
                st.info("🤖 **Gemini Analysis:** Evidence verified. The attached documentation matches the permit requirements for the city. Proceed with installation scheduling.")

def view_head_of_bd():
    st.header("👔 Head of BD Dashboard")
    # Reduced for brevity, keep the same as previous versions.
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
