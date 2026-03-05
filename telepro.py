import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. EXECUTIVE THEME CONFIGURATION ---
st.set_page_config(page_title="Telecall Pro - Executive MD", layout="wide")
DB_FILE = 'telecaller_database.csv'
LOG_FILE = 'system_audit.csv'

# Clean Professional White/Navy Theme
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #1E1E1E; }
    .stSidebar { background-color: #F0F2F6 !important; }
    .login-card { background-color: #F8F9FA; padding: 40px; border-radius: 15px; border: 2px solid #E9ECEF; box-shadow: 5px 5px 15px rgba(0,0,0,0.05); }
    h1, h2, h3 { color: #003366 !important; }
    .stButton>button { background-color: #003366; color: white; border-radius: 5px; border: none; font-weight: 600; }
    .stDataFrame { border: 1px solid #dee2e6; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE SECURITY GATEWAY ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

def login_portal():
    st.markdown("<h1 style='text-align: center;'>🏛️ Solomon Telecall MD Portal</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        user_id = st.text_input("👤 Management ID")
        pin_code = st.text_input("🔑 Security PIN", type="password")
        if st.button("Access Command Center"):
            if pin_code == "123456" and user_id.lower() == "ben":
                st.session_state['auth'] = True
                st.session_state['role'] = "Managing Director"
                st.rerun()
            elif pin_code == "0000":
                st.session_state['auth'] = True
                st.session_state['role'] = "Telecaller"
                st.session_state['name'] = user_id if user_id else "Agent"
                st.rerun()
            else:
                st.error("Access Refused: Invalid Credentials")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

if not st.session_state['auth']:
    login_portal()

# --- 3. SYSTEM INTERFACE ---
st.sidebar.title("Telecall Pro v4.0")
st.sidebar.markdown(f"**Session:** {st.session_state['role']}")
if st.sidebar.button("🔐 Logout"):
    st.session_state.clear()
    st.rerun()

if st.session_state['role'] == "Managing Director":
    nav = st.sidebar.radio("Navigation", ["📈 Dashboard", "📂 Sync Leads", "🎯 Call Station", "📝 Logs"])
else:
    nav = st.sidebar.radio("Navigation", ["📂 Sync Leads", "🎯 Call Station"])

def load_db(): return pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame()

# --- 4. NAVIGATION LOGIC ---
if nav == "📈 Dashboard":
    st.header("📈 Operational Performance")
    df = load_db()
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c
