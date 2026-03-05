import streamlit as st
import pandas as pd
from datetime import datetime
import os
if st.sidebar.button('🗑️ Clear All Leads'):
    st.session_state.clear()
    st.rerun()
# --- 1. PERMANENT DATABASE SETUP ---
DB_FILE = "telecaller_database.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    # Creates the file if it doesn't exist on your laptop
    return pd.DataFrame(columns=["ID", "Name", "Number", "Location", "Status", "Telecaller", "Last_Call", "Notes"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

# --- 2. DASHBOARD LAYOUT ---
st.set_page_config(page_title="Telecaller Pro SaaS", layout="wide")

if 'logged_in' not in st.session_state:
    st.title("🛡️ Tele-Connect Login")
    user_type = st.radio("Login as:", ["Telecaller", "Manager"])
    username = st.text_input("Username")
    if st.button("Login"):
        st.session_state.logged_in = True
        st.session_state.user_type = user_type
        st.session_state.username = username
        st.rerun()
else:
    page = st.sidebar.radio("Navigate", ["Upload Leads", "Call Center", "Reports"])

    # --- 3. UPLOAD (WITH SMART EXCEL & COLUMN FIXES) ---
    if page == "Upload Leads":
        st.header("📤 Add New Clients")
        uploaded_file = st.file_uploader("Upload Excel/CSV", type=["csv", "xlsx"])
if uploaded_file:
if uploaded_file:
        if uploaded_file.name.endswith('.csv'):
            new_leads = pd.read_csv(uploaded_file)
        else:
            new_leads = pd.read_excel(uploaded_file)
        new_leads.columns = new_leads.columns.str.strip()
        new_leads = new_leads.rename(columns={
            'CLIENT NAME': 'Name',
            'CLIENT CODE': 'ID',
            'Number ': 'Number', 
            'Mobile': 'Number'
        })
            # Ensure Number column exists before proceeding
            if 'Number' in new_leads.columns:
                existing_numbers = st.session_state.db['Number'].astype(str).tolist()
                new_leads['Number'] = new_leads['Number'].astype(str)
                is_new = ~new_leads['Number'].isin(existing_numbers)
                to_add = new_leads[is_new].copy()

                if st.button(f"Sync {len(to_add)} New Leads"):
                    to_add['Status'] = "Pending"
                    to_add['Telecaller'] = st.session_state.username
                    st.session_state.db = pd.concat([st.session_state.db, to_add], ignore_index=True)
                    save_data(st.session_state.db)
                    st.success("✅ Success! Leads saved to your laptop database.")
            else:
                st.error("❌ Error: I couldn't find a 'Number' or 'Mobile' column in your file.")

    # --- 4. CALL CENTER ---
    elif page == "Call Center":
        st.header("📞 Calling Station")
        
        # ADD "Not Connected" TO THIS LIST:
        list_type = st.radio("Select List", ["Pending", "Follow-up", "Completed", "Not Connected"], horizontal=True)
        
        current_list = st.session_state.db[st.session_state.db['Status'] == list_type]
        st.dataframe(current_list, use_container_width=True)    

    # --- 5. REPORTS & SEARCH ---
    elif page == "Reports":
        st.header("📊 Manager's Dashboard")

        # 1. Create a dropdown list of all unique telecaller names
        all_callers = st.session_state.db['Telecaller'].unique().tolist()
        selected_caller = st.selectbox("Select Telecaller to Audit", ["All"] + all_callers)

        # 2. Filter the database based on the selection
        if selected_caller == "All":
            report_df = st.session_state.db
        else:
            report_df = st.session_state.db[st.session_state.db['Telecaller'] == selected_caller]

        # 3. Show a summary count for the Supervisor
        st.subheader(f"Total Calls for {selected_caller}: {len(report_df)}")

        st.dataframe(report_df, use_container_width=True)









