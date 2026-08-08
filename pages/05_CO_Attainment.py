"""
OBE Analytics Pro v1.3
05_CO_Attainment.py
STEP 9 - CO ATTAINMENT

Uses the fixed assessment-to-CO distribution defined for v1.3.

THEORY
    CE  -> CO1-CO5 equally
    S1  -> CO1-CO2 equally
    S2  -> CO3-CO5 equally

    CE /25, S1 /30, S2 /45
    Each CO maximum = 20 marks.

THEORY + PRACTICAL
    Theory = 70%
        CE /25, S1 /30, S2 /45
        Fixed Theory CO distribution as above.

    Practical = 30%
        Record Work /60 -> CO1-CO5 equally
        Mid 1 /20       -> CO1-CO2 equally
        Mid 2 /20       -> CO3-CO5 equally

    Practical CO maximums are assessment-derived and therefore:
        CO1/CO2 = 60/5 + 20/2 = 22
        CO3/CO4/CO5 = 60/5 + 20/3 = 18.6667

    Practical attainment is normalized to 100% per CO and then
    weighted by 30%. Theory attainment is weighted by 70%.

CAPSTONE PROJECT
    Continuous Evaluation /100 -> CO1-CO5 equally.

INTERNSHIP
    Continuous Evaluation /50 -> CO1-CO5 equally.

CE grade conversion has already been performed during marks entry
for Theory and Theory + Practical:
    O=25, A+=22.25, A=19.75, B+=17.25, B=14.75,
    C=13.50, P=12.25, L/F=0.

This module:
    - generates CO-wise student marks using fixed rules
    - applies the institutional 70% student threshold
    - calculates Student Achievement (%) for each CO
    - assigns CO Attainment Level 0/1/2/3
    - stores generated CO marks in co_marks
    - stores Student Achievement (%) and Attainment Level in co_attainment

Institutional CO Attainment Rule:
    Student threshold = 70% of the maximum marks allocated to the CO.

    >= 60% students meeting the threshold -> Level 3 (High)
    >= 50% students meeting the threshold -> Level 2 (Medium)
    >= 40% students meeting the threshold -> Level 1 (Low)
    <  40% students meeting the threshold -> Level 0 (Not Attained)

It does NOT calculate CO-PO mapping or PO attainment.
"""

from __future__ import annotations

import sqlite3
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st

from database import (
    execute_query,
    fetch_all,
    fetch_dataframe,
    get_active_course,
    get_connection,
    initialize_database,
)


# ------------------------------------------------------------
# Page Configuration
# ------------------------------------------------------------

st.set_page_config(
    page_title="CO Attainment",
    page_icon="🎯",
    layout="wide",
)

initialize_database()
def ensure_co_attainment_columns() -> None:
    """Add v1.4 CO-attainment evidence columns safely."""

    conn = get_connection()

    try:
        columns = {
            row[1]
            for row in conn.execute(
                "PRAGMA table_info(co_attainment)"
            ).fetchall()
        }

        if "achievement_percent" not in columns:
            conn.execute(
                """
                ALTER TABLE co_attainment
                ADD COLUMN achievement_percent REAL DEFAULT 0
                """
            )

        if "attainment_level" not in columns:
            conn.execute(
                """
                ALTER TABLE co_attainment
                ADD COLUMN attainment_level INTEGER DEFAULT 0
                """
            )

        conn.commit()

    finally:
        conn.close()

ensure_co_attainment_columns()


# ------------------------------------------------------------
# Fixed Assessment Rules
# ------------------------------------------------------------

THEORY_DISTRIBUTION = {
    "CE": {1: 0.20, 2: 0.20, 3: 0.20, 4: 0.20, 5: 0.20},
    "S1": {1: 0.50, 2: 0.50, 3: 0.00, 4: 0.00, 5: 0.00},
    "S2": {1: 0.00, 2: 0.00, 3: 1 / 3, 4: 1 / 3, 5: 1 / 3},
}

THEORY_MAX = {
    "CE": 25.0,
    "S1": 30.0,
    "S2": 45.0,
}

