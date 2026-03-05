import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(page_title="Telecall Pro - MD Portal", layout="wide")
DB_FILE = 'telecaller_database.csv'
LOG_FILE = 'system_audit.csv'

# Professional Dark Theme CSS
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .login-container { background-color: #1c1f26; padding: 30px; border-radius: 12px; border: 1px solid #3b3e45; }
    .stButton>button { background-color: #0066cc; color: white; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE MANAGING DIRECTOR ACCESS PORTAL ---
if 'access_granted' not in st.session_state:
    st.session_state['access_granted'] = False

def login_portal():
    st.markdown("<h1 style='text-align: center; color: #4dabf7;'>📞 Telecall Pro Access Control</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 2, 1])
    with col:
        with st.container():
            st.markdown("<div class='login-container'>", unsafe_allow_html=True)
            user = st.text_input("👤 System User ID")
            code = st.text_input("🔑 Security PIN", type="password")
            if st.button("Authorize Login"):
                if code == "123456" and user.lower() == "ben":
                    st.session_state['access_granted'] = True
                    st.session_state['role'] = "Managing Director"
                    st.rerun()
                elif code == "0000":
                    st.session_state['access_granted'] = True
                    st.session_state['role'] = "Telecaller"
                    st.session_state['user_name'] = user if user else "Staff"
                    st.rerun()
                else:
                    st.error("Access Denied: Check Credentials")
            st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

if not st.session_state['access_granted']:
    login_portal()

# --- 3. CORE SYSTEM INTERFACE ---
st.sidebar.title("🛠️ System Control")
st.sidebar.subheader(f"Role: {st.session_state['role']}")
if st.sidebar.button("🔐 End Session"):
    st.session_state.clear()
    st.rerun()

# MD gets full access; Telecaller gets limited tools
if st.session_state['role'] == "Managing Director":
    nav = st.sidebar.radio("Command Center", ["📊 Live Stats", "📥 Import Leads", "🎯 Calling Station", "📜 Audit Trail"])
else:
    nav = st.sidebar.radio("Staff Station", ["📥 Import Leads", "🎯 Calling Station"])

# Data Helper
def get_db(): return pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame()

# --- 4. FUNCTIONAL PAGES ---
if nav == "📊 Live Stats":
    st.header("📊 Real-Time Operations Overview")
    df = get_db()
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Records", len(df))
        c2.metric("Success Rate", f"{(len(df[df['Status'] == 'Completed'])/len(df)*100):.1f}%" if len(df)>0 else "0%")
        c3.metric("Follow-ups", len(df[df['Status'] == 'Follow-up']))
        st.bar_chart(df['Status'].value_counts())
    else: st.info("Database is currently empty.")

elif nav == "📥 Import Leads":
    st.header("📥 Bulk Lead Synchronization")
    up = st.file_uploader("Drop Excel/CSV Here", type=['csv', 'xlsx'])
    if up:
        new_df = pd.read_csv(up) if up.name.endswith('.csv') else pd.read_excel(up)
        new_df.columns = new_df.columns.str.strip().str.upper()
        new_df = new_df.rename(columns={'CLIENT NAME':'Name','CLIENT CODE':'ID','MOBILE':'Number','NUMBER':'Number'})
        for c in ['Status', 'Notes']:
            if c not in new_df.columns: new_df[c] = 'Pending' if c == 'Status' else ''
        if st.button("🔥 Confirm Synchronization"):
            pd.concat([get_db(), new_df], ignore_index=True).to_csv(DB_FILE, index=False)
            st.success("Master Records Updated Successfully.")

elif nav == "🎯 Calling Station":
    st.header("🎯 Active Dialer Terminal")
    df = get_db()
    if not df.empty:
        search = st.text_input("🔍 Filter by Client Name/ID")
        if search: df = df[df['Name'].astype(str).str.contains(search, case=False) | df['ID'].astype(str).str.contains(search)]
        edited = st.data_editor(df, use_container_width=True, num_rows="dynamic", key="dialer_v4")
        if st.button("💾 Lock All Updates"):
            df.update(edited)
            df.to_csv(DB_FILE, index=False)
            st.success("Progress Synchronized to Server.")
    else: st.warning("No active leads found.")

elif nav == "📜 Audit Trail":
    st.header("📜 System Audit Trail")
    if os.path.exists(LOG_FILE): st.dataframe(pd.read_csv(LOG_FILE).tail(15), use_container_width=True)
    else: st.info("No system events recorded yet.")
