"""
OBE Analytics Pro v1.3
04_CO_PO_Mapping.py

CO-PO Mapping for the Active Course.

Current architecture:
    CO1-CO5  ->  PO1-PO12

Mapping level:
    0 = No Mapping
    1 = Low
    2 = Moderate
    3 = High

This module only stores CO-PO mapping.
It does not calculate CO attainment or PO attainment.

PSO1-PSO3 are maintained separately in the CO/PSO Entry module.
PSO mapping is not calculated in this module.
"""

from __future__ import annotations

import sqlite3
import pandas as pd
import streamlit as st

from database import (
    get_active_course,
    fetch_all,
    execute_query,
    get_connection,
)


# ------------------------------------------------------------
# Database: CO-PSO Mapping
# ------------------------------------------------------------

def ensure_pso_mapping_table() -> None:
    """Create the CO-PSO mapping table without altering existing data."""

    conn = get_connection()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS pso_mapping(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            co_no INTEGER NOT NULL,
            pso_no INTEGER NOT NULL,
            mapping_level INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(course_id) REFERENCES course(id),
            UNIQUE(course_id, co_no, pso_no)
        )
        """
    )

    conn.commit()
    conn.close()


ensure_pso_mapping_table()


# ------------------------------------------------------------
# Page Configuration
# ------------------------------------------------------------

st.set_page_config(
    page_title="CO-PO Mapping",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🔗 CO–PO Mapping")
st.divider()


# ------------------------------------------------------------
# Constants
# ------------------------------------------------------------

CO_NUMBERS = [1, 2, 3, 4, 5]
PO_NUMBERS = list(range(1, 13))
PSO_NUMBERS = [1, 2, 3]

MAPPING_LEVELS = {
    0: "No Mapping",
    1: "Low",
    2: "Moderate",
    3: "High",
}


# ------------------------------------------------------------
# Active Course
# ------------------------------------------------------------

course = get_active_course()

if course is None:
    st.warning(
        "Please select an Active Course from Course Management."
    )
    st.stop()

course_id = int(course["id"])

st.success(
    f"""
### Active Course

**Course Code :** {course["course_code"]}

**Course Name :** {course["course_name"]}

**Faculty :** {course["faculty"]}

**Semester :** {course["semester"]}

**Academic Year :** {course["academic_year"]}

