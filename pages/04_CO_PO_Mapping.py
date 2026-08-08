"""
=========================================================
OBE Analytics
04_CO_PO_Mapping.py
CO-PO Mapping
=========================================================
"""

import streamlit as st
import pandas as pd

from database import (
    get_active_course,
    fetch_all,
    execute_query
)

# --------------------------------------------------------
# Page Configuration
# --------------------------------------------------------

st.set_page_config(
    page_title="CO-PO Mapping",
    page_icon="🔗",
    layout="wide"
)

st.title("🔗 CO–PO Mapping")

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
        "Please define all 5 Course Outcomes before creating CO–PO Mapping."
    )

    st.stop()

st.subheader("Course Outcomes")

for co in cos:

    st.write(
        f"**CO{co['co_no']}** — "
        f"{co['co_statement']} "
        f"({co['bloom_level']})"
    )

st.divider()

st.info(
    "Mapping values will be assigned in the next part."
)
# --------------------------------------------------------
# Load Existing CO-PO Mapping
# --------------------------------------------------------

saved_mappings = fetch_all(
    """
    SELECT
        co_no,
        po_no,
        mapping_level
    FROM mapping
    WHERE course_id=?
    """,
    (course["id"],)
)

existing_mapping = {}

for row in saved_mappings:

    existing_mapping[
        (
            int(row["co_no"]),
            int(row["po_no"])
        )
    ] = int(row["mapping_level"])
# --------------------------------------------------------
# CO-PO Mapping Matrix
# --------------------------------------------------------

st.subheader("CO–PO Mapping Matrix")

st.caption(
    "Enter mapping level: 0 = No Mapping, 1 = Low, "
    "2 = Moderate, 3 = High"
)

# Create matrix data

matrix_data = []

for co in cos:

    co_no = int(co["co_no"])

    row = {
        "CO": f"CO{co_no}"
    }

    for po in range(1, 13):

        row[f"PO{po}"] = existing_mapping.get(
            (co_no, po),
            0
        )

    matrix_data.append(row)

mapping_df = pd.DataFrame(matrix_data)

# Editable mapping matrix

edited_mapping = st.data_editor(
    mapping_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "CO": st.column_config.TextColumn(
            "CO",
            disabled=True
        )
    },
    disabled=["CO"],
    key="co_po_editor"
)
# --------------------------------------------------------
# Save CO-PO Mapping
# --------------------------------------------------------

st.divider()

if st.button(
    "💾 Save CO–PO Mapping",
    type="primary"
):

    try:

        # Remove existing mappings
        execute_query(
            """
            DELETE FROM mapping
            WHERE course_id=?
            """,
            (course["id"],)
        )

        # Save edited matrix
        for _, row in edited_mapping.iterrows():

            co_no = int(
                row["CO"].replace("CO", "")
            )

            for po_no in range(1, 13):

                mapping_level = int(
                    row[f"PO{po_no}"]
                )

                execute_query(
                    """
                    INSERT INTO mapping
                    (
                        course_id,
                        co_no,
                        po_no,
                        mapping_level
                    )
                    VALUES
                    (?, ?, ?, ?)
                    """,
                    (
                        course["id"],
                        co_no,
                        po_no,
                        mapping_level
                    )
                )

        st.success(
            "✅ CO–PO Mapping saved successfully."
        )

    except Exception as e:

        st.error(
            "Unable to save CO–PO Mapping."
        )

        st.exception(e)
# --------------------------------------------------------
# Reset CO-PO Mapping
# --------------------------------------------------------

st.divider()

st.subheader("Reset Mapping")

st.warning(
    "Reset will remove all CO–PO mappings for the active course."
)

if st.button("🗑 Reset CO–PO Mapping"):

    try:

        execute_query(
            """
            DELETE FROM mapping
            WHERE course_id=?
            """,
            (course["id"],)
        )

        st.success(
            "CO–PO Mapping has been reset."
        )

        st.rerun()

    except Exception as e:

        st.error(
            "Unable to reset CO–PO Mapping."
        )

        st.exception(e)
# --------------------------------------------------------
# Mapping Summary
# --------------------------------------------------------

st.divider()

st.subheader("📊 Mapping Summary")

summary_data = []

for co in cos:

    co_no = int(co["co_no"])

    mapped_count = 0
    high_count = 0

    for po in range(1, 13):

        level = existing_mapping.get(
            (co_no, po),
            0
        )

        if level > 0:
            mapped_count += 1

        if level == 3:
            high_count += 1

    summary_data.append(
        {
            "CO": f"CO{co_no}",
            "Mapped POs": mapped_count,
            "High Mappings (3)": high_count
        }
    )

summary_df = pd.DataFrame(summary_data)

st.dataframe(
    summary_df,
    use_container_width=True,
    hide_index=True
)