import streamlit as st

def init_mock_data():
    if 'admins' not in st.session_state:
        st.session_state.admins = {
            "admin": {
                "password": "password123",
                "name": "Super Admin"
            }
        }
    if 'students' not in st.session_state:
        st.session_state.students = {
            "S101": {
                "password": "password123",
                "name": "Kavya Sree B",
                "email": "kavya@example.com",
                "phone": "+91 9876543210",
                "room_id": "101A"
            }
        }
    if 'rooms' not in st.session_state:
        st.session_state.rooms = {
            "101A": {
                "capacity": 2,
                "occupancy": 1,
                "status": "Available"
            }
        }
    if 'billing' not in st.session_state:
        st.session_state.billing = {
            "S101": {
                "total_due": 5000,
                "last_bill": 10000,
                "due_date": "2026-05-10",
                "status": "Pending"
            }
        }
    if 'complaints' not in st.session_state:
        st.session_state.complaints = [
            {"id": 1, "student_id": "S101", "category": "Maintenance", "description": "Fan is not working", "status": "Pending"},
            {"id": 2, "student_id": "S101", "category": "Cleaning", "description": "Room not cleaned for 3 days", "status": "Resolved"}
        ]

def require_login():
    if not st.session_state.get("logged_in"):
        st.warning("Please log in from the main app page to access this page.")
        st.stop()
