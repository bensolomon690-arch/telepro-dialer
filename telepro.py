import streamlit as st
import pandas as pd
import os
st.set_page_config(page_title="Solomon Pro", layout="wide")
DB_FILE = 'telecaller_master_db.csv'
st.markdown("""<style>.stApp { background-color: #FFFFFF; color: #1E1E1E; } [data-testid="stSidebar"] { background-color: #F8F9FA !important; border-right: 1px solid #E9ECEF; } h1, h2, h3 { color: #003366 !important; font-weight: 700 !important; } .stButton>button { background-color: #003366; color: white; border-radius: 6px; font-weight: 600; width: 100%; height: 3.5em; }</style>""", unsafe_allow_html=True)
STATUS_LIST = ["Pending", "Completed", "Bending", "no incoming call", "out off service", "no idea", "FOLLOWINGS", "NOT ANSWERING", "CUT THE CALL", "STOCK INVESTMENT / SELLING", "insurance", "fno followings", "rnt followings", "re activation followings", "pre ipo followings", "visiting office", "switch off", "account opening followings", "no response", "mutual fund followings", "not interested", "payin followings"]
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    st.markdown("<h1 style='text-align: center;'>🏛️ Solomon Empire Access</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        u_id = st.text_input("👤 Identity")
        u_pin = st.text_input("🔑 PIN", type="password")
        if st.button("Authorize"):
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
def load_db(): 
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['Status'] = df['Status'].fillna('Pending').astype(str)
        return df
    return pd.DataFrame()
def save_db(df): df.to_csv(DB_FILE, index=False)
if st.sidebar.button("🔐 Logout"):
    st.session_state.clear()
    st.rerun()
nav = st.sidebar.radio("Menu", ["📊 Dashboard", "📥 Import", "🎯 Dialer"])
if nav == "📊 Dashboard":
    st.header("📊 Intelligence")
    df = load_db()
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Leads", len(df))
        c2.metric("Completed", len(df[df['Status'] == 'Completed']))
        f_count = len(df[df['Status'].str.lower().str.contains('follow', na=False)])
        c3.metric("Follow-ups", f_count)
        st.bar_chart(df['Status'].value_counts())
elif nav == "📥 Import":
    st.header("📥 Sync")
    up = st.file_uploader("Upload", type=['csv', 'xlsx'])
    if up:
        new_df = pd.read_csv(up) if up.name.endswith('.csv') else pd.read_excel(up)
        new_df.columns = new_df.columns.str.strip().str.upper()
        m = {'CLIENT NAME':'Name','NAME':'Name','CLIENT CODE':'ID','MOBILE':'Number','NUMBER':'Number','MOBILE NUMBER':'Number','CURRENT STATUS':'Status','STATUS':'Status'}
        new_df = new_df.rename(columns=m)
        if 'Status' not in new_df.columns: new_df['Status'] = 'Pending'
        if 'Notes' not in new_df.columns: new_df['Notes'] = ''
        st.dataframe(new_df.head(5))
        if st.button("🔥 Sync Leads"):
            existing = load_db()
            final = pd.concat([existing, new_df], ignore_index=True)
            # Remove duplicate columns if they exist
            final = final.loc[:, ~final.columns.duplicated()]
            save_db(final)
            st.success("Database Updated")
elif nav == "🎯 Dialer":
    st.header("🎯 Terminal")
    df = load_db()
    if not df.empty:
        v = st.radio("View", ["All", "Pending", "Completed", "Follow-ups"], horizontal=True)
        d = df.copy()
        if v == "Pending": d = d[d['Status'] == 'Pending']
        elif v == "Completed": d = d[d['Status'] == 'Completed']
        elif v == "Follow-ups": 
            # This fixes the section bug - it finds ALL types of followings
            d = d[d['Status'].str.lower().str.contains('follow', na=False)]
        s = st.text_input("🔍 Search")
        if s: d = d[d['Name'].astype(str).str.contains(s, case=False)]
        ed = st.data_editor(d, use_container_width=True, num_rows="dynamic", column_config={"Status": st.column_config.SelectboxColumn("Status", options=STATUS_LIST, required=True)}, key="v11_ed")
        if st.button("💾 SAVE & REFRESH"):
            master = load_db()
            master.update(ed)
            save_db(master)
            st.success("Saved")
            st.rerun()
