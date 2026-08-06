"""
Course Master
OBE Analytics Pro v1.1.2
"""

import streamlit as st
import pandas as pd

from database import (
    save_course,
    get_all_courses,
    delete_course,
)

import config


# ---------------------------------------------------------
# PAGE TITLE
# ---------------------------------------------------------

st.title("📘 Course Master")
st.caption("Create and maintain course information.")

# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

if "course_code" not in st.session_state:
    st.session_state.course_code = ""

if "course_name" not in st.session_state:
    st.session_state.course_name = ""

if "faculty" not in st.session_state:
    st.session_state.faculty = ""

if "department" not in st.session_state:
    st.session_state.department = ""

if "programme" not in st.session_state:
    st.session_state.programme = ""

if "semester" not in st.session_state:
    st.session_state.semester = 1

if "credits" not in st.session_state:
    st.session_state.credits = 4

if "academic_year" not in st.session_state:
    st.session_state.academic_year = config.DEFAULT_ACADEMIC_YEAR

# ---------------------------------------------------------
# FORM
# ---------------------------------------------------------

with st.form("course_form"):

    col1, col2 = st.columns(2)

    with col1:
        course_code = st.text_input(
            "Course Code *",
            value=st.session_state.course_code
        )

        faculty = st.text_input(
            "Faculty Name *",
            value=st.session_state.faculty
        )

        department = st.text_input(
            "Department *",
            value=st.session_state.department
        )

        semester = st.selectbox(
            "Semester",
            [1, 2, 3, 4, 5, 6, 7, 8],
            index=st.session_state.semester - 1
        )

    with col2:
        course_name = st.text_input(
            "Course Name *",
            value=st.session_state.course_name
        )

        programme = st.text_input(
            "Programme *",
            value=st.session_state.programme
        )

        credits = st.selectbox(
            "Credits",
            [1, 2, 3, 4, 5],
            index=st.session_state.credits - 1
        )

        academic_year = st.text_input(
            "Academic Year",
            value=st.session_state.academic_year
        )

    col_save, col_new, col_delete = st.columns(3)

    with col_save:
        save = st.form_submit_button(
            "💾 Save Course",
            use_container_width=True
        )

    with col_new:
        clear = st.form_submit_button(
            "🆕 New",
            use_container_width=True
        )

    with col_delete:
        delete = st.form_submit_button(
            "🗑 Delete",
            use_container_width=True
        )

# ---------------------------------------------------------
# CLEAR
# ---------------------------------------------------------

if clear:
    st.session_state.course_code = ""
    st.session_state.course_name = ""
    st.session_state.faculty = ""
    st.session_state.department = ""
    st.session_state.programme = ""
    st.session_state.semester = 1
    st.session_state.credits = 4
    st.session_state.academic_year = config.DEFAULT_ACADEMIC_YEAR

    st.rerun()

# ---------------------------------------------------------
# DELETE
# ---------------------------------------------------------

if delete:
    if not course_code.strip():
        st.error("Enter Course Code to delete.")
    else:
        delete_course(course_code.strip().upper())
        st.success("Course deleted successfully.")

        st.session_state.course_code = ""
        st.session_state.course_name = ""
        st.session_state.faculty = ""
        st.session_state.department = ""
        st.session_state.programme = ""
        st.session_state.semester = 1
        st.session_state.credits = 4
        st.session_state.academic_year = config.DEFAULT_ACADEMIC_YEAR

        st.rerun()

# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

if save:
    errors = []

    if not course_code.strip():
        errors.append("Course Code")

    if not course_name.strip():
        errors.append("Course Name")

    if not faculty.strip():
        errors.append("Faculty")

    if not department.strip():
        errors.append("Department")

    if not programme.strip():
        errors.append("Programme")

    if not academic_year.strip():
        errors.append("Academic Year")

    if errors:
        st.error("Please enter: " + ", ".join(errors))
    else:
        save_course((
            course_code.strip().upper(),
            course_name.strip(),
            faculty.strip(),
            department.strip(),
            programme.strip(),
            semester,
            credits,
            academic_year.strip()
        ))

        st.success("✅ Course saved successfully.")

        st.session_state.course_code = course_code.strip().upper()
        st.session_state.course_name = course_name.strip()
        st.session_state.faculty = faculty.strip()
        st.session_state.department = department.strip()
        st.session_state.programme = programme.strip()
        st.session_state.semester = semester
        st.session_state.credits = credits
        st.session_state.academic_year = academic_year.strip()

# ---------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------

st.divider()

st.subheader("Current Course")

if st.session_state.course_code:
    st.info(f"""
**Course Code:** {st.session_state.course_code}

**Course Name:** {st.session_state.course_name}

**Faculty:** {st.session_state.faculty}

**Programme:** {st.session_state.programme}

**Academic Year:** {st.session_state.academic_year}
""")
else:
    st.warning("No course selected.")

# ---------------------------------------------------------
# EXISTING COURSES
# ---------------------------------------------------------

st.divider()

st.subheader("Existing Courses")

courses = get_all_courses()

if courses:
    df = pd.DataFrame([
        {
            "Course Code": row["course_code"],
            "Course Name": row["course_name"],
            "Programme": row["programme"],
            "Semester": row["semester"],
            "Academic Year": row["academic_year"]
        }
        for row in courses
    ])

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No courses available.")

# ---------------------------------------------------------
# METRIC
# ---------------------------------------------------------

st.divider()

st.metric(
    "Total Courses",
    len(courses) if courses else 0
)