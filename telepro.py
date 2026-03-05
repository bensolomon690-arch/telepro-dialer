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
if st.session_state['role'] == 'Admin':
    nav_options = ["Upload Leads", "Call Center", "Manager Dashboard"]
else:
    nav_options = ["Upload Leads", "Call Center"]
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
        if 'Status' not in new_leads.columns: new_leads['Status'] = 'Pending'
        if 'Notes' not in new_leads.columns: new_leads['Notes'] = ''
        if st.button("✅ Import to Dialer"):
            if os.path.exists('telecaller_database.csv'):
                existing_df = pd.read_csv('telecaller_database.csv')
                updated_df = pd.concat([existing_df, new_leads], ignore_index=True)
            else:
                updated_df = new_leads
            updated_df.to_csv('telecaller_database.csv', index=False)
            st.success("Success!")
elif page == "Call Center":
    st.header("🎯 Calling Station")
    if os.path.exists('telecaller_database.csv'):
        df = pd.read_csv('telecaller_database.csv')
        status_filter = st.radio("Select List", ["All", "Pending", "Follow-up", "Completed", "Not Connected"], horizontal=True)
        df_f = df[df['Status'] == status_filter] if status_filter != "All" else df
        edited_df = st.data_editor(df_f, num_rows="dynamic", key="call_editor")
        if st.button("💾 Save Progress"):
            df.update(edited_df)
            df.to_csv('telecaller_database.csv', index=False)
            st.success("Saved!")
    else:
        st.info("No leads found.")
elif page == "Manager Dashboard":
    st.header("📊 Manager's Dashboard")
    if os.path.exists('telecaller_database.csv'):
        df = pd.read_csv('telecaller_database.csv')
        st.write(f"### Total Calls to Audit: {len(df)}")
        st.dataframe(df[['ID', 'Name', 'Number', 'Status', 'Notes']])
        st.bar_chart(df['Status'].value_counts())