PRACTICAL_DISTRIBUTION = {
    "Record Work": {1: 0.20, 2: 0.20, 3: 0.20, 4: 0.20, 5: 0.20},
    "Mid 1": {1: 0.50, 2: 0.50, 3: 0.00, 4: 0.00, 5: 0.00},
    "Mid 2": {1: 0.00, 2: 0.00, 3: 1 / 3, 4: 1 / 3, 5: 1 / 3},
}

PRACTICAL_MAX = {
    "Record Work": 60.0,
    "Mid 1": 20.0,
    "Mid 2": 20.0,
}

CO_NUMBERS = [1, 2, 3, 4, 5]


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def safe_float(value) -> float:
    if value is None or pd.isna(value):
        return 0.0
    return float(value)


def calculate_theory_co_marks(row) -> Dict[int, float]:
    """Return raw theory CO marks, maximum 20 for each CO."""

    ce = safe_float(row["ce"])
    s1 = safe_float(row["s1"])
    s2 = safe_float(row["s2"])

    return {
        1: ce * 0.20 + s1 * 0.50,
        2: ce * 0.20 + s1 * 0.50,
        3: ce * 0.20 + s2 * (1 / 3),
        4: ce * 0.20 + s2 * (1 / 3),
        5: ce * 0.20 + s2 * (1 / 3),
    }


def calculate_practical_co_marks(row) -> Dict[int, float]:
    """Return raw practical CO marks using fixed distributions."""

    record_work = safe_float(row["record_work"])
    mid1 = safe_float(row["mid1"])
    mid2 = safe_float(row["mid2"])

    return {
        1: record_work * 0.20 + mid1 * 0.50,
        2: record_work * 0.20 + mid1 * 0.50,
        3: record_work * 0.20 + mid2 * (1 / 3),
        4: record_work * 0.20 + mid2 * (1 / 3),
        5: record_work * 0.20 + mid2 * (1 / 3),
    }


def practical_co_maximums() -> Dict[int, float]:
    return {
        1: 60.0 * 0.20 + 20.0 * 0.50,
        2: 60.0 * 0.20 + 20.0 * 0.50,
        3: 60.0 * 0.20 + 20.0 * (1 / 3),
        4: 60.0 * 0.20 + 20.0 * (1 / 3),
        5: 60.0 * 0.20 + 20.0 * (1 / 3),
    }



def attainment_level_from_student_percent(student_percent: float) -> int:
    """Return institutional CO attainment level 0-3."""

    if student_percent >= 60.0:
        return 3

    if student_percent >= 50.0:
        return 2

    if student_percent >= 40.0:
        return 1

    return 0


def calculate_theory_co_maximums() -> Dict[int, float]:
    """Maximum Theory CO marks after fixed distribution."""

    return {
        1: 20.0,
        2: 20.0,
        3: 20.0,
        4: 20.0,
        5: 20.0,
    }


def calculate_practical_co_maximums() -> Dict[int, float]:
    """Maximum Practical CO marks from the fixed assessments."""

    return {
        1: 60.0 * 0.20 + 20.0 * 0.50,
        2: 60.0 * 0.20 + 20.0 * 0.50,
        3: 60.0 * 0.20 + 20.0 * (1 / 3),
        4: 60.0 * 0.20 + 20.0 * (1 / 3),
        5: 60.0 * 0.20 + 20.0 * (1 / 3),
    }


