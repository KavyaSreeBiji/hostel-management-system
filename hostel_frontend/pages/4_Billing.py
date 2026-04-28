import streamlit as st
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import require_login
from db import fetch_all_billing, fetch_all_students, process_payment

require_login()

st.set_page_config(page_title="Admin Billing", page_icon=":material/payments:", layout="wide")
st.title(":material/payments: Billing Management", anchor=False)

billing = fetch_all_billing()
students = fetch_all_students()

# Create a student lookup dictionary
student_dict = {s['Student_ID']: s['Name'] for s in students} if students else {}

# ------------------ OVERVIEW ------------------
st.subheader(":material/insights: Billing Overview", anchor=False)

total_revenue = 0
pending_amount = 0
paid_count = 0
pending_count = 0

if billing:
    for b in billing:
        if b.get("Status") == "Paid":
            paid_count += 1
            total_revenue += b.get("Amount", 0)
        else:
            pending_count += 1
            pending_amount += b.get("Amount", 0)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Total Revenue", f"₹{total_revenue}")
with c2:
    st.metric("Pending Amount", f"₹{pending_amount}")
with c3:
    st.metric("Paid Bills", paid_count)
with c4:
    st.metric("Pending Bills", pending_count)

st.divider()

# ------------------ BILLING MANAGEMENT ------------------
st.subheader(":material/table: Manage Billing", anchor=False)

if not billing:
    st.info("No billing records found in the database.")
else:
    for bill in billing:
        student_name = student_dict.get(bill['Student_ID'], 'Unknown')

        col1, col2, col3, col4, col5 = st.columns([1.2, 1.5, 1.2, 1.2, 2])

        with col1:
            st.markdown(f"**{student_name}**")
            st.caption(f"Student ID: {bill['Student_ID']} | Bill ID: {bill['Bill_ID']}")

        with col2:
            st.caption("Bill Amount")
            st.write(f"₹{bill.get('Amount', 0)}")

        with col3:
            st.caption("Due Date")
            st.write(bill.get("Due_Date", "N/A"))

        with col4:
            if bill.get("Status") == "Paid":
                st.success("Paid")
            else:
                st.warning("Not Paid")

        with col5:
            if bill.get("Status") != "Paid":
                if st.button("Mark as Paid", key=f"pay_{bill['Bill_ID']}"):
                    if process_payment(bill['Bill_ID']):
                        st.success(f"Payment marked for {student_name}")
                        st.rerun()
                    else:
                        st.error("Failed to update payment status.")
            else:
                st.caption("No action")

st.divider()

# ------------------ QUICK INSIGHTS ------------------
st.subheader(":material/insights: Insights", anchor=False)

if pending_count > 0:
    st.warning(f"{pending_count} pending payments require attention.")
else:
    st.success("All payments are cleared.")

if pending_amount > 0:
    st.info(f"Total pending collection: ₹{pending_amount}")
