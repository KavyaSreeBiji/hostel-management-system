import streamlit as st
import sys
import os

# Ensure the root directory is in sys.path so we can import utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils import init_mock_data
from db import register_student, authenticate_student

st.set_page_config(page_title="Hostel Management System", page_icon=":material/apartment:", layout="centered")

init_mock_data()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.current_user_id = None
    st.session_state.current_user_name = None

def login_page():
    st.title(":material/apartment: Hostel Management System", anchor=False)
    st.markdown("Welcome to the Student and Admin portal.")
    
    role = st.radio("Select Login Role", ["Student", "Admin"], horizontal=True)
    
    if role == "Student":
        tab1, tab2 = st.tabs([":material/lock: Student Login", ":material/edit_document: Register"])
        
        with tab1:
            student_id_str = st.text_input("Student ID (e.g., 1)")
            password = st.text_input("Password", type="password")
            if st.button("Login", use_container_width=True):
                if not student_id_str.isdigit():
                    st.error("Student ID must be an integer.")
                else:
                    success, result_msg = authenticate_student(int(student_id_str), password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.role = "Student"
                        st.session_state.current_user_id = int(student_id_str)
                        st.session_state.current_user_name = result_msg # API returns Name on success
                        st.rerun()
                    else:
                        st.error(result_msg)
                    
        with tab2:
            st.info("Your Student ID will be automatically generated upon registration.")
            new_name = st.text_input("Full Name")
            new_email = st.text_input("Email")
            new_phone = st.text_input("Phone Number")
            new_password = st.text_input("Choose Password", type="password")
            
            if st.button("Register as Student", use_container_width=True):
                if not new_name or not new_email or not new_password:
                    st.error("Name, Email, and Password are required!")
                else:
                    success, result = register_student(new_name, new_email, new_phone, new_password)
                    if success:
                        st.success(f"Registration successful! Your DB Student ID is **{result}**. Please log in!")
                    else:
                        st.error(result)

    elif role == "Admin":
        st.info("System Administrators must be pre-provisioned via secure database controls.")
        admin_id = st.text_input("Admin Username")
        password = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True, key="admin_login"):
            # New Import
            from db import authenticate_admin
            
            success, usr_name, sys_admin_id = authenticate_admin(admin_id, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.role = "Admin"
                st.session_state.current_user_id = sys_admin_id
                st.session_state.current_user_name = usr_name
                st.rerun()
            else:
                st.error("Invalid Admin Username or Password. Connections are monitored natively.")

def logout_page():
    st.title(":material/logout: Logout")
    st.write(f"Logged in as: **{st.session_state.current_user_name}** ({st.session_state.role})")
    if st.button("Log Out"):
        st.session_state.logged_in =False
        st.session_state.role = None
        st.session_state.current_user_id = None
        st.session_state.current_user_name = None
        st.rerun()


# ---------------- MULTI-PAGE NAVIGATION ---------------- #
# We define the available pages for each role and let st.navigation handle the sidebar rendering

# Calculate paths relative to App.py to ensure Streamlit finds them regardless of run location
base_dir = os.path.dirname(os.path.abspath(__file__))
def get_page_path(filename):
    return os.path.join(base_dir, "pages", filename)

if not st.session_state.logged_in:
    pg = st.navigation([st.Page(login_page, title="Login", icon=":material/login:")])
else:
    # Role-based pages configuration
    if st.session_state.role == "Admin":
        pg = st.navigation({
            "Dashboard": [
                st.Page(get_page_path("2_Admin_Dashboard.py"), title="Admin Dashboard", icon=":material/dashboard:"),
                st.Page(get_page_path("3_Room_Allocation.py"), title="Room Allocation", icon=":material/hotel:")
            ],
            "Account": [
                st.Page(logout_page, title="Log Out", icon=":material/logout:")
            ]
        })
    else:
        # Student role setup
        pg = st.navigation({
            "Dashboard": [
                st.Page(get_page_path("1_User_Dashboard.py"), title="Student Dashboard", icon=":material/dashboard:"),
                st.Page(get_page_path("4_Billing.py"), title="Billing", icon=":material/payments:"),
                st.Page(get_page_path("5_Complaints.py"), title="Complaints", icon=":material/campaign:")
            ],
            "Hostel Life": [
                st.Page(get_page_path("7_Room_Booking.py"), title="Book Room", icon=":material/bed:")
            ],
            "Profile": [
                st.Page(get_page_path("6_Profile.py"), title="My Profile", icon=":material/person:")
            ],
            "Account": [
                st.Page(logout_page, title="Log Out", icon=":material/logout:")
            ]
        })

    with st.sidebar:
        st.divider()
        with st.expander("⚙️ System Settings"):
            st.warning("Deletes ALL Active Data!")
            if st.button("Factory Reset Database", type="primary", use_container_width=True):
                from db import reset_database
                if reset_database():
                    st.session_state.clear()
                    st.success("Database System Flushed and Destroyed.")
                    st.rerun()
                else:
                    st.error("Failed to execute native reset.")

pg.run()
