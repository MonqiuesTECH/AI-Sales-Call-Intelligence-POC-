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
            "Type": "Call", "Direction": "Outbound", "Rep": "Elena Rostova", "Deal_ID": "D-105",
            "Content": "Prospect: 'I read that the solar tax credit is only 30%.' \n\nElena: 'No, listen to me, if you sign today I guarantee you a 100% write-off. My buddy does taxes. Just sign the DocuSign right now.'",
            "Analysis": {
                "kpi_scores": {"clarity": 2, "confidence": 9, "objection_handling": 1, "closing": 1},
                "key_takeaways": ["Violated federal compliance", "Aggressive tone"],
                "manager_coaching_playbook": "🚨 CRITICAL: Elena provided fraudulent tax advice. Halt outbound privileges."
            }
        },
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

    # New: CEO Financial & Agent State
    st.session_state.ceo_metrics = {
        "ARR": 10400000,
        "Cash_Runway_Months": 14,
        "Burn_Rate": 450000,
        "Active_Agents": 3
    }
    
    st.session_state.active_view = "CEO Command Center"

# --- BULLETPROOF INITIALIZATION ---
required_keys = ['crm_deals', 'ops_tasks', 'marketing_data', 'interactions', 'ceo_metrics', 'active_view']
for key in required_keys:
    if key not in st.session_state:
        init_db()
        break

