"""
=========================================================
OBE Analytics Pro v1.3
03_Student_Marks.py
Student Marks
=========================================================

Step 2:
    Theory + Practical assessment entry.

Theory:
    Roll Number | Student Name | CE | S1 | S2

Theory + Practical:
    Roll Number | Student Name | CE | S1 | S2 |
    Record Work | Mid 1 | Mid 2

Practical:
    Record Work = 60 marks
    Mid 1       = 20 marks
    Mid 2       = 20 marks
    Total       = 100 marks

Practical CO distribution is fixed for the next
calculation step:
    Record Work -> CO1-CO5 equally
    Mid 1       -> CO1-CO2 equally
    Mid 2       -> CO3-CO5 equally

IMPORTANT:
    This step stores the practical marks only.
    The 70:30 calculation and CO attainment changes
    are NOT implemented yet.
=========================================================
"""

import streamlit as st
import pandas as pd
from io import BytesIO

from database import (
    get_active_course,
    fetch_one,
    fetch_dataframe,
    execute_query
)


# -------------------------------------------------------
# Page Configuration
# -------------------------------------------------------

st.set_page_config(
    page_title="Student Marks",
    page_icon="📝",
    layout="wide"
)

st.title("📝 Student Marks")
st.divider()


# -------------------------------------------------------
# Active Course
# -------------------------------------------------------

course = get_active_course()

if course is None:

    st.warning(
        "Please select an Active Course from the Course page."
    )

    st.stop()


course_type = (
    course["course_type"]
    if "course_type" in course.keys()
    and course["course_type"]
    else "Theory"
)

st.success(
    f"""
### Active Course

**Course Code :** {course['course_code']}

**Course Name :** {course['course_name']}

**Course Type :** {course_type}

**Faculty :** {course['faculty']}

**Semester :** {course['semester']}

**Academic Year :** {course['academic_year']}
"""
)

st.divider()


# -------------------------------------------------------
# Prepare Practical Columns
# -------------------------------------------------------

try:

    columns = fetch_dataframe(
        "PRAGMA table_info(marks)"
    )

    existing_columns = set(
        columns["name"].tolist()
    )

    practical_columns = {
        "record_work": "REAL DEFAULT 0",
        "practical_mid1": "REAL DEFAULT 0",
        "practical_mid2": "REAL DEFAULT 0"
    }

    for column_name, column_definition in practical_columns.items():

        if column_name not in existing_columns:

            execute_query(
                f"""
                ALTER TABLE marks
                ADD COLUMN {column_name} {column_definition}
                """
            )

except Exception as e:

    st.error(
        "Unable to prepare Practical Marks fields."
    )

    st.exception(e)

    st.stop()


# -------------------------------------------------------
# Entry Mode
# -------------------------------------------------------

entry_mode = st.radio(
    "Select Entry Mode",
    [
        "Manual Entry",
        "Upload Excel"
    ],
    horizontal=True
)


# =======================================================
# MANUAL ENTRY
# =======================================================

