"""
CO Distribution
OBE Analytics Pro v1.1.2
"""

import streamlit as st
import pandas as pd

from database.co_distribution import (
    get_courses,
    get_distribution,
    save_distribution,
    delete_distribution,
)

st.title("📘 CO Distribution")
st.caption("Assessment-wise CO Marks Distribution")

# -------------------------------------------------
# Load Courses
# -------------------------------------------------

courses = get_courses()

if not courses:
    st.warning("No courses found. Please create a course first.")
    st.stop()

course_dict = {
    f"{c[0]} - {c[1]}": c[0]
    for c in courses
}

selected = st.selectbox(
    "Select Course",
    list(course_dict.keys())
)

course_code = course_dict[selected]

# -------------------------------------------------
# Load Existing Distribution
# -------------------------------------------------

rows = get_distribution(course_code)

if rows:

    df = pd.DataFrame(
        rows,
        columns=[
            "Assessment",
            "CO",
            "Marks"
        ]
    )

else:

    df = pd.DataFrame(
        columns=[
            "Assessment",
            "CO",
            "Marks"
        ]
    )

# -------------------------------------------------
# Editable Table
# -------------------------------------------------

edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    column_config={
        "Assessment": st.column_config.SelectboxColumn(
            "Assessment",
            options=[
                "Assignment",
                "Quiz",
                "Mid-1",
                "Mid-2",
                "Lab",
                "End Semester"
            ],
        ),
        "CO": st.column_config.SelectboxColumn(
            "CO",
            options=[
                "CO1","CO2","CO3",
                "CO4","CO5","CO6"
            ],
        ),
        "Marks": st.column_config.NumberColumn(
            "Marks",
            min_value=0,
            step=1
        ),
    },
)

col1, col2 = st.columns(2)

with col1:
    save = st.button(
        "💾 Save Distribution",
        use_container_width=True
    )

with col2:
    clear = st.button(
        "🗑 Clear Distribution",
        use_container_width=True
    )

# -------------------------------------------------
# Save
# -------------------------------------------------

if save:

    data = []

    for _, row in edited_df.iterrows():

        if row["Assessment"] and row["CO"]:

            data.append(
                (
                    row["Assessment"],
                    row["CO"],
                    int(row["Marks"])
                )
            )

    save_distribution(course_code, data)

    st.success("Distribution saved successfully.")

    st.rerun()

# -------------------------------------------------
# Delete
# -------------------------------------------------

if clear:

    delete_distribution(course_code)

    st.success("Distribution deleted successfully.")

    st.rerun()

# -------------------------------------------------
# Preview
# -------------------------------------------------

st.divider()

st.subheader("Saved Distribution")

st.dataframe(
    edited_df,
    use_container_width=True,
    hide_index=True
)

st.metric(
    "Total Entries",
    len(edited_df)
)