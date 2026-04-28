import streamlit as st
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import init_mock_data, require_login

init_mock_data()
require_login()

st.set_page_config(page_title="Admin Billing", page_icon=":material/payments:", layout="wide")
st.title(":material/payments: Billing Management", anchor=False)

billing = st.session_state.billing
students = st.session_state.students

# ------------------ OVERVIEW ------------------
st.subheader(":material/insights: Billing Overview", anchor=False)

total_revenue = 0
pending_amount = 0
paid_count = 0
pending_count = 0

for b in billing.values():
    total_revenue += b.get("last_bill", 0)
    if b.get("status") == "Paid":
        paid_count += 1
    else:
        pending_count += 1
        pending_amount += b.get("total_due", 0)

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

for student_id, bill in billing.items():
    student = students.get(student_id, {})

    col1, col2, col3, col4, col5 = st.columns([1.2, 1.5, 1.2, 1.2, 2])

    with col1:
        st.markdown(f"**{student.get('name', 'Unknown')}**")
        st.caption(f"ID: {student_id}")

    with col2:
        st.caption(f"Last Bill: ₹{bill.get('last_bill', 0)}")
        st.caption(f"Total Due: ₹{bill.get('total_due', 0)}")

    with col3:
        st.caption("Due Date")
        st.write(bill.get("due_date", "N/A"))

    with col4:
        if bill.get("status") == "Paid":
            st.success("Paid")
        else:
            st.warning("Pending")

    with col5:
        if bill.get("status") == "Pending":
            if st.button("Mark as Paid", key=f"pay_{student_id}"):
                bill["status"] = "Paid"
                st.success(f"{student.get('name')} marked as Paid")
        else:
            st.caption("No action")

st.divider()

# ------------------ QUICK INSIGHTS ------------------
st.subheader(":material/insights: Insights", anchor=False)

if pending_count > 0:
    st.warning(f"{pending_count} students have pending payments.")
else:
    st.success("All payments are cleared.")

if pending_amount > 0:
    st.info(f"Total pending collection: ₹{pending_amount}")
