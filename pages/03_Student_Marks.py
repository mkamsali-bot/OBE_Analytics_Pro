"""
OBE Analytics Pro v1.3
03_Marks_Entry.py
STEP 7 - MARKS ENTRY + CE GRADE CONVERSION

CE grade conversion applies ONLY to:
    1. Theory
    2. Theory + Practical

Grade conversion:
    O   = 100% -> 25.00
    A+  =  89% -> 22.25
    A   =  79% -> 19.75
    B+  =  69% -> 17.25
    B   =  59% -> 14.75
    C   =  54% -> 13.50
    P   =  49% -> 12.25
    L/F =   0% ->  0.00

Normalized CE mark = Upper Value (%) / 4

This module handles data entry/import only.
It does NOT calculate CO attainment or PO attainment.
"""

from __future__ import annotations

import sqlite3
from io import BytesIO
from typing import Any, Dict, List

import pandas as pd
import streamlit as st

from database import (
    execute_query,
    fetch_all,
    fetch_one,
    get_active_course,
    get_connection,
    initialize_database,
)


st.set_page_config(
    page_title="OBE Analytics Pro - Marks Entry",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

initialize_database()


# ------------------------------------------------------------
# CE Grade Conversion
# ------------------------------------------------------------

CE_GRADE_UPPER_PERCENT = {
    "O": 100.0,
    "A+": 89.0,
    "A": 79.0,
    "B+": 69.0,
    "B": 59.0,
    "C": 54.0,
    "P": 49.0,
    "L": 0.0,
    "F": 0.0,
}


def normalize_grade(value: Any) -> str:
    if pd.isna(value):
        return ""

    return str(value).strip().upper().replace(" ", "")


def grade_to_ce_mark(grade: Any) -> float:
    normalized = normalize_grade(grade)

    if normalized not in CE_GRADE_UPPER_PERCENT:
        raise ValueError(
            f"Invalid CE grade '{grade}'. "
            "Allowed grades: O, A+, A, B+, B, C, P, L, F."
        )

    return CE_GRADE_UPPER_PERCENT[normalized] / 4.0


def ensure_marks_columns() -> None:
    """
    Safely extend the existing marks table for the assessment structures.
    Existing data is preserved.
    """
    conn = get_connection()

    columns = {
        row["name"]
        for row in conn.execute(
            "PRAGMA table_info(marks)"
        ).fetchall()
    }

    additions = {
        "ce_grade": "TEXT",
        "record_work": "REAL",
        "mid1": "REAL",
        "mid2": "REAL",
        "continuous_evaluation": "REAL",
    }

    changed = False

    for column, sql_type in additions.items():
        if column not in columns:
            conn.execute(
                f'ALTER TABLE marks ADD COLUMN "{column}" {sql_type}'
            )
            changed = True

    if changed:
        conn.commit()

    conn.close()


ensure_marks_columns()


# ------------------------------------------------------------
# Active Course
# ------------------------------------------------------------

active_course = get_active_course()

st.title("📝 Marks Entry")
st.caption(
    "OBE Analytics Pro v1.3 · STEP 7 - CE Grade Conversion + Marks Import"
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
# Course-specific assessment structure
# ------------------------------------------------------------

st.subheader("Assessment Structure")

if course_type == "Theory":
    st.write("CE Grade → normalized CE mark /25")
    st.write("S1")
    st.write("S2")

elif course_type == "Theory + Practical":
    st.write("Theory: CE + S1 + S2 → 70%")
    st.write("Practical: Record Work /60 + Mid 1 /20 + Mid 2 /20 → 30%")

elif course_type == "Capstone Project":
    st.write("Continuous Evaluation /100")
    st.info(
        "CE grade conversion is not applicable to Capstone Project."
    )

elif course_type == "Internship":
    st.write("Continuous Evaluation /50")
    st.info(
        "CE grade conversion is not applicable to Internship."
    )


# ------------------------------------------------------------
# CE Conversion Reference
# ------------------------------------------------------------

if course_type in {"Theory", "Theory + Practical"}:

    with st.expander(
        "CE Grade → Normalized Mark Conversion",
        expanded=True,
    ):

        conversion_rows = []

        for grade, upper_percent in CE_GRADE_UPPER_PERCENT.items():
            conversion_rows.append(
                {
                    "CE Grade": grade,
                    "Upper Value (%)": upper_percent,
                    "Normalized CE Mark (/25)": round(
                        upper_percent / 4.0,
                        2,
                    ),
                }
            )

        st.dataframe(
            conversion_rows,
            use_container_width=True,
            hide_index=True,
        )


# ------------------------------------------------------------
# Excel Template
# ------------------------------------------------------------

st.divider()
st.subheader("Excel Import")

if course_type == "Theory":
    expected_columns = [
        "Roll Number",
        "Student Name",
        "CE Grade",
        "S1",
        "S2",
    ]

elif course_type == "Theory + Practical":
    expected_columns = [
        "Roll Number",
        "Student Name",
        "CE Grade",
        "S1",
        "S2",
        "Record Work",
        "Mid 1",
        "Mid 2",
    ]

elif course_type == "Capstone Project":
    expected_columns = [
        "Roll Number",
        "Student Name",
        "Continuous Evaluation",
    ]

else:
    expected_columns = [
        "Roll Number",
        "Student Name",
        "Continuous Evaluation",
    ]


st.write("Required Excel columns:")

st.code("\n".join(expected_columns))

template_df = pd.DataFrame(columns=expected_columns)

st.download_button(
    "Download Excel Template",
    data=(
        __import__("io").BytesIO()
    ).getvalue()
    if False
    else template_df.to_csv(index=False).encode("utf-8"),
    file_name=f"{active_course['course_code']}_{course_type.replace(' ', '_')}_Marks_Template.csv",
    mime="text/csv",
)

uploaded_file = st.file_uploader(
    "Upload Student Marks Excel/CSV",
    type=["xlsx", "xls", "csv"],
)


# ------------------------------------------------------------
# Read upload
# ------------------------------------------------------------

def read_uploaded_file(uploaded) -> pd.DataFrame:

    if uploaded.name.lower().endswith(".csv"):
        return pd.read_csv(uploaded)

    return pd.read_excel(uploaded)


def validate_columns(
    dataframe: pd.DataFrame,
    required: List[str],
) -> List[str]:

    actual = {
        str(column).strip()
        for column in dataframe.columns
    }

    return [
        column
        for column in required
        if column not in actual
    ]


def numeric_value(value: Any, field: str) -> float:

    if pd.isna(value) or str(value).strip() == "":
        return 0.0

    try:
        return float(value)
    except Exception:
        raise ValueError(
            f"{field} must be numeric."
        )


if uploaded_file is not None:

    try:

        dataframe = read_uploaded_file(uploaded_file)

        missing = validate_columns(
            dataframe,
            expected_columns,
        )

        if missing:
            st.error(
                "Missing required columns: "
                + ", ".join(missing)
            )
            st.stop()

        st.success(
            f"{len(dataframe)} student record(s) loaded."
        )

        st.dataframe(
            dataframe,
            use_container_width=True,
            hide_index=True,
        )

    except Exception as exc:
        st.error("Unable to read the uploaded file.")
        st.exception(exc)
        st.stop()


# ------------------------------------------------------------
# Save imported marks
# ------------------------------------------------------------

if uploaded_file is not None:

    if st.button(
        "Validate and Save Marks",
        type="primary",
    ):

        errors = []
        prepared_rows: List[Dict[str, Any]] = []

        for index, row in dataframe.iterrows():

            excel_row = index + 2

            roll_number = str(
                row["Roll Number"]
            ).strip()

            student_name = str(
                row["Student Name"]
            ).strip()

            if not roll_number:
                errors.append(
                    f"Excel row {excel_row}: Roll Number is required."
                )
                continue

            if not student_name:
                errors.append(
                    f"Excel row {excel_row}: Student Name is required."
                )
                continue

            try:

                record = {
                    "student_id": roll_number,
                    "student_name": student_name,
                    "ce": None,
                    "ce_grade": None,
                    "s1": None,
                    "s2": None,
                    "record_work": None,
                    "mid1": None,
                    "mid2": None,
                    "continuous_evaluation": None,
                }

                if course_type in {
                    "Theory",
                    "Theory + Practical",
                }:

                    grade = normalize_grade(
                        row["CE Grade"]
                    )

                    if grade not in CE_GRADE_UPPER_PERCENT:
                        raise ValueError(
                            f"Invalid CE Grade '{row['CE Grade']}'."
                        )

                    record["ce_grade"] = grade
                    record["ce"] = grade_to_ce_mark(grade)

                    record["s1"] = numeric_value(
                        row["S1"],
                        "S1",
                    )

                    record["s2"] = numeric_value(
                        row["S2"],
                        "S2",
                    )

                if course_type == "Theory + Practical":

                    record["record_work"] = numeric_value(
                        row["Record Work"],
                        "Record Work",
                    )

                    record["mid1"] = numeric_value(
                        row["Mid 1"],
                        "Mid 1",
                    )

                    record["mid2"] = numeric_value(
                        row["Mid 2"],
                        "Mid 2",
                    )

                    if record["record_work"] > 60:
                        raise ValueError(
                            "Record Work cannot exceed 60."
                        )

                    if record["mid1"] > 20:
                        raise ValueError(
                            "Mid 1 cannot exceed 20."
                        )

                    if record["mid2"] > 20:
                        raise ValueError(
                            "Mid 2 cannot exceed 20."
                        )

                elif course_type in {
                    "Capstone Project",
                    "Internship",
                }:

                    record["continuous_evaluation"] = numeric_value(
                        row["Continuous Evaluation"],
                        "Continuous Evaluation",
                    )

                    maximum = (
                        100
                        if course_type == "Capstone Project"
                        else 50
                    )

                    if (
                        record["continuous_evaluation"]
                        > maximum
                    ):
                        raise ValueError(
                            f"Continuous Evaluation cannot exceed {maximum}."
                        )

                prepared_rows.append(record)

            except ValueError as exc:

                errors.append(
                    f"Excel row {excel_row}: {exc}"
                )

        if errors:

            st.error(
                f"{len(errors)} validation error(s) found."
            )

            for error in errors:
                st.error(error)

        else:

            try:

                conn = get_connection()
                cur = conn.cursor()

                for record in prepared_rows:

                    cur.execute(
                        """
                        SELECT id
                        FROM marks
                        WHERE course_id=?
                          AND student_id=?
                        """,
                        (
                            course_id,
                            record["student_id"],
                        ),
                    )

                    existing = cur.fetchone()

                    if existing:

                        cur.execute(
                            """
                            UPDATE marks
                            SET
                                student_name=?,
                                ce=?,
                                s1=?,
                                s2=?,
                                ce_grade=?,
                                record_work=?,
                                mid1=?,
                                mid2=?,
                                continuous_evaluation=?
                            WHERE course_id=?
                              AND student_id=?
                            """,
                            (
                                record["student_name"],
                                record["ce"],
                                record["s1"],
                                record["s2"],
                                record["ce_grade"],
                                record["record_work"],
                                record["mid1"],
                                record["mid2"],
                                record["continuous_evaluation"],
                                course_id,
                                record["student_id"],
                            ),
                        )

                    else:

                        cur.execute(
                            """
                            INSERT INTO marks(
                                course_id,
                                student_id,
                                student_name,
                                ce,
                                s1,
                                s2,
                                ce_grade,
                                record_work,
                                mid1,
                                mid2,
                                continuous_evaluation
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                course_id,
                                record["student_id"],
                                record["student_name"],
                                record["ce"],
                                record["s1"],
                                record["s2"],
                                record["ce_grade"],
                                record["record_work"],
                                record["mid1"],
                                record["mid2"],
                                record["continuous_evaluation"],
                            ),
                        )

                conn.commit()
                conn.close()

                st.success(
                    f"{len(prepared_rows)} student mark record(s) saved successfully."
                )

            except sqlite3.Error as exc:

                st.error(
                    "Database error while saving marks."
                )
                st.exception(exc)


# ------------------------------------------------------------
# Current Marks
# ------------------------------------------------------------

st.divider()
st.subheader("Current Student Marks")

current_marks = fetch_all(
    """
    SELECT
        student_id,
        student_name,
        ce_grade,
        ce,
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

if current_marks:

    display_rows = []

    for row in current_marks:

        item = {
            "Roll Number": row["student_id"],
            "Student Name": row["student_name"],
        }

        if course_type in {
            "Theory",
            "Theory + Practical",
        }:
            item["CE Grade"] = row["ce_grade"] or ""
            item["CE Mark (/25)"] = row["ce"]

            item["S1"] = row["s1"]
            item["S2"] = row["s2"]

        if course_type == "Theory + Practical":
            item["Record Work (/60)"] = row["record_work"]
            item["Mid 1 (/20)"] = row["mid1"]
            item["Mid 2 (/20)"] = row["mid2"]

        if course_type in {
            "Capstone Project",
            "Internship",
        }:
            maximum = (
                100
                if course_type == "Capstone Project"
                else 50
            )
            item[
                f"Continuous Evaluation (/{maximum})"
            ] = row["continuous_evaluation"]

        display_rows.append(item)

    st.dataframe(
        display_rows,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "No student marks have been entered for this Active Course."
    )


st.caption(
    "STEP 7 handles assessment data entry and CE grade conversion only. "
    "CO attainment and PO attainment calculations are not performed here."
)
