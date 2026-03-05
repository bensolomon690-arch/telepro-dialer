import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. EXECUTIVE THEME & CONFIG ---
st.set_page_config(page_title="Solomon Executive Pro", layout="wide")
DB_FILE = 'telecaller_master_db.csv'
AUDIT_FILE = 'system_audit_log.csv'

# Clean Professional Theme (No Black Background)
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #1E1E1E; }
    [data-testid="stSidebar"] { background-color: #F8F9FA !important; border-right: 1px solid #E9ECEF; }
    .executive-card { background-color: #FFFFFF; padding: 20px; border-radius: 10px; border: 1px solid #DEE2E6; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    h1, h2, h3 { color: #003366 !important; }
    .stButton>button { background-color: #003366; color: white; border-radius: 6px; font-weight: 600; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTHENTICATION ENGINE ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

def login_portal():
    st.markdown("<h1 style='text-align: center;'>🏛️ Solomon Empire Access</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<div class='executive-card'>", unsafe_allow_html=True)
        u_id = st.text_input("👤 Management Identity")
        u_pin = st.text_input("🔑 Security PIN", type="password")
        if st.button("Authorize Access"):
            if u_pin == "123456" and u_id.lower() == "ben":
                st.session_state['auth'] = True
                st.session_state['role'] = "Managing Director"
                st.session_state['user'] = "Ben Solomon"
                st.rerun()
            elif u_pin == "0000":
                st.session_state['auth'] = True
                st.session_state['role'] = "Telecaller"
                st.session_state['user'] = u_id if u_id else "Staff"
                st.rerun()
            else:
                st.error("Invalid Credentials")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

if not st.session_state['auth']:
    login_portal()

# --- 3. DATA PERSISTENCE ---
def load_db(): return pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame()
def save_db(df): df.to_csv(DB_FILE, index=False)

# --- 4. NAVIGATION ---
st.sidebar.markdown(f"### 👤 {st.session_state['user']}")
st.sidebar.markdown(f"**Role:** {st.session_state['role']}")
if st.sidebar.button("🔐 Logout"):
    st.session_state.clear()
    st.rerun()

if st.session_state['role'] == "Managing Director":
    nav = st.sidebar.radio("Command Center", ["📊 Intelligence", "📥 Sync Leads", "🎯 Call Station", "📜 Audit Log"])
else:
    nav = st.sidebar.radio("Staff Station", ["📥 Sync Leads", "🎯 Call Station"])

# --- 5. PAGES ---
if nav == "📊 Intelligence":
    st.header("📊 Real-Time Operations Intelligence")
    df = load_db()
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Clients", len(df))
        c2.metric("Completed", len(df[df['Status'] == 'Completed']))
        c3.metric("Follow-ups", len(df[df['Status'] == 'Follow-up']))
        
        # Fixed Chart Logic (Solves image_32368a error)
        st.subheader("Call Status Breakdown")
        status_counts = df['Status'].value_counts()
        st.bar_chart(status_counts)
    else: st.info("Database is empty. Please synchronize leads.")

elif nav == "📥 Sync Leads":
    st.header("📥 Client Data Synchronization")
    up = st.file_uploader("Upload Excel/CSV Source", type=['csv', 'xlsx'])
    if up:
        new_df = pd.read_csv(up) if up.name.endswith('.csv') else pd.read_excel(up)
        new_df.columns = new_df.columns.str.strip().str.upper()
        # Smart Map (Solves image_338916 "None" error)
        map_cols = {'CLIENT NAME':'Name','NAME':'Name','CLIENT CODE':'ID','MOBILE':'Number','NUMBER':'Number','CONTACT':'Number'}
        new_df = new_df.rename(columns=map_cols)
        for c in ['Status', 'Notes']:
            if c not in new_df.columns: new_df[c] = 'Pending' if c == 'Status' else ''
        
        st.dataframe(new_df.head(10))
        if st.button("🔥 Finalize Sync"):
            pd.concat([load_db(), new_df], ignore_index=True).to_csv(DB_FILE, index=False)
            st.success("Master Records Updated.")

elif nav == "🎯 Call Station":
    st.header("🎯 Active Dialer Terminal")
    df = load_db()
    if not df.empty:
        search = st.text_input("🔍 Search Client Name or ID")
        if search: df = df[df['Name'].astype(str).str.contains(search, case=False) | df['ID'].astype(str).str.contains(search)]
        
        # Editable Station
        edited = st.data_editor(df, use_container_width=True, num_rows="dynamic", key="dialer_vFinal")
        if st.button("💾 Save All Progress"):
            df.update(edited)
            save_db(df)
            st.success("Progress Saved to Server.")
    else: st.warning("No leads found.")

elif nav == "📜 Audit Log":
    st.header("📜 System Audit History")
    if os.path.exists(AUDIT_FILE): st.dataframe(pd.read_csv(AUDIT_FILE).tail(20), use_container_width=True)
    else: st.info("No audit logs recorded yet.")
