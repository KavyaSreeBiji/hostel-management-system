import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import require_login
from db import fetch_student_profile, update_student_profile, get_billing_by_student, process_payment

require_login()

st.set_page_config(page_title="Profile & Dashboard", page_icon=":material/person:", layout="centered")
st.title(":material/person: My Dashboard", anchor=False)

user_id = st.session_state.current_user_id
students_db_data = fetch_student_profile(user_id)

if not students_db_data:
    st.error("Failed to fetch User data from the Database.")
    st.stop()

student_data = students_db_data

# --- LIVE OVERVIEW CARD ---
st.subheader("My Status Overview", anchor=False)
with st.container(border=True):
    ocr1, ocr2 = st.columns(2)
    with ocr1:
        if student_data['Room_ID']:
            st.metric("Assigned Room", f"Room {student_data['Room_ID']}")
        else:
            st.metric("Assigned Room", "None")
    with ocr2:
        total_due = student_data.get('Total_Due') or 0.00
        st.metric("Total Pending Balance", f"₹{total_due}")

st.divider()

# --- MY PENDING BILLS ---
st.subheader("My Pending Bills", anchor=False)
my_bills = get_billing_by_student(user_id)
if my_bills:
    pending_bills = [b for b in my_bills if b['Status'] == 'Not Paid']
else:
    pending_bills = []

if not pending_bills:
    st.info("You have no pending bills!")
else:
    for bill in pending_bills:
        with st.container(border=True):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.write(f"**Amount:** ₹{bill['Amount']}")
                st.caption(f"Bill ID: {bill['Bill_ID']}")
            with col2:
                st.write(f"**Due Date:** {bill['Due_Date']}")
                st.caption(f"Issued: {bill['Issue_Date']}")
            with col3:
                if st.button("Pay Now", key=f"pay_btn_{bill['Bill_ID']}", use_container_width=True):
                    if process_payment(bill['Bill_ID']):
                        st.success("Payment successful!")
                        st.rerun()
                    else:
                        st.error("Payment failed.")

st.divider()

st.header("View & Edit Profile", anchor=False)

with st.form("profile_form"):
    st.write(f"**Student ID:** {user_id} (Non-editable)")
    
    new_name = st.text_input("Full Name", value=student_data.get("Name", ""))
    new_email = st.text_input("Email", value=student_data.get("Email", ""))
    new_phone = st.text_input("Phone Number", value=student_data.get("Phone", ""))
    
    st.write("---")
    new_password = st.text_input("New Password (leave blank to keep current)", type="password")
    
    submitted = st.form_submit_button("Save Changes")
    
    if submitted:
        success = update_student_profile(user_id, new_name, new_email, new_phone, new_password)
            
        if success:
            st.session_state.current_user_name = new_name
            st.success("Profile updated strictly to the Live Database successfully!")
            st.rerun()
        else:
            st.error("Engine failed to synchronize with Live DB metrics.")
