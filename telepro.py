import streamlit as st
import pandas as pd
import os
if 'role' not in st.session_state:
    st.session_state['role'] = None
if not st.session_state['role']:
    st.title("🔒 Ben's Private Dialer")
    pass_code = st.text_input("Enter Access Code", type="password")
    if st.button("Login"):
        if pass_code == "123456":
            st.session_state['role'] = 'Admin'
            st.rerun()
        elif pass_code == "0000":
            st.session_state['role'] = 'Telecaller'
            st.rerun()
        else:
            st.error("Incorrect Code")
    st.stop()
if st.sidebar.button('🗑️ Log Out'):
    st.session_state.clear()
    st.rerun()
st.title(f"📞 Telecaller Pro - {st.session_state['role']} Mode")
nav_options = ["Upload Leads", "Call Center", "Manager Dashboard"] if st.session_state['role'] == 'Admin' else ["Upload Leads", "Call Center"]
page = st.sidebar.radio("Navigate", nav_options)
if page == "Upload Leads":
    st.header("📤 Add New Clients")
    uploaded_file = st.file_uploader("Upload Excel/CSV", type=["csv", "xlsx"])
    if uploaded_file:
        if uploaded_file.name.endswith('.csv'):
            new_leads = pd.read_csv(uploaded_file)
        else:
            new_leads = pd.read_excel(uploaded_file)
        new_leads.columns = new_leads.columns.str.strip()
        new_leads = new_leads.rename(columns={'CLIENT NAME':'Name','CLIENT CODE':'ID','Number ':'Number','Mobile':'Number'})
        for col in ['Status', 'Notes']:
            if col not in new_leads.columns: new_leads[col] = 'Pending' if col == 'Status' else ''
        if st.button("✅ Import to Dialer"):
            db_file = 'telecaller_database.csv'
            df_to_save = pd.concat([pd.read_csv(db_file), new_leads], ignore_index=True) if os.path.exists(db_file) else new_leads
            df_to_save.to_csv(db_file, index=False)
            st.success("Imported Successfully!")
elif page == "Call Center":
    st.header("🎯 Calling Station")
    if os.path.exists('telecaller_database.csv'):
        df = pd.read_csv('telecaller_database.csv')
        status_filter = st.radio("Select List", ["All", "Pending", "Follow-up", "Completed", "Not Connected"], horizontal=True)
        df_f = df[df['Status'] == status_filter] if status_filter != "All" else df
        # FIX: Added 'key' and 'on_change' logic support
        edited_df = st.data_editor(df_f, use_container_width=True, num_rows="dynamic", key="main_editor")
        if st.button("💾 Save All Progress"):
            # Update the main database with the edited rows
            df.update(edited_df)
            df.to_csv('telecaller_database.csv', index=False)
            st.success("Database Updated!")
    else:
        st.info("No leads found.")
elif page == "Manager Dashboard":
    st.header("📊 Manager's Dashboard")
    if os.path.exists('telecaller_database.csv'):
        df = pd.read_csv('telecaller_database.csv')
        st.write(f"### Total Calls to Audit: {len(df)}")
        st.dataframe(df[['ID', 'Name', 'Number', 'Status', 'Notes']])
        st.bar_chart(df['Status'].value_counts())
