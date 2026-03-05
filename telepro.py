import streamlit as st
import pandas as pd
from datetime import datetime
import os
if st.sidebar.button('🗑️ Clear All Leads'):
    st.session_state.clear()
    st.rerun()
st.title("📞 Telecaller Pro - Elite Edition")
page = st.sidebar.radio("Navigate", ["Upload Leads", "Call Center", "Reports"])
if page == "Upload Leads":
    st.header("📤 Add New Clients")
    uploaded_file = st.file_uploader("Upload Excel/CSV", type=["csv", "xlsx"])
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
        if st.button("✅ Import to Dialer"):
            if os.path.exists('telecaller_database.csv'):
                existing_df = pd.read_csv('telecaller_database.csv')
                updated_df = pd.concat([existing_df, new_leads], ignore_index=True)
            else:
                updated_df = new_leads
            updated_df.to_csv('telecaller_database.csv', index=False)
            st.success(f"Successfully imported {len(new_leads)} clients!")
elif page == "Call Center":
    st.header("🎯 Calling Station")
    if os.path.exists('telecaller_database.csv'):
        df = pd.read_csv('telecaller_database.csv')
        st.dataframe(df)
    else:
        st.info("No leads found. Please upload a file first.")
elif page == "Reports":
    st.header("📊 Performance Reports")
    st.write("Report logic and history will appear here.")







