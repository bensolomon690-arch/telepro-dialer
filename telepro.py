import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. EXECUTIVE THEME (Bright & High-Contrast) ---
st.set_page_config(page_title="Solomon Executive Pro", layout="wide")
DB_FILE = 'telecaller_master_db.csv'

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #1E1E1E; }
    [data-testid="stSidebar"] { background-color: #F8F9FA !important; border-right: 1px solid #E9ECEF; }
    h1, h2, h3 { color: #003366 !important; font-weight: 700 !important; }
    .stButton>button { background-color: #003366; color: white; border-radius: 6px; font-weight: 600; width: 100%; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SECURITY GATEWAY ---
if 'auth' not in st.session_state: st.session_state['auth'] = False

def login():
    st.markdown("<h1 style='text-align: center;'>🏛️ Solomon Empire Access</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        u_id = st.text_input("👤 Identity (e.g., Ben)")
        u_pin = st.text_input("🔑 PIN", type="password")
        if st.button("Authorize Access"):
            if u_pin == "123456" and u_id.lower() == "ben":
                st.session_state['auth'] = True
                st.session_state['role'] = "Managing Director"
                st.rerun()
            elif u_pin == "0000":
                st.session_state['auth'] = True
                st.session_state['role'] = "Telecaller"
                st.rerun()
            else: st.error("Access Denied")
    st.stop()

if not st.session_state['auth']: login()

# --- 3. DATA PERSISTENCE ---
def load_db(): return pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame()

# --- 4. NAVIGATION ---
st.sidebar.title("Telecall Pro v5.0")
if st.sidebar.button("🔐 Logout"):
    st.session_state.clear()
    st.rerun()

if st.session_state['role'] == "Managing Director":
    nav = st.sidebar.radio("Command Center", ["📊 Stats", "📥 Sync Leads", "🎯 Call Station"])
else:
    nav = st.sidebar.radio("Staff Station", ["📥 Sync Leads", "🎯 Call Station"])

# --- 5. FUNCTIONAL PAGES ---
if nav == "📊 Stats":
    st.header("📊 Real-Time Operations")
    df = load_db()
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Clients", len(df))
        c2.metric("Completed", len(df[df['Status'] == 'Completed']))
        c3.metric("Pending", len(df[df['Status'] == 'Pending']))
        # FIXED CHART: Simple and error-free
        st.subheader("Status Summary")
        st.bar_chart(df['Status'].value_counts())
    else: st.info("Database is empty.")

elif nav == "📥 Sync Leads":
    st.header("📥 Data Synchronization")
    up = st.file_uploader("Upload Excel/CSV", type=['csv', 'xlsx'])
    if up:
        new_df = pd.read_csv(up) if up.name.endswith('.csv') else pd.read_excel(up)
        new_df.columns = new_df.columns.str.strip().str.upper()
        # SMART MAPPING: Fixes the "None" column error
        map_cols = {'CLIENT NAME':'Name','NAME':'Name','CLIENT CODE':'ID','MOBILE':'Number','NUMBER':'Number','CONTACT':'Number'}
        new_df = new_df.rename(columns=map_cols)
        for c in ['Status', 'Notes']:
            if c not in new_df.columns: new_df[c] = 'Pending' if c == 'Status' else ''
        st.dataframe(new_df.head(5))
        if st.button("🔥 Finalize Sync"):
            pd.concat([load_db(), new_df], ignore_index=True).to_csv(DB_FILE, index=False)
            st.success("Master Database Updated.")

elif nav == "🎯 Call Station":
    st.header("🎯 Active Dialer Terminal")
    df = load_db()
    if not df.empty:
        search = st.text_input("🔍 Search Client Name or ID")
        if search: df = df[df['Name'].astype(str).str.contains(search, case=False) | df['ID'].astype(str).str.contains(search)]
        
        # EDITABLE TABLE: With unique key for saving
        edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic", key="v5_dialer")
        
        # SAVE BUTTON: This is what you were missing
        if st.button("💾 SAVE ALL PROGRESS"):
            master_df = load_db()
            # Update the original master file with your new edits
            master_df.update(edited_df)
            master_df.to_csv(DB_FILE, index=False)
            st.success("Data successfully saved to server! You can now switch pages.")
    else: st.warning("No leads found.")
