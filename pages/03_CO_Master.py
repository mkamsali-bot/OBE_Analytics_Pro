"""
CO Master
OBE Analytics Pro v1.1.2
"""

import streamlit as st
import pandas as pd

from database import (
    save_all_cos,
    get_all_cos,
    delete_all_cos,
)

# ---------------------------------------------------------
# PAGE TITLE
# ---------------------------------------------------------

st.title("📗 CO Master")
st.caption("Create and maintain Course Outcomes")

# ---------------------------------------------------------
# LOAD EXISTING DATA
# ---------------------------------------------------------

rows = get_all_cos()

if rows:

    df = pd.DataFrame(
        rows,
        columns=[
            "CO No",
            "CO Statement",
            "Bloom Level"
        ]
    )

else:

    df = pd.DataFrame({
        "CO No":[
            "CO1",
            "CO2",
            "CO3",
            "CO4",
            "CO5",
            "CO6",
        ],
        "CO Statement":[""]*6,
        "Bloom Level":["L1"]*6
    })

    # ---------------------------------------------------------
# EDITABLE TABLE
# ---------------------------------------------------------

edited_df = st.data_editor(
    df,
    use_container_width=True,
    hide_index=True,
    num_rows="fixed",
    key="co_editor"
)

st.divider()

col1, col2 = st.columns(2)

with col1:

    save = st.button(
        "💾 Save All COs",
        use_container_width=True
    )

with col2:

    clear = st.button(
        "🗑 Clear All",
        use_container_width=True
    )

# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

if save:

    data = []

    for _, row in edited_df.iterrows():

        data.append(
            (
                row["CO No"],
                row["CO Statement"],
                row["Bloom Level"]
            )
        )

    save_all_cos(data)

    st.success("Course Outcomes saved successfully.")

    st.rerun()

# ---------------------------------------------------------
# DELETE
# ---------------------------------------------------------

if clear:

    delete_all_cos()

    st.success("All Course Outcomes deleted.")

    st.rerun()

# ---------------------------------------------------------
# PREVIEW
# ---------------------------------------------------------

st.divider()

st.subheader("Current Course Outcomes")

st.dataframe(
    edited_df,
    use_container_width=True,
    hide_index=True
)

st.metric(
    "Total COs",
    len(edited_df)
)