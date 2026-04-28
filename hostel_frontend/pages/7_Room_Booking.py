import streamlit as st
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import check_room_availability, create_room_request, fetch_all_students, fetch_student_profile

st.set_page_config(page_title="Room Booking", page_icon=":material/bed:", layout="wide")
st.title(":material/bed: Room Booking", anchor=False)

user_id = st.session_state.current_user_id
user_profile = fetch_student_profile(user_id)

st.markdown("Browse and book available rooms directly from our live database!")

available_rooms = check_room_availability()
students = fetch_all_students() or []

if not available_rooms:
    st.info("No rooms are currently available. Please check back later.")
else:
    st.subheader("Available Rooms")
    
    for room in available_rooms:
        with st.container(border=True):
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                st.markdown(f"### Room {room['Room_ID']}")
                st.markdown(f"**Price:** ₹{room['Price']}")
            
            with col2:
                st.write(f"**Capacity:** {room['Capacity']}")
                st.write(f"**Current Occupants:** {room['Occupancy']}")
            
            with col3:
                with st.popover(f"Request Room {room['Room_ID']}"):
                    st.write(f"Submit request for **Room {room['Room_ID']}**.")
                    if st.button("Submit Request", key=f"btn_{room['Room_ID']}", type="primary"):
                        success, msg = create_room_request(user_id, room['Room_ID'])
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)
