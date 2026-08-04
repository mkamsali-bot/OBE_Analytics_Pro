import streamlit as st

from database import (
    get_course,
    get_all_cos,
    get_all_pos,
    get_mapping,
)


def show_dashboard():

    st.title("🎓 OBE Analytics Pro")
    st.subheader("Dashboard")

    # ----------------------------
    # Load Data
    # ----------------------------

    course = get_course()

    if course:
        course_code = course["course_code"]
    else:
        course_code = "Not Configured"

    co_count = len(get_all_cos())
    po_count = len(get_all_pos())
    mapping_count = len(get_mapping())

    # ----------------------------
    # Dashboard Metrics
    # ----------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Course", course_code)
    col2.metric("COs", co_count)
    col3.metric("POs", po_count)
    col4.metric("Mappings", mapping_count)

    st.divider()

    st.success("✅ OBE Analytics Pro v1.0.0")

    st.markdown("""
### Modules

- ✅ Dashboard
- ✅ Course
- ✅ Course Outcomes
- ✅ Program Outcomes
- ✅ CO–PO Mapping
- ⏳ Preview
- ⏳ Reports
""")