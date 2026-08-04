import streamlit as st
from database import get_course, save_course
import config


def show_course():

    st.header("📘 Course Details")
    st.write("Enter the details of the course.")

    # -----------------------------
    # Load Existing Course
    # -----------------------------
    course = get_course()

    # -----------------------------
    # Default Values
    # -----------------------------
    if course:
        course_code = course["course_code"]
        course_name = course["course_name"]
        faculty = course["faculty"]
        department = course["department"]
        programme = course["programme"]
        semester = course["semester"]
        credits = course["credits"]
        academic_year = course["academic_year"]
    else:
        course_code = ""
        course_name = ""
        faculty = ""
        department = ""
        programme = ""
        semester = 1
        credits = 4
        academic_year = config.DEFAULT_ACADEMIC_YEAR

    # -----------------------------
    # Course Form
    # -----------------------------
    with st.form("course_form"):

        col1, col2 = st.columns(2)

        with col1:

            course_code = st.text_input(
                "Course Code *",
                value=course_code
            )

            faculty = st.text_input(
                "Faculty Name *",
                value=faculty
            )

            department = st.text_input(
                "Department *",
                value=department
            )

            semester = st.selectbox(
                "Semester *",
                [1, 2, 3, 4, 5, 6, 7, 8],
                index=semester - 1
            )

        with col2:

            course_name = st.text_input(
                "Course Name *",
                value=course_name
            )

            programme = st.text_input(
                "Programme *",
                value=programme
            )

            credits = st.selectbox(
                "Credits *",
                [1, 2, 3, 4, 5],
                index=credits - 1
            )

            academic_year = st.text_input(
                "Academic Year *",
                value=academic_year
            )

        submitted = st.form_submit_button(
            "💾 Save Course",
            use_container_width=True
        )

    # -----------------------------
    # Save
    # -----------------------------
    if submitted:

        errors = []

        if not course_code.strip():
            errors.append("Course Code")

        if not course_name.strip():
            errors.append("Course Name")

        if not faculty.strip():
            errors.append("Faculty Name")

        if not department.strip():
            errors.append("Department")

        if not programme.strip():
            errors.append("Programme")

        if not academic_year.strip():
            errors.append("Academic Year")

        if errors:

            st.error(
                "Please enter: " + ", ".join(errors)
            )

        else:

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

            st.success("✅ Course information saved successfully.")

            st.rerun()

    # -----------------------------
    # Summary
    # -----------------------------
    if course:

        st.divider()

        st.subheader("Current Course")

        st.info(
            f"""
**Course Code :** {course['course_code']}

**Course Name :** {course['course_name']}

**Faculty :** {course['faculty']}

**Programme :** {course['programme']}
"""
        )