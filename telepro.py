import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime
import plotly.express as px

# --- 1. GLOBAL EMPIRE CONFIGURATION ---
st.set_page_config(
    page_title="Solomon Executive Pro",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants for file storage
DB_FILE = 'telecaller_master_db.csv'
AUDIT_FILE = 'empire_audit_log.csv'
ADMIN_CODE = "123456"
STAFF_CODE = "0000"

# --- 2. EXECUTIVE BRANDING & THEME (NO BLACK BACKGROUND) ---
st.markdown("""
    <style>
    /* Main Background: Pure Professional White */
    .stApp { background-color: #FFFFFF; color: #1E1E1E; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* Sidebar Styling: Soft Executive Gray */
    [data-testid="stSidebar"] { background-color: #F8F9FA !important; border-right: 1px solid #E9ECEF; }
    
    /* Executive Card Styling */
    .executive-card { background-color: #FFFFFF; padding: 25px; border-radius: 12px; border: 1px solid #DEE2E6; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; }
    
    /* Button Styling: Deep Navy Blue */
    .stButton>button { background-color: #003366; color: white; border-radius: 6px; border: none; font-weight: 600; padding: 0.5rem 1rem; transition: all 0.3s ease; width: 100%; }
    .stButton>button:hover { background-color: #002244; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    
    /* Header Styling */
    h1, h2, h3 { color: #003366 !important; font-weight: 700 !important; }
    
    /* Metrics Styling */
    [data-testid="stMetricValue"] { color: #003366 !important; font-weight: bold !important; }
    
    /* Data Editor Styling */
    .stDataEditor { border: 1px solid #DEE2E6; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION & SECURITY ENGINE ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = None

def log_event(action):
    """Records every major action in the empire audit trail."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user = st.session_state.get('username', 'Unknown')
    new_log = pd.DataFrame([{"Timestamp": timestamp, "User": user, "Action": action}])
    new_log.to_csv(AUDIT_FILE, mode='a', header=not os.path.exists(AUDIT_FILE), index=False)

# --- 4. THE REDESIGNED LOGIN PORTAL ---
def show_login():
    st.markdown("<h1 style='text-align: center;'>🏛️ Solomon Empire Access Control</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6C757D;'>Secure Terminal for Managing Director & Authorized Personnel</p>", unsafe_allow_html=True)
    
    _, center_col, _ = st.columns([1, 1.2, 1])
    
    with center_col:
        st.markdown("<div class='executive-card'>", unsafe_allow_html=True)
        login_id = st.text_input("👤 System Identity", placeholder="Enter ID (e.g., Ben)")
        security_pin = st.text_input("🔑 Security PIN", type="password", placeholder="••••••")
        
        if st.button("Authorize Entry"):
            if security_pin == ADMIN_CODE and login_id.lower() == "ben":
                st.session_state['authenticated'] = True
                st.session_state['user_role'] = "Managing Director"
                st.session_state['username'] = "Ben Solomon"
                log_event("MD Login Successful")
                st.success("Authorized: Welcome, Managing Director.")
                time.sleep(1)
                st.rerun()
            elif security_pin == STAFF_CODE:
                st.session_state['authenticated'] = True
                st.session_state['user_role'] = "Telecaller"
                st.session_state['username'] = login_id if login_id else "Staff_Agent"
                log_event(f"Staff Login: {st.session_state['username']}")
                st.success(f"Authorized: System Active for {st.session_state['username']}")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Access Refused: Credentials Invalid")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

if not st.session_state['authenticated']:
    show_login()

# --- 5. DATA PERSISTENCE LAYER ---
def load_empire_db():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame()

def save_empire_db(df):
    df.to_csv(DB_FILE, index=False)

# --- 6. SIDEBAR NAVIGATION & EXECUTIVE TOOLS ---
st.sidebar.markdown(f"### 👤 {st.session_state['username']}")
st.sidebar.markdown(f"**Level:** {st.session_state['user_role']}")
st.sidebar.divider()

# Navigation logic
if st.session_state['user_role'] == "Managing Director":
    nav_options = ["📊 Live Intelligence", "📥 Client Sync", "🎯 Dialer Station", "📜 Audit Trail", "⚙️ System Control"]
else:
    nav_options = ["📥 Client Sync", "🎯 Dialer Station"]

page = st.sidebar.radio("Navigate System", nav_options)

if st.sidebar.button("🔐 End Session"):
    log_event("Session Ended Manually")
    st.session_state.clear()
    st.rerun()

# --- 7. PAGE: LIVE INTELLIGENCE (DASHBOARD) ---
if page == "📊 Live Intelligence":
    st.header("📊 Real-Time Operations Overview")
    df = load_empire_db()
    
    if not df.empty:
        # High-level Metrics Row
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Total Clients", len(df))
        with c2: st.metric("Completed", len(df[df['Status'] == 'Completed']))
        with c3: st.metric("Pending", len(df[df['Status'] == 'Pending']))
        with c4: 
            conv = (len(df[df['Status'] == 'Completed']) / len(df) * 100) if len(df)>0 else 0
            st.metric("Success Rate", f"{conv:.1f}%")
        
        # Charts Row
        st.divider()
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Call Status Volume")
            status_df = df['Status'].value_counts().reset_index()
            fig = px.bar(status_df, x='index', y='Status', labels={'index':'Status', 'Status':'Count'},
                         color_discrete_sequence=['#003366'])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            st.subheader("Progress Timeline")
            st.write("Tracking lead activity across system synchronization events.")
            st.line_chart(df['Status'].value_counts())
    else:
        st.info("The database is empty. Please synchronize client leads.")

# --- 8. PAGE: CLIENT SYNC (UPLOAD) ---
elif page == "📥 Client Sync":
    st.header("📥 Client Data Synchronization")
    st.write("Merge new office Excel/CSV files into the master Solomon database.")
    
    file_upload = st.file_uploader("Select Business Source File", type=['xlsx', 'csv'])
    
    if file_upload:
        if file_upload.name.endswith('.csv'):
            new_df = pd.read_csv(file_upload)
        else:
            new_df = pd.read_excel(file_upload)
        
        # Smart Header Mapping (Solves the "None" issues from earlier trials)
        new_df.columns = new_df.columns.str.strip().str.upper()
        mapping = {
            'CLIENT NAME': 'Name', 'NAME': 'Name',
            'CLIENT CODE': 'ID', 'ID': 'ID',
            'MOBILE': 'Number', 'NUMBER': 'Number', 'PHONE': 'Number'
        }
        new_df = new_df.rename(columns=mapping)
        
        # Ensure standard empire columns exist
        for c in ['Status', 'Notes', 'Last_Call']:
            if c not in new_df.columns:
                new_df[c] = 'Pending' if c == 'Status' else 'None'
        
        st.markdown("<div class='executive-card'>", unsafe_allow_html=True)
        st.subheader(f"Preview: {len(new_df)} New Records")
        st.dataframe(new_df.head(10), use_container_width=True)
        
        if st.button("🔥 Confirm Database Synchronization"):
            current_db = load_empire_db()
            final_db = pd.concat([current_db, new_df], ignore_index=True)
            save_empire_db(final_db)
            log_event(f"Imported {len(new_df)} leads")
            st.success("Empire Records Successfully Synchronized.")
        st.markdown("</div>", unsafe_allow_html=True)

# --- 9. PAGE: DIALER STATION (THE CORE WORKSPACE) ---
elif page == "🎯 Dialer Station":
    st.header("🎯 Active Dialer Terminal")
    df = load_empire_db()
    
    if not df.empty:
        # Search & Quick Filtering
        col_s1, col_s2 = st.columns([2, 1])
        with col_s1: 
            search = st.text_input("🔍 Search Database (Name, ID, or Phone)")
        with col_s2:
            status_filter = st.selectbox("Status Filter", ["All", "Pending", "Follow-up", "Completed", "Not Connected"])
        
        # Processing filters
        filtered_df = df.copy()
        if search:
            filtered_df = filtered_df[filtered_df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df['Status'] == status_filter]
            
        st.write(f"Showing **{len(filtered_df)}** Actionable Leads:")
        
        # THE EDITABLE CORE - Enhanced for visibility
        edited_leads = st.data_editor(
            filtered_df, 
            use_container_width=True, 
            num_rows="dynamic",
            key="empire_editor_v5"
        )
        
        st.divider()
        col_act1, col_act2 = st.columns([1, 1.5])
        with col_act1:
            if st.button("💾 Permanently Save Progress"):
                # Align edits back to main DB
                df.update(edited_leads)
                save_empire_db(df)
                log_event("Batch calling progress saved")
                st.success("Changes Locked to Server.")
        with col_act2:
            st.info("💡 Pro-Tip: Update 'Status' to 'Completed' to remove leads from the 'Pending' list.")
    else:
        st.warning("No leads found. Please head to 'Client Sync' to upload your data.")

# --- 10. PAGE: AUDIT TRAIL (MD ONLY) ---
elif page == "📜 Audit Trail":
    st.header("📜 System Audit & Security Trail")
    if os.path.exists(AUDIT_FILE):
        audit_log = pd.read_csv(AUDIT_FILE)
        st.dataframe(audit_log.sort_values(by='Timestamp', ascending=False), use_container_width=True)
        st.download_button("Export Security Log", audit_log.to_csv(), "security_audit.csv")
    else:
        st.info("No security events recorded yet.")

# --- 11. PAGE: SYSTEM CONTROL (MD ONLY) ---
elif page == "⚙️ System Control":
    st.header("⚙️ Administrative System Control")
    st.warning("These operations are permanent and impact the entire database.")
    
    col_reset, col_info = st.columns(2)
    with col_reset:
        st.subheader("Database Management")
        if st.button("🚨 Wipe Entire Database"):
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
                log_event("MASTER DATABASE WIPED")
                st.success("Database erased successfully.")
                st.rerun()
    with col_info:
        st.subheader("Empire Statistics")
        st.write(f"**Storage Path:** {DB_FILE}")
        st.write(f"**Security Protocol:** PIN Authorization")
        st.write(f"**Last Sync:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
