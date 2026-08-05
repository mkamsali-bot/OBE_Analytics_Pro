"""
Preview Module
OBE Analytics Pro v1.0.0
"""

import pandas as pd
import streamlit as st

from database import (
    get_course,
    get_all_cos,
    get_all_pos,
    get_mapping,
)

def show_preview():

    st.title("👁 OBE Preview")

    st.divider()

    # =====================================
    # Course Information
    # =====================================

    st.subheader("📘 Course Information")

    course = get_course()

    if course is None:
        st.warning("Course information not available.")
        return

    col1, col2 = st.columns(2)

    with col1:

        st.write(f"**Course Code :** {course['course_code']}")
        st.write(f"**Course Name :** {course['course_name']}")
        st.write(f"**Faculty :** {course['faculty']}")
        st.write(f"**Department :** {course['department']}")

    with col2:

        st.write(f"**Programme :** {course['programme']}")
        st.write(f"**Semester :** {course['semester']}")
        st.write(f"**Credits :** {course['credits']}")
        st.write(f"**Academic Year :** {course['academic_year']}")

    st.divider()

    # =====================================
    # Course Outcomes
    # =====================================

    st.subheader("🎯 Course Outcomes")

    rows = get_all_cos()

    data = []

    for row in rows:

        data.append({

            "CO No": row["co_no"],
            "Course Outcome": row["co_statement"],
            "Bloom Level": row["bloom_level"]

        })

    df = pd.DataFrame(data)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # =====================================
    # Program Outcomes
    # =====================================

    st.subheader("🎓 Program Outcomes")

    rows = get_all_pos()

    data = []

    for row in rows:

        data.append({

            "PO No": row["po_no"],
            "Program Outcome": row["po_statement"]

        })

    po_df = pd.DataFrame(data)

    st.dataframe(
        po_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # =====================================
    # CO-PO Mapping
    # =====================================

    st.subheader("🔗 CO–PO Mapping")

    cos = get_all_cos()
if not rows:
    st.info("No Course Outcomes available.")
else:
    data = []

    for row in rows:
        data.append({
            "CO No": row["co_no"],
            "Course Outcome": row["co_statement"],
            "Bloom Level": row["bloom_level"]
        })

    df = pd.DataFrame(data)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    pos = get_all_pos()
    mappings = get_mapping()

    mapping_data = []

    for co in cos:

        row = {"CO": co["co_no"]}

        for po in pos:
            row[po["po_no"]] = 0

        mapping_data.append(row)

    mapping_df = pd.DataFrame(mapping_data)

    for item in mappings:

        mapping_df.loc[
            mapping_df["CO"] == item["co_no"],
            item["po_no"]
        ] = item["level"]

    st.dataframe(
        mapping_df,
        use_container_width=True,
        hide_index=True
    )