def calculate_student_co_result(
    row,
    course_type: str
) -> Tuple[Dict[int, float], Dict[int, float], Dict[int, float]]:
    """
    Return:
        final CO marks,
        CO maximum marks,
        student-level CO achievement percentages.

    The returned achievement percentage is the percentage of the
    maximum CO marks achieved by this student.

    For Theory + Practical, the 70:30 course weighting is applied
    at the CO level before the student-level 70% threshold is tested.
    """

    if course_type == "Theory":

        theory_marks = calculate_theory_co_marks(row)
        theory_maximums = calculate_theory_co_maximums()

        achievement = {
            co_no: (
                theory_marks[co_no]
                / theory_maximums[co_no]
                * 100.0
                if theory_maximums[co_no] > 0
                else 0.0
            )
            for co_no in CO_NUMBERS
        }

        return (
            theory_marks,
            theory_maximums,
            achievement,
        )

    if course_type == "Theory + Practical":

        theory_marks = calculate_theory_co_marks(row)
        practical_marks = calculate_practical_co_marks(row)

        theory_maximums = calculate_theory_co_maximums()
        practical_maximums = calculate_practical_co_maximums()

        # The course-level 70:30 weighting is applied to each
        # student's CO marks and CO maximums.
        final_marks = {}
        final_maximums = {}
        achievement = {}

        for co_no in CO_NUMBERS:

            weighted_theory_max = (
                0.70 * theory_maximums[co_no]
            )

            weighted_practical_max = (
                0.30 * practical_maximums[co_no]
            )

            final_maximum = (
                weighted_theory_max
                + weighted_practical_max
            )

            weighted_theory_marks = (
                0.70 * theory_marks[co_no]
            )

            weighted_practical_marks = (
                0.30 * practical_marks[co_no]
            )

            final_mark = (
                weighted_theory_marks
                + weighted_practical_marks
            )

            final_maximums[co_no] = final_maximum
            final_marks[co_no] = final_mark

            achievement[co_no] = (
                final_mark / final_maximum * 100.0
                if final_maximum > 0
                else 0.0
            )

        return (
            final_marks,
            final_maximums,
            achievement,
        )

    if course_type == "Capstone Project":

        ce = safe_float(row["continuous_evaluation"])

        # CE /100, equally distributed across 5 COs.
        co_marks = {
            co_no: ce / 5.0
            for co_no in CO_NUMBERS
        }

        # Each CO maximum = 100/5 = 20.
        co_maximums = {
            co_no: 20.0
            for co_no in CO_NUMBERS
        }

        achievement = {
            co_no: (
                co_marks[co_no]
                / co_maximums[co_no]
                * 100.0
            )
            for co_no in CO_NUMBERS
        }

        return (
            co_marks,
            co_maximums,
            achievement,
        )

    if course_type == "Internship":

        ce = safe_float(row["continuous_evaluation"])

        # CE /50, equally distributed across 5 COs.
        co_marks = {
            co_no: ce / 5.0
            for co_no in CO_NUMBERS
        }

        # Each CO maximum = 50/5 = 10.
        co_maximums = {
            co_no: 10.0
            for co_no in CO_NUMBERS
        }

        achievement = {
            co_no: (
                co_marks[co_no]
                / co_maximums[co_no]
                * 100.0
            )
            for co_no in CO_NUMBERS
        }

        return (
            co_marks,
            co_maximums,
            achievement,
        )

    raise ValueError(
        f"Unsupported Course Type: {course_type}"
    )


def save_co_mark(
    course_id: int,
    student_id: str,
    co_no: int,
    marks_value: float,
) -> None:

    execute_query(
        """
        INSERT INTO co_marks(
            course_id,
            student_id,
            co_no,
            marks
        )
        VALUES (?, ?, ?, ?)
        ON CONFLICT(course_id, student_id, co_no)
        DO UPDATE SET
            marks=excluded.marks
        """,
        (
            course_id,
            student_id,
            co_no,
            marks_value,
        ),
    )