# --- AI PROCESSING LOGIC ---
def analyze_interaction_with_ai(content, rep_name, type="call"):
    prompt = f"""Analyze this {type} for {rep_name}. Output valid JSON: {{"kpi_scores": {{"clarity": int, "confidence": int, "objection_handling": int, "closing": int}}, "key_takeaways": ["point 1"], "manager_coaching_playbook": "Actionable advice."}} Text: {content}"""
    response = client.chat.completions.create(
        model="llama3-8b-8192", messages=[{"role": "user", "content": prompt}], temperature=0.1, response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

# --- VIEWS ---

def view_ceo_command_center():
    st.header("🏢 CEO Command Center")
    st.markdown("The Company Brain: Cross-departmental synthesis powered by Gemini OS.")
    
    # 1. TOP LEVEL FINANCIALS (CFO Hub Preview)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Projected ARR", f"${st.session_state.ceo_metrics['ARR']:,.0f}", "+12% YoY")
    c2.metric("Cash Runway", f"{st.session_state.ceo_metrics['Cash_Runway_Months']} Months", "-1 Month")
    c3.metric("Total Pipeline", "$1,950,000")
    c4.metric("Ops Delivery Health", "80%", "-2 Stuck Projects", delta_color="inverse")
    
    st.divider()

    # 2. AUTONOMOUS AGENT MONITORING
    st.subheader("🤖 Autonomous Workspace Agents (Live Status)")
    st.markdown("Agents are currently monitoring Google Workspace and internal databases.")
    
    a1, a2, a3 = st.columns(3)
    with a1:
        st.info("**📧 Inbound Lead Parser**\n\nStatus: *Active*\n\nProcessed 42 emails today. Created 3 new CRM records.")
    with a2:
        st.warning("**🏗️ Ops Permitting Agent**\n\nStatus: *Blocked*\n\nWaiting on City of Chesapeake API response for Deal D-103.")
    with a3:
        st.error("**🚨 Compliance Monitor**\n\nStatus: *Active Alert*\n\nFlagged Elena Rostova's call for illegal tax advice.")

    st.divider()

    # 3. EXECUTIVE SYNTHESIS (The real power of the 2026 platform)
    st.subheader("🧠 Gemini Executive Synthesis")
    st.markdown("Cross-departmental friction points identified by the Company Brain:")
    
    st.error("🚨 **Systemic Risk Detected (Sales vs. Ops):** Deal D-103 (GreenTech Warehouse) was marked 'Closed Won' by Sarah Chen, but the Operations Board shows 'Submit City Permits' is currently STUCK. Revenue recognition will be delayed. Recommend immediate COO intervention.")
    st.warning("⚠️ **Marketing vs. Sales Alignment:** Facebook Lead Forms are generating high volume (310 leads), but AI Sales Ratings for these leads average 45%. Sales is struggling to close low-intent social media leads. Recommend Marketing shift budget to Google Local Service Ads.")

def view_sales_rep():
    st.header("👤 Sales Representative Hub")
    st.dataframe(st.session_state.crm_deals, use_container_width=True, hide_index=True, column_config={"Value": st.column_config.NumberColumn("Value", format="$%d")})
    st.divider()
    
    st.subheader("🤖 Gemini Workspace Integration")
    st.markdown("Instead of manual entry, let the Gemini Agent scan your Gmail and calendar to log activity.")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        selected_rep = st.selectbox("Identify User", st.session_state.crm_deals['Rep'].unique())
        selected_deal = st.selectbox("Associate Deal", st.session_state.crm_deals[st.session_state.crm_deals['Rep'] == selected_rep]['Deal_ID'])
    
    with col2:
        if st.button("✨ Auto-Sync with Gemini (Gmail & Meet)", type="primary"):
            with st.spinner("Gemini is reading your Google Workspace inbox..."):
                # Simulating the agent finding an email
                mock_scraped_email = f"Hey {selected_rep}, thanks for the proposal. I have a few questions about the inverter warranties before we sign. Can we chat tomorrow?"
                analysis_data = analyze_interaction_with_ai(mock_scraped_email, selected_rep, type="email")
                
                st.session_state.interactions.append({
                    "Type": "Email", "Direction": "Inbound", "Rep": selected_rep, "Deal_ID": selected_deal, 
                    "Content": mock_scraped_email, "Analysis": analysis_data
                })
            st.success("Gemini found 1 relevant thread and automatically synced it to the CRM.")
            st.info(f"**Email Parsed:** {mock_scraped_email}")

def view_operations_board():
    st.header("📋 Operations & Project Board")
    st.markdown("Internal task management and post-sale project tracking.")
    
    stuck_tasks = len(st.session_state.ops_tasks[st.session_state.ops_tasks['Status'] == 'Stuck'])
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Active Projects", len(st.session_state.ops_tasks))
    c2.metric("Tasks Completed", len(st.session_state.ops_tasks[st.session_state.ops_tasks['Status'] == 'Done']))
    c3.metric("Blocked/Stuck Tasks", stuck_tasks, delta_color="inverse" if stuck_tasks > 0 else "normal", delta=f"{stuck_tasks} Needs Attention")

    st.divider()
    
    st.session_state.ops_tasks['Timeline'] = pd.to_datetime(st.session_state.ops_tasks['Timeline']).dt.date
    edited_df = st.data_editor(
        st.session_state.ops_tasks, use_container_width=True, hide_index=True, num_rows="dynamic",
        column_config={
            "Status": st.column_config.SelectboxColumn("Status", options=["To Do", "Working on it", "Stuck", "Done"], required=True),
            "Priority": st.column_config.SelectboxColumn("Priority", options=["Low", "Medium", "High", "Critical"], required=True),
            "Timeline": st.column_config.DateColumn("Timeline", format="YYYY-MM-DD")
        }
    )
    st.session_state.ops_tasks = edited_df

def view_head_of_bd():
    st.header("👔 Head of BD Dashboard")
    
    total_calls = sum(1 for i in st.session_state.interactions if i['Type'] == 'Call')
    clean_values = st.session_state.crm_deals['Value'].astype(str).str.replace(r'[$,]', '', regex=True)
    total_pipeline = pd.to_numeric(clean_values, errors='coerce').sum()
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Comm Logs Processed", len(st.session_state.interactions))
    m2.metric("Active Pipeline", f"${total_pipeline:,.0f}")
    m3.metric("AI Sales Rating", "82.5%")
    m4.metric("Critical Alerts", "1", delta="Elena Rostova", delta_color="inverse")
    
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🎯 Targeted AI Coaching")
        for log in st.session_state.interactions:
            icon = "🚨" if "CRITICAL" in log['Analysis']['manager_coaching_playbook'] else "💡"
            with st.expander(f"{icon} Coach {log['Rep']} - {log['Type']}"):
                st.write(log['Analysis']['manager_coaching_playbook'])

    with c2:
        st.subheader("🗄️ Team Comm Archive")
        for log in st.session_state.interactions:
            with st.expander(f"🎙️ {log['Rep']} (Deal {log['Deal_ID']})"):
                st.markdown(f"**Content:**\n\n*{log['Content']}*")

# --- MAIN APP ROUTING ---
st.sidebar.title("🧠 The Company Brain")

# Creating the profiles you mentioned
app_mode = st.sidebar.radio("Access Profile:", [
    "CEO Command Center",
    "Head of BD (Sales Hub)", 
    "Operations Director",
    "Sales Rep Terminal"
])
st.sidebar.divider()

if st.sidebar.button("🔄 Reset Global Database"):
    for key in required_keys:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# Router Logic
if app_mode == "CEO Command Center":
    view_ceo_command_center()
elif app_mode == "Sales Rep Terminal":
    view_sales_rep()
elif app_mode == "Operations Director":
    view_operations_board()
elif app_mode == "Head of BD (Sales Hub)":
    view_head_of_bd()
