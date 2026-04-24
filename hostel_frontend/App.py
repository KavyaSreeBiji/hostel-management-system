import streamlit as st
import sys
import os

# Ensure the root directory is in sys.path so we can import utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils import init_mock_data

st.set_page_config(page_title="Hostel Management System", page_icon=":material/apartment:", layout="centered")

init_mock_data()

st.title(":material/apartment: Hostel Management System", anchor=False)
st.markdown("Welcome to the student and admin portal.")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    st.success(f"Welcome back, **{st.session_state.current_user_name}**!")
    st.info("Please use the sidebar to navigate to your Dashboard, Complaints, or Profile.", icon=":material/arrow_back:")
    if st.button("Log Out", type="primary"):
        st.session_state.logged_in = False
        st.session_state.current_user_id = None
        st.session_state.current_user_name = None
        st.rerun()
else:
    tab1, tab2 = st.tabs([":material/lock: Login", ":material/edit_document: Register"])
    
    with tab1:
        st.header("Student Login", anchor=False)
        student_id = st.text_input("Student ID")
        password = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
            students = st.session_state.students
            if student_id in students and students[student_id]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.current_user_id = student_id
                st.session_state.current_user_name = students[student_id]["name"]
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid Student ID or Password")
                
    with tab2:
        st.header("New Student Registration", anchor=False)
        new_id = st.text_input("New Student ID")
        new_name = st.text_input("Full Name")
        new_email = st.text_input("Email")
        new_phone = st.text_input("Phone Number")
        new_password = st.text_input("Choose Password", type="password")
        
        if st.button("Register", use_container_width=True):
            if new_id in st.session_state.students:
                st.error("Student ID already exists!")
            elif not new_id or not new_password:
                st.error("Student ID and Password are required!")
            else:
                st.session_state.students[new_id] = {
                    "password": new_password,
                    "name": new_name,
                    "email": new_email,
                    "phone": new_phone,
                    "room_id": None
                }
                # Initialize empty billing for new user
                st.session_state.billing[new_id] = {
                    "total_due": 0, "last_bill": 0, "due_date": "N/A", "status": "Paid"
                }
                st.success("Registration successful! You can now log in.")
