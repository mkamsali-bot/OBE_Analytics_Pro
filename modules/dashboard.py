import streamlit as st
from database import get_course, get_all_cos


def show():

    st.header("🏠 Dashboard")

    course = get_course()
    total_cos = len(get_all_cos())

    # Calculate mappings
    mappings = total_cos * 12

    # Summary Cards
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Courses", "1")

    with c2:
        st.metric("COs", total_cos)

    with c3:
        st.metric("POs", "12")

    with c4:
        st.metric("Mappings", mappings)

    st.divider()

    # Course Information
    if course:

        st.subheader("Course Information")

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Course Code:** {course['course_code']}")
            st.write(f"**Course Name:** {course['course_name']}")
            st.write(f"**Faculty:** {course['faculty']}")
            st.write(f"**Department:** {course['department']}")

        with col2:
            st.write(f"**Programme:** {course['programme']}")
            st.write(f"**Semester:** {course['semester']}")
            st.write(f"**Credits:** {course['credits']}")
            st.write(f"**Academic Year:** {course['academic_year']}")

    else:
        st.warning("No course has been created yet.")

    st.divider()

    # Progress
    progress = 0

    if course:
        progress += 50

    if total_cos > 0:
        progress += 25

    st.subheader("Overall Progress")

    st.progress(progress / 100)

    st.write(f"**Completion : {progress}%**")