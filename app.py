import streamlit as st

from database import initialize_database

from modules import (
    dashboard,
    course,
    co,
    po,
    mapping,
    preview,
    reports
)

initialize_database()

st.set_page_config(
    page_title="OBE Analytics Pro",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 OBE Analytics Pro")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Course",
        "Course Outcomes",
        "Program Outcomes",
        "CO-PO Mapping",
        "Preview",
        "Reports"
    ]
)

if page == "Dashboard":
    dashboard.show()

elif page == "Course":
    course.show()

elif page == "Course Outcomes":
    co.show()

elif page == "Program Outcomes":
    po.show()

elif page == "CO-PO Mapping":
    mapping.show()

elif page == "Preview":
    preview.show()

elif page == "Reports":
    reports.show()