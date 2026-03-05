import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime
import plotly.express as px # For advanced empire charts

# --- 1. THE EMPIRE ENGINE (Configuration) ---
st.set_page_config(page_title="Solomon Business Empire", layout="wide", initial_sidebar_state="expanded")
DB_FILE = 'telecaller_database.csv'
LOG_FILE = 'empire_audit_trail.csv'
VERSION = "v3.0.0 - Grand Edition"

# Custom CSS for a Professional "Corporate" Look
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #004b87; color: white; }
    .sidebar .sidebar-content { background-image: linear-gradient(#2e7bcf,#2e7bcf); color: white; }
    .metric-card { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SECURITY & AUTHENTICATION SYSTEM ---
if 'auth_level' not in st.session_state:
    st.session_state['auth_level'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = None

def login_system():
    st.title("🏛️ Solomon Empire Access Portal")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("System Authorization")
        u_name = st.text_input("Username")
        p_code = st.text_input("Access Pin", type="password")
        if st.button("Authorize"):
            # Master Admin (Ben Solomon)
            if p_code == "123456" and u_name.lower() == "ben":
                st.session_state['auth_level'] = "Managing Director"
                st.session_state['username'] = "Ben Solomon"
                st.rerun()
            # Telecaller Staff
            elif p_code == "0000":
                st.session_state['auth_level'] = "Telecaller"
                st.session_state['username'] = u_name if u_name else "Staff_User"
                st.rerun()
            else:
                st.error("Invalid Credentials. Access Denied.")
    st.stop()

if not st.session_state['auth_level']:
    login_system()

# --- 3. HELPER FUNCTIONS (Data Persistence) ---
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame()

def save_data(df):
    df.to_csv(DB_FILE, index=False)

def log_action(action):
    log_df = pd.DataFrame([{"Timestamp": datetime.now(), "User": st.session_state['username'], "Action": action}])
    log_df.to_csv(LOG_FILE, mode='a', header=not os.path.exists(LOG_FILE), index=False)

# --- 4. SIDEBAR & NAVIGATION ---
st.sidebar.title(f"Solomon Empire")
st.sidebar.write(f"Logged as: **{st.session_state['auth_level']}**")
st.sidebar.divider()

if st.session_state['auth_level'] == "Managing Director":
    menu = ["📊 Dashboard", "📥 Lead Import", "🎯 Calling Station", "📜 Audit Logs", "⚙️ Empire Settings"]
else:
    menu = ["📥 Lead Import", "🎯 Calling Station"]

choice = st.sidebar.selectbox("Navigation Menu", menu)

if st.sidebar.button("🔐 Secure Logout"):
    st.session_state.clear()
    st.rerun()

# --- 5. PAGE: EMPIRE DASHBOARD ---
if choice == "📊 Dashboard":
    st.header("📊 Managing Director's Overview")
    df = load_data()
    
    if not df.empty:
        # High-level Metrics
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("Total Clients", len(df))
        with m2: st.metric("Completed Calls", len(df[df['Status'] == 'Completed']))
        with m3: st.metric("Follow-ups Due", len(df[df['Status'] == 'Follow-up']))
        with m4: 
            success = (len(df[df['Status'] == 'Completed']) / len(df) * 100) if len(df)>0 else 0
            st.metric("Conversion Rate", f"{success:.1f}%")
        
        # Visual Analytics
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Call Status Distribution")
            fig_status = px.pie(df, names='Status', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_status, use_container_width=True)
        with c2:
            st.subheader("Leads by Category")
            if 'Category' in df.columns:
                fig_cat = px.bar(df['Category'].value_counts(), color_discrete_sequence=['#004b87'])
                st.plotly_chart(fig_cat, use_container_width=True)
            else:
                st.info("Add categories during import to see this chart.")
    else:
        st.info("No data available. Please import leads.")

# --- 6. PAGE: LEAD IMPORT (With Smart Mapping) ---
elif choice == "📥 Lead Import":
    st.header("📤 Bulk Data Synchronization")
    biz_type = st.selectbox("Industry Category", ["Hospitals", "Schools", "Clothing", "Stock Market", "Other"])
    up = st.file_uploader("Upload Excel/CSV", type=['xlsx', 'csv'])
    
    if up:
        df_new = pd.read_csv(up) if up.name.endswith('.csv') else pd.read_excel(up)
        
        # Smart Header Mapping Logic
        df_new.columns = df_new.columns.str.strip().str.upper()
        map_cols = {'CLIENT NAME':'Name','NAME':'Name','CLIENT CODE':'ID','MOBILE':'Number','NUMBER':'Number','CONTACT':'Number','PHONE':'Number'}
        df_new = df_new.rename(columns=map_cols)
        
        # Initialize Core Empire Columns
        df_new['Category'] = biz_type
        for col in ['Status', 'Notes', 'Last_Call_Date']:
            if col not in df_new.columns: 
                df_new[col] = 'Pending' if col == 'Status' else 'None'
        
        st.write(f"Validating **{len(df_new)}** leads for **{biz_type}**...")
        st.dataframe(df_new.head())
        
        if st.button("🔥 Finalize Import"):
            master_df = pd.concat([load_data(), df_new], ignore_index=True) if os.path.exists(DB_FILE) else df_new
            save_data(master_df)
            log_action(f"Imported {len(df_new)} leads into {biz_type}")
            st.success("Empire Database Updated!")

# --- 7. PAGE: CALLING STATION (Editable & Actionable) ---
elif choice == "🎯 Calling Station":
    st.header("🎯 Live Calling Terminal")
    df = load_data()
    
    if not df.empty:
        # Advanced Filtering
        col_f1, col_f2, col_f3 = st.columns([2, 1, 1])
        with col_f1: search = st.text_input("🔍 Search Empire Records")
        with col_f2: cat_f = st.selectbox("Category Filter", ["All"] + list(df['Category'].unique()))
        with col_f3: stat_f = st.selectbox("Status Filter", ["All", "Pending", "Follow-up", "Completed", "Not Connected"])
        
        # Applying Filters
        d_df = df.copy()
        if search: d_df = d_df[d_df['Name'].astype(str).str.contains(search, case=False) | d_df['ID'].astype(str).str.contains(search)]
        if cat_f != "All": d_df = d_df[d_df['Category'] == cat_f]
        if stat_f != "All": d_df = d_df[d_df['Status'] == stat_f]
        
        st.write(f"Showing {len(d_df)} actionable leads.")
        
        # THE EDITABLE CORE
        edited_df = st.data_editor(d_df, use_container_width=True, num_rows="dynamic", key="dialer_3.0")
        
        # Quick Actions
        st.divider()
        c_a1, c_a2 = st.columns(2)
        with c_a1:
            if st.button("💾 Save Progress"):
                df.update(edited_df)
                save_data(df)
                log_action("Manual update of calling records")
                st.success("Data persistence confirmed.")
        with c_a2:
            st.write("📲 **Quick Communication Tool**")
            p_num = st.text_input("Enter number from table for WhatsApp")
            if p_num:
                wa_link = f"https://wa.me/91{p_num}"
                st.markdown(f"[Click to Open WhatsApp]({wa_link})")
    else:
        st.info("No leads available for dialing.")

# --- 8. PAGE: AUDIT LOGS (Security) ---
elif choice == "📜 Audit Logs":
    st.header("📜 Empire Transaction History")
    if os.path.exists(LOG_FILE):
        logs = pd.read_csv(LOG_FILE)
        st.dataframe(logs.sort_values(by='Timestamp', ascending=False), use_container_width=True)
        st.download_button("Export Logs to CSV", logs.to_csv(), "empire_logs.csv")
    else:
        st.info("No audit history found yet.")

# --- 9. PAGE: SETTINGS (Admin Only) ---
elif choice == "⚙️ Empire Settings":
    st.header("⚙️ System Management")
    st.warning("Critical Operations Area")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("🚨 Wipe Database"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            log_action("FULL DATABASE WIPE")
            st.rerun()
    with col_s2:
        st.write("**System Status:** Active")
        st.write(f"**Build Version:** {VERSION}")
        st.write(f"**Server Time:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
