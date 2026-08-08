"""
OBE Analytics Pro v1.3
04_CO_Distribution.py
STEP 8 - CO DISTRIBUTION

Defines assessment-to-CO distribution for the Active Course.

Rules:
1. Theory:
   CE -> CO1-CO5 equally
   S1 -> CO1-CO2 equally
   S2 -> CO3-CO5 equally
   These distributions are fixed by the system.

2. Theory + Practical:
   Theory:
       CE -> CO1-CO5 equally
       S1 -> CO1-CO2 equally
       S2 -> CO3-CO5 equally
   Practical is FIXED:
       Record Work -> CO1-CO5 equally
       Mid 1       -> CO1-CO2 equally
       Mid 2       -> CO3-CO5 equally

3. Capstone Project:
   Continuous Evaluation /100 -> CO1-CO5 equally

4. Internship:
   Continuous Evaluation /50 -> CO1-CO5 equally

This module stores distribution rules only.
It does NOT calculate CO attainment or PO attainment.
"""

from __future__ import annotations

import sqlite3
from typing import Dict, List

import streamlit as st

from database import (
    execute_query,
    fetch_all,
    fetch_one,
    get_active_course,
    get_connection,
    initialize_database,
)


# ------------------------------------------------------------
# Page Configuration
# ------------------------------------------------------------