**Course Type :** {course["course_type"] or "Theory"}
"""
)

st.divider()


# ------------------------------------------------------------
# Load Course Outcomes
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

co_map = {
    int(row["co_no"]): row
    for row in cos
    if row["co_no"] is not None
}

missing_cos = [
    f"CO{co_no}"
    for co_no in CO_NUMBERS
    if co_no not in co_map
]

if missing_cos:
    st.warning(
        "Please define all five Course Outcomes before creating "
        "CO–PO Mapping. Missing: "
        + ", ".join(missing_cos)
    )
    st.stop()


# ------------------------------------------------------------
# Course Outcomes
# ------------------------------------------------------------

st.subheader("Course Outcomes")

co_display = []

for co_no in CO_NUMBERS:
    row = co_map[co_no]

    co_display.append(
        {
            "CO": f"CO{co_no}",
            "Course Outcome": row["co_statement"] or "",
            "Bloom Level": row["bloom_level"] or "",
        }
    )

st.dataframe(
    co_display,
    use_container_width=True,
    hide_index=True,
)

st.divider()


# ------------------------------------------------------------
# Load Existing CO-PO Mapping
# ------------------------------------------------------------

saved_mappings = fetch_all(
    """
    SELECT
        co_no,
        po_no,
        mapping_level
    FROM mapping
    WHERE course_id=?
    ORDER BY co_no, po_no
    """,
    (course_id,),
)

existing_mapping = {}

for row in saved_mappings:
    try:
        existing_mapping[
            (
                int(row["co_no"]),
                int(row["po_no"]),
            )
        ] = int(row["mapping_level"])
    except (TypeError, ValueError):
        continue


# ------------------------------------------------------------
# CO-PO Mapping Matrix
# ------------------------------------------------------------

st.subheader("CO–PO Mapping Matrix")

st.caption(
    "Mapping level: 0 = No Mapping, 1 = Low, "
    "2 = Moderate, 3 = High."
)

matrix_data = []

for co_no in CO_NUMBERS:

    row = {
        "CO": f"CO{co_no}"
    }

    for po_no in PO_NUMBERS:
        row[f"PO{po_no}"] = existing_mapping.get(
            (co_no, po_no),
            0,
        )

    matrix_data.append(row)

mapping_df = pd.DataFrame(matrix_data)

edited_mapping = st.data_editor(
    mapping_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "CO": st.column_config.TextColumn(
            "CO",
            disabled=True,
        ),
        **{
            f"PO{po_no}": st.column_config.SelectboxColumn(
                f"PO{po_no}",
                options=[0, 1, 2, 3],
                help=(
                    "0 = No Mapping, 1 = Low, "
                    "2 = Moderate, 3 = High"
                ),
                required=True,
            )
            for po_no in PO_NUMBERS
        },
    },
    key="co_po_editor_v13",
)


# ------------------------------------------------------------
# Validate Mapping Values
# ------------------------------------------------------------

def validate_mapping(dataframe: pd.DataFrame) -> list[str]:

    errors = []

    for _, row in dataframe.iterrows():

        co_label = str(row["CO"])

        for po_no in PO_NUMBERS:

            value = row[f"PO{po_no}"]

            try:
                value = int(value)
            except (TypeError, ValueError):
                errors.append(
                    f"{co_label} → PO{po_no}: "
                    "mapping must be 0, 1, 2 or 3."
                )
                continue

            if value not in MAPPING_LEVELS:
                errors.append(
                    f"{co_label} → PO{po_no}: "
                    "mapping must be 0, 1, 2 or 3."
                )

    return errors


# ------------------------------------------------------------
# Save CO-PO Mapping
# ------------------------------------------------------------

st.divider()

if st.button(
    "💾 Save CO–PO Mapping",
    type="primary",
):

    validation_errors = validate_mapping(
        edited_mapping
    )

    if validation_errors:

        st.error(
            f"{len(validation_errors)} mapping error(s) found."
        )

        for error in validation_errors:
            st.error(error)

    else:

        try:

            # Save all mappings in one transaction.
            # The existing mapping table is retained.
            from database import get_connection

            conn = get_connection()

            try:

                conn.execute(
                    """
                    DELETE FROM mapping
                    WHERE course_id=?
                    """,
                    (course_id,),
                )

                for _, row in edited_mapping.iterrows():

                    co_no = int(
                        str(row["CO"]).replace("CO", "")
                    )

                    for po_no in PO_NUMBERS:

                        mapping_level = int(
                            row[f"PO{po_no}"]
                        )

                        conn.execute(
                            """
                            INSERT INTO mapping(
                                course_id,
                                co_no,
                                po_no,
                                mapping_level
                            )
                            VALUES (?, ?, ?, ?)
                            """,
                            (
                                course_id,
                                co_no,
                                po_no,
                                mapping_level,
                            ),
                        )

                conn.commit()

            finally:
                conn.close()

            st.success(
                "✅ CO–PO Mapping saved successfully."
            )

            st.rerun()

        except sqlite3.Error as exc:

            st.error(
                "Unable to save CO–PO Mapping because of "
                "a database error."
            )
            st.exception(exc)

        except Exception as exc:

            st.error(
                "Unable to save CO–PO Mapping."
            )
            st.exception(exc)


# ------------------------------------------------------------
# CO-PSO Mapping
# ------------------------------------------------------------

st.divider()
st.subheader("CO–PSO Mapping Matrix")

st.caption(
    "PSO mapping level: 0 = No Mapping, 1 = Low, "
    "2 = Moderate, 3 = High."
)

# Load PSOs for the Active Course.
psos = fetch_all(
    """
    SELECT
        pso_no,
        pso_statement
    FROM pso
    WHERE course_id=?
    ORDER BY pso_no
    """,
    (course_id,),
)

pso_map = {
    int(row["pso_no"]): row
    for row in psos
    if row["pso_no"] is not None
}

missing_psos = [
    f"PSO{pso_no}"
    for pso_no in PSO_NUMBERS
    if pso_no not in pso_map
]

if missing_psos:

    st.warning(
        "Please define all three PSOs before creating CO–PSO Mapping. "
        "Missing: " + ", ".join(missing_psos)
    )

else:

    pso_display = []

    for pso_no in PSO_NUMBERS:
        pso_display.append(
            {
                "PSO": f"PSO{pso_no}",
                "Program Specific Outcome": (
                    pso_map[pso_no]["pso_statement"] or ""
                ),
            }
        )

    st.markdown("### Program Specific Outcomes")

    st.dataframe(
        pso_display,
        use_container_width=True,
        hide_index=True,
    )

    # Load saved CO-PSO mapping.
    saved_pso_mappings = fetch_all(
        """
        SELECT
            co_no,
            pso_no,
            mapping_level
        FROM pso_mapping
        WHERE course_id=?
        ORDER BY co_no, pso_no
        """,
        (course_id,),
    )

    existing_pso_mapping = {}

    for row in saved_pso_mappings:
        try:
            existing_pso_mapping[
                (
                    int(row["co_no"]),
                    int(row["pso_no"]),
                )
            ] = int(row["mapping_level"])
        except (TypeError, ValueError):
            continue

    pso_matrix_data = []

    for co_no in CO_NUMBERS:

        row = {
            "CO": f"CO{co_no}"
        }

        for pso_no in PSO_NUMBERS:
            row[f"PSO{pso_no}"] = existing_pso_mapping.get(
                (co_no, pso_no),
                0,
            )

        pso_matrix_data.append(row)

    pso_mapping_df = pd.DataFrame(
        pso_matrix_data
    )

    edited_pso_mapping = st.data_editor(
        pso_mapping_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "CO": st.column_config.TextColumn(
                "CO",
                disabled=True,
            ),
            **{
                f"PSO{pso_no}": st.column_config.SelectboxColumn(
                    f"PSO{pso_no}",
                    options=[0, 1, 2, 3],
                    help=(
                        "0 = No Mapping, 1 = Low, "
                        "2 = Moderate, 3 = High"
                    ),
                    required=True,
                )
                for pso_no in PSO_NUMBERS
            },
        },
        key="co_pso_editor_v13",
    )

    if st.button(
        "💾 Save CO–PSO Mapping",
        type="primary",
    ):

        try:

            conn = get_connection()

            try:

                conn.execute(
                    """
                    DELETE FROM pso_mapping
                    WHERE course_id=?
                    """,
                    (course_id,),
                )

                for _, row in edited_pso_mapping.iterrows():

                    co_no = int(
                        str(row["CO"]).replace("CO", "")
                    )

                    for pso_no in PSO_NUMBERS:

                        mapping_level = int(
                            row[f"PSO{pso_no}"]
                        )

                        conn.execute(
                            """
                            INSERT INTO pso_mapping(
                                course_id,
                                co_no,
                                pso_no,
                                mapping_level
                            )
                            VALUES (?, ?, ?, ?)
                            """,
                            (
                                course_id,
                                co_no,
                                pso_no,
                                mapping_level,
                            ),
                        )

                conn.commit()

            finally:
                conn.close()

            st.success(
                "✅ CO–PSO Mapping saved successfully."
            )

            st.rerun()

        except sqlite3.Error as exc:

            st.error(
                "Unable to save CO–PSO Mapping because of "
                "a database error."
            )
            st.exception(exc)

        except Exception as exc:

            st.error(
                "Unable to save CO–PSO Mapping."
            )
            st.exception(exc)


# ------------------------------------------------------------
# CO-PSO Mapping Summary
# ------------------------------------------------------------

if not missing_psos:

    st.subheader("📊 CO–PSO Mapping Summary")

    pso_summary_data = []

    for co_no in CO_NUMBERS:

        mapped_count = 0
        high_count = 0

        for pso_no in PSO_NUMBERS:

            level = existing_pso_mapping.get(
                (co_no, pso_no),
                0,
            )

            if level > 0:
                mapped_count += 1

            if level == 3:
                high_count += 1

        pso_summary_data.append(
            {
                "CO": f"CO{co_no}",
                "Mapped PSOs": mapped_count,
                "High Mappings (3)": high_count,
            }
        )

    st.dataframe(
        pd.DataFrame(pso_summary_data),
        use_container_width=True,
        hide_index=True,
    )


# ------------------------------------------------------------
# Reset CO-PO Mapping
# ------------------------------------------------------------

st.divider()

st.subheader("Reset Mapping")

st.warning(
    "Reset will remove all CO–PO mappings for the Active Course."
)

if st.button(
    "🗑 Reset CO–PO Mapping",
):

    try:

        execute_query(
            """
            DELETE FROM mapping
            WHERE course_id=?
            """,
            (course_id,),
        )

        st.success(
            "CO–PO Mapping has been reset."
        )

        st.rerun()

    except Exception as exc:

        st.error(
            "Unable to reset CO–PO Mapping."
        )
        st.exception(exc)


# ------------------------------------------------------------
# Mapping Summary
# ------------------------------------------------------------

st.divider()

st.subheader("📊 Mapping Summary")

summary_data = []

for co_no in CO_NUMBERS:

    mapped_count = 0
    high_count = 0

    for po_no in PO_NUMBERS:

        level = existing_mapping.get(
            (co_no, po_no),
            0,
        )

        if level > 0:
            mapped_count += 1

        if level == 3:
            high_count += 1

    summary_data.append(
        {
            "CO": f"CO{co_no}",
            "Mapped POs": mapped_count,
            "High Mappings (3)": high_count,
        }
    )

summary_df = pd.DataFrame(summary_data)

st.dataframe(
    summary_df,
    use_container_width=True,
    hide_index=True,
)


# ------------------------------------------------------------
# PSO Status
# ------------------------------------------------------------

st.divider()

st.subheader("Program Specific Outcomes")

st.info(
    "PSO1–PSO3 are maintained in the CO/PSO Entry module. "
    "CO–PSO mapping is included here using the same 1/2/3 "
    "mapping scale."
)


st.caption(
    "CO–PO and CO–PSO Mapping only. CO attainment and PO "
    "attainment calculations are not performed in this module."
)
