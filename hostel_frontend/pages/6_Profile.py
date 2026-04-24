import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import init_mock_data, require_login

init_mock_data()
require_login()

st.set_page_config(page_title="Profile", page_icon=":material/person:", layout="centered")
st.title(":material/person: My Profile", anchor=False)

user_id = st.session_state.current_user_id
student_data = st.session_state.students.get(user_id, {})

st.header("View & Edit Profile", anchor=False)

with st.form("profile_form"):
    st.write(f"**Student ID:** {user_id} (Non-editable)")
    
    new_name = st.text_input("Full Name", value=student_data.get("name", ""))
    new_email = st.text_input("Email", value=student_data.get("email", ""))
    new_phone = st.text_input("Phone Number", value=student_data.get("phone", ""))
    
    st.write("---")
    new_password = st.text_input("New Password (leave blank to keep current)", type="password")
    
    submitted = st.form_submit_button("Save Changes")
    
    if submitted:
        st.session_state.students[user_id]["name"] = new_name
        st.session_state.students[user_id]["email"] = new_email
        st.session_state.students[user_id]["phone"] = new_phone
        
        if new_password.strip():
            st.session_state.students[user_id]["password"] = new_password
            
        # Update current user name in session if changed
        st.session_state.current_user_name = new_name
        
        st.success("Profile updated successfully!")
