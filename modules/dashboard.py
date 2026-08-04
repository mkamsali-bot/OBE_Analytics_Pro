import streamlit as st
from database import get_course, get_all_cos
import config


def show():

    st.header("🏠 Dashboard")

    # -----------------------------
    # Load Data
    # -----------------------------

    course = get_course()
    cos = get_all_cos()

    total_courses = 1 if course else 0
    total_cos = len(cos)
    total_pos = config.TOTAL_POS
    total_mapping = total_cos * total_pos

    # -----------------------------
    # Summary Cards
    # -----------------------------

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("📘 Courses", total_courses)

    with c2:
        st.metric("🎯 COs", total_cos)

    with c3:
        st.metric("🎓 POs", total_pos)

    with c4:
        st.metric("🔗 Mapping Cells", total_mapping)

    st.divider()

    # -----------------------------
    # Course Information
    # -----------------------------

    st.subheader("📘 Current Course")

    if course:

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Course Code :** {course['course_code']}")
            st.write(f"**Course Name :** {course['course_name']}")
            st.write(f"**Faculty :** {course['faculty']}")
            st.write(f"**Department :** {course['department']}")

        with col2:
            st.write(f"**Programme :** {course['programme']}")
            st.write(f"**Semester :** {course['semester']}")
            st.write(f"**Credits :** {course['credits']}")
            st.write(f"**Academic Year :** {course['academic_year']}")

    else:
        st.info("No course has been created.")

    st.divider()

    # -----------------------------
    # Progress
    # -----------------------------

    progress = 0

    if course:
        progress += 25

    if total_cos > 0:
        progress += 25

    if total_mapping > 0:
        progress += 25

    st.subheader("📈 Overall Progress")

    st.progress(progress / 100)

    st.write(f"**Completion : {progress}%**")

    st.divider()

    # -----------------------------
    # Quick Actions
    # -----------------------------

    st.subheader("⚡ Quick Actions")

    q1, q2, q3 = st.columns(3)

    with q1:
        st.button("📘 Edit Course", use_container_width=True)

    with q2:
        st.button("🎯 Manage COs", use_container_width=True)

    with q3:
        st.button("🔗 Open Mapping", use_container_width=True)

    st.divider()

    # -----------------------------
    # Status
    # -----------------------------

    st.success("Application initialized successfully.")