st.set_page_config(
    page_title="OBE Analytics Pro - CO Distribution",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

initialize_database()


# ------------------------------------------------------------
# Database Migration
# ------------------------------------------------------------

def ensure_co_distribution_table() -> None:
    """Create the assessment-to-CO distribution table if needed."""

    conn = get_connection()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS co_distribution(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            assessment TEXT NOT NULL,
            co_no INTEGER NOT NULL,
            distribution REAL NOT NULL DEFAULT 0,
            FOREIGN KEY(course_id) REFERENCES course(id),
            UNIQUE(course_id, assessment, co_no)
        )
        """
    )

    conn.commit()
    conn.close()


ensure_co_distribution_table()


# ------------------------------------------------------------
# Constants
# ------------------------------------------------------------

CO_NUMBERS = [1, 2, 3, 4, 5]

THEORY_ASSESSMENTS = [
    "CE",
    "S1",
    "S2",
]

PRACTICAL_ASSESSMENTS = [
    "Record Work",
    "Mid 1",
    "Mid 2",
]

FIXED_DISTRIBUTION = {
    "Record Work": {
        1: 20.0,
        2: 20.0,
        3: 20.0,
        4: 20.0,
        5: 20.0,
    },
    "Mid 1": {
        1: 50.0,
        2: 50.0,
        3: 0.0,
        4: 0.0,
        5: 0.0,
    },
    "Mid 2": {
        1: 0.0,
        2: 0.0,
        3: 100.0 / 3.0,
        4: 100.0 / 3.0,
        5: 100.0 / 3.0,
    },
    "Continuous Evaluation": {
        1: 20.0,
        2: 20.0,
        3: 20.0,
        4: 20.0,
        5: 20.0,
    },
}


# ------------------------------------------------------------
# Active Course
# ------------------------------------------------------------

active_course = get_active_course()

st.title("📊 CO Distribution")
st.caption(
    "OBE Analytics Pro v1.3 · CO Distribution"
)

if active_course is None:
    st.warning(
        "No Active Course is selected. "
        "Go to Course Management and select an Active Course first."
    )
    st.stop()

course_id = int(active_course["id"])
course_type = active_course["course_type"] or "Theory"

st.success(
    f"Active Course: {active_course['course_code']} - "
    f"{active_course['course_name']} | {course_type}"
)


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def get_distribution(
    course_id: int,
    assessment: str,
) -> Dict[int, float]:

    rows = fetch_all(
        """
        SELECT co_no, distribution
        FROM co_distribution
        WHERE course_id=?
          AND assessment=?
        ORDER BY co_no
        """,
        (course_id, assessment),
    )

    return {
        int(row["co_no"]): float(row["distribution"])
        for row in rows
    }


def save_distribution(
    course_id: int,
    assessment: str,
    values: Dict[int, float],
) -> None:

    conn = get_connection()

    for co_no, distribution in values.items():

        conn.execute(
            """
            INSERT INTO co_distribution(
                course_id,
                assessment,
                co_no,
                distribution
            )
            VALUES (?, ?, ?, ?)
            ON CONFLICT(course_id, assessment, co_no)
            DO UPDATE SET
                distribution=excluded.distribution
            """,
            (
                course_id,
                assessment,
                co_no,
                distribution,
            ),
        )

    conn.commit()
    conn.close()


def validate_distribution(
    values: Dict[int, float],
) -> str | None:

    for co_no in CO_NUMBERS:

        value = float(values.get(co_no, 0.0))

        if value < 0 or value > 100:
            return (
                f"CO{co_no} distribution must be "
                "between 0% and 100%."
            )

    total = sum(
        float(values.get(co_no, 0.0))
        for co_no in CO_NUMBERS
    )

    if abs(total - 100.0) > 0.01:
        return (
            f"Distribution total is {total:.2f}%. "
            "It must equal exactly 100%."
        )

    return None


def render_distribution_table(
    assessment: str,
    values: Dict[int, float],
    editable: bool,
) -> Dict[int, float]:

    st.markdown(f"#### {assessment}")

    if editable:

        cols = st.columns(5)

        result = {}

        for index, co_no in enumerate(CO_NUMBERS):

            with cols[index]:

                result[co_no] = st.number_input(
                    f"CO{co_no} (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(
                        values.get(co_no, 0.0)
                    ),
                    step=1.0,
                    key=(
                        f"dist_{course_id}_"
                        f"{assessment}_{co_no}"
                    ),
                )

        total = sum(result.values())

        if abs(total - 100.0) < 0.01:
            st.success(f"Total: {total:.2f}%")
        else:
            st.warning(
                f"Total: {total:.2f}% — must be 100%"
            )

        return result

    else:

        display = [
            {
                "CO": f"CO{co_no}",
                "Distribution (%)": round(
                    values.get(co_no, 0.0),
                    2,
                ),
            }
            for co_no in CO_NUMBERS
        ]

        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True,
        )

        st.success(
            f"Total: {sum(values.values()):.2f}%"
        )

        return values


# ------------------------------------------------------------
# Check CO definitions
# ------------------------------------------------------------

co_rows = fetch_all(
    """
    SELECT co_no, co_statement
    FROM co
    WHERE course_id=?
    ORDER BY co_no
    """,
    (course_id,),
)

defined_co_numbers = {
    int(row["co_no"])
    for row in co_rows
    if row["co_no"] is not None
}

if not all(co_no in defined_co_numbers for co_no in CO_NUMBERS):

    missing = [
        f"CO{co_no}"
        for co_no in CO_NUMBERS
        if co_no not in defined_co_numbers
    ]

    st.warning(
        "CO definitions are incomplete. Missing: "
        + ", ".join(missing)
        + ". Please complete CO Entry first."
    )


# ------------------------------------------------------------
# THEORY DISTRIBUTION
# ------------------------------------------------------------

FIXED_THEORY_DISTRIBUTION = {
    "CE": {
        1: 20.0,
        2: 20.0,
        3: 20.0,
        4: 20.0,
        5: 20.0,
    },
    "S1": {
        1: 50.0,
        2: 50.0,
        3: 0.0,
        4: 0.0,
        5: 0.0,
    },
    "S2": {
        1: 0.0,
        2: 0.0,
        3: 100.0 / 3.0,
        4: 100.0 / 3.0,
        5: 100.0 / 3.0,
    },
}


if course_type in {
    "Theory",
    "Theory + Practical",
}:

    st.divider()
    st.subheader("Theory Component")

    st.info(
        "Theory CO distribution is fixed by the system. "
        "Faculty cannot manually edit these values."
    )

    for assessment in THEORY_ASSESSMENTS:

        values = FIXED_THEORY_DISTRIBUTION[assessment]

        save_distribution(
            course_id,
            assessment,
            values,
        )

        render_distribution_table(
            assessment,
            values,
            editable=False,
        )

        if assessment != "S2":
            st.divider()


# ------------------------------------------------------------
# PRACTICAL DISTRIBUTION
# ------------------------------------------------------------

if course_type == "Theory + Practical":

    st.divider()
    st.subheader("Practical Component")

    st.info(
        "The Practical CO distribution is fixed by the system. "
        "Faculty cannot edit these values."
    )

    for assessment in PRACTICAL_ASSESSMENTS:

        values = FIXED_DISTRIBUTION[assessment]

        save_distribution(
            course_id,
            assessment,
            values,
        )

        render_distribution_table(
            assessment,
            values,
            editable=False,
        )

        if assessment != "Mid 2":
            st.divider()


# ------------------------------------------------------------
# CAPSTONE
# ------------------------------------------------------------

if course_type == "Capstone Project":

    st.divider()
    st.subheader("Capstone Project")

    st.info(
        "Continuous Evaluation /100 is distributed equally "
        "across CO1–CO5."
    )

    values = FIXED_DISTRIBUTION[
        "Continuous Evaluation"
    ]

    save_distribution(
        course_id,
        "Continuous Evaluation",
        values,
    )

    render_distribution_table(
        "Continuous Evaluation /100",
        values,
        editable=False,
    )


# ------------------------------------------------------------
# INTERNSHIP
# ------------------------------------------------------------

if course_type == "Internship":

    st.divider()
    st.subheader("Internship")

    st.info(
        "Continuous Evaluation /50 is distributed equally "
        "across CO1–CO5."
    )

    values = FIXED_DISTRIBUTION[
        "Continuous Evaluation"
    ]

    save_distribution(
        course_id,
        "Continuous Evaluation",
        values,
    )

    render_distribution_table(
        "Continuous Evaluation /50",
        values,
        editable=False,
    )


# ------------------------------------------------------------
# Current Saved Distribution
# ------------------------------------------------------------

st.divider()
st.subheader("Saved CO Distribution")

saved_rows = fetch_all(
    """
    SELECT
        assessment,
        co_no,
        distribution
    FROM co_distribution
    WHERE course_id=?
    ORDER BY
        CASE assessment
            WHEN 'CE' THEN 1
            WHEN 'S1' THEN 2
            WHEN 'S2' THEN 3
            WHEN 'Record Work' THEN 4
            WHEN 'Mid 1' THEN 5
            WHEN 'Mid 2' THEN 6
            WHEN 'Continuous Evaluation' THEN 7
            ELSE 99
        END,
        co_no
    """,
    (course_id,),
)

if saved_rows:

    saved_table = []

    for row in saved_rows:

        saved_table.append(
            {
                "Assessment": row["assessment"],
                "CO": f"CO{row['co_no']}",
                "Distribution (%)": round(
                    float(row["distribution"]),
                    2,
                ),
            }
        )

    st.dataframe(
        saved_table,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "No CO distribution has been saved yet."
    )


st.caption(
    "STEP 8 defines assessment-to-CO distribution only. "
    "CO attainment and PO attainment calculations are not "
    "performed in this module."
)
