"""
OBE Analytics Pro v1.3
02_CO_Entry.py
STEP 6 - COURSE OUTCOME ENTRY

For the selected Active Course, enter exactly five Course Outcomes:
CO1 through CO5.

Fields:
- CO Number
- CO Statement
- Bloom Level

Bloom levels:
L1 - Remember
L2 - Understand
L3 - Apply
L4 - Analyze
L5 - Evaluate
L6 - Create

CO data is stored in the existing `co` table:
    id, course_id, co_no, co_statement, bloom_level

This module does not perform CO attainment, CO distribution,
CO-PO mapping, or PO calculations.
"""

from __future__ import annotations

import sqlite3
import streamlit as st

from database import (
    execute_query,
    fetch_all,
    fetch_one,
    get_active_course,
    initialize_database,
)


# ------------------------------------------------------------
# Page Configuration
# ------------------------------------------------------------

st.set_page_config(
    page_title="OBE Analytics Pro - CO Entry",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

initialize_database()


def ensure_pso_table() -> None:
    """Create the PSO table if it does not already exist."""
    conn = __import__("database").get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS pso(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER,
            pso_no INTEGER,
            pso_statement TEXT,
            FOREIGN KEY(course_id) REFERENCES course(id),
            UNIQUE(course_id, pso_no)
        )
        """
    )
    conn.commit()
    conn.close()


ensure_pso_table()


# ------------------------------------------------------------
# Constants
# ------------------------------------------------------------

BLOOM_LEVELS = [
    "L1 - Remember",
    "L2 - Understand",
    "L3 - Apply",
    "L4 - Analyze",
    "L5 - Evaluate",
    "L6 - Create",
]

CO_NUMBERS = [1, 2, 3, 4, 5]
PSO_NUMBERS = [1, 2, 3]


# ------------------------------------------------------------
# Active Course
# ------------------------------------------------------------

active_course = get_active_course()

st.title("🎯 Course Outcomes")
st.caption(
    "OBE Analytics Pro v1.3 · STEP 6 - CO Entry"
)

if active_course is None:
    st.warning(
        "No Active Course is selected. "
        "Go to Course Management and select an Active Course first."
    )
    st.stop()

course_id = int(active_course["id"])

st.success(
    f"Active Course: {active_course['course_code']} - "
    f"{active_course['course_name']}"
)

if active_course["academic_year"]:
    st.caption(
        f"Academic Year: {active_course['academic_year']}"
    )

st.divider()


# ------------------------------------------------------------
# PSO Database Functions
# ------------------------------------------------------------

def get_program_specific_outcomes(course_id: int):
    return fetch_all(
        """
        SELECT
            id,
            course_id,
            pso_no,
            pso_statement
        FROM pso
        WHERE course_id=?
        ORDER BY pso_no
        """,
        (course_id,),
    )


def get_existing_pso(course_id: int, pso_no: int):
    return fetch_one(
        """
        SELECT
            id,
            pso_statement
        FROM pso
        WHERE course_id=?
          AND pso_no=?
        """,
        (course_id, pso_no),
    )


def save_pso(
    course_id: int,
    pso_no: int,
    pso_statement: str,
) -> None:

    existing = get_existing_pso(course_id, pso_no)

    if existing:
        execute_query(
            """
            UPDATE pso
            SET pso_statement=?
            WHERE course_id=?
              AND pso_no=?
            """,
            (
                pso_statement,
                course_id,
                pso_no,
            ),
        )
    else:
        execute_query(
            """
            INSERT INTO pso(
                course_id,
                pso_no,
                pso_statement
            )
            VALUES (?, ?, ?)
            """,
            (
                course_id,
                pso_no,
                pso_statement,
            ),
        )


# ------------------------------------------------------------
# CO Database Functions
# ------------------------------------------------------------

def get_course_outcomes(course_id: int):
    return fetch_all(
        """
        SELECT
            id,
            course_id,
            co_no,
            co_statement,
            bloom_level
        FROM co
        WHERE course_id=?
        ORDER BY co_no
        """,
        (course_id,),
    )


def get_existing_co(course_id: int, co_no: int):
    return fetch_one(
        """
        SELECT
            id,
            co_statement,
            bloom_level
        FROM co
        WHERE course_id=?
          AND co_no=?
        """,
        (course_id, co_no),
    )


def save_co(
    course_id: int,
    co_no: int,
    co_statement: str,
    bloom_level: str,
) -> None:

    existing = get_existing_co(course_id, co_no)

    if existing:
        execute_query(
            """
            UPDATE co
            SET
                co_statement=?,
                bloom_level=?
            WHERE course_id=?
              AND co_no=?
            """,
            (
                co_statement,
                bloom_level,
                course_id,
                co_no,
            ),
        )
    else:
        execute_query(
            """
            INSERT INTO co(
                course_id,
                co_no,
                co_statement,
                bloom_level
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                course_id,
                co_no,
                co_statement,
                bloom_level,
            ),
        )


