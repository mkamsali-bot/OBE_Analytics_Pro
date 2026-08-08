"""
=========================================================
OBE Analytics
05_CO_Attainment.py
CO Attainment
=========================================================

Automatic CO mark generation rule:
    CE -> CO1, CO2, CO3, CO4, CO5 equally
    S1 -> CO1, CO2 equally
    S2 -> CO3, CO4, CO5 equally

For each student:
    CO1 = CE/5 + S1/2
    CO2 = CE/5 + S1/2
    CO3 = CE/5 + S2/3
    CO4 = CE/5 + S2/3
    CO5 = CE/5 + S2/3

The generated values are stored in co_marks and can then be used
by the CO attainment calculation.
=========================================================
"""

import streamlit as st
import pandas as pd

from database import (
    get_active_course,
    fetch_all,
    fetch_dataframe,
    execute_query
)

from calculations import (
    calculate_direct_attainment,
    calculate_co_attainment,
    calculate_final_co_attainment
)


# --------------------------------------------------------
# Page Configuration
# --------------------------------------------------------

st.set_page_config(
    page_title="CO Attainment",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 CO Attainment")
st.divider()


# --------------------------------------------------------
# Active Course
# --------------------------------------------------------

course = get_active_course()

if course is None:
    st.warning(
        "Please select an Active Course from Course Management."
    )
    st.stop()

st.success(
    f"""
### Active Course

**Course Code :** {course['course_code']}

**Course Name :** {course['course_name']}

**Faculty :** {course['faculty']}

**Semester :** {course['semester']}

**Academic Year :** {course['academic_year']}
"""
)

st.divider()


# --------------------------------------------------------
# Load Course Outcomes
# --------------------------------------------------------

cos = fetch_all(
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

if len(cos) != 5:
    st.warning(
        "Please define all 5 Course Outcomes first."
    )
    st.stop()


# --------------------------------------------------------
# Load Student Marks
# --------------------------------------------------------

students = fetch_dataframe(
    """
    SELECT
        student_id,
        student_name,
        ce,
        s1,
        s2
    FROM marks
    WHERE course_id=?
    ORDER BY student_id
    """,
    (course["id"],)
)

if students.empty:
    st.warning(
        "No student marks are available for this course."
    )
    st.stop()

st.info(
    f"Total Students: {len(students)}"
)

st.divider()


# --------------------------------------------------------
# Direct / Indirect Settings
# --------------------------------------------------------

use_indirect = bool(
    course["use_indirect"]
)

direct_weight = float(
    course["direct_weight"]
)

indirect_weight = float(
    course["indirect_weight"]
)

st.subheader("Attainment Settings")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Direct Weight",
        f"{direct_weight:.0f}%"
        if use_indirect else "100%"
    )

with col2:
    st.metric(
        "Indirect Weight",
        f"{indirect_weight:.0f}%"
        if use_indirect else "0%"
    )

with col3:
    st.metric(
        "Total Weight",
        "100%"
    )

if use_indirect:
    st.info(
        f"Final CO Attainment = Direct "
        f"({direct_weight:.0f}%) + Indirect "
        f"({indirect_weight:.0f}%)"
    )
else:
    st.info(
        "Indirect attainment is disabled. "
        "Direct attainment is treated as 100%."
    )

st.divider()


# --------------------------------------------------------
# CO Assessment Distribution
# --------------------------------------------------------

st.subheader("CO Assessment Distribution")

st.caption(
    "Enter the maximum marks contributing to each CO. "
    "The total must be 100."
)

co_distribution = {}

cols = st.columns(5)

for index, co in enumerate(cos):

    co_no = int(co["co_no"])

    with cols[index]:

        co_distribution[co_no] = st.number_input(
            f"CO{co_no} Maximum Marks",
            min_value=0.0,
            max_value=100.0,
            value=20.0,
            step=1.0,
            key=f"co_max_{co_no}"
        )

distribution_total = sum(
    co_distribution.values()
)

st.metric(
    "Total CO Marks",
    f"{distribution_total:.1f}"
)

if distribution_total != 100:
    st.warning(
        "CO assessment distribution must total 100 marks."
    )
else:
    st.success(
        "CO assessment distribution is valid."
    )


# ========================================================
# AUTOMATIC CO MARK GENERATION
# ========================================================

st.divider()

st.subheader(
    "⚙️ Automatic CO Mark Generation"
)

st.info(
    """
The system can generate CO-wise marks automatically from the
existing CE, S1 and S2 marks using the following rule:

• CE is distributed equally among CO1–CO5.
• S1 is distributed equally between CO1 and CO2.
• S2 is distributed equally among CO3, CO4 and CO5.
"""
)

st.caption(
    "This is an equal-distribution assumption and should be "
    "documented as the CO mark generation methodology."
)

if st.button(
    "⚙️ Generate CO Marks Automatically",
    type="primary",
    key="generate_co_marks"
):

    try:

        generated_count = 0

        for _, student in students.iterrows():

            student_id = str(
                student["student_id"]
            )

            ce = float(
                student["ce"] or 0
            )

            s1 = float(
                student["s1"] or 0
            )

            s2 = float(
                student["s2"] or 0
            )

            ce_part = ce / 5.0
            s1_part = s1 / 2.0
            s2_part = s2 / 3.0

            generated_marks = {
                1: ce_part + s1_part,
                2: ce_part + s1_part,
                3: ce_part + s2_part,
                4: ce_part + s2_part,
                5: ce_part + s2_part
            }

            for co_no, marks_value in generated_marks.items():

                execute_query(
                    """
                    INSERT INTO co_marks
                    (
                        course_id,
                        student_id,
                        co_no,
                        marks
                    )
                    VALUES (?, ?, ?, ?)

                    ON CONFLICT(
                        course_id,
                        student_id,
                        co_no
                    )

                    DO UPDATE SET
                        marks=excluded.marks
                    """,
                    (
                        course["id"],
                        student_id,
                        co_no,
                        marks_value
                    )
                )

            generated_count += 1

        st.success(
            f"✅ CO marks generated successfully for "
            f"{generated_count} students."
        )

        st.rerun()

    except Exception as e:

        st.error(
            "Unable to generate automatic CO marks."
        )

        st.exception(e)


# --------------------------------------------------------
# CO Marks Data Status
# --------------------------------------------------------

st.subheader("CO Marks Data Status")

co_status = fetch_dataframe(
    """
    SELECT
        COUNT(DISTINCT student_id) AS students_with_co_marks
    FROM co_marks
    WHERE course_id=?
    """,
    (course["id"],)
)

students_with_co_marks = 0

if not co_status.empty:
    students_with_co_marks = int(
        co_status.iloc[0]["students_with_co_marks"] or 0
    )

c1, c2 = st.columns(2)

with c1:
    st.metric(
        "Students",
        len(students)
    )

with c2:
    st.metric(
        "Students with CO Marks",
        students_with_co_marks
    )

if students_with_co_marks == len(students):

    st.success(
        "✅ CO marks are available for all students."
    )

else:

    st.warning(
        f"{len(students) - students_with_co_marks} "
        "student(s) still do not have CO marks."
    )


st.divider()


# --------------------------------------------------------
# CO-wise Student Marks - Manual Entry
# --------------------------------------------------------

st.subheader("CO-wise Student Marks")

st.info(
    "Manual entry is available when individual CO marks need "
    "to be corrected after automatic generation."
)

student_options = (
    students["student_id"].astype(str)
    + " - "
    + students["student_name"].astype(str)
)

selected_student = st.selectbox(
    "Select Student",
    student_options,
    key="co_marks_student"
)

selected_student_id = selected_student.split(
    " - ",
    1
)[0]


# --------------------------------------------------------
# Existing CO Marks
# --------------------------------------------------------

existing_co_marks = fetch_all(
    """
    SELECT
        co_no,
        marks
    FROM co_marks
    WHERE course_id=?
    AND student_id=?
    """,
    (
        course["id"],
        selected_student_id
    )
)

existing_marks = {}

for row in existing_co_marks:

    existing_marks[
        int(row["co_no"])
    ] = float(row["marks"])


# --------------------------------------------------------
# CO Marks Entry
# --------------------------------------------------------

co_marks_values = {}

mark_cols = st.columns(5)

for index, co in enumerate(cos):

    co_no = int(co["co_no"])

    maximum = float(
        co_distribution[co_no]
    )

    with mark_cols[index]:

        co_marks_values[co_no] = st.number_input(
            f"CO{co_no}",
            min_value=0.0,
            max_value=maximum,
            value=min(
                existing_marks.get(
                    co_no,
                    0.0
                ),
                maximum
            ),
            step=0.5,
            key=f"student_{selected_student_id}_co_{co_no}"
        )


# --------------------------------------------------------
# Save Manual CO Marks
# --------------------------------------------------------

if st.button(
    "💾 Save CO Marks",
    type="secondary"
):

    try:

        for co_no, marks_value in co_marks_values.items():

            execute_query(
                """
                INSERT INTO co_marks
                (
                    course_id,
                    student_id,
                    co_no,
                    marks
                )
                VALUES (?, ?, ?, ?)

                ON CONFLICT(
                    course_id,
                    student_id,
                    co_no
                )

                DO UPDATE SET
                    marks=excluded.marks
                """,
                (
                    course["id"],
                    selected_student_id,
                    co_no,
                    marks_value
                )
            )

        st.success(
            f"CO marks saved for student "
            f"{selected_student_id}."
        )

        st.rerun()

    except Exception as e:

        st.error(
            "Unable to save CO marks."
        )

        st.exception(e)


# ========================================================
# CO ATTAINMENT CALCULATION
# ========================================================

st.divider()

st.subheader("📊 CO Attainment Calculation")

if distribution_total != 100:

    st.warning(
        "Set the CO assessment distribution total to 100 "
        "before calculating attainment."
    )

else:

    co_attainment_rows = []

    for co in cos:

        co_no = int(
            co["co_no"]
        )

        maximum = float(
            co_distribution[co_no]
        )

        co_data = fetch_dataframe(
            """
            SELECT
                cm.student_id,
                cm.marks
            FROM co_marks cm
            INNER JOIN marks m
                ON m.course_id = cm.course_id
                AND m.student_id = cm.student_id
            WHERE cm.course_id=?
            AND cm.co_no=?
            """,
            (
                course["id"],
                co_no
            )
        )

        if co_data.empty:

            average_marks = 0.0
            direct_attainment = 0.0

        else:

            average_marks = float(
                co_data["marks"].mean()
            )

            if maximum > 0:

                direct_attainment = (
                    average_marks / maximum
                ) * 100.0

            else:

                direct_attainment = 0.0

        co_attainment_rows.append(
            {
                "CO": f"CO{co_no}",
                "Maximum Marks": round(
                    maximum,
                    2
                ),
                "Average Marks": round(
                    average_marks,
                    2
                ),
                "Direct Attainment (%)": round(
                    direct_attainment,
                    2
                )
            }
        )

    attainment_df = pd.DataFrame(
        co_attainment_rows
    )

    st.dataframe(
        attainment_df,
        use_container_width=True,
        hide_index=True
    )

    st.success(
        "CO attainment calculated from the generated/manual "
        "CO-wise marks."
    )
