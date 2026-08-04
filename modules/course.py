import streamlit as st
from database import save_course, get_course


def show():

    st.header("📘 Course Details")

    course = get_course()

    with st.form("course_form"):

        course_code = st.text_input(
            "Course Code",
            value=course["course_code"] if course else ""
        )

        course_name = st.text_input(
            "Course Name",
            value=course["course_name"] if course else ""
        )

        faculty = st.text_input(
            "Faculty Name",
            value=course["faculty"] if course else ""
        )

        col1, col2 = st.columns(2)

        with col1:
            department = st.text_input(
                "Department",
                value=course["department"] if course else ""
            )

            semester = st.selectbox(
                "Semester",
                [1,2,3,4,5,6,7,8],
                index=(course["semester"]-1) if course else 0
            )

        with col2:
            programme = st.text_input(
                "Programme",
                value=course["programme"] if course else ""
            )

            credits = st.selectbox(
                "Credits",
                [1,2,3,4,5],
                index=(course["credits"]-1) if course else 2
            )

        academic_year = st.text_input(
            "Academic Year",
            value=course["academic_year"] if course else "2026-27"
        )

        submitted = st.form_submit_button(
            "💾 Save Course",
            use_container_width=True
        )

        if submitted:

            if course_code == "" or course_name == "":
                st.error("Course Code and Course Name are mandatory.")
                return

            save_course((
                course_code,
                course_name,
                faculty,
                department,
                programme,
                semester,
                credits,
                academic_year
            ))

            st.success("Course Details Saved Successfully")

            st.rerun()