def delete_course_outcomes(course_id: int) -> None:
    execute_query(
        """
        DELETE FROM co
        WHERE course_id=?
        """,
        (course_id,),
    )


# ------------------------------------------------------------
# Existing COs
# ------------------------------------------------------------

existing_cos = get_course_outcomes(course_id)

existing_map = {
    int(row["co_no"]): row
    for row in existing_cos
    if row["co_no"] is not None
}


# ------------------------------------------------------------
# CO Entry Form
# ------------------------------------------------------------

st.subheader("Course Outcome Entry")

st.info(
    "Enter five Course Outcomes for the selected course. "
    "CO1–CO5 are used by the Theory + Practical fixed practical "
    "CO distribution."
)

with st.form("co_entry_form_v13"):

    co_inputs = {}

    for co_no in CO_NUMBERS:

        row = existing_map.get(co_no)

        default_statement = (
            row["co_statement"]
            if row and row["co_statement"]
            else ""
        )

        default_bloom = (
            row["bloom_level"]
            if row and row["bloom_level"]
            else "L3 - Apply"
        )

        st.markdown(f"### CO{co_no}")

        statement = st.text_area(
            f"CO{co_no} Statement",
            value=default_statement,
            placeholder=(
                f"Enter the Course Outcome statement for CO{co_no}"
            ),
            height=90,
            key=f"co_statement_{co_no}",
        )

        if default_bloom not in BLOOM_LEVELS:
            default_bloom = "L3 - Apply"

        bloom = st.selectbox(
            f"CO{co_no} Bloom Level",
            BLOOM_LEVELS,
            index=BLOOM_LEVELS.index(default_bloom),
            key=f"co_bloom_{co_no}",
        )

        co_inputs[co_no] = {
            "statement": statement,
            "bloom": bloom,
        }

        if co_no < 5:
            st.divider()

    submitted = st.form_submit_button(
        "Save Course Outcomes",
        type="primary",
    )


# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

if submitted:

    errors = []

    for co_no in CO_NUMBERS:

        statement = co_inputs[co_no]["statement"].strip()

        if not statement:
            errors.append(
                f"CO{co_no} statement is required."
            )

    if errors:

        for error in errors:
            st.error(error)

    else:

        try:

            for co_no in CO_NUMBERS:

                save_co(
                    course_id=course_id,
                    co_no=co_no,
                    co_statement=co_inputs[co_no]["statement"].strip(),
                    bloom_level=co_inputs[co_no]["bloom"],
                )

            st.success(
                "CO1–CO5 saved successfully for the Active Course."
            )

            st.rerun()

        except sqlite3.IntegrityError as exc:

            st.error(
                "The Course Outcomes could not be saved because "
                "of a database constraint."
            )
            st.exception(exc)

        except Exception as exc:

            st.error(
                "Unable to save Course Outcomes."
            )
            st.exception(exc)


# ------------------------------------------------------------
# PSO Entry
# ------------------------------------------------------------

st.divider()
st.subheader("Program Specific Outcomes (PSOs)")

st.info(
    "Enter exactly three Program Specific Outcomes (PSO1–PSO3) "
    "for the Active Course."
)

