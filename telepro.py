import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. EXECUTIVE THEME & SYSTEM CONFIG ---
st.set_page_config(page_title="Solomon Empire Pro", layout="wide")
DB_FILE = 'telecaller_master_db.csv'

# Professional Executive Theme (White & Navy Blue)
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #1E1E1E; }
    [data-testid="stSidebar"] { background-color: #F8F9FA !important; border-right: 1px solid #E9ECEF; }
    h1, h2, h3 { color: #003366 !important; font-weight: 700 !important; }
    .stButton>button { background-color: #003366; color: white; border-radius: 6px; font-weight: 600; width: 100%; height: 3.5em; }
    .stDataFrame { border: 1px solid #DEE2E6; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE MASTER STATUS LIST (All your custom options) ---
EMPIRE_STATUSES = [
    "Pending", "Completed", "Bending", "no incoming call", "out off service", "no idea", 
    "FOLLOWINGS", "NOT ANSWERING", "CUT THE CALL", "STOCK INVESTMENT / SELLING",
    "insurance", "fno followings", "rnt followings", "re activation followings",
    "pre ipo followings", "visiting office", "switch off", "account opening followings",
    "no response", "mutual fund followings", "not interested", "payin followings"
]

# --- 3. SECURITY & AUTHENTICATION ---
if 'auth' not in st.session_state: st.session_state['auth'] = False

def login_portal():
    st.markdown("<h1 style='text-align: center;'>🏛️ Solomon Empire Access Portal</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        u_id = st.text_input("👤 System Identity (e.g., Ben)")
        u_pin = st.text_input("🔑 Security PIN", type="password")
        if st.button("Authorize Entry"):
            if u_pin == "123456" and u_id.lower() == "ben":
                st.session_state['auth'] = True
                st.session_state['role'] = "Managing Director"
                st.rerun()
            elif u_pin == "0000":
                st.session_state['auth'] = True
                st.session_state['role'] = "Telecaller"
                st.rerun()
            else: st.error("Access Refused")
    st.stop()

if not st.session_state['auth']: login_portal()

# --- 4. DATA PERSISTENCE ENGINE ---
def load_db(): 
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame()

def save_db(df):
    df.to_csv(DB_FILE, index=False)

# --- 5. EXECUTIVE NAVIGATION ---
st.sidebar.title("Solomon Pro v7.0")
if st.sidebar.button("🔐 Logout System"):
    st.session_state.clear()
    st.rerun()

if st.session_state['role'] == "Managing Director":
    nav = st.sidebar.radio("Command Center", ["📊 Real-Time Stats", "📥 Sync Leads", "🎯 Call Station"])
else:
    nav = st.sidebar.radio("Staff Station", ["📥 Sync Leads", "🎯 Call Station"])

# --- 6. PAGE LOGIC ---
if nav == "📊 Real-Time Stats":
    st.header("📊 Real-Time Operations Intelligence")
    df = load_db()
    if not df.empty:
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Empire Leads", len(df))
        m2.metric("Completed", len(df[df['Status'] == 'Completed']))
        m3.metric("Critical Follow-ups", len(df[df['Status'].str.contains('followings|FOLLOWINGS', na=False)]))
        st.subheader("Performance Breakdown")
        st.bar_chart(df['Status'].value_counts())
    else: st.info("Database is empty. Please synchronize leads.")

elif nav == "📥 Sync Leads":
    st.header("📥 Bulk Data Synchronization")
    up = st.file_uploader("Upload Office Excel/CSV", type=['csv', 'xlsx'])
    if up:
        new_df = pd.read_csv(up) if up.name.endswith('.csv') else pd.read_excel(up)
        new_df.columns = new_df.columns.str.strip().str.upper()
        # SMART MAPPING
        map_cols = {'CLIENT NAME':'Name','NAME':'Name','CLIENT CODE':'ID','MOBILE':'Number','NUMBER':'Number','CURRENT STATUS':'Status','STATUS':'Status'}
        new_df = new_df.rename(columns=map_cols)
        for c in ['Status', 'Notes']:
            if c not in new_df.columns: new_df[c] = 'Pending' if c == 'Status' else ''
        st.dataframe(new_df.head(10))
        if st.button("🔥 Finalize Synchronize"):
            save_db(pd.concat([load_db(), new_df], ignore_index=True))
            st.success("Empire Records Successfully Updated.")

elif nav == "🎯 Call Station":
    st.header("🎯 Active Dialer Station")
    df = load_db()
    if not df.empty:
        # Filter Bar
        s_filter = st.radio("Select View", ["All", "Pending", "Completed", "Follow-ups", "Not Interested"], horizontal=True)
        
        display_df = df.copy()
        if s_filter == "Pending": display_df = display_df[display_df['Status'] == 'Pending']
        elif s_filter == "Completed": display_df = display_df[display_df['Status'] == 'Completed']
        elif s_filter == "Follow-ups": display_df = display_df[display_df['Status'].str.contains('followings|FOLLOWINGS', na=False)]
        elif s_filter == "Not Interested": display_df = display_df[display_df['Status'] == 'not interested']
        
        search = st.text_input("🔍 Search Database (Name or ID)")
        if search: display_df = display_df[display_df['Name'].astype(str).str.contains(search, case=False)]
        
        # EDITABLE TABLE WITH DROPDOWN FIX
        st.write(f"Displaying {len(display_df)} clients:")
        edited_df = st.data_editor(
            display_df, 
            use_container_width=True, 
            num_rows="dynamic",
            column_config={
                "Status": st.column_config.SelectboxColumn(
                    "Call Status",
                    help="Select the outcome of the call",
                    options=EMPIRE_STATUSES,
                    required=True,
                )
            },
            key="v7_editor"
        )
        
        # CRITICAL SAVE BUTTON
        if st.button("💾 SAVE ALL PROGRESS & REFRESH"):
            # This logic merges the edits back to the main DB file
            master_df = load_db()
            master_df.update(edited_df)
            save_db(master_df)
            st.success("Progress Saved! Lead will move to the correct list upon refresh.")
            st.rerun() # Forces the radio filter to update immediately
    else: st.warning("No leads found.")
