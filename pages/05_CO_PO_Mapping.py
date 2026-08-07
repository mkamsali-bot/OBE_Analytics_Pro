"""
CO-PO Mapping
OBE Analytics Pro v1.2 RC2
"""

import streamlit as st
import pandas as pd

from database import (
    get_all_cos,
    get_all_pos,
    save_mapping,
    get_mapping,
    delete_mapping,
    get_course,
)

st.title("📕 CO-PO Mapping")
st.caption("Map Course Outcomes with Program Outcomes")

# ---------------------------------------------------------
# CURRENT COURSE
# ---------------------------------------------------------

course = get_course()

if course is None:
    st.warning("Please create a course first.")
    st.stop()

course_code = course[0]

st.info(f"Course : {course_code}")

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

cos = get_all_cos(course_code)
pos = get_all_pos()

co_list = [row[0] for row in cos]
po_list = [row[0] for row in pos]

saved = get_mapping(course_code)

if saved:

    df = pd.DataFrame(
        saved,
        columns=[
            "CO",
            "PO",
            "Level",
        ],
    )

else:

    df = pd.DataFrame(
        columns=[
            "CO",
            "PO",
            "Level",
        ]
    )


# ---------------------------------------------------------
# EDITOR
# ---------------------------------------------------------

edited_df = st.data_editor(
    df,
    column_config={
        "CO": st.column_config.SelectboxColumn(
            "CO",
            options=co_list,
        ),
        "PO": st.column_config.SelectboxColumn(
            "PO",
            options=po_list,
        ),
        "Level": st.column_config.SelectboxColumn(
            "Level",
            options=[0, 1, 2, 3],
        ),
    },
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
)

st.divider()

col1, col2 = st.columns(2)

with col1:

    save = st.button(
        "💾 Save Mapping",
        use_container_width=True,
    )

with col2:

    clear = st.button(
        "🗑 Clear Mapping",
        use_container_width=True,
    )

#
# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

if save:

    data = []

    for _, row in edited_df.iterrows():

        if (
            pd.isna(row["CO"])
            or pd.isna(row["PO"])
            or pd.isna(row["Level"])
        ):
            continue

        data.append(
            (
                str(row["CO"]),
                str(row["PO"]),
                int(float(row["Level"])),
            )
        )

    st.write("Rows to be saved:")
    st.write(data)

    save_mapping(course_code, data)
    st.write("Rows to be saved:")
    st.write(data)

    
    st.success("CO-PO Mapping saved successfully.")

    st.rerun()

# ---------------------------------------------------------
# DELETE
# ---------------------------------------------------------

if clear:

    delete_mapping(course_code)

    st.success("All mappings deleted.")

    st.rerun()

# ---------------------------------------------------------
# PREVIEW
# ---------------------------------------------------------

st.divider()

st.subheader("Current Mapping")

st.dataframe(
    edited_df,
    use_container_width=True,
    hide_index=True,
)

st.metric(
    "Total Mappings",
    len(edited_df),
)