existing_psos = get_program_specific_outcomes(course_id)

existing_pso_map = {
    int(row["pso_no"]): row
    for row in existing_psos
    if row["pso_no"] is not None
}

with st.form("pso_entry_form_v13"):

    pso_inputs = {}

    for pso_no in PSO_NUMBERS:

        row = existing_pso_map.get(pso_no)

        default_statement = (
            row["pso_statement"]
            if row and row["pso_statement"]
            else ""
        )

        st.markdown(f"### PSO{pso_no}")

        statement = st.text_area(
            f"PSO{pso_no} Statement",
            value=default_statement,
            placeholder=(
                f"Enter the Program Specific Outcome statement for PSO{pso_no}"
            ),
            height=90,
            key=f"pso_statement_{pso_no}",
        )

        pso_inputs[pso_no] = statement

        if pso_no < 3:
            st.divider()

    pso_submitted = st.form_submit_button(
        "Save PSO1–PSO3",
        type="primary",
    )


if pso_submitted:

    pso_errors = []

    for pso_no in PSO_NUMBERS:

        statement = pso_inputs[pso_no].strip()

        if not statement:
            pso_errors.append(
                f"PSO{pso_no} statement is required."
            )

    if pso_errors:

        for error in pso_errors:
            st.error(error)

    else:

        try:

            for pso_no in PSO_NUMBERS:
                save_pso(
                    course_id=course_id,
                    pso_no=pso_no,
                    pso_statement=pso_inputs[pso_no].strip(),
                )

            st.success(
                "PSO1–PSO3 saved successfully for the Active Course."
            )

            st.rerun()

        except sqlite3.IntegrityError as exc:

            st.error(
                "The PSOs could not be saved because "
                "of a database constraint."
            )
            st.exception(exc)

        except Exception as exc:

            st.error("Unable to save PSOs.")
            st.exception(exc)


st.subheader("Current PSOs")

current_psos = get_program_specific_outcomes(course_id)

if current_psos:

    pso_table = []

    for row in current_psos:
        pso_table.append(
            {
                "PSO": f"PSO{row['pso_no']}",
                "Program Specific Outcome": (
                    row["pso_statement"] or ""
                ),
            }
        )

    st.dataframe(
        pso_table,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "No PSOs have been entered yet."
    )


# ------------------------------------------------------------
# Current CO Table
# ------------------------------------------------------------

st.divider()
st.subheader("Current Course Outcomes")

current_cos = get_course_outcomes(course_id)

if current_cos:

    table_data = []

    for row in current_cos:

        table_data.append(
            {
                "CO": f"CO{row['co_no']}",
                "Course Outcome": row["co_statement"] or "",
                "Bloom Level": row["bloom_level"] or "",
            }
        )

    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        f"{len(current_cos)} Course Outcome(s) defined "
        f"for the Active Course."
    )

else:

    st.info(
        "No Course Outcomes have been entered yet."
    )


# ------------------------------------------------------------
# Validation
# ------------------------------------------------------------

st.divider()
st.subheader("CO Validation")

current_numbers = sorted(
    int(row["co_no"])
    for row in current_cos
    if row["co_no"] is not None
)

expected_numbers = CO_NUMBERS

if current_numbers == expected_numbers:

    st.success(
        "✓ CO1–CO5 are defined. "
        "The course is ready for the next OBE step."
    )

else:

    missing = [
        f"CO{number}"
        for number in expected_numbers
        if number not in current_numbers
    ]

    extra = [
        f"CO{number}"
        for number in current_numbers
        if number not in expected_numbers
    ]

    if missing:
        st.warning(
            "Missing: " + ", ".join(missing)
        )

    if extra:
        st.warning(
            "Unexpected CO numbers: " + ", ".join(extra)
        )


st.caption(
    "STEP 6 defines CO1–CO5 and PSO1–PSO3. "
    "CO attainment, CO distribution, CO-PO mapping, PSO mapping, "
    "and PO attainment are not calculated in this module."
)
