"""
OBE Analytics Pro v1.3
01_Course.py
STEP 2 - COURSE ENTRY

Uses the existing root-level database.py architecture.

Course fields:
- Course Code
- Course Name
- Faculty
- Semester
- Academic Year
- CE Maximum
- S1 Maximum
- S2 Maximum
- Use Indirect Attainment
- Direct Weight
- Indirect Weight

The selected course is also stored as the application's Active Course.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Optional

import streamlit as st

from database import (
    DB_NAME,
    execute_query,
    fetch_all,
    fetch_one,
    get_connection,
    initialize_database,
    set_active_course,
)


# ------------------------------------------------------------
# Page Configuration
# ------------------------------------------------------------

st.set_page_config(
    page_title="OBE Analytics Pro - Course",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ------------------------------------------------------------
# Database Initialization
# ------------------------------------------------------------

initialize_database()


def ensure_course_type_column() -> None:
    """Add course_type to existing course tables without losing data."""
    conn = get_connection()
    columns = [
        row["name"]
        for row in conn.execute("PRAGMA table_info(course)").fetchall()
    ]

    if "course_type" not in columns:
        conn.execute(
            """
            ALTER TABLE course
            ADD COLUMN course_type TEXT DEFAULT 'Theory'
            """
        )
        conn.commit()

    conn.close()


ensure_course_type_column()


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def get_courses():
    return fetch_all(
        """
        SELECT
            id,
            course_code,
            course_name,
            course_type,
            faculty,
            semester,
            academic_year,
            ce_max,
            s1_max,
            s2_max,
            use_indirect,
            direct_weight,
            indirect_weight
        FROM course
        ORDER BY academic_year DESC, course_code
        """
    )


def get_course(course_id: int):
    return fetch_one(
        """
        SELECT
            id,
            course_code,
            course_name,
            course_type,
            faculty,
            semester,
            academic_year,
            ce_max,
            s1_max,
            s2_max,
            use_indirect,
            direct_weight,
            indirect_weight
        FROM course
        WHERE id=?
        """,
        (course_id,),
    )


def get_stored_active_course_id() -> Optional[int]:
    row = fetch_one(
        """
        SELECT active_course_id
        FROM settings
        WHERE id=1
        """
    )

    if row is None:
        return None

    value = row["active_course_id"]

    if value is None:
        return None

    return int(value)


def course_label(row: Any) -> str:
    code = row["course_code"] or ""
    name = row["course_name"] or ""
    year = row["academic_year"] or ""

    label = f"{code} - {name}"

    if year:
        label += f" | {year}"

    return label


def save_course(
    course_code: str,
    course_name: str,
    course_type: str,
    faculty: str,
    semester: str,
    academic_year: str,
    ce_max: int,
    s1_max: int,
    s2_max: int,
    use_indirect: int,
    direct_weight: float,
    indirect_weight: float,
) -> int:

    return_id = fetch_one(
        "SELECT id FROM course WHERE course_code=?",
        (course_code,),
    )

    if return_id is not None:
        raise ValueError(
            f"Course Code '{course_code}' already exists."
        )

    course_id = None

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO course(
            course_code,
            course_name,
            course_type,
            faculty,
            semester,
            academic_year,
            ce_max,
            s1_max,
            s2_max,
            use_indirect,
            direct_weight,
            indirect_weight
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            course_code,
            course_name,
            course_type,
            faculty,
            semester,
            academic_year,
            ce_max,
            s1_max,
            s2_max,
            use_indirect,
            direct_weight,
            indirect_weight,
        ),
    )

    course_id = cur.lastrowid

    conn.commit()
    conn.close()

    return int(course_id)


def update_course(
    course_id: int,
    course_code: str,
    course_name: str,
    course_type: str,
    faculty: str,
    semester: str,
    academic_year: str,
    ce_max: int,
    s1_max: int,
    s2_max: int,
    use_indirect: int,
    direct_weight: float,
    indirect_weight: float,
) -> None:

    existing = fetch_one(
        """
        SELECT id
        FROM course
        WHERE course_code=?
          AND id<>?
        """,
        (course_code, course_id),
    )

    if existing is not None:
        raise ValueError(
            f"Course Code '{course_code}' is already used by another course."
        )

    execute_query(
        """
        UPDATE course
        SET
            course_code=?,
            course_name=?,
            course_type=?,
            faculty=?,
            semester=?,
            academic_year=?,
            ce_max=?,
            s1_max=?,
            s2_max=?,
            use_indirect=?,
            direct_weight=?,
            indirect_weight=?
        WHERE id=?
        """,
        (
            course_code,
            course_name,
            course_type,
            faculty,
            semester,
            academic_year,
            ce_max,
            s1_max,
            s2_max,
            use_indirect,
            direct_weight,
            indirect_weight,
            course_id,
        ),
    )


# ------------------------------------------------------------
# Header
# ------------------------------------------------------------

st.title("🎓 Course Management")
st.caption(
    "OBE Analytics Pro v1.3 · STEP 2 - Course Entry"
)


# ------------------------------------------------------------
# Existing Courses / Active Course
# ------------------------------------------------------------

courses = get_courses()

stored_active_id = get_stored_active_course_id()

if courses:
    st.subheader("Active Course")

    course_options = {
        course_label(row): int(row["id"])
        for row in courses
    }

    option_labels = list(course_options.keys())

    default_index = 0

    if stored_active_id is not None:
        for index, label in enumerate(option_labels):
            if course_options[label] == stored_active_id:
                default_index = index
                break

    selected_label = st.selectbox(
        "Select Active Course",
        option_labels,
        index=default_index,
        key="active_course_selector_v13",
    )

    selected_course_id = course_options[selected_label]

    if st.button(
        "Set as Active Course",
        type="primary",
        key="set_active_course_v13",
    ):
        set_active_course(selected_course_id)
        st.session_state["active_course_id"] = selected_course_id
        st.success(
            f"Active Course set to: {selected_label}"
        )
        st.rerun()

    current_active_id = get_stored_active_course_id()

    if current_active_id is not None:
        active_course = get_course(current_active_id)

        if active_course:
            st.success(
                "Active Course: "
                + course_label(active_course)
            )

st.divider()


# ------------------------------------------------------------
# Course Entry / Edit
# ------------------------------------------------------------

st.subheader("Course Details")

mode = st.radio(
    "Course Operation",
    ["New Course", "Edit Existing Course"],
    horizontal=True,
    key="course_operation_v13",
)


if mode == "Edit Existing Course" and courses:

    edit_options = {
        course_label(row): int(row["id"])
        for row in courses
    }

    edit_label = st.selectbox(
        "Select Course to Edit",
        list(edit_options.keys()),
        key="edit_course_selector_v13",
    )

    edit_id = edit_options[edit_label]
    existing = get_course(edit_id)

else:
    edit_id = None
    existing = None


with st.form(
    "course_entry_form_v13",
    clear_on_submit=False,
):

    col1, col2 = st.columns(2)

    with col1:
        course_code = st.text_input(
            "Course Code *",
            value=(
                existing["course_code"]
                if existing
                else ""
            ),
            placeholder="Example: ECE301",
        )

        course_name = st.text_input(
            "Course Name *",
            value=(
                existing["course_name"]
                if existing
                else ""
            ),
            placeholder="Example: Digital Signal Processing",
        )

        course_types = [
            "Theory",
            "Theory + Practical",
            "Capstone Project",
            "Internship",
        ]

        existing_course_type = (
            existing["course_type"]
            if existing and existing["course_type"]
            else "Theory"
        )

        course_type = st.selectbox(
            "Course Type *",
            course_types,
            index=(
                course_types.index(existing_course_type)
                if existing_course_type in course_types
                else 0
            ),
        )

        faculty = st.text_input(
            "Faculty / Course Instructor",
            value=(
                existing["faculty"] or ""
                if existing
                else ""
            ),
            placeholder="Faculty name",
        )

        semester = st.text_input(
            "Semester",
            value=(
                existing["semester"] or ""
                if existing
                else ""
            ),
            placeholder="Example: V",
        )

        academic_year = st.text_input(
            "Academic Year *",
            value=(
                existing["academic_year"] or ""
                if existing
                else ""
            ),
            placeholder="Example: 2026-27",
        )

    with col2:

        st.markdown("**Assessment Maximum Marks**")

        ce_max = st.number_input(
            "CE Maximum",
            min_value=0,
            max_value=1000,
            value=(
                int(existing["ce_max"])
                if existing and existing["ce_max"] is not None
                else 25
            ),
            step=1,
        )

        s1_max = st.number_input(
            "S1 Maximum",
            min_value=0,
            max_value=1000,
            value=(
                int(existing["s1_max"])
                if existing and existing["s1_max"] is not None
                else 30
            ),
            step=1,
        )

        s2_max = st.number_input(
            "S2 Maximum",
            min_value=0,
            max_value=1000,
            value=(
                int(existing["s2_max"])
                if existing and existing["s2_max"] is not None
                else 45
            ),
            step=1,
        )

        use_indirect = st.checkbox(
            "Use Indirect Attainment",
            value=(
                bool(existing["use_indirect"])
                if existing
                else True
            ),
        )

        direct_weight = st.number_input(
            "Direct Attainment Weight (%)",
            min_value=0.0,
            max_value=100.0,
            value=(
                float(existing["direct_weight"])
                if existing and existing["direct_weight"] is not None
                else 80.0
            ),
            step=5.0,
        )

        indirect_weight = st.number_input(
            "Indirect Attainment Weight (%)",
            min_value=0.0,
            max_value=100.0,
            value=(
                float(existing["indirect_weight"])
                if existing and existing["indirect_weight"] is not None
                else 20.0
            ),
            step=5.0,
        )

    submitted = st.form_submit_button(
        "Update Course"
        if existing
        else "Create Course",
        type="primary",
    )


# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

if submitted:

    course_code = course_code.strip()
    course_name = course_name.strip()
    faculty = faculty.strip()
    semester = semester.strip()
    academic_year = academic_year.strip()

    if not course_code:
        st.error("Course Code is required.")

    elif not course_name:
        st.error("Course Name is required.")

    elif not academic_year:
        st.error("Academic Year is required.")

    elif abs(
        float(direct_weight)
        + float(indirect_weight)
        - 100.0
    ) > 0.001:
        st.error(
            "Direct and Indirect Attainment weights "
            "must total 100%."
        )

    else:
        try:

            if existing:

                update_course(
                    course_id=edit_id,
                    course_code=course_code,
                    course_name=course_name,
                    course_type=course_type,
                    faculty=faculty,
                    semester=semester,
                    academic_year=academic_year,
                    ce_max=int(ce_max),
                    s1_max=int(s1_max),
                    s2_max=int(s2_max),
                    use_indirect=int(use_indirect),
                    direct_weight=float(direct_weight),
                    indirect_weight=float(indirect_weight),
                )

                st.success(
                    f"Course '{course_code}' updated successfully."
                )

            else:

                new_course_id = save_course(
                    course_code=course_code,
                    course_name=course_name,
                    course_type=course_type,
                    faculty=faculty,
                    semester=semester,
                    academic_year=academic_year,
                    ce_max=int(ce_max),
                    s1_max=int(s1_max),
                    s2_max=int(s2_max),
                    use_indirect=int(use_indirect),
                    direct_weight=float(direct_weight),
                    indirect_weight=float(indirect_weight),
                )

                set_active_course(new_course_id)

                st.session_state["active_course_id"] = (
                    new_course_id
                )

                st.success(
                    f"Course '{course_code}' created successfully "
                    "and set as Active Course."
                )

            st.rerun()

        except sqlite3.IntegrityError as exc:
            st.error(
                "The Course Code already exists or violates "
                "a database constraint."
            )
            st.exception(exc)

        except ValueError as exc:
            st.error(str(exc))

        except Exception as exc:
            st.error("Unable to save the course.")
            st.exception(exc)


# ------------------------------------------------------------
# Assessment Structure
# ------------------------------------------------------------

if existing:
    display_course_type = existing["course_type"] or "Theory"
else:
    display_course_type = course_type

if display_course_type == "Theory + Practical":
    st.divider()
    st.subheader("Theory + Practical Assessment Structure")

    # --------------------------------------------------------
    # Overall weighting
    # --------------------------------------------------------
    st.markdown("### Overall Weighting")

    weight_col1, weight_col2 = st.columns(2)

    with weight_col1:
        st.metric("Theory", "70%")

    with weight_col2:
        st.metric("Practical", "30%")

    # --------------------------------------------------------
    # Theory component
    # --------------------------------------------------------
    st.markdown("### THEORY COMPONENT")

    theory_component = [
        {
            "Assessment": "CE",
            "Maximum": int(ce_max),
        },
        {
            "Assessment": "S1",
            "Maximum": int(s1_max),
        },
        {
            "Assessment": "S2",
            "Maximum": int(s2_max),
        },
        {
            "Assessment": "Theory Total",
            "Maximum": int(ce_max) + int(s1_max) + int(s2_max),
        },
    ]

    st.dataframe(
        theory_component,
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------------
    # Practical component
    # --------------------------------------------------------
    st.markdown("### PRACTICAL COMPONENT")

    practical_component = [
        {
            "Assessment": "Record Work",
            "Maximum": 60,
        },
        {
            "Assessment": "Mid 1",
            "Maximum": 20,
        },
        {
            "Assessment": "Mid 2",
            "Maximum": 20,
        },
        {
            "Assessment": "Practical Total",
            "Maximum": 100,
        },
    ]

    st.dataframe(
        practical_component,
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------------
    # Fixed practical CO distribution
    # --------------------------------------------------------
    st.markdown("### Fixed Practical CO Distribution")

    practical_co_distribution = [
        {
            "Assessment": "Record Work",
            "Maximum": 60,
            "CO1": "20%",
            "CO2": "20%",
            "CO3": "20%",
            "CO4": "20%",
            "CO5": "20%",
        },
        {
            "Assessment": "Mid 1",
            "Maximum": 20,
            "CO1": "50%",
            "CO2": "50%",
            "CO3": "—",
            "CO4": "—",
            "CO5": "—",
        },
        {
            "Assessment": "Mid 2",
            "Maximum": 20,
            "CO1": "—",
            "CO2": "—",
            "CO3": "33.33%",
            "CO4": "33.33%",
            "CO5": "33.33%",
        },
    ]

    st.dataframe(
        practical_co_distribution,
        use_container_width=True,
        hide_index=True,
    )

    st.info(
        "The Practical CO distribution is fixed by the system. "
        "Faculty cannot manually change the CO allocation."
    )

    # --------------------------------------------------------
    # Excel import structure
    # --------------------------------------------------------
    st.markdown("### Theory + Practical Excel Import Columns")

    excel_columns = [
        "Roll Number",
        "Student Name",
        "CE",
        "S1",
        "S2",
        "Record Work",
        "Mid 1",
        "Mid 2",
    ]

    st.dataframe(
        [{"Column": column} for column in excel_columns],
        use_container_width=True,
        hide_index=True,
    )

    st.code(
        "Roll Number\n"
        "Student Name\n"
        "CE\n"
        "S1\n"
        "S2\n"
        "Record Work\n"
        "Mid 1\n"
        "Mid 2"
    )

elif display_course_type == "Theory":
    st.divider()
    st.subheader("Theory Assessment Structure")
    st.write("CE")
    st.write("S1")
    st.write("S2")

elif display_course_type == "Capstone Project":
    st.divider()
    st.subheader("Capstone Project Assessment Structure")

    st.markdown("### CONTINUOUS EVALUATION")
    st.write("Continuous Evaluation — **/100**")

    st.markdown("### Fixed CO Distribution")

    st.dataframe(
        [
            {
                "Assessment": "Continuous Evaluation",
                "Maximum": 100,
                "CO Distribution": "CO1, CO2, CO3, CO4, CO5 equally",
            }
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.info(
        "Capstone Project: Continuous Evaluation is 100 marks. "
        "The 100 marks are distributed equally across CO1–CO5."
    )

    st.markdown("### Excel Import Columns")
    st.code(
        "Roll Number\\n"
        "Student Name\\n"
        "Continuous Evaluation"
    )

elif display_course_type == "Internship":
    st.divider()
    st.subheader("Internship Assessment Structure")

    st.markdown("### CONTINUOUS EVALUATION")
    st.write("Continuous Evaluation — **/50**")

    st.markdown("### Fixed CO Distribution")

    st.dataframe(
        [
            {
                "Assessment": "Continuous Evaluation",
                "Maximum": 50,
                "CO Distribution": "CO1, CO2, CO3, CO4, CO5 equally",
            }
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.info(
        "Internship: Continuous Evaluation is 50 marks. "
        "The 50 marks are distributed equally across CO1–CO5."
    )

    st.markdown("### Excel Import Columns")
    st.code(
        "Roll Number\\n"
        "Student Name\\n"
        "Continuous Evaluation"
    )


# ------------------------------------------------------------
# Current Course List
# ------------------------------------------------------------

st.divider()
st.subheader("Course List")

courses = get_courses()

if courses:

    rows = []

    for row in courses:
        rows.append(
            {
                "ID": row["id"],
                "Course Code": row["course_code"],
                "Course Name": row["course_name"],
                "Course Type": row["course_type"] or "Theory",
                "Faculty": row["faculty"] or "",
                "Semester": row["semester"] or "",
                "Academic Year": row["academic_year"] or "",
                "CE Max": row["ce_max"],
                "S1 Max": row["s1_max"],
                "S2 Max": row["s2_max"],
                "Indirect": (
                    "Yes"
                    if row["use_indirect"]
                    else "No"
                ),
                "Direct %": row["direct_weight"],
                "Indirect %": row["indirect_weight"],
            }
        )

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )

else:
    st.info(
        "No courses have been created yet. "
        "Use New Course above to create the first course."
    )