if entry_mode == "Manual Entry":

    st.subheader(
        "Manual Student Entry"
    )

    with st.form("student_form"):

        col1, col2 = st.columns(2)

        # ------------------------------------------------
        # Student Details
        # ------------------------------------------------

        with col1:

            roll_no = st.text_input(
                "Roll Number"
            )

            student_name = st.text_input(
                "Student Name"
            )

        # ------------------------------------------------
        # Theory Marks
        # ------------------------------------------------

        with col2:

            ce = st.number_input(
                f"CE ({course['ce_max']})",
                min_value=0.0,
                max_value=float(course["ce_max"]),
                value=0.0,
                step=0.5
            )

            s1 = st.number_input(
                f"S1 ({course['s1_max']})",
                min_value=0.0,
                max_value=float(course["s1_max"]),
                value=0.0,
                step=0.5
            )

            s2 = st.number_input(
                f"S2 ({course['s2_max']})",
                min_value=0.0,
                max_value=float(course["s2_max"]),
                value=0.0,
                step=0.5
            )

        # ------------------------------------------------
        # Practical Marks
        # ------------------------------------------------

        if course_type == "Theory + Practical":

            st.divider()

            st.subheader(
                "Practical Component"
            )

            p1, p2, p3 = st.columns(3)

            with p1:

                record_work = st.number_input(
                    "Record Work (60)",
                    min_value=0.0,
                    max_value=60.0,
                    value=0.0,
                    step=0.5
                )

            with p2:

                practical_mid1 = st.number_input(
                    "Practical Mid 1 (20)",
                    min_value=0.0,
                    max_value=20.0,
                    value=0.0,
                    step=0.5
                )

            with p3:

                practical_mid2 = st.number_input(
                    "Practical Mid 2 (20)",
                    min_value=0.0,
                    max_value=20.0,
                    value=0.0,
                    step=0.5
                )

            practical_total = (
                record_work
                + practical_mid1
                + practical_mid2
            )

            st.info(
                f"Practical Total = "
                f"{practical_total:.2f} / 100"
            )

        else:

            record_work = 0.0
            practical_mid1 = 0.0
            practical_mid2 = 0.0

        # ------------------------------------------------
        # Theory Total
        # ------------------------------------------------

        theory_total = ce + s1 + s2

        st.info(
            f"Theory Total = {theory_total:.2f}"
        )

        save_student = st.form_submit_button(
            "💾 Save Student"
        )

    # ---------------------------------------------------
    # Save Student
    # ---------------------------------------------------

    if save_student:

        if roll_no.strip() == "":

            st.error(
                "Roll Number is required."
            )

        elif student_name.strip() == "":

            st.error(
                "Student Name is required."
            )

        else:

            student = fetch_one(
                """
                SELECT *
                FROM marks
                WHERE course_id=?
                AND student_id=?
                """,
                (
                    course["id"],
                    roll_no.strip()
                )
            )

            try:

                if student is not None:

                    if course_type == "Theory + Practical":

                        execute_query(
                            """
                            UPDATE marks
                            SET
                                student_name=?,
                                ce=?,
                                s1=?,
                                s2=?,
                                record_work=?,
                                practical_mid1=?,
                                practical_mid2=?
                            WHERE course_id=?
                            AND student_id=?
                            """,
                            (
                                student_name.strip(),
                                ce,
                                s1,
                                s2,
                                record_work,
                                practical_mid1,
                                practical_mid2,
                                course["id"],
                                roll_no.strip()
                            )
                        )

                        st.success(
                            "Existing student updated successfully."
                        )

                    else:

                        st.warning(
                            "Roll Number already exists."
                        )

                else:

                    execute_query(
                        """
                        INSERT INTO marks
                        (
                            course_id,
                            student_id,
                            student_name,
                            ce,
                            s1,
                            s2,
                            record_work,
                            practical_mid1,
                            practical_mid2
                        )
                        VALUES
                        (
                            ?,?,?,?,?,?,?,?,?
                        )
                        """,
                        (
                            course["id"],
                            roll_no.strip(),
                            student_name.strip(),
                            ce,
                            s1,
                            s2,
                            record_work,
                            practical_mid1,
                            practical_mid2
                        )
                    )

                    st.success(
                        "Student saved successfully."
                    )

            except Exception as e:

                st.error(
                    "Unable to save student."
                )

                st.exception(e)


# =======================================================
# EXCEL UPLOAD
# =======================================================