def save_co_attainment(
    course_id: int,
    co_no: int,
    achievement_percent: float,
    attainment_level: int,
) -> None:

    execute_query(
        """
        INSERT INTO co_attainment(
            course_id,
            co_no,
            attainment,
            achievement_percent,
            attainment_level
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            course_id,
            co_no,
            achievement_percent,
            achievement_percent,
            attainment_level,
        ),
    )


def clear_course_attainment(course_id: int) -> None:

    execute_query(
        """
        DELETE FROM co_attainment
        WHERE course_id=?
        """,
        (course_id,),
    )


# ------------------------------------------------------------
# Active Course
# ------------------------------------------------------------

course = get_active_course()

st.title("🎯 CO Attainment")

if course is None:
    st.warning(
        "Please select an Active Course from Course Management."
    )
    st.stop()

course_id = int(course["id"])
course_type = course["course_type"] or "Theory"

st.success(
    f"**Active Course:** {course['course_code']} - "
    f"{course['course_name']} | {course_type}"
)

st.caption(
    f"Academic Year: {course['academic_year'] or 'Not specified'}"
)


# ------------------------------------------------------------
# CO Validation
# ------------------------------------------------------------

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
    (course_id,),
)

co_numbers = {
    int(row["co_no"])
    for row in cos
    if row["co_no"] is not None
}

if len(cos) != 5 or co_numbers != set(CO_NUMBERS):

    st.error(
        "CO Attainment requires CO1–CO5 to be defined "
        "for the Active Course."
    )
    st.stop()


# ------------------------------------------------------------
# Load Student Marks
# ------------------------------------------------------------

students = fetch_dataframe(
    """
    SELECT
        student_id,
        student_name,
        ce,
        ce_grade,
        s1,
        s2,
        record_work,
        mid1,
        mid2,
        continuous_evaluation
    FROM marks
    WHERE course_id=?
    ORDER BY student_id
    """,
    (course_id,),
)

if students.empty:

    st.warning(
        "No student marks are available for this course."
    )
    st.stop()

st.info(
    f"Total Students: {len(students)}"
)


# ------------------------------------------------------------
# Assessment Rules Display
# ------------------------------------------------------------

st.divider()
st.subheader("Fixed CO Assessment Distribution")

if course_type in {"Theory", "Theory + Practical"}:

    theory_table = pd.DataFrame(
        [
            {
                "Assessment": "CE",
                "CO1": "20%",
                "CO2": "20%",
                "CO3": "20%",
                "CO4": "20%",
                "CO5": "20%",
            },
            {
                "Assessment": "S1",
                "CO1": "50%",
                "CO2": "50%",
                "CO3": "—",
                "CO4": "—",
                "CO5": "—",
            },
            {
                "Assessment": "S2",
                "CO1": "—",
                "CO2": "—",
                "CO3": "33.33%",
                "CO4": "33.33%",
                "CO5": "33.33%",
            },
        ]
    )

    st.markdown("**Theory Component**")
    st.dataframe(
        theory_table,
        use_container_width=True,
        hide_index=True,
    )

if course_type == "Theory + Practical":

    practical_table = pd.DataFrame(
        [
            {
                "Assessment": "Record Work",
                "Maximum": 60,
                "CO Distribution": "CO1–CO5 equally",
            },
            {
                "Assessment": "Mid 1",
                "Maximum": 20,
                "CO Distribution": "CO1–CO2 equally",
            },
            {
                "Assessment": "Mid 2",
                "Maximum": 20,
                "CO Distribution": "CO3–CO5 equally",
            },
        ]
    )

    st.markdown("**Practical Component — 30%**")
    st.dataframe(
        practical_table,
        use_container_width=True,
        hide_index=True,
    )

    st.info(
        "Theory = 70% and Practical = 30%. "
        "Practical CO attainment is normalized per CO before "
        "applying the 30% practical weight."
    )

if course_type == "Capstone Project":

    st.info(
        "Continuous Evaluation /100 is distributed equally "
        "across CO1–CO5."
    )

if course_type == "Internship":

    st.info(
        "Continuous Evaluation /50 is distributed equally "
        "across CO1–CO5."
    )


# ------------------------------------------------------------
# Generate CO Marks and Calculate Attainment
# ------------------------------------------------------------

st.divider()
st.subheader("CO Attainment Calculation")

st.write(
    "The system applies the institutional CO Attainment rule: "
    "a student must score at least 70% of the maximum CO marks. "
    "The CO level is then assigned from the percentage of students "
    "meeting that threshold."
)

if st.button(
    "Calculate CO Attainment",
    type="primary",
    key="calculate_co_attainment_v13",
):

    try:

        generated_count = 0

        student_achievement = {
            co_no: []
            for co_no in CO_NUMBERS
        }

        co_maximums = {
            co_no: []
            for co_no in CO_NUMBERS
        }

        clear_course_attainment(course_id)

        for _, student in students.iterrows():

            student_id = str(
                student["student_id"]
            )

            (
                final_co_marks,
                final_co_maximums,
                achievement
            ) = calculate_student_co_result(
                student,
                course_type,
            )

            for co_no in CO_NUMBERS:

                save_co_mark(
                    course_id=course_id,
                    student_id=student_id,
                    co_no=co_no,
                    marks_value=final_co_marks[co_no],
                )

                student_achievement[co_no].append(
                    achievement[co_no]
                )

                co_maximums[co_no].append(
                    final_co_maximums[co_no]
                )

            generated_count += 1

        final_rows = []

        for co_no in CO_NUMBERS:

            achievement_values = student_achievement[co_no]

            maximum_values = co_maximums[co_no]

            # Student qualifies when the student's CO achievement
            # is at least 70% of the CO maximum.
            qualifying_students = sum(
                1
                for value in achievement_values
                if value >= 70.0
            )

            total_students = len(
                achievement_values
            )

            student_percent = (
                qualifying_students
                / total_students
                * 100.0
                if total_students > 0
                else 0.0
            )

            attainment_level = (
                attainment_level_from_student_percent(
                    student_percent
                )
            )

            representative_maximum = (
                maximum_values[0]
                if maximum_values
                else 0.0
            )

            threshold = (
                representative_maximum * 0.70
            )

            save_co_attainment(
                course_id=course_id,
                co_no=co_no,
                achievement_percent=student_percent,
                attainment_level=attainment_level,
            )

            final_rows.append(
                {
                    "CO": f"CO{co_no}",
                    "CO Maximum Marks": round(
                        representative_maximum,
                        4,
                    ),
                    "70% Threshold": round(
                        threshold,
                        4,
                    ),
                    "Students ≥ Threshold": (
                        f"{qualifying_students}/"
                        f"{total_students}"
                    ),
                    "Student Achievement (%)": round(
                        student_percent,
                        2,
                    ),
                    "CO Attainment Level": (
                        f"{attainment_level} – "
                        f"{['Not Attained', 'Low', 'Medium', 'High'][attainment_level]}"
                    ),
                }
            )

        st.success(
            f"CO attainment calculated successfully for "
            f"{generated_count} students."
        )

        st.dataframe(
            pd.DataFrame(final_rows),
            use_container_width=True,
            hide_index=True,
        )

    except Exception as exc:

        st.error(
            "Unable to calculate CO attainment."
        )
        st.exception(exc)


# ------------------------------------------------------------
# Stored CO Attainment
# ------------------------------------------------------------

st.divider()
st.subheader("Stored CO Attainment")

stored = fetch_all(
    """
    SELECT
        co_no,
        attainment,
        achievement_percent,
        attainment_level
    FROM co_attainment
    WHERE course_id=?
    ORDER BY co_no
    """,
    (course_id,),
)

if stored:

    stored_table = pd.DataFrame(
        [
            {
                "CO": f"CO{row['co_no']}",
                "Student Achievement (%)": round(
                    float(
                        row["achievement_percent"]
                        if row["achievement_percent"] is not None
                        else row["attainment"]
                    ),
                    2,
                ),
                "Attainment Level": (
                    f"{int(row['attainment_level'])} – "
                    f"{['Not Attained', 'Low', 'Medium', 'High'][int(row['attainment_level'])]}"
                ),
            }
            for row in stored
        ]
    )

    st.dataframe(
        stored_table,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "CO attainment has not been calculated yet."
    )


# ------------------------------------------------------------
# CO-wise Student Marks
# ------------------------------------------------------------

st.divider()
st.subheader("Generated CO-wise Student Marks")

co_marks_data = fetch_dataframe(
    """
    SELECT
        cm.student_id AS "Roll Number",
        m.student_name AS "Student Name",
        cm.co_no AS "CO",
        cm.marks AS "CO Marks"
    FROM co_marks cm
    INNER JOIN marks m
        ON m.course_id=cm.course_id
       AND m.student_id=cm.student_id
    WHERE cm.course_id=?
    ORDER BY cm.student_id, cm.co_no
    """,
    (course_id,),
)

if not co_marks_data.empty:

    st.dataframe(
        co_marks_data,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "CO-wise marks have not been generated yet."
    )


st.caption(
    "CO Attainment uses the institutional 70% student threshold "
    "and 0/1/2/3 attainment levels. CO–PO Mapping and PO Attainment "
    "are separate modules."
)
