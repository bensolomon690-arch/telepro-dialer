import streamlit as st
import pandas as pd
import os

# --- 1. EXECUTIVE CONFIGURATION ---
st.set_page_config(page_title="Solomon Empire Pro", layout="wide")
DB_FILE = 'telecaller_master_db.csv'

# Professional Executive White Theme (High Visibility)
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #1E1E1E; }
    [data-testid="stSidebar"] { background-color: #F8F9FA !important; border-right: 1px solid #E9ECEF; }
    h1, h2, h3 { color: #003366 !important; font-weight: 700 !important; }
    .stButton>button { background-color: #003366; color: white; border-radius: 6px; font-weight: 600; width: 100%; height: 3.5em; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. COMPLETE STATUS LIST ---
# This includes every category you requested
EMPIRE_STATUSES = [
    "Pending", "Completed", "Bending", "no incoming call", "out off service", 
    "no idea", "FOLLOWINGS", "NOT ANSWERING", "CUT THE CALL", 
    "STOCK INVESTMENT / SELLING", "insurance", "fno followings", 
    "rnt followings", "re activation followings", "pre ipo followings", 
    "visiting office", "switch off", "account opening followings", 
    "no response", "mutual fund followings", "not interested", "payin followings"
]

# --- 3. SECURITY GATEWAY ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

def login():
    st.markdown("<h1 style='text-align: center;'>🏛️ Solomon Empire Access</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        u_id = st.text_input("👤 System Identity (e.g., ben)")
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
            else:
                st.error("Access Refused")
    st.stop()

if not st.session_state['auth']:
    login()

# --- 4. DATA ENGINE (FIXES ATTRIBUTEERROR) ---
def load_db(): 
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        # FIX: Force Status to string to prevent image_968da6 error
        df['Status'] = df['Status'].fillna('Pending').astype(str)
        return df
    return pd.DataFrame()

def save_db(df):
    df.to_csv(DB_FILE, index=False)

# --- 5. NAVIGATION ---
st.sidebar.title("Telecall Pro v9.0")
if st.sidebar.button("🔐 Logout System"):
    st.session_state.clear()
    st.rerun()

nav = st.sidebar.radio("Command Center", ["📊 Stats", "📥 Sync Leads", "🎯 Call Station"])

# --- 6. PAGE LOGIC ---
if nav == "📊 Stats":
    st.header("📊 Intelligence Dashboard")
    df = load_db()
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Empire Leads", len(df))
        c2.metric
