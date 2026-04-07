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

# --- MOCK DATABASE (SOLAR + OPS PRE-LOAD) ---
def init_db():
    st.session_state.crm_deals = pd.DataFrame({
        'Deal_ID': ['D-101', 'D-102', 'D-103', 'D-104', 'D-105'],
        'Client': ['SunCity Commercial Array', 'Oakridge HOA Residential', 'GreenTech Warehouse', 'Horizon Farms Microgrid', 'Metro Park Facilities'],
        'Rep': ['Monique Bruce', 'Alex Rivera', 'Sarah Chen', 'David Thorne', 'Elena Rostova'],
        'Stage': ['Negotiation', 'Discovery', 'Closed Won', 'Prospecting', 'Proposal'],
        'Value': [350000, 120000, 850000, 420000, 210000] 
    })
    
    # Notice the Timeline uses pd.to_datetime().dt.date to ensure it is a native Date object
    st.session_state.ops_tasks = pd.DataFrame({
        'Task_ID': ['T-01', 'T-02', 'T-03', 'T-04', 'T-05'],
        'Deal_ID': ['D-103', 'D-103', 'D-101', 'D-105', 'Internal'],
        'Task Name': ['Submit City Permits', 'Order Inverters', 'Draft HOA Proposal', 'Site Shading Analysis', 'Update Sales Deck'],
        'Owner': ['Ops Team', 'Procurement', 'Alex Rivera', 'Engineering', 'Monique Bruce'],
        'Status': ['Working on it', 'Done', 'Stuck', 'To Do', 'Working on it'],
        'Priority': ['High', 'Critical', 'Medium', 'High', 'Low'],
        'Timeline': pd.to_datetime(['2026-04-10', '2026-04-05', '2026-04-12', '2026-04-15', '2026-04-20']).date
    })

    st.session_state.bd_view = "overview" 

    st.session_state.marketing_data = pd.DataFrame({
        "Channel": ["Google Local Service Ads", "Door-to-Door Canvassing", "Facebook Lead Forms", "Commercial Outbound"],
        "Traffic/Volume": ["15k impressions", "800 doors knocked", "12k clicks", "5k emails sent"],
        "Leads Generated": [180, 45, 310, 85],
        "AI Health Score (%)": [88, 71, 62, 78] 
    })

    st.session_state.interactions = [
        {
            "Type": "Call", "Direction": "Inbound", "Rep": "Sarah Chen", "Deal_ID": "D-103",
            "Content": "Customer was concerned about roof warranty voiding. Sarah cleanly explained our flashing techniques and provided the engineering documentation, securing the verbal agreement.",
            "Analysis": {
                "kpi_scores": {"clarity": 9, "confidence": 9, "objection_handling": 9, "closing": 8},
                "key_takeaways": ["Excellent technical knowledge", "Strong trust building"],
                "manager_coaching_playbook": "Sarah is performing exceptionally. Consider having her lead the next team meeting on objection handling regarding roof warranties."
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
    
    # Top Level Ops Metrics
    stuck_tasks = len(st.session_state.ops_tasks[st.session_state.ops_tasks['Status'] == 'Stuck'])
    completed_tasks = len(st.session_state.ops_tasks[st.session_state.ops_tasks['Status'] == 'Done'])
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Active Projects", len(st.session_state.ops_tasks))
    c2.metric("Tasks Completed", completed_tasks)
    c3.metric("Blocked/Stuck Tasks", stuck_tasks, delta_color="inverse" if stuck_tasks > 0 else "normal", delta=f"{stuck_tasks} Needs Attention")

    st.divider()
    st.subheader("Active Tasks (Interactive Board)")
    
    # FAILSAFE: This forcefully converts any cached string dates from your broken session into actual Date objects
    # so Streamlit doesn't crash when rendering the column.
    st.session_state.ops_tasks['Timeline'] = pd.to_datetime(st.session_state.ops_tasks['Timeline']).dt.date
    
    edited_df = st.data_editor(
        st.session_state.ops_tasks,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "Status": st.column_config.SelectboxColumn(
                "Status",
                help="Current task status",
                options=["To Do", "Working on it", "Stuck", "Done"],
                required=True,
            ),
            "Priority": st.column_config.SelectboxColumn(
                "Priority",
                options=["Low", "Medium", "High", "Critical"],
                required=True,
            ),
            "Timeline": st.column_config.DateColumn(
                "Timeline",
                format="YYYY-MM-DD",
            )
        }
    )
    
    st.session_state.ops_tasks = edited_df
    st.info("💡 **Tip:** Double click any cell to edit it, or click the '+' at the bottom to add a new task, just like Monday.com.")

def view_head_of_bd():
    st.header("👔 Head of BD Dashboard (Team Overview)")
    
    total_calls = sum(1 for i in st.session_state.interactions if i['Type'] == 'Call')
    clean_values = st.session_state.crm_deals['Value'].astype(str).str.replace(r'[$,]', '', regex=True)
    total_pipeline = pd.to_numeric(clean_values, errors='coerce').sum()
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Comm Logs", len(st.session_state.interactions))
    m2.metric("Active Solar Pipeline", f"${total_pipeline:,.0f}")
    m3.metric("AI Sales Rating", "82.5%")
    
    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🎯 Targeted AI Coaching")
        for log in reversed(st.session_state.interactions):
            with st.expander(f"Coach {log['Rep']} - {log['Type']}"):
                st.write(log['Analysis']['manager_coaching_playbook'])

    with c2:
        st.subheader("🗄️ Team Comm Archive")
        for log in reversed(st.session_state.interactions):
            with st.expander(f"🎙️ {log['Rep']} (Deal {log['Deal_ID']})"):
                st.write(log['Content'])

# --- MAIN APP ROUTING ---
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Select View:", ["Sales Rep Hub", "Operations Board (Monday.com Clone)", "Head of BD Dashboard"])
st.sidebar.divider()

if st.sidebar.button("🔄 Reset Database / Clear Cache"):
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