else:

    st.subheader(
        "📂 Upload Student Marks"
    )

    if course_type == "Theory":

        required_columns = [
            "Roll Number",
            "Student Name",
            "CE",
            "S1",
            "S2"
        ]

        st.info(
            "Theory Excel columns: "
            "Roll Number, Student Name, CE, S1, S2"
        )

    elif course_type == "Theory + Practical":

        required_columns = [
            "Roll Number",
            "Student Name",
            "CE",
            "S1",
            "S2",
            "Record Work",
            "Mid 1",
            "Mid 2"
        ]

        st.info(
            "Theory + Practical Excel columns: "
            "Roll Number, Student Name, CE, S1, S2, "
            "Record Work, Mid 1, Mid 2"
        )

    else:

        required_columns = [
            "Roll Number",
            "Student Name"
        ]

        st.info(
            "Student identity can be uploaded now. "
            "Assessment rules for Capstone Project and "
            "Internship will be added later."
        )

    # ---------------------------------------------------
    # Template
    # ---------------------------------------------------

    template = pd.DataFrame(
        columns=required_columns
    )

    template_buffer = BytesIO()

    with pd.ExcelWriter(
        template_buffer,
        engine="openpyxl"
    ) as writer:

        template.to_excel(
            writer,
            index=False,
            sheet_name="Student Marks"
        )

    st.download_button(
        "⬇️ Download Excel Template",
        data=template_buffer.getvalue(),
        file_name=(
            "Theory_Practical_Student_Marks_Template.xlsx"
            if course_type == "Theory + Practical"
            else "Student_Marks_Template.xlsx"
        ),
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )

    uploaded_file = st.file_uploader(
        "Choose Excel File",
        type=["xlsx"]
    )

    if uploaded_file is not None:

        try:

            df = pd.read_excel(
                uploaded_file
            )

            # -------------------------------------------
            # Column Validation
            # -------------------------------------------

            missing_columns = [
                column
                for column in required_columns
                if column not in df.columns
            ]

            if missing_columns:

                st.error(
                    "Missing required Excel columns: "
                    + ", ".join(missing_columns)
                )

                st.stop()

            # Keep only required columns.
            df = df[
                required_columns
            ].copy()

            # -------------------------------------------
            # Roll Number Cleaning
            # -------------------------------------------

            df["Roll Number"] = (
                df["Roll Number"]
                .astype(str)
                .str.strip()
                .str.replace(
                    ".0",
                    "",
                    regex=False
                )
            )

            df["Student Name"] = (
                df["Student Name"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

            # -------------------------------------------
            # Blank Student Validation
            # -------------------------------------------

            invalid_identity = df[
                (df["Roll Number"] == "")
                |
                (df["Student Name"] == "")
                |
                (df["Roll Number"].str.lower() == "nan")
            ]

            if not invalid_identity.empty:

                st.error(
                    f"{len(invalid_identity)} row(s) have "
                    "invalid Roll Number or Student Name."
                )

                st.stop()

            # -------------------------------------------
            # Numeric Validation
            # -------------------------------------------

            numeric_columns = [
                "CE",
                "S1",
                "S2"
            ]

            if course_type == "Theory + Practical":

                numeric_columns.extend(
                    [
                        "Record Work",
                        "Mid 1",
                        "Mid 2"
                    ]
                )

            for column in numeric_columns:

                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce"
                )

                if df[column].isna().any():

                    bad_rows = int(
                        df[column].isna().sum()
                    )

                    st.error(
                        f"{bad_rows} row(s) have invalid "
                        f"or blank marks in '{column}'."
                    )

                    st.stop()

            # -------------------------------------------
            # Range Validation
            # -------------------------------------------

            ranges = {
                "CE": float(course["ce_max"]),
                "S1": float(course["s1_max"]),
                "S2": float(course["s2_max"])
            }

            if course_type == "Theory + Practical":

                ranges.update(
                    {
                        "Record Work": 60.0,
                        "Mid 1": 20.0,
                        "Mid 2": 20.0
                    }
                )

            invalid_range_rows = set()

            for column, maximum in ranges.items():

                bad = df[
                    (df[column] < 0)
                    |
                    (df[column] > maximum)
                ]

                invalid_range_rows.update(
                    bad.index.tolist()
                )

            if invalid_range_rows:

                st.error(
                    f"{len(invalid_range_rows)} row(s) contain "
                    "marks outside the allowed range."
                )

                st.stop()

            # -------------------------------------------
            # Duplicate Roll Numbers Inside Excel
            # -------------------------------------------

            excel_duplicates = (
                df[
                    df["Roll Number"].duplicated(
                        keep=False
                    )
                ]["Roll Number"]
                .unique()
                .tolist()
            )

            if excel_duplicates:

                st.error(
                    "Duplicate Roll Numbers found inside "
                    "the uploaded Excel file:"
                )

                st.write(
                    sorted(excel_duplicates)
                )

                st.stop()

            st.success(
                f"{len(df)} row(s) loaded."
            )

            st.success(
                "Excel data passed validation."
            )

            # -------------------------------------------
            # Existing Database Roll Numbers
            # -------------------------------------------

            existing_df = fetch_dataframe(
                """
                SELECT student_id
                FROM marks
                WHERE course_id=?
                """,
                (
                    course["id"],
                )
            )

            existing_roll_numbers = set(
                existing_df["student_id"]
                .astype(str)
                .str.strip()
                .tolist()
            )

            upload_roll_numbers = set(
                df["Roll Number"]
                .tolist()
            )

            duplicate_database = (
                upload_roll_numbers
                & existing_roll_numbers
            )

            new_roll_numbers = (
                upload_roll_numbers
                - existing_roll_numbers
            )

            # -------------------------------------------
            # Duplicate Display
            # -------------------------------------------

            if duplicate_database:

                if course_type == "Theory + Practical":

                    st.warning(
                        f"{len(duplicate_database)} student(s) "
                        "already exist. Their Practical marks "
                        "will be updated."
                    )

                else:

                    st.warning(
                        f"{len(duplicate_database)} student(s) "
                        "already exist and will be skipped."
                    )

            st.info(
                f"{len(new_roll_numbers)} new student(s) "
                "are ready to import."
            )

            # -------------------------------------------
            # Preview
            # -------------------------------------------

            st.subheader(
                "Preview"
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            # -------------------------------------------
            # Import
            # -------------------------------------------

            if st.button(
                "⬆️ Import Student Marks",
                type="primary"
            ):

                imported = 0
                updated = 0
                skipped = 0

                try:

                    for _, row in df.iterrows():

                        roll = str(
                            row["Roll Number"]
                        ).strip()

                        name = str(
                            row["Student Name"]
                        ).strip()

                        existing = fetch_one(
                            """
                            SELECT id
                            FROM marks
                            WHERE course_id=?
                            AND student_id=?
                            """,
                            (
                                course["id"],
                                roll
                            )
                        )

                        if existing is not None:

                            if course_type == "Theory + Practical":

                                execute_query(
                                    """
                                    UPDATE marks
                                    SET
                                        student_name=?,
                                        ce=?,
                                        s1=?,
                                        s2=?,
                                        record_work=?,
                                        practical_mid1=?,
                                        practical_mid2=?
                                    WHERE course_id=?
                                    AND student_id=?
                                    """,
                                    (
                                        name,
                                        float(row["CE"]),
                                        float(row["S1"]),
                                        float(row["S2"]),
                                        float(row["Record Work"]),
                                        float(row["Mid 1"]),
                                        float(row["Mid 2"]),
                                        course["id"],
                                        roll
                                    )
                                )

                                updated += 1

                            else:

                                skipped += 1

                            continue

                        execute_query(
                            """
                            INSERT INTO marks
                            (
                                course_id,
                                student_id,
                                student_name,
                                ce,
                                s1,
                                s2,
                                record_work,
                                practical_mid1,
                                practical_mid2
                            )
                            VALUES
                            (
                                ?,?,?,?,?,?,?,?,?
                            )
                            """,
                            (
                                course["id"],
                                roll,
                                name,
                                float(row["CE"]),
                                float(row["S1"]),
                                float(row["S2"]),
                                (
                                    float(row["Record Work"])
                                    if course_type
                                    == "Theory + Practical"
                                    else 0.0
                                ),
                                (
                                    float(row["Mid 1"])
                                    if course_type
                                    == "Theory + Practical"
                                    else 0.0
                                ),
                                (
                                    float(row["Mid 2"])
                                    if course_type
                                    == "Theory + Practical"
                                    else 0.0
                                )
                            )
                        )

                        imported += 1

                    st.success(
                        "Student marks imported successfully."
                    )

                    st.write(
                        f"New students imported: {imported}"
                    )

                    if course_type == "Theory + Practical":

                        st.write(
                            f"Existing students updated: {updated}"
                        )

                    else:

                        st.write(
                            f"Existing students skipped: {skipped}"
                        )

                except Exception as e:

                    st.error(
                        "Unable to import student marks."
                    )

                    st.exception(e)


        except Exception as e:

            st.error(
                "Unable to process the uploaded Excel file."
            )

            st.exception(e)
# =======================================================
# SAVED STUDENTS
# =======================================================

st.divider()

st.subheader(
    "### Student Records"
)

students = fetch_dataframe(
    """
    SELECT
        id,
        student_id,
        student_name,
        ce,
        s1,
        s2,
        record_work,
        practical_mid1,
        practical_mid2
    FROM marks
    WHERE course_id=?
    ORDER BY student_id
    """,
    (
        course["id"],
    )
)

if students.empty:

    st.info(
        "No student records found."
    )

else:

    students["Theory Total"] = (
        students["ce"]
        + students["s1"]
        + students["s2"]
    )

    if course_type == "Theory + Practical":

        students["Practical Total"] = (
            students["record_work"]
            + students["practical_mid1"]
            + students["practical_mid2"]
        )

        display = students[
            [
                "student_id",
                "student_name",
                "ce",
                "s1",
                "s2",
                "Theory Total",
                "record_work",
                "practical_mid1",
                "practical_mid2",
                "Practical Total"
            ]
        ].copy()

        display.columns = [
            "Roll No",
            "Student Name",
            "CE",
            "S1",
            "S2",
            "Theory Total",
            "Record Work",
            "Practical Mid 1",
            "Practical Mid 2",
            "Practical Total"
        ]

    else:

        display = students[
            [
                "student_id",
                "student_name",
                "ce",
                "s1",
                "s2",
                "Theory Total"
            ]
        ].copy()

        display.columns = [
            "Roll No",
            "Student Name",
            "CE",
            "S1",
            "S2",
            "Total"
        ]

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True
    )


# =======================================================
# DELETE STUDENT
# =======================================================

if not students.empty:

    st.divider()

    st.subheader(
        "Delete Student"
    )

    student_options = (
        students["student_id"].astype(str)
        + " - "
        + students["student_name"].astype(str)
    )

    option = st.selectbox(
        "Select Student",
        student_options
    )

    if st.button(
        "🗑 Delete Student"
    ):

        selected = students[
            student_options == option
        ]

        execute_query(
            """
            DELETE FROM marks
            WHERE id=?
            """,
            (
                int(
                    selected.iloc[0]["id"]
                ),
            )
        )

        st.success(
            "Student deleted successfully."
        )

        st.rerun()
