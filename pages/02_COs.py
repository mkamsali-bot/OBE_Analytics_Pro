"""
=========================================================
OBE Analytics
02_COs.py
Course Outcomes
=========================================================
"""

import streamlit as st

from database import (
    get_active_course,
    fetch_all,
    execute_query,
    fetch_dataframe
)

# --------------------------------------------------------
# Page Configuration
# --------------------------------------------------------

st.set_page_config(
    page_title="Course Outcomes",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Course Outcomes")
st.divider()

# --------------------------------------------------------
# Active Course
# --------------------------------------------------------

course = get_active_course()

if course is None:

    st.warning("Please select an Active Course from the Course page.")

    st.stop()

st.success(
    f"""
**Active Course**

Course Code : {course['course_code']}

Course Name : {course['course_name']}

Faculty : {course['faculty']}

Semester : {course['semester']}

Academic Year : {course['academic_year']}
"""
)

st.divider()
# --------------------------------------------------------
# CO Entry Form
# --------------------------------------------------------

st.subheader("Course Outcomes")

bloom_levels = [
    "L1 - Remember",
    "L2 - Understand",
    "L3 - Apply",
    "L4 - Analyze",
    "L5 - Evaluate",
    "L6 - Create"
]

with st.form("co_form"):

    co_data = []

    for i in range(1, 6):

        st.markdown(f"### CO{i}")

        col1, col2 = st.columns([4, 1])

        with col1:

            statement = st.text_area(
                f"CO{i} Statement",
                key=f"co{i}",
                height=80
            )

        with col2:

            bloom = st.selectbox(
                "Bloom",
                bloom_levels,
                key=f"bloom{i}"
            )

        co_data.append(
            (
                i,
                statement,
                bloom
            )
        )

    save_cos = st.form_submit_button(
        "💾 Save Course Outcomes"
    )
    # --------------------------------------------------------
# Save COs
# --------------------------------------------------------

if save_cos:

    # Check that all 5 COs have statements
    valid = True

    for co_no, statement, bloom in co_data:

        if statement.strip() == "":
            st.error(f"Please enter the statement for CO{co_no}.")
            valid = False
            break

    if valid:

        try:

            # Delete existing COs for this course
            execute_query(
                """
                DELETE FROM co
                WHERE course_id = ?
                """,
                (course["id"],)
            )

            # Insert the 5 COs
            for co_no, statement, bloom in co_data:

                execute_query(
                    """
                    INSERT INTO co
                    (
                        course_id,
                        co_no,
                        co_statement,
                        bloom_level
                    )
                    VALUES
                    (
                        ?, ?, ?, ?
                    )
                    """,
                    (
                        course["id"],
                        co_no,
                        statement.strip(),
                        bloom
                    )
                )

            st.success("Course Outcomes saved successfully.")

        except Exception as e:

            st.error("Unable to save Course Outcomes.")
            st.code(str(e))
            # --------------------------------------------------------
# Display Saved COs
# --------------------------------------------------------

st.divider()

st.subheader("Saved Course Outcomes")

rows = fetch_all(
    """
    SELECT
        co_no,
        co_statement,
        bloom_level
    FROM co
    WHERE course_id=?
    ORDER BY co_no
    """,
    (course["id"],)
)

if len(rows) == 0:

    st.info("No Course Outcomes available.")

else:

    table = []

    for row in rows:

        table.append(
            {
                "CO": f"CO{row['co_no']}",
                "Course Outcome": row["co_statement"],
                "Bloom Level": row["bloom_level"]
            }
        )

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True
    )