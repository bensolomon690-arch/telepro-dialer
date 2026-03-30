import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Solomon telecaller Pro", layout="wide")
DB_FILE = 'telecaller_master_db.csv'

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #1E1E1E; }
    [data-testid="stSidebar"] { background-color: #F8F9FA !important; border-right: 1px solid #E9ECEF; }
    h1, h2, h3 { color: #003366 !important; font-weight: 700 !important; }
    .stButton>button { background-color: #003366; color: white; border-radius: 6px; font-weight: 600; width: 100%; height: 3.5em; }
    </style>
    """, unsafe_allow_html=True)

EMPIRE_STATUSES = [
    "Pending", "Completed", "Bending", "no incoming call", "out off service", 
    "no idea", "FOLLOWINGS", "NOT ANSWERING", "CUT THE CALL", 
    "STOCK INVESTMENT / SELLING", "insurance", "fno followings", 
    "rnt followings", "re activation followings", "pre ipo followings", 
    "visiting office", "switch off", "account opening followings", 
    "no response", "mutual fund followings", "not interested", "payin followings"
]

if 'auth' not in st.session_state: st.session_state['auth'] = False

def login():
    st.markdown("<h1 style='text-align: center;'>🏛️ Solomon Empire Access</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        u_id = st.text_input("👤 Identity (e.g., ben)")
        u_pin = st.text_input("🔑 PIN", type="password")
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

if not st.session_state['auth']: login()

def load_db(): 
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        # CRITICAL: Fixes image_968da6.png AttributeError
        df['Status'] = df['Status'].fillna('Pending').astype(str)
        return df
    return pd.DataFrame()

def save_db(df): df.to_csv(DB_FILE, index=False)

st.sidebar.title("Telecall Pro v10.0")
if st.sidebar.button("🔐 Logout System"):
    st.session_state.clear()
    st.rerun()

nav = st.sidebar.radio("Command Center", ["📊 Dashboard", "📥 Import Leads", "🎯 Calling Station"])

if nav == "📊 Dashboard":
    st.header("📊 Intelligence Dashboard")
    df = load_db()
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        # Version-Safe Metrics (Removed 'border' to prevent errors)
        c1.metric("Total Empire Leads", len(df))
        c2.metric("Completed Calls", len(df[df['Status'] == 'Completed']))
        # Logic to find all types of followings
        f_count = len(df[df['Status'].str.lower().str.contains('follow', na=False)])
        c3.metric("Total Follow-ups", f_count)
        
        st.subheader("Performance Breakdown")
        st.bar_chart(df['Status'].value_counts())
    else: st.info("Database is empty. Please upload leads.")

elif nav == "📥 Import Leads":
    st.header("📥 Bulk Synchronization")
    up = st.file_uploader("Upload Excel/CSV", type=['csv', 'xlsx'])
    if up:
        new_df = pd.read_csv(up) if up.name.endswith('.csv') else pd.read_excel(up)
        new_df.columns = new_df.columns.str.strip().str.upper()
        # FIXED MAPPING: Your data will no longer stay 'Pending' or 'None'
        map_cols = {
            'CLIENT NAME':'Name','NAME':'Name','CLIENT CODE':'ID',
            'MOBILE':'Number','NUMBER':'Number','MOBILE NUMBER':'Number',
            'STATUS':'Status','CURRENT STATUS':'Status' # Maps directly to Status
        }
        new_df = new_df.rename(columns=map_cols)
        
        if 'Status' not in new_df.columns: new_df['Status'] = 'Pending'
        if 'Notes' not in new_df.columns: new_df['Notes'] = ''
        
        st.dataframe(new_df.head(10))
        if st.button("🔥 Finalize Synchronize"):
            save_db(pd.concat([load_db(), new_df], ignore_index=True))
            st.success("Empire Records Updated Successfully.")

elif nav == "🎯 Calling Station":
    st.header("🎯 Active Dialer Terminal")
    df = load_db()
    if not df.empty:
        # Improved Filter Bar
        s_filter = st.radio("Select View", ["All", "Pending", "Completed", "Follow-ups"], horizontal=True)
        
        disp_df = df.copy()
        if s_filter == "Pending": disp_df = disp_df[disp_df['Status'] == 'Pending']
        elif s_filter == "Completed": disp_df = disp_df[disp_df['Status'] == 'Completed']
        elif s_filter == "Follow-ups": disp_df = disp_df[disp_df['Status'].str.lower().str.contains('follow', na=False)]
        
        search = st.text_input("🔍 Search Database (Name or ID)")
        if search: disp_df = disp_df[disp_df['Name'].astype(str).str.contains(search, case=False)]
        
        edited_df = st.data_editor(
            disp_df, 
            use_container_width=True, 
            num_rows="dynamic",
            column_config={
                "Status": st.column_config.SelectboxColumn("Status", options=EMPIRE_STATUSES, required=True)
            },
            key="v10_editor"
        )
        
        if st.button("💾 SAVE ALL PROGRESS & REFRESH"):
            master_df = load_db()
            master_df.update(edited_df)
            save_db(master_df)
            st.success("Saved! Moving leads to correct tabs...")
            st.rerun() # Forces instant update
    else: st.warning("No leads found. Head to 'Import Leads' to begin.")
