"""
Dashboard
OBE Analytics Pro v1.1.2
"""

import streamlit as st

from database import (
    get_course,
    get_all_cos,
    get_all_pos,
    get_mapping,
)

# ---------------------------------------------------------
# PAGE TITLE
# ---------------------------------------------------------

st.title("🎓 OBE Analytics Pro")
st.caption("Outcome Based Education Analytics System")

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

course = get_course()

if course:
    course_code = course["course_code"]
    course_name = course["course_name"]
else:
    course_code = "Not Configured"
    course_name = "-"

co_count = len(get_all_cos())
po_count = len(get_all_pos())
mapping_count = len(get_mapping())

# ---------------------------------------------------------
# DASHBOARD METRICS
# ---------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Course", course_code)

with col2:
    st.metric("COs", co_count)

with col3:
    st.metric("POs", po_count)

with col4:
    st.metric("CO-PO Mappings", mapping_count)

st.divider()

# ---------------------------------------------------------
# COURSE DETAILS
# ---------------------------------------------------------

st.subheader("Current Course")

if course:

    st.info(f"""
**Course Code:** {course['course_code']}

**Course Name:** {course['course_name']}

**Faculty:** {course['faculty']}

**Programme:** {course['programme']}

**Academic Year:** {course['academic_year']}
""")

else:

    st.warning("No course has been configured yet.")

st.divider()

# ---------------------------------------------------------
# MODULE STATUS
# ---------------------------------------------------------

st.subheader("Module Status")

status = [
    ("Dashboard", "✅"),
    ("Course Master", "✅"),
    ("CO Master", "✅"),
    ("PO Master", "✅"),
    ("CO-PO Mapping", "✅"),
    ("CO Distribution", "🚧"),
    ("Assessment Entry", "🚧"),
    ("CO Attainment", "⏳"),
    ("PO Attainment", "⏳"),
    ("Reports", "⏳"),
]

for module, state in status:
    st.write(f"{state} {module}")

st.divider()

st.success("OBE Analytics Pro v1.